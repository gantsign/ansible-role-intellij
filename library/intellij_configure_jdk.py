import grp
import os
import pwd
import xml.sax.saxutils
import zipfile
from pathlib import Path
from typing import Dict, Tuple

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.compat.version import LooseVersion

DOCUMENTATION = '''
---
module: intellij_configure_jdk

short_description: Configures the specified JDK for the given IntelliJ user.

description:
    - Configures the specified JDK for the given IntelliJ user.

options:
    intellij_user_config_dir:
        description:
            - >
                This is the dir where the user's IntelliJ configuration is
                located.
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
- name: Configure JDKs
  become: yes
  become_user: bob
  intellij_configure_jdk:
    intellij_user_config_dir: '.IntelliJIdea2018.1/config'
    jdk_name: '1.8'
    jdk_home: '/opt/java/jdk/1.8'
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


def get_java_version(module: AnsibleModule, jdk_home: Path) -> str:
    executable = jdk_home / 'bin' / 'java'
    if not executable.is_file():
        module.fail_json(msg=f'File not found: {executable}')

    rc, out, err = module.run_command([str(executable), '-version'])
    if rc != 0:
        module.fail_json(msg=f'Error while querying Java version: {out + err}')
    return err.splitlines()[0]


def get_class_path(module: AnsibleModule, jdk_home: Path) -> str:
    jre_lib = jdk_home / 'jre' / 'lib'

    jre_ext = jre_lib / 'ext'

    jmods = jdk_home / 'jmods'

    if jre_ext.is_dir():

        files = list(jre_lib.iterdir()) + list(jre_ext.iterdir())

        files = [x for x in files if x.is_file() and x.suffix == '.jar']

        files = sorted(files)

        urls = [f'jar://{str(x)}!/' for x in files]

        elements = [f'<root url={xml.sax.saxutils.quoteattr(x)} type="simple" />' for x in urls]

        return "\n".join(elements)

    elif jmods.is_dir():

        files = list(jmods.iterdir())

        files = [x for x in files if x.is_file() and x.suffix == '.jmod']

        module_names = [x.stem for x in files]

        module_names = sorted(module_names)

        urls = [f'jrt://{jdk_home}!/{x}' for x in module_names]

        elements = [f'<root url={xml.sax.saxutils.quoteattr(x)} type="simple" />' for x in urls]
        return "\n".join(elements)

    else:
        module.fail_json(
            msg=(
                f"Unsupported JDK directory layout: {jdk_home}. If you're "
                "using Java > 9 you may need to install the "
                "jmods package e.g. yum install "
                "java-11-openjdk-jmods."
            )
        )


def get_source_path(module: AnsibleModule, jdk_home: Path) -> str:
    jmod_src = jdk_home / 'lib' / 'src.zip'

    if jmod_src.is_file():

        with zipfile.ZipFile(jmod_src, 'r') as srczip:
            files = srczip.namelist()

        files = [x for x in files if x.endswith('/module-info.java')]

        module_names = [x[:-len('/module-info.java')] for x in files]

        module_names = sorted(module_names)

        urls = [f'jar://{jdk_home / "lib" / "src.zip"}!/{x}' for x in module_names]

        elements = [f'<root url={xml.sax.saxutils.quoteattr(str(x))} type="simple" />' for x in urls]
        return "\n".join(elements)

    elif jdk_home.is_dir():

        files = list(jdk_home.iterdir())

        files = [x for x in files if x.is_file() and x.name.endswith('src.zip')]

        files = sorted(files)

        urls = [f'jar://{x}!/' for x in files]

        elements = [f'<root url={xml.sax.saxutils.quoteattr(x)} type="simple" />' for x in urls]

        return "\n".join(elements)

    else:
        module.fail_json(msg=f'Directory not found: {jdk_home}')


def create_jdk_xml(module: AnsibleModule, jdk_name: str, jdk_home: Path) -> etree.Element:
    java_version = get_java_version(module, jdk_home)
    class_path = get_class_path(module, jdk_home)
    source_path = get_source_path(module, jdk_home)

    return etree.fromstring(f'''
<jdk version="2">
  <name value={xml.sax.saxutils.quoteattr(jdk_name)} />
  <type value="JavaSDK" />
  <version value={xml.sax.saxutils.quoteattr(java_version)} />
  <homePath value={xml.sax.saxutils.quoteattr(str(jdk_home))} />
  <roots>
    <annotationsPath>
      <root type="composite">
        <root url="jar://$APPLICATION_HOME_DIR$/lib/jdkAnnotations.jar!/"
              type="simple" />
      </root>
    </annotationsPath>
    <classPath>
      <root type="composite">{class_path}</root>
    </classPath>
    <javadocPath>
      <root type="composite" />
    </javadocPath>
    <sourcePath>
      <root type="composite">{source_path}</root>
    </sourcePath>
  </roots>
  <additional />
