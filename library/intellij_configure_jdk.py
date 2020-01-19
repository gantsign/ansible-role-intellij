#!/usr/bin/python

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: intellij_configure_jdk

short_description: Configures the specified JDK for the given IntelliJ user.

description:
    - Configures the specified JDK for the given IntelliJ user.

options:
    intellij_user_dir:
        description:
            - This is the dir where the user's IntelliJ configuration is located.
        required: true
    jdk_name:
        description:
            - This is the name of the JDK to use in the IntelliJ configuration.
        required: true
    jdk_home:
        description:
            - This is the path to the JDK home.
        required: true
    owner:
        description:
            - The user who you're configuring IntelliJ for.
        required: true
    group:
        description:
            - The group for the files and directories created.
        required: true

author:
    - John Freeman (GantSign Ltd.)
'''

EXAMPLES = '''
- name: configure JDKs
  become: yes
  become_user: bob
  intellij_configure_jdk:
    intellij_user_dir: '.IntelliJIdea2018.1'
    jdk_name: '1.8'
    jdk_home: '/opt/java/jdk/1.8'
    owner: bob
    group: bob
'''

import os
import grp
import pwd
import xml.sax.saxutils
import zipfile
from distutils.version import LooseVersion

from ansible.module_utils._text import to_bytes, to_native
from ansible.module_utils.basic import AnsibleModule

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False


def pretty_print(elem):
    text = etree.tostring(elem, encoding='iso-8859-1')
    parser = etree.XMLParser(remove_blank_text=True)
    xml = etree.fromstring(text, parser)
    return etree.tostring(
        xml, encoding='iso-8859-1', pretty_print=True, xml_declaration=False)


def get_java_version(module, jdk_home):
    executable = os.path.join(jdk_home, 'bin', 'java')
    if not os.path.isfile(executable):
        module.fail_json(msg='File not found: %s' % executable)

    rc, out, err = module.run_command([executable, '-version'])
    if rc != 0:
        module.fail_json(msg='Error while querying Java version: %s' % (
            out + err))
    return err.splitlines()[0]


def get_class_path(module, jdk_home):
    jre_lib = os.path.join(jdk_home, 'jre', 'lib')

    jre_ext = os.path.join(jre_lib, 'ext')

    jmods = os.path.join(jdk_home, 'jmods')

    if os.path.isdir(jre_ext):

        files = [os.path.join(jre_lib, x) for x in os.listdir(jre_lib)]
        files = files + [os.path.join(jre_ext, x) for x in os.listdir(jre_ext)]

        files = [x for x in files if os.path.isfile(x) and x.endswith('.jar')]

        files = sorted(files)

        urls = ['jar://%s!/' % x for x in files]

        elements = [
            '<root url=%s type="simple" />' % xml.sax.saxutils.quoteattr(x)
            for x in urls
        ]

        return "\n".join(elements)

    elif os.path.isdir(jmods):

        files = [os.path.join(jmods, x) for x in os.listdir(jmods)]

        files = [x for x in files if os.path.isfile(x) and x.endswith('.jmod')]

        module_names = [os.path.basename(x)[:-5] for x in files]

        module_names = sorted(module_names)

        urls = ['jrt://%s!/%s' % (jdk_home, x) for x in module_names]

        elements = [
            '<root url=%s type="simple" />' % xml.sax.saxutils.quoteattr(x)
            for x in urls
        ]
        return "\n".join(elements)

    else:
        module.fail_json(msg=("Unsupported JDK directory layout: %s. If you're "
                              "using Java > 9 you may need to install the "
                              "jmods package e.g. yum install "
                              "java-11-openjdk-jmods.") % jdk_home)


def get_source_path(module, jdk_home):
    jmod_src = os.path.join(jdk_home, 'lib', 'src.zip')

    if os.path.isfile(jmod_src):

        with zipfile.ZipFile(jmod_src, 'r') as srczip:
            files = srczip.namelist()

        files = [x for x in files if x.endswith('/module-info.java')]

        module_names = [x[:-len('/module-info.java')] for x in files]

        module_names = sorted(module_names)

        urls = [
            'jar://%s/lib/src.zip!/%s' % (jdk_home, x) for x in module_names
        ]

        elements = [
            '<root url=%s type="simple" />' % xml.sax.saxutils.quoteattr(x)
            for x in urls
        ]
        return "\n".join(elements)

    elif os.path.isdir(jdk_home):

        files = [os.path.join(jdk_home, x) for x in os.listdir(jdk_home)]

        files = [
            x for x in files if os.path.isfile(x) and x.endswith('src.zip')
        ]

        files = sorted(files)

        urls = ['jar://%s!/' % x for x in files]

        elements = [
            '<root url=%s type="simple" />' % xml.sax.saxutils.quoteattr(x)
            for x in urls
        ]

        return "\n".join(elements)

    else:
        module.fail_json(msg='Directory not found: %s' % jdk_home)


def create_jdk_xml(module, intellij_user_dir, jdk_name, jdk_home):
    params = {
        'jdk_name':
        xml.sax.saxutils.quoteattr(jdk_name),
        'java_version':
        xml.sax.saxutils.quoteattr(get_java_version(module, jdk_home)),
        'jdk_home':
        xml.sax.saxutils.quoteattr(jdk_home),
        'class_path':
        get_class_path(module, jdk_home),
        'source_path':
        get_source_path(module, jdk_home)
    }

    return etree.fromstring('''
    <jdk version="2">
      <name value=%(jdk_name)s />
      <type value="JavaSDK" />
      <version value=%(java_version)s />
      <homePath value=%(jdk_home)s />
      <roots>
        <annotationsPath>
          <root type="composite">
            <root url="jar://$APPLICATION_HOME_DIR$/lib/jdkAnnotations.jar!/" type="simple" />
          </root>
        </annotationsPath>
        <classPath>
          <root type="composite">%(class_path)s</root>
        </classPath>
        <javadocPath>
          <root type="composite" />
        </javadocPath>
        <sourcePath>
          <root type="composite">%(source_path)s</root>
        </sourcePath>
      </roots>
      <additional />
    </jdk>''' % params)


def make_dirs(path, mode, uid, gid):
    dirs = [path]
    dirname = os.path.dirname(path)
    while dirname != '/':
        dirs.insert(0, dirname)
        dirname = os.path.dirname(dirname)

    for dirname in dirs:
        if not os.path.exists(dirname):
            os.mkdir(dirname, mode)
            os.chown(dirname, uid, gid)


def configure_jdk(module, intellij_user_dir, jdk_name, jdk_home, uid, gid):
    options_dir = os.path.join(intellij_user_dir, 'config', 'options')

    project_default_path = os.path.join(options_dir, 'jdk.table.xml')

    if (not os.path.isfile(project_default_path)
       ) or os.path.getsize(project_default_path) == 0:
        if not module.check_mode:
            if not os.path.isdir(options_dir):
                make_dirs(options_dir, 0o775, uid, gid)

            if not os.path.isfile(project_default_path):
                with open(project_default_path, 'wb', 0o664) as xml_file:
                    xml_file.write(to_bytes(''))
                os.chown(project_default_path, uid, gid)

        jdk_table_root = etree.Element('application')
        jdk_table_doc = etree.ElementTree(jdk_table_root)
        before = ''
    else:
        jdk_table_doc = etree.parse(project_default_path)
        jdk_table_root = jdk_table_doc.getroot()
        before = pretty_print(jdk_table_root)

    if jdk_table_root.tag != 'application':
        module.fail_json(
            msg='Unsupported root element: %s' % jdk_table_root.tag)

    project_jdk_table = jdk_table_root.find(
        './component[@name="ProjectJdkTable"]')
    if project_jdk_table is None:
        project_jdk_table = etree.SubElement(
            jdk_table_root, 'component', name='ProjectJdkTable')

    new_jdk = create_jdk_xml(module, intellij_user_dir, jdk_name, jdk_home)
    new_jdk_string = pretty_print(new_jdk)

    old_jdk = project_jdk_table.find('./jdk/name[@value="%s"]/..' % jdk_name)
    if old_jdk is None:
        old_jdk_string = ''
        changed = True
        project_jdk_table.append(new_jdk)
    else:
        old_jdk_string = pretty_print(old_jdk)
        changed = old_jdk_string != new_jdk_string
        if changed:
            project_jdk_table.replace(old_jdk, new_jdk)

    after = pretty_print(jdk_table_root)

    if changed and not module.check_mode:
        with open(project_default_path, 'wb') as xml_file:
            xml_file.write(to_bytes(after))

    return changed, {'before:': before, 'after': after}


def run_module():

    module_args = dict(
        intellij_user_dir=dict(type='str', required=True),
        jdk_name=dict(type='str', required=True),
        jdk_home=dict(type='str', required=True),
        owner=dict(type='str', required=True),
        group=dict(type='str', required=True))

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    owner = module.params['owner']
    group = module.params['group']

    try:
        uid = int(owner)
    except ValueError:
        uid = pwd.getpwnam(owner).pw_uid
    username = pwd.getpwuid(uid).pw_name

    try:
        gid = int(group)
    except ValueError:
        gid = grp.getgrnam(group).gr_gid

    intellij_user_dir = os.path.expanduser(
        os.path.join('~' + username, module.params['intellij_user_dir']))
    jdk_name = module.params['jdk_name']
    jdk_home = os.path.expanduser(module.params['jdk_home'])

    # Check if we have lxml 2.3.0 or newer installed
    if not HAS_LXML:
        module.fail_json(
            msg=
            'The xml ansible module requires the lxml python library installed on the managed machine'
        )
    elif LooseVersion('.'.join(
            to_native(f) for f in etree.LXML_VERSION)) < LooseVersion('2.3.0'):
        module.fail_json(
            msg=
            'The xml ansible module requires lxml 2.3.0 or newer installed on the managed machine'
        )
    elif LooseVersion('.'.join(
            to_native(f) for f in etree.LXML_VERSION)) < LooseVersion('3.0.0'):
        module.warn(
            'Using lxml version lower than 3.0.0 does not guarantee predictable element attribute order.'
        )

    changed, diff = configure_jdk(module, intellij_user_dir, jdk_name, jdk_home, uid, gid)

    if changed:
        msg = 'JDK %s has been configured' % jdk_name
    else:
        msg = 'JDK %s was already configured' % jdk_name

    module.exit_json(changed=changed, msg=msg, diff=diff)


def main():
    run_module()


if __name__ == '__main__':
    main()
