#!/usr/bin/env python3

import grp
import hashlib
import json
import os
import pwd
import re
import shutil
import tempfile
import time
import urllib.parse
import zipfile
from pathlib import Path
from typing import Any, Optional, Tuple

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.compat.version import LooseVersion
from ansible.module_utils.urls import fetch_url

DOCUMENTATION = '''
---
module: intellij_install_plugin

short_description: Installs the specified plugin for the specified user.

description:
    - Installs the specified plugin for the specified user.

options:
    plugin_manager_url:
        description:
            - URL of the JetBrains plugin manager API.
        required: true
    intellij_home:
        description:
            - The root directory of the IntelliJ installation.
        required: true
    intellij_user_plugins_dir:
        description:
            - This is the dir where the user's IntelliJ plugins are located.
        required: true
    owner:
        description:
            - The user to install the plugin for.
        required: true
    group:
        description:
            - The group for the files and directories created.
        required: true
    plugin_id:
        description:
            - The ID of the plugin to install.
        required: true
    download_cache:
        description:
            - The directory to cache downloads in.
        required: true

author:
    - John Freeman (GantSign Ltd.)
'''

EXAMPLES = '''
- name: Install plugin
  become: yes
  intellij_install_plugin:
    plugin_manager_url: 'https://plugins.jetbrains.com/pluginManager/'
    intellij_home: '/opt/idea/idea-ultimate-2018.1.1'
    intellij_user_plugins_dir: '.IntelliJIdea2018.1/config/plugins'
    owner: bob
    group: bob
    plugin_id: google-java-format
    download_cache: '/tmp/downloads'
'''

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False


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


def get_root_dirname_from_zip(module: AnsibleModule, zipfile_path: Path) -> str:
    if not zipfile_path.is_file():
        module.fail_json(msg=f'File not found: {zipfile_path}')

    with zipfile.ZipFile(zipfile_path, 'r') as z:
        files = z.namelist()

    if not files:
        module.fail_json(msg=f'Plugin is empty: {zipfile_path}')

    return files[0].split('/')[0]


def extract_zip(module: AnsibleModule, output_dir: Path, zipfile_path: Path, uid: int, gid: int) -> None:
    if not zipfile_path.is_file():
        module.fail_json(msg=f'File not found: {zipfile_path}')

    with zipfile.ZipFile(zipfile_path, 'r') as z:
        z.extractall(output_dir)
        files = z.namelist()

    output_dir_resolved = output_dir.resolve()

    for file_entry in files:
        absolute_file = (output_dir / file_entry).resolve()
        while not absolute_file.samefile(output_dir_resolved):
            os.chown(absolute_file, uid, gid)
            absolute_file = absolute_file.parent.resolve()


def get_build_number_from_xml(module: AnsibleModule, intellij_home: Path, xml: Any) -> str:
    info_doc = etree.parse(xml)
    build = info_doc.find('./build/[@number]')
    if build is None:
        build = info_doc.find('./{http://jetbrains.org/intellij/schema/application-info}build/''[@number]')
    if build is None:
        module.fail_json(msg=f'Unable to determine IntelliJ version from path: {intellij_home} (unsupported schema - missing build element)')

    build_number = build.get('number')
    if build_number is None:
        module.fail_json(msg=f'Unable to determine IntelliJ version from path: {intellij_home} (unsupported schema - missing build number value)')

    return build_number


def get_build_number_from_jar(module: AnsibleModule, intellij_home: Path) -> Optional[str]:
    resources_jar = intellij_home / 'lib' / 'resources.jar'

    if not resources_jar.is_file():
        return None

    with zipfile.ZipFile(resources_jar, 'r') as resource_zip:
        try:
            with resource_zip.open('idea/IdeaApplicationInfo.xml') as xml:
                return get_build_number_from_xml(module, intellij_home, xml)
        except KeyError:
            try:
                with resource_zip.open('idea/ApplicationInfo.xml') as xml:
                    return get_build_number_from_xml(module, intellij_home, xml)
            except KeyError:
                module.fail_json(msg=f'Unable to determine IntelliJ version from path: {intellij_home} (XML info file not found in "lib/resources.jar")')


def get_build_number_from_json(module: AnsibleModule, intellij_home: Path) -> str:
    product_info_path = intellij_home / 'product-info.json'

    if not product_info_path.is_file():
        module.fail_json(msg=f'Unable to determine IntelliJ version from path: {intellij_home} ("product-info.json" not found)')

    with product_info_path.open() as product_info_file:
        product_info = json.load(product_info_file)
        return product_info['buildNumber']


def get_build_number(module: AnsibleModule, intellij_home: Path) -> str:
    return get_build_number_from_jar(module, intellij_home) or get_build_number_from_json(module, intellij_home)