</jdk>''')


def make_dirs(path: Path, mode: int, uid: int, gid: int) -> None:
    dirs = []
    current = path
    while not current.exists():
        dirs.append(current)
        current = current.parent
    dirs.reverse()
    for dirpath in dirs:
        dirpath.mkdir(mode=mode)
        os.chown(str(dirpath), uid, gid)
        dirpath.chmod(mode)


def configure_jdk(module: AnsibleModule, intellij_user_config_dir: Path, jdk_name: str, jdk_home: Path, uid: int, gid: int) -> Tuple[bool, Dict[str, str]]:
    options_dir = intellij_user_config_dir / 'options'
    project_default_path = options_dir / 'jdk.table.xml'

    create_jdk_table = (not project_default_path.is_file()) or project_default_path.stat().st_size == 0
    if create_jdk_table:
        if not module.check_mode:
            if not options_dir.is_dir():
                make_dirs(options_dir, 0o775, uid, gid)

            if not project_default_path.is_file():
                project_default_path.touch()
                os.chown(str(project_default_path), uid, gid)
                project_default_path.chmod(0o664)

        jdk_table_root = etree.Element('application')
        jdk_table_doc = etree.ElementTree(jdk_table_root)
        before = ''
    else:
        jdk_table_doc = etree.parse(str(project_default_path))
        jdk_table_root = jdk_table_doc.getroot()
        before = pretty_print(jdk_table_root)

    if jdk_table_root.tag != 'application':
        module.fail_json(msg=f'Unsupported root element: {jdk_table_root.tag}')

    project_jdk_table = jdk_table_root.find('./component[@name="ProjectJdkTable"]')
    if project_jdk_table is None:
        project_jdk_table = etree.SubElement(jdk_table_root, 'component', name='ProjectJdkTable')

    new_jdk = create_jdk_xml(module, jdk_name, jdk_home)
    new_jdk_string = pretty_print(new_jdk)

    old_jdk = project_jdk_table.find(f'./jdk/name[@value="{jdk_name}"]/..')
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
        project_default_path.write_text(after, encoding='iso-8859-1')

    return changed, {'before': before, 'after': after}


def run_module() -> None:
    module_args = dict(
        intellij_user_config_dir=dict(type='str', required=True),
        jdk_name=dict(type='str', required=True),
        jdk_home=dict(type='str', required=True),
        owner=dict(type='str', required=True),
        group=dict(type='str', required=True)
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    owner = module.params['owner']
    group = module.params['group']

    try:
        uid = int(owner)
    except ValueError:
        try:
            uid = pwd.getpwnam(owner).pw_uid
        except KeyError:
            module.fail_json(msg=f"User '{owner}' does not exist")
    username = pwd.getpwuid(uid).pw_name

    try:
        gid = int(group)
    except ValueError:
        try:
            gid = grp.getgrnam(group).gr_gid
        except KeyError:
            module.fail_json(msg=f"Group '{group}' does not exist")

    intellij_user_config_dir = Path('~' + username, module.params['intellij_user_config_dir']).expanduser()
    jdk_name = module.params['jdk_name']
    jdk_home = Path(module.params['jdk_home']).expanduser()

    # Check if we have lxml 2.3.0 or newer installed
    if not HAS_LXML:
        module.fail_json(msg='The xml ansible module requires the lxml python library installed on the managed machine')
    else:
        lxml_version = LooseVersion('.'.join(str(f) for f in etree.LXML_VERSION))
        if lxml_version < LooseVersion('2.3.0'):
            module.fail_json(msg='The xml ansible module requires lxml 2.3.0 or newer installed on the managed machine')
        elif lxml_version < LooseVersion('3.0.0'):
            module.warn('Using lxml version lower than 3.0.0 does not guarantee predictable element attribute order.')

    changed, diff = configure_jdk(module, intellij_user_config_dir, jdk_name, jdk_home, uid, gid)

    if changed:
        msg = f'JDK {jdk_name} has been configured'
    else:
        msg = f'JDK {jdk_name} was already configured'

    module.exit_json(changed=changed, msg=msg, diff=diff)


def main() -> None:
    run_module()


if __name__ == '__main__':
    main()
