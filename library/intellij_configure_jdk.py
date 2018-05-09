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
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native
from distutils.version import LooseVersion
import os
import xml.sax.saxutils
import zipfile

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False


def pretty_print(elem):
    text = etree.tostring(elem, encoding='iso-8859-1')
    parser = etree.XMLParser(remove_blank_text=True)
    xml = etree.fromstring(text, parser)
    return etree.tostring(xml, encoding='iso-8859-1', pretty_print=True, xml_declaration=False)


def get_java_version(module, jdk_home):
    executable = os.path.join(jdk_home, 'bin', 'java')
    b_executable = os.path.expanduser(to_bytes(executable))
    if not os.path.isfile(b_executable):
        module.fail_json(msg='File not found: %s' % executable)

    rc, out, err = module.run_command([b_executable, '-version'])
    if rc != 0:
        module.fail_json(
            msg='Error while querying Java version: %s' % (out + err))
    return err.splitlines()[0]


def get_class_path(module, jdk_home):
    jre_lib = os.path.join(jdk_home, 'jre', 'lib')
    b_jre_lib = os.path.expanduser(to_bytes(jre_lib))

    jre_ext = os.path.join(jre_lib, 'ext')
    b_jre_ext = os.path.expanduser(to_bytes(jre_ext))

    jmods = os.path.join(jdk_home, 'jmods')
    b_jmods = os.path.expanduser(to_bytes(jmods))

    if os.path.isdir(b_jre_ext):

        b_files = [os.path.join(b_jre_lib, x) for x in os.listdir(b_jre_lib)]
        b_files = b_files + [os.path.join(b_jre_ext, x)
                             for x in os.listdir(b_jre_ext)]

        b_files = [x for x in b_files if os.path.isfile(
            x) and to_native(x).endswith('.jar')]

        files = [to_native(x) for x in b_files]

        files = sorted(files)

        urls = ['jar://%s!/' % x for x in files]

        elements = ['<root url=%s type="simple" />' %
                    xml.sax.saxutils.quoteattr(x) for x in urls]

        return "\n".join(elements)

    elif os.path.isdir(b_jmods):

        b_files = [os.path.join(b_jmods, x) for x in os.listdir(b_jmods)]

        b_files = [x for x in b_files if os.path.isfile(
            x) and to_native(x).endswith('.jmod')]

        module_names = [to_native(os.path.basename(x)[:-5]) for x in b_files]

        module_names = sorted(module_names)

        urls = ['jrt://%s!/%s' % (jdk_home, x) for x in module_names]

        elements = ['<root url=%s type="simple" />' %
                    xml.sax.saxutils.quoteattr(x) for x in urls]
        return "\n".join(elements)

    else:
        module.fail_json(msg='Unsupported JDK directory layout: %s' % jdk_home)


def get_source_path(module, jdk_home):
    b_jdk_home = os.path.expanduser(to_bytes(jdk_home))

    jmod_src = os.path.join(jdk_home, 'lib', 'src.zip')
    b_jmod_src = os.path.expanduser(to_bytes(jmod_src))

    if os.path.isfile(b_jmod_src):

        with zipfile.ZipFile(to_native(b_jmod_src), 'r') as srczip:
            files = srczip.namelist()

        files = [x for x in files if x.endswith('/module-info.java')]

        module_names = [x[:-len('/module-info.java')] for x in files]

        module_names = sorted(module_names)

        urls = ['jar://%s/lib/src.zip!/%s' %
                (jdk_home, x) for x in module_names]

        elements = ['<root url=%s type="simple" />' %
                    xml.sax.saxutils.quoteattr(x) for x in urls]
        return "\n".join(elements)

    elif os.path.isdir(b_jdk_home):

        b_files = [os.path.join(b_jdk_home, x) for x in os.listdir(b_jdk_home)]

        b_files = [x for x in b_files if os.path.isfile(
            x) and to_native(x).endswith('src.zip')]

        files = [to_native(x) for x in b_files]

        files = sorted(files)

        urls = ['jar://%s!/' % x for x in files]

        elements = ['<root url=%s type="simple" />' %
                    xml.sax.saxutils.quoteattr(x) for x in urls]

        return "\n".join(elements)

    else:
        module.fail_json(msg='Unsupported JDK directory layout: %s' % jdk_home)


def create_jdk_xml(module, intellij_user_dir, jdk_name, jdk_home):
    params = {
        'jdk_name': xml.sax.saxutils.quoteattr(jdk_name),
        'java_version': xml.sax.saxutils.quoteattr(get_java_version(module, jdk_home)),
        'jdk_home': xml.sax.saxutils.quoteattr(jdk_home),
        'class_path': get_class_path(module, jdk_home),
        'source_path': get_source_path(module, jdk_home)
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


def configure_jdk(module, intellij_user_dir, jdk_name, jdk_home):
    options_dir = os.path.join('~', intellij_user_dir, 'config', 'options')
    b_options_dir = os.path.expanduser(to_bytes(options_dir))

    project_default_path = os.path.join(options_dir, 'jdk.table.xml')
    b_project_default_path = os.path.expanduser(to_bytes(project_default_path))

    if (not os.path.isfile(b_project_default_path)) or os.path.getsize(b_project_default_path) == 0:
        if not module.check_mode:
            if not os.path.isdir(b_options_dir):
                os.makedirs(b_options_dir, 0o775)

            if not os.path.isfile(b_project_default_path):
                with open(b_project_default_path, 'wb', 0o664) as xml_file:
                    xml_file.write(to_bytes(''))

        jdk_table_root = etree.Element('application')
        jdk_table_doc = etree.ElementTree(jdk_table_root)
        b_before = ''
    else:
        jdk_table_doc = etree.parse(b_project_default_path)
        jdk_table_root = jdk_table_doc.getroot()
        b_before = pretty_print(jdk_table_root)

    if jdk_table_root.tag != 'application':
        module.fail_json(msg='Unsupported root element: %s' %
                         jdk_table_root.tag)

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

    b_after = pretty_print(jdk_table_root)

    if changed and not module.check_mode:
        with open(b_project_default_path, 'wb') as xml_file:
            xml_file.write(b_after)

    return changed, {'before:': b_before, 'after': b_after}


def run_module():

    module_args = dict(
        intellij_user_dir=dict(type='str', required=True),
        jdk_name=dict(type='str', required=True),
        jdk_home=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    intellij_user_dir = module.params['intellij_user_dir']
    jdk_name = module.params['jdk_name']
    jdk_home = module.params['jdk_home']

    # Check if we have lxml 2.3.0 or newer installed
    if not HAS_LXML:
        module.fail_json(
            msg='The xml ansible module requires the lxml python library installed on the managed machine')
    elif LooseVersion('.'.join(to_native(f) for f in etree.LXML_VERSION)) < LooseVersion('2.3.0'):
        module.fail_json(
            msg='The xml ansible module requires lxml 2.3.0 or newer installed on the managed machine')
    elif LooseVersion('.'.join(to_native(f) for f in etree.LXML_VERSION)) < LooseVersion('3.0.0'):
        module.warn(
            'Using lxml version lower than 3.0.0 does not guarantee predictable element attribute order.')

    changed, diff = configure_jdk(
        module, intellij_user_dir, jdk_name, jdk_home)

    if changed:
        msg = 'JDK %s has been configured' % jdk_name
    else:
        msg = 'JDK %s was already configured' % jdk_name

    module.exit_json(changed=changed, msg=msg, diff=diff)


def main():
    run_module()


if __name__ == '__main__':
    main()
