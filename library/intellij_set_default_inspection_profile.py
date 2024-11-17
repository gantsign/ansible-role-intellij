import grp
import os
import pwd
from pathlib import Path
from typing import Dict, Tuple

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.compat.version import LooseVersion

DOCUMENTATION = '''
---
module: intellij_set_default_inspection_profile

short_description: >
    Set the default inspection profile for the given IntelliJ user.

description:
    - Set the default inspection profile for the given IntelliJ user.

options:
    intellij_user_config_dir:
        description:
            - >
                This is the dir where the user's IntelliJ configuration is
                located.
        required: true
    profile_name:
        description:
            - >
                This is the name of the inspection profile given in the
                configuration.
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
- name: Set default inspection profile
  become: yes
  become_user: bob
  intellij_set_default_inspection_profile:
    intellij_user_config_dir: '.IntelliJIdea2018.1/config'
    profile_name: 'Acme'
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


def set_option(elem: etree.Element, key: str, value: str) -> bool:
    option = elem.find(f'./option[@name="{key}"]')
    if option is None:
        option = etree.SubElement(elem, 'option', name=key)

    if option.attrib.get('value') == value:
        return False

    option.set('value', value)
    return True


def set_version(elem: etree.Element, value: str) -> bool:
    version = elem.find('./version')
    if version is None:
        version = etree.SubElement(elem, 'version', value=value)

    if version.attrib.get('value') == value:
        return False

    version.set('value', value)
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


def set_default_inspection_profile(
    module: AnsibleModule,
    intellij_user_config_dir: Path,
    profile_name: str,
    uid: int,
    gid: int
) -> Tuple[bool, Dict[str, str]]:
    options_dir = intellij_user_config_dir / 'options'
    project_default_path = options_dir / 'project.default.xml'

    create_project_default = (
        not project_default_path.is_file()
        or project_default_path.stat().st_size == 0
    )
    if create_project_default:
        if not module.check_mode:
            if not options_dir.is_dir():
                make_dirs(options_dir, 0o775, uid, gid)

            if not project_default_path.is_file():
                project_default_path.touch()
                os.chown(project_default_path, uid, gid)
                project_default_path.chmod(0o664)

        project_default_root = etree.Element('application')
        before = ''
    else:
        project_default_root = etree.parse(str(project_default_path)).getroot()
        before = pretty_print(project_default_root)

    if project_default_root.tag != 'application':
        module.fail_json(msg=f'Unsupported root element: {project_default_root.tag}')

    project_manager = project_default_root.find('./component[@name="ProjectManager"]')
    if project_manager is None:
        project_manager = etree.SubElement(project_default_root, 'component', name='ProjectManager')

    default_project = project_manager.find('./defaultProject')
    if default_project is None:
        default_project = etree.SubElement(project_manager, 'defaultProject')

    profile_manager = default_project.find('./component[@name="InspectionProjectProfileManager"]')
    if profile_manager is None:
        profile_manager = etree.SubElement(default_project, 'component', name='InspectionProjectProfileManager')

    changed = any([
        set_option(profile_manager, 'PROJECT_PROFILE', profile_name),
        set_option(profile_manager, 'USE_PROJECT_PROFILE', 'false'),
        set_version(profile_manager, '1.0')
    ])

    after = pretty_print(project_default_root)

    if changed and not module.check_mode:
        project_default_path.write_text(after, encoding='iso-8859-1')

    return changed, {'before': before, 'after': after}


def run_module() -> None:

    module_args = dict(
        intellij_user_config_dir=dict(type='str', required=True),
        profile_name=dict(type='str', required=True),
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

    intellij_user_config_dir = Path(f'~{username}', module.params['intellij_user_config_dir']).expanduser()
    profile_name = module.params['profile_name']

    # Check if we have lxml 2.3.0 or newer installed
    if not HAS_LXML:
        module.fail_json(msg='The xml ansible module requires the lxml python library installed on the managed machine')
    else:
        lxml_version = LooseVersion('.'.join(str(f) for f in etree.LXML_VERSION))
        if lxml_version < LooseVersion('2.3.0'):
            module.fail_json(msg='The xml ansible module requires lxml 2.3.0 or newer installed on the managed machine')
        elif lxml_version < LooseVersion('3.0.0'):
            module.warn('Using lxml version lower than 3.0.0 does not guarantee predictable element attribute order.')

    changed, diff = set_default_inspection_profile(module, intellij_user_config_dir, profile_name, uid, gid)

    if changed:
        msg = f'{profile_name} is now the default inspection profile'
    else:
        msg = f'{profile_name} is already the default inspection profile'

    module.exit_json(changed=changed, msg=msg, diff=diff)


def main() -> None:
    run_module()


if __name__ == '__main__':
    main()
