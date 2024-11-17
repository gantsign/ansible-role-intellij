import grp
import os
import pwd
import tempfile
from pathlib import Path
from typing import Any, Dict, Tuple

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.compat.version import LooseVersion

DOCUMENTATION = '''
---
module: intellij_set_default_jdk

short_description: Set the default JDK for the given IntelliJ user.

description:
    - Set the default JDK for the given IntelliJ user.

options:
    intellij_user_config_dir:
        description:
            - >
                This is the dir where the user's IntelliJ configuration is
                located.
        required: true
    jdk_name:
        description:
            - This is the name of the JDK given in the configuration.
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
- name: Set default JDK
  become: yes
  become_user: bob
  intellij_set_default_jdk:
    intellij_user_config_dir: '.IntelliJIdea2018.1/config'
    jdk_name: '1.8'
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
    if elem.attrib.get(key) == value:
        return False

    elem.set(key, value)
    return True


def jdk_home(module: AnsibleModule, intellij_user_config_dir: Path, jdk_name: str) -> Path:
    jdk_table_path = intellij_user_config_dir / 'options' / 'jdk.table.xml'
    if not jdk_table_path.is_file():
        module.fail_json(msg=f'File not found: {jdk_table_path}')

    jdk_table_doc = etree.parse(str(jdk_table_path))
    jdk = jdk_table_doc.find(f'./component[@name="ProjectJdkTable"]/jdk/name[@value="{jdk_name}"]/..')
    if jdk is None:
        module.fail_json(msg=f'Unable to find JDK with name "{jdk_name}" in jdk.table.xml')

    path_node = jdk.find('./homePath')
    if path_node is None:
        module.fail_json(msg=f'Invalid XML: homePath missing for JDK: {jdk_name}')

    path = path_node.attrib.get('value')
    if path is None:
        module.fail_json(msg=f'Invalid XML: homePath/@value missing for JDK: {jdk_name}')

    return Path(path)


def specification_version(module: AnsibleModule, jdk_home: Path) -> str:
    javac = jdk_home / 'bin' / 'javac'
    if not javac.is_file():
        module.fail_json(msg=f'File not found: {javac}')

    java = jdk_home / 'bin' / 'java'
    if not java.is_file():
        module.fail_json(msg=f'File not found: {java}')

    with tempfile.TemporaryDirectory() as dirpath:
        dirpath = Path(dirpath)
        src_file = dirpath / 'SpecificationVersion.java'
        src_file.write_text('''
public class SpecificationVersion {
    public static void main(String[] args) {
        System.out.print(System.getProperty("java.specification.version"));
    }
}
''')
        rc, out, err = module.run_command([str(javac), 'SpecificationVersion.java'], cwd=str(dirpath))
        if rc != 0 or err:
            module.fail_json(msg=f'Error while querying Java specification version: {out}{err}')

        rc, out, err = module.run_command([str(java), 'SpecificationVersion'], cwd=str(dirpath))
        if rc != 0 or err:
            module.fail_json(msg=f'Error while querying Java specification version: {out}{err}')

        return out.strip()


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


def set_default_jdk(module: AnsibleModule, intellij_user_config_dir: Path, jdk_name: str, uid: int, gid: int) -> Tuple[bool, Dict[str, Any]]:
    options_dir = intellij_user_config_dir / 'options'
    project_default_path = options_dir / 'project.default.xml'

    create_project_default = not project_default_path.is_file() or project_default_path.stat().st_size == 0

    if create_project_default:
        if not module.check_mode:
            if not options_dir.is_dir():
                make_dirs(options_dir, 0o775, uid, gid)

            if not project_default_path.is_file():
                project_default_path.touch()
                project_default_path.chmod(project_default_path, 0o664)
                os.chown(str(project_default_path), uid, gid)

        project_default_root = etree.Element('application')
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

    project_root_manager = default_project.find('./component[@name="ProjectRootManager"]')
    if project_root_manager is None:
        project_root_manager = etree.SubElement(default_project, 'component', name='ProjectRootManager')

    default_jdk_home = jdk_home(module, intellij_user_config_dir, jdk_name)
    language_level = specification_version(module, default_jdk_home)

    changed = any([
        set_attrib(project_root_manager, 'version', '2'),
        set_attrib(project_root_manager, 'languageLevel', f'JDK_{language_level.replace(".", "_")}'),
        set_attrib(project_root_manager, 'default', 'true'),
        set_attrib(project_root_manager, 'assert-keyword', 'true'),
        set_attrib(project_root_manager, 'jdk-15', 'true'),
        set_attrib(project_root_manager, 'project-jdk-name', jdk_name),
        set_attrib(project_root_manager, 'project-jdk-type', 'JavaSDK')
    ])

    after = pretty_print(project_default_root)

    if changed and not module.check_mode:
        project_default_path.write_text(after, encoding='iso-8859-1')
        os.chown(str(project_default_path), uid, gid)

    return changed, {'before': before, 'after': after}


def run_module() -> None:
    module_args = dict(
        intellij_user_config_dir=dict(type='str', required=True),
        jdk_name=dict(type='str', required=True),
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
    jdk_name = module.params['jdk_name']

    # Check if we have lxml 2.3.0 or newer installed
    if not HAS_LXML:
        module.fail_json(msg='The xml ansible module requires the lxml python library installed on the managed machine')
    else:
        lxml_version = LooseVersion('.'.join(str(f) for f in etree.LXML_VERSION))
        if lxml_version < LooseVersion('2.3.0'):
            module.fail_json(msg='The xml ansible module requires lxml 2.3.0 or newer installed on the managed machine')
        elif lxml_version < LooseVersion('3.0.0'):
            module.warn('Using lxml version lower than 3.0.0 does not guarantee predictable element attribute order.')

    changed, diff = set_default_jdk(module, intellij_user_config_dir, jdk_name, uid, gid)

    if changed:
        msg = f'{jdk_name} is now the default JDK'
    else:
        msg = f'{jdk_name} is already the default JDK'

    module.exit_json(changed=changed, msg=msg, diff=diff)


def main() -> None:
    run_module()


if __name__ == '__main__':
    main()
