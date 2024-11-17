#!/usr/bin/env python3

import grp
import os
import pwd
from pathlib import Path
from typing import Dict, Tuple

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.compat.version import LooseVersion

DOCUMENTATION = '''
---
module: intellij_set_default_maven

short_description: >
    Set the default Maven installation for the given IntelliJ user.

description:
    - Set the default Maven installation for the given IntelliJ user.

options:
    intellij_user_config_dir:
        description:
            - >
                This is the dir where the user's IntelliJ configuration is
                located.
        required: true
    maven_home:
        description:
            - This is the path to the default Maven installation.
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
- name: Set default Maven
  become: yes
  become_user: bob
  intellij_set_default_maven:
    intellij_user_config_dir: '.IntelliJIdea2018.1'
    maven_home: '/opt/maven/apache-maven-3.5.3'
    owner: bob
    group: bob
'''

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False


def pretty_print(elem: etree.Element) -> str:
    text = etree.tostring(elem, encoding='unicode')
    parser = etree.XMLParser(remove_blank_text=True)
    xml = etree.fromstring(text, parser)
    return etree.tostring(xml, encoding='unicode', pretty_print=True, xml_declaration=False)


def set_attrib(elem: etree.Element, key: str, value: str) -> bool:
    if elem.attrib.get(key, None) == value:
        return False

    elem.set(key, value)
    return True


def make_dirs(path: Path, mode: int, uid: int, gid: int) -> None:
    dirs_to_create = []

    while not path.exists():
        dirs_to_create.append(path)
        if path.parent == path:
            # Reached the root directory
            break
        path = path.parent

    dirs_to_create.reverse()

    for dir_path in dirs_to_create:
        if not dir_path.exists():
            dir_path.mkdir(mode=mode, exist_ok=True)
            os.chown(str(dir_path), uid, gid)


def set_default_maven(module: AnsibleModule, intellij_user_config_dir: Path, maven_home: Path, uid: int, gid: int) -> Tuple[bool, Dict[str, str]]:

    options_dir = intellij_user_config_dir / 'options'
    project_default_path = options_dir / 'project.default.xml'

    create_project_default = (not project_default_path.is_file()) or project_default_path.stat().st_size == 0

    if create_project_default:
        if not module.check_mode:
            if not options_dir.is_dir():
                make_dirs(options_dir, 0o775, uid, gid)

            if not project_default_path.is_file():
                project_default_path.touch(mode=0o664)
                os.chown(str(project_default_path), uid, gid)

        project_default_root = etree.Element('application')
        project_default_doc = etree.ElementTree(project_default_root)
        before = ''
    else:
        project_default_doc = etree.parse(str(project_default_path))
        project_default_root = project_default_doc.getroot()
        before = pretty_print(project_default_root)

    if project_default_root.tag != 'application':
        module.fail_json(msg=f'Unsupported root element: {project_default_root.tag}')

    project_manager = project_default_root.find('./component[@name="ProjectManager"]')
    if project_manager is None:
        project_manager = etree.SubElement(project_default_root, 'component', name='ProjectManager')

    default_project = project_manager.find('./defaultProject')
    if default_project is None:
        default_project = etree.SubElement(project_manager, 'defaultProject')

    mvn_import_prefs = default_project.find('./component[@name="MavenImportPreferences"]')
    if mvn_import_prefs is None:
        mvn_import_prefs = etree.SubElement(default_project, 'component', name='MavenImportPreferences')

    general_settings = mvn_import_prefs.find('./option[@name="generalSettings"]')
    if general_settings is None:
        general_settings = etree.SubElement(mvn_import_prefs, 'option', name='generalSettings')

    mvn_general_settings = general_settings.find('./MavenGeneralSettings')
    if mvn_general_settings is None:
        mvn_general_settings = etree.SubElement(general_settings, 'MavenGeneralSettings')

    mvn_home_option = mvn_general_settings.find('./option[@name="mavenHome"]')
    if mvn_home_option is None:
        mvn_home_option = etree.SubElement(mvn_general_settings, 'option', name='mavenHome')

    changed = set_attrib(mvn_home_option, 'value', str(maven_home.expanduser()))

    after = pretty_print(project_default_root)

    if changed and not module.check_mode:
        project_default_path.write_text(after, encoding='iso-8859-1')

    return changed, {'before': before, 'after': after}


def run_module() -> None:

    module_args = dict(
        intellij_user_config_dir=dict(type='str', required=True),
        maven_home=dict(type='str', required=True),
        owner=dict(type='str', required=True),
        group=dict(type='str', required=True)
    )

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

    intellij_user_config_dir = Path('~' + username).expanduser() / module.params['intellij_user_config_dir']
    maven_home = Path(module.params['maven_home']).expanduser()

    # Check if we have lxml 2.3.0 or newer installed
    if not HAS_LXML:
        module.fail_json(msg='The xml ansible module requires the lxml python library installed on the managed machine')
    else:
        lxml_version = LooseVersion('.'.join(str(f) for f in etree.LXML_VERSION))
        if lxml_version < LooseVersion('2.3.0'):
            module.fail_json(msg='The xml ansible module requires lxml 2.3.0 or newer installed on the managed machine')
        elif lxml_version < LooseVersion('3.0.0'):
            module.warn('Using lxml version lower than 3.0.0 does not guarantee predictable element attribute order.')

    changed, diff = set_default_maven(module, intellij_user_config_dir, maven_home, uid, gid)

    if changed:
        msg = '%s is now the default Maven installation' % maven_home
    else:
        msg = '%s is already the default Maven installation' % maven_home

    module.exit_json(changed=changed, msg=msg, diff=diff)


def main() -> None:
    run_module()


if __name__ == '__main__':
    main()