def get_plugin_info(module: AnsibleModule, plugin_manager_url: str, intellij_home: Path, plugin_id: str) -> Tuple[str, str]:
    build_number = get_build_number(module, intellij_home)

    params = {'action': 'download', 'build': build_number, 'id': plugin_id}

    query_params = urllib.parse.urlencode(params)

    url = f'{plugin_manager_url}?{query_params}'

    for _ in range(3):
        module.params['follow_redirects'] = 'none'
        resp, info = fetch_url(module, url, method='HEAD', timeout=3)
        if resp:
            resp.close()
        status_code = info.get('status', -1)
        if status_code == 404:
            module.fail_json(msg=f'Unable to find plugin "{plugin_id}" for build "{build_number}"')
        if 0 <= status_code < 400:
            break
        # 3 retries 5 seconds apart
        time.sleep(5)

    if status_code == -1 or status_code >= 400:
        module.fail_json(msg=f'Error querying url "{url}": {info.get("msg", "Unknown error")}')

    location = info.get('location') or info.get('Location')
    if not location:
        module.fail_json(msg=f'Unsupported HTTP response for: {url} (status={status_code})')

    if location.startswith('http'):
        plugin_url = location
    else:
        plugin_url = urllib.parse.urljoin(plugin_manager_url, location)

    jar_pattern = re.compile(r'/(?P<file_name>[^/]+\.jar)(?:\?.*)$')
    jar_matcher = jar_pattern.search(plugin_url)

    if jar_matcher:
        file_name = jar_matcher.group('file_name')
    else:
        versioned_pattern = re.compile(r'(?P<plugin_id>[0-9]+)/(?P<update_id>[0-9]+)/(?P<file_name>[^/]+)(?:\?.*)$')

        versioned_matcher = versioned_pattern.search(plugin_url)
        if versioned_matcher:
            plugin_id = versioned_matcher.group('plugin_id')
            update_id = versioned_matcher.group('update_id')
            file_name = versioned_matcher.group('file_name')
            file_name = f'{plugin_id}-{update_id}-{file_name}'
        else:
            hash_object = hashlib.sha256(plugin_url.encode())
            file_name = f'{plugin_id}-{hash_object.hexdigest()}.zip'

    return plugin_url, file_name


def download_plugin(module: AnsibleModule, plugin_url: str, file_name: str, download_cache: Path) -> Path:
    if not download_cache.is_dir():
        download_cache.mkdir(mode=0o775, parents=True)

    download_path = download_cache / file_name

    if download_path.is_file():
        return download_path

    for _ in range(3):
        module.params['follow_redirects'] = 'all'
        resp, info = fetch_url(module, plugin_url, method='GET', timeout=20)
        status_code = info.get('status', -1)

        if 200 <= status_code < 300:
            tmp_dest = module.tmpdir

            fd, tempname = tempfile.mkstemp(dir=tmp_dest)

            with os.fdopen(fd, 'wb') as f:
                try:
                    shutil.copyfileobj(resp, f)
                except Exception as e:
                    os.remove(tempname)
                    if resp:
                        resp.close()
                    module.fail_json(msg=f'Failed to create temporary content file: {e}')
            if resp:
                resp.close()
            module.atomic_move(tempname, str(download_path))
            return download_path

        if resp:
            resp.close()

    module.fail_json(msg=f'Error downloading url "{plugin_url}": {info["msg"]}')


def install_plugin(
        module: AnsibleModule,
        plugin_manager_url: str,
        intellij_home: Path,
        plugins_dir: Path,
        uid: int,
        gid: int,
        plugin_id: str,
        download_cache: Path) -> bool:
    plugin_url, file_name = get_plugin_info(module, plugin_manager_url, intellij_home, plugin_id)

    plugin_path = download_plugin(module, plugin_url, file_name, download_cache)

    if not module.check_mode:
        make_dirs(plugins_dir, 0o775, uid, gid)

    if plugin_path.suffix == '.jar':
        dest_path = plugins_dir / plugin_path.name
        if dest_path.exists():
            return False

        if not module.check_mode:
            shutil.copy(plugin_path, dest_path)
            os.chown(dest_path, uid, gid)
            dest_path.chmod(0o664)
        return True
    else:
        root_dirname = get_root_dirname_from_zip(module, plugin_path)
        plugin_dir = plugins_dir / root_dirname

        if plugin_dir.exists():
            return False

        if not module.check_mode:
            extract_zip(module, plugins_dir, plugin_path, uid, gid)
        return True


def run_module() -> None:

    module_args = dict(
        plugin_manager_url=dict(type='str', required=True),
        intellij_home=dict(type='path', required=True),
        intellij_user_plugins_dir=dict(type='path', required=True),
        owner=dict(type='str', required=True),
        group=dict(type='str', required=True),
        plugin_id=dict(type='str', required=True),
        download_cache=dict(type='path', required=True)
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    plugin_manager_url = module.params['plugin_manager_url']
    intellij_home = Path(os.path.expanduser(module.params['intellij_home']))
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

    intellij_user_plugins_dir = (Path('~' + username) / module.params['intellij_user_plugins_dir']).expanduser()
    plugin_id = module.params['plugin_id']
    download_cache = Path(module.params['download_cache']).expanduser()

    # Check if we have lxml 2.3.0 or newer installed
    if not HAS_LXML:
        module.fail_json(msg='The xml ansible module requires the lxml python library installed on the managed machine')
    else:
        lxml_version = LooseVersion('.'.join(str(f) for f in etree.LXML_VERSION))
        if lxml_version < LooseVersion('2.3.0'):
            module.fail_json(msg='The xml ansible module requires lxml 2.3.0 or newer installed on the managed machine')
        elif lxml_version < LooseVersion('3.0.0'):
            module.warn('Using lxml version lower than 3.0.0 does not guarantee predictable element attribute order.')

    changed = install_plugin(module, plugin_manager_url, intellij_home, intellij_user_plugins_dir, uid, gid, plugin_id, download_cache)

    if changed:
        msg = f'Plugin "{plugin_id}" has been installed'
    else:
        msg = f'Plugin "{plugin_id}" was already installed'

    module.exit_json(changed=changed, msg=msg)


def main() -> None:
    run_module()


if __name__ == '__main__':
    main()
