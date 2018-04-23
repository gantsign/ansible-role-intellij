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
module: intellij_set_default_jdk

short_description: Set the default JDK for the given IntelliJ user.

description:
    - Set the default JDK for the given IntelliJ user.

options:
    intellij_user_dir:
        description:
            - This is the dir where the user's IntelliJ configuration is located.
        required: true
    jdk_name:
        description:
            - This is the name of the JDK given in the configuration.
        required: true

author:
    - John Freeman (GantSign Ltd.)
'''

EXAMPLES = '''
- name: set default JDK
  become: yes
  become_user: bob
  intellij_set_default_jdk:
    intellij_user_dir: '.IntelliJIdea2018.1'
    jdk_name: '1.8'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native
from distutils.version import LooseVersion
import os

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


def set_attrib(elem, key, value):
    if elem.attrib.get(key, None) == value:
        return False

    elem.set(key, value)
    return True


def jdk_home(module, intellij_user_dir, jdk_name):
    jdk_table_path = os.path.join(
        '~', intellij_user_dir, 'config', 'options', 'jdk.table.xml')
    b_jdk_table_path = os.path.expanduser(to_bytes(jdk_table_path))
    if not os.path.isfile(b_jdk_table_path):
        module.fail_json(msg='File not found: %s' % jdk_table_path)

    jdk_table_doc = etree.parse(b_jdk_table_path)

    jdk = jdk_table_doc.find(
        './component[@name="ProjectJdkTable"]/jdk/name[@value="%s"]/..' % jdk_name)
    if jdk is None:
        module.fail_json(
            msg='Unable to find JDK with name "%s" in jdk.table.xml' % jdk_name)

    path_node = jdk.find('./homePath')
    if path_node is None:
        module.fail_json(
            msg='Invalid XML: homePath missing for JDK: %s' % jdk_name)

    path = path_node.attrib.get('value', None)
    if path is None:
        module.fail_json(
            msg='Invalid XML: homePath/@value missing for JDK: %s' % jdk_name)

    return path


def specification_version(module, jdk_home):
    executable = os.path.join(jdk_home, 'bin', 'jrunscript')
    b_executable = os.path.expanduser(to_bytes(executable))
    if not os.path.isfile(b_executable):
        module.fail_json(msg='File not found: %s' % executable)

    rc, out, err = module.run_command(
        [b_executable, '-e', 'print(java.lang.System.getProperty("java.specification.version"))'])
    if rc != 0 or err:
        module.fail_json(
            msg='Error while querying Java specification version: %s' % (out + err))
    return out.strip()


def set_default_jdk(module, intellij_user_dir, jdk_name):
    options_dir = os.path.join('~', intellij_user_dir, 'config', 'options')
    b_options_dir = os.path.expanduser(to_bytes(options_dir))

    project_default_path = os.path.join(options_dir, 'project.default.xml')
    b_project_default_path = os.path.expanduser(to_bytes(project_default_path))

    if (not os.path.isfile(b_project_default_path)) or os.path.getsize(b_project_default_path) == 0:
        if not module.check_mode:
            if not os.path.isdir(b_options_dir):
                os.makedirs(b_options_dir, 0o775)

            if not os.path.isfile(b_project_default_path):
                with open(b_project_default_path, 'wb', 0o664) as xml_file:
                    xml_file.write('')

        project_default_root = etree.Element('application')
        project_default_doc = etree.ElementTree(project_default_root)
        b_before = ''
    else:
        project_default_doc = etree.parse(b_project_default_path)
        project_default_root = project_default_doc.getroot()
        b_before = pretty_print(project_default_root)

    if project_default_root.tag != 'application':
        module.fail_json(msg='Unsupported root element: %s' %
                         project_default_root.tag)

    project_manager = project_default_root.find(
        './component[@name="ProjectManager"]')
    if project_manager is None:
        project_manager = etree.SubElement(
            project_default_root, 'component', name='ProjectManager')

    default_project = project_manager.find('./defaultProject')
    if default_project is None:
        default_project = etree.SubElement(project_manager, 'defaultProject')

    project_root_manager = default_project.find(
        './component[@name="ProjectRootManager"]')
    if project_root_manager is None:
        project_root_manager = etree.SubElement(
            default_project, 'component', name='ProjectRootManager')

    default_jdk_home = jdk_home(module, intellij_user_dir, jdk_name)
    language_level = specification_version(module, default_jdk_home)

    changed = True in [
        set_attrib(project_root_manager, 'version', '2'),
        set_attrib(project_root_manager, 'languageLevel',
                   'JDK_%s' % language_level),
        set_attrib(project_root_manager, 'default', 'true'),
        set_attrib(project_root_manager, 'assert-keyword', 'true'),
        set_attrib(project_root_manager, 'jdk-15', 'true'),
        set_attrib(project_root_manager, 'project-jdk-name', jdk_name),
        set_attrib(project_root_manager, 'project-jdk-type', 'JavaSDK')
    ]

    b_after = pretty_print(project_default_root)

    if changed and not module.check_mode:
        with open(b_project_default_path, 'wb') as xml_file:
            xml_file.write(b_after)

    return changed, {'before:': b_before, 'after': b_after}


def run_module():

    module_args = dict(
        intellij_user_dir=dict(type='str', required=True),
        jdk_name=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    intellij_user_dir = module.params['intellij_user_dir']
    jdk_name = module.params['jdk_name']

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

    changed, diff = set_default_jdk(module, intellij_user_dir, jdk_name)

    if changed:
        msg = '%s is now the default JDK' % jdk_name
    else:
        msg = '%s is already the default JDK' % jdk_name

    module.exit_json(changed=changed, msg=msg, diff=diff)


def main():
    run_module()


if __name__ == '__main__':
    main()
