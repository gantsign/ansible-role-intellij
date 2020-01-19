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
module: intellij_set_default_inspection_profile

short_description: Set the default inspection profile for the given IntelliJ user.

description:
    - Set the default inspection profile for the given IntelliJ user.

options:
    intellij_user_dir:
        description:
            - This is the dir where the user's IntelliJ configuration is located.
        required: true
    profile_name:
        description:
            - This is the name of the inspection profile given in the configuration.
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
- name: set default inspection profile
  become: yes
  become_user: bob
  intellij_set_default_inspection_profile:
    intellij_user_dir: '.IntelliJIdea2018.1'
    profile_name: 'Acme'
    owner: bob
    group: bob
'''

import os
import grp
import pwd
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


def set_option(elem, key, value):
    option = elem.find('./option[@name="%s"]' % key)
    if option is None:
        option = etree.SubElement(elem, 'option', name=key)

    if option.attrib.get('value', None) == value:
        return False

    option.set('value', value)
    return True


def set_version(elem, value):
    version = elem.find('./version')
    if version is None:
        version = etree.SubElement(elem, 'version', value=value)

    if version.attrib.get('value', None) == value:
        return False

    version.set('value', value)
    return True


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


def set_default_inspection_profile(module, intellij_user_dir, profile_name, uid, gid):
    options_dir = os.path.join(intellij_user_dir, 'config', 'options')

    project_default_path = os.path.join(options_dir, 'project.default.xml')

    if (not os.path.isfile(project_default_path)
       ) or os.path.getsize(project_default_path) == 0:
        if not module.check_mode:
            if not os.path.isdir(options_dir):
                make_dirs(options_dir, 0o775, uid, gid)

            if not os.path.isfile(project_default_path):
                with open(project_default_path, 'wb', 0o664) as xml_file:
                    xml_file.write('')
                os.chown(project_default_path, uid, gid)

        project_default_root = etree.Element('application')
        project_default_doc = etree.ElementTree(project_default_root)
        before = ''
    else:
        project_default_doc = etree.parse(project_default_path)
        project_default_root = project_default_doc.getroot()
        before = pretty_print(project_default_root)

    if project_default_root.tag != 'application':
        module.fail_json(
            msg='Unsupported root element: %s' % project_default_root.tag)

    project_manager = project_default_root.find(
        './component[@name="ProjectManager"]')
    if project_manager is None:
        project_manager = etree.SubElement(
            project_default_root, 'component', name='ProjectManager')

    default_project = project_manager.find('./defaultProject')
    if default_project is None:
        default_project = etree.SubElement(project_manager, 'defaultProject')

    profile_manager = default_project.find(
        './component[@name="InspectionProjectProfileManager"]')
    if profile_manager is None:
        profile_manager = etree.SubElement(
            default_project, 'component', name='InspectionProjectProfileManager')

    changed = True in [
        set_option(profile_manager, 'PROJECT_PROFILE', profile_name),
        set_option(profile_manager, 'USE_PROJECT_PROFILE', 'false'),
        set_version(profile_manager, '1.0')
    ]

    after = pretty_print(project_default_root)

    if changed and not module.check_mode:
        with open(project_default_path, 'wb') as xml_file:
            xml_file.write(to_bytes(after))

    return changed, {'before:': before, 'after': after}


def run_module():

    module_args = dict(
        intellij_user_dir=dict(type='str', required=True),
        profile_name=dict(type='str', required=True),
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
    profile_name = os.path.expanduser(module.params['profile_name'])

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

    changed, diff = set_default_inspection_profile(module, intellij_user_dir, profile_name, uid, gid)

    if changed:
        msg = '%s is now the default inspection profile' % profile_name
    else:
        msg = '%s is already the default inspection profile' % profile_name

    module.exit_json(changed=changed, msg=msg, diff=diff)


def main():
    run_module()


if __name__ == '__main__':
    main()
