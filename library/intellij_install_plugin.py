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
    intellij_user_dir:
        description:
            - This is the dir where the user's IntelliJ configuration is located.
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
- name: install plugin
  become: yes
  intellij_install_plugin:
    plugin_manager_url: 'https://plugins.jetbrains.com/pluginManager/'
    intellij_home: '/opt/idea/idea-ultimate-2018.1.1'
    intellij_user_dir: '.IntelliJIdea2018.1'
    owner: bob
    group: bob
    plugin_id: google-java-format
    download_cache: '/tmp/downloads'
'''

import grp
import hashlib
import os
import pwd
import re
import shutil
import socket
import tempfile
import time
import traceback
import zipfile
from distutils.version import LooseVersion

import ansible.module_utils.six.moves.urllib.error as urllib_error
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule, get_distribution
from ansible.module_utils.urls import ConnectionError, NoSSLError, open_url

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False

try:
    from ansible.module_utils.six.moves.urllib.parse import urlparse, urlunparse, urlencode, urljoin
    HAS_URLPARSE = True
except:
    HAS_URLPARSE = False


def make_dirs(module, path, mode, uid, gid):
    dirs = [path]
    dirname = os.path.dirname(path)
    while dirname != '/':
        dirs.insert(0, dirname)
        dirname = os.path.dirname(dirname)

    for dirname in dirs:
        if not os.path.exists(dirname):
            os.mkdir(dirname, mode)
            os.chown(dirname, uid, gid)


def get_root_dirname_from_zip(module, zipfile_path):
    if not os.path.isfile(zipfile_path):
        module.fail_json(msg='File not found: %s' % zipfile_path)

    with zipfile.ZipFile(zipfile_path, 'r') as z:
        files = z.namelist()

    if len(files) == 0:
        module.fail_json(msg='Plugin is empty: %s' % zipfile_path)

    return files[0].split('/')[0]


def extract_zip(module, output_dir, zipfile_path, uid, gid):
    if not os.path.isfile(zipfile_path):
        module.fail_json(msg='File not found: %s' % zipfile_path)

    with zipfile.ZipFile(zipfile_path, 'r') as z:
        z.extractall(output_dir)
        files = z.namelist()

    for file_entry in files:
        absolute_file = os.path.join(output_dir, file_entry)
        os.chown(absolute_file, uid, gid)


def fetch_url(module, url, method=None, timeout=10, follow_redirects=True):

    if not HAS_URLPARSE:
        module.fail_json(msg='urlparse is not installed')

    # ensure we use proper tempdir
    old_tempdir = tempfile.tempdir
    tempfile.tempdir = getattr(module, 'tmpdir', old_tempdir)

    r = None
    info = dict(url=url)
    try:
        r = open_url(
            url,
            method=method,
            timeout=timeout,
            follow_redirects=follow_redirects)
        info.update(r.info())
        # finally update the result with a message about the fetch
        info.update(
            dict(
                msg='OK (%s bytes)' % r.headers.get('Content-Length',
                                                    'unknown'),
                url=r.geturl(),
                status=r.code))
    except NoSSLError as e:
        distribution = get_distribution()
        if distribution is not None and distribution.lower() == 'redhat':
            module.fail_json(msg='%s. You can also install python-ssl from EPEL'
                             % to_native(e))
        else:
            module.fail_json(msg='%s' % to_native(e))
    except (ConnectionError, ValueError) as e:
        module.fail_json(msg=to_native(e))
    except urllib_error.HTTPError as e:
        try:
            body = e.read()
        except AttributeError:
            body = ''

        # Try to add exception info to the output but don't fail if we can't
        try:
            info.update(dict(**e.info()))
        except:
            pass

        info.update({'msg': to_native(e), 'body': body, 'status': e.code})

    except urllib_error.URLError as e:
        code = int(getattr(e, 'code', -1))
        info.update(dict(msg='Request failed: %s' % to_native(e), status=code))
    except socket.error as e:
        info.update(
            dict(msg='Connection failure: %s' % to_native(e), status=-1))
    except Exception as e:
        info.update(
            dict(msg='An unknown error occurred: %s' % to_native(e), status=-1),
            exception=traceback.format_exc())
    finally:
        tempfile.tempdir = old_tempdir

    return r, info


def get_build_number_from_xml(module, intellij_home, xml):
    info_doc = etree.parse(xml)
    build = info_doc.find('./build/[@number]')
    if build is None:
        build = info_doc.find(
            './{http://jetbrains.org/intellij/schema/application-info}build/[@number]'
        )
    if build is None:
        module.fail_json(
            msg=
            'Unable to determine IntelliJ version from path: %s (unsupported schema - missing build element)'
            % intellij_home)

    build_number = build.get('number')
    if build_number is None:
        module.fail_json(
            msg=
            'Unable to determine IntelliJ version from path: %s (unsupported schema - missing build number value)'
            % intellij_home)

    return build_number


def get_build_number(module, intellij_home):
    resources_jar = os.path.join(intellij_home, 'lib', 'resources.jar')

    if not os.path.isfile(resources_jar):
        module.fail_json(
            msg=
            'Unable to determine IntelliJ version from path: %s ("lib/resources.jar" not found)'
            % intellij_home)

    with zipfile.ZipFile(resources_jar, 'r') as resource_zip:
        try:
            with resource_zip.open('idea/IdeaApplicationInfo.xml') as xml:
                return get_build_number_from_xml(module, intellij_home, xml)
        except KeyError:
            try:
                with resource_zip.open('idea/ApplicationInfo.xml') as xml:
                    return get_build_number_from_xml(module, intellij_home, xml)
            except KeyError:
                module.fail_json(
                    msg=
                    'Unable to determine IntelliJ version from path: %s (XML info file not found in "lib/resources.jar")'
                    % intellij_home)


def get_plugin_info(module, plugin_manager_url, intellij_home, plugin_id):

    build_number = get_build_number(module, intellij_home)

    params = {'action': 'download', 'build': build_number, 'id': plugin_id}

    query_params = urlencode(params)

    url = '%s?%s' % (plugin_manager_url, query_params)
    for _ in range(0, 3):
        resp, info = fetch_url(
            module, url, method='HEAD', timeout=3, follow_redirects=False)
        if resp is not None:
            resp.close()
        status_code = info['status']
        if status_code == 404:
            module.fail_json(msg='Unable to find plugin "%s" for build "%s"' % (
                plugin_id, build_number))
        if status_code > -1 and status_code < 400:
            break
        # 3 retries 5 seconds appart
        time.sleep(5)

    if status_code == -1 or status_code >= 400:
        module.fail_json(msg='Error querying url "%s": %s' % (url, info['msg']))

    location = info.get('location')
    if location is None:
        location = info.get('Location')
    if location is None:
        module.fail_json(msg='Unsupported HTTP response for: %s (status=%s)' % (
            url, status_code))

    if location.startswith('http'):
        plugin_url = location
    else:
        plugin_url = urljoin(plugin_manager_url, location)

    jar_pattern = re.compile(r'/(?P<file_name>[^/]+\.jar)(?:\?.*)$')
    jar_matcher = jar_pattern.search(plugin_url)

    if jar_matcher:
        file_name = jar_matcher.group('file_name')
    else:
        versioned_pattern = re.compile(
            r'(?P<plugin_id>[0-9]+)/(?P<update_id>[0-9]+)/(?P<file_name>[^/]+)(?:\?.*)$'
        )

        versioned_matcher = versioned_pattern.search(plugin_url)
        if versioned_matcher:
            file_name = '%s-%s-%s' % (versioned_matcher.group('plugin_id'),
                                      versioned_matcher.group('update_id'),
                                      versioned_matcher.group('file_name'))
        else:
            hash_object = hashlib.sha256(plugin_url)
            file_name = '%s-%s.zip' % (plugin_id, hash_object.hexdigest())

    return plugin_url, file_name


def download_plugin(module, plugin_url, file_name, download_cache):
    if not os.path.isdir(download_cache):
        os.makedirs(download_cache, 0o775)

    download_path = os.path.join(download_cache, file_name)

    if os.path.isfile(download_path):
        return download_path

    for _ in range(0, 3):
        resp, info = fetch_url(
            module, plugin_url, method='GET', timeout=20, follow_redirects=True)
        status_code = info['status']

        if status_code >= 200 and status_code < 300:
            tmp_dest = getattr(module, 'tmpdir', None)

            fd, b_tempname = tempfile.mkstemp(dir=tmp_dest)

            f = os.fdopen(fd, 'wb')
            try:
                shutil.copyfileobj(resp, f)
            except Exception as e:
                os.remove(b_tempname)
                resp.close()
                module.fail_json(
                    msg='Failed to create temporary content file: %s' %
                    to_native(e))
            f.close()
            resp.close()

            module.atomic_move(to_native(b_tempname), download_path)

            return download_path

        if resp is not None:
            resp.close()

    module.fail_json(msg='Error downloading url "%s": %s' % (plugin_url,
                                                             info['msg']))


def install_plugin(module, plugin_manager_url, intellij_home, intellij_user_dir,
                   uid, gid, plugin_id, download_cache):
    plugin_url, file_name = get_plugin_info(module, plugin_manager_url,
                                            intellij_home, plugin_id)

    plugin_path = download_plugin(module, plugin_url, file_name, download_cache)

    plugins_dir = os.path.join(intellij_user_dir, 'config', 'plugins')
    if not module.check_mode:
        make_dirs(module, plugins_dir, 0o775, uid, gid)

    if plugin_path.endswith('.jar'):
        dest_path = os.path.join(plugins_dir, os.path.basename(plugin_path))

        if os.path.exists(dest_path):
            return False

        if not module.check_mode:
            shutil.copy(plugin_path, dest_path)
            os.chown(dest_path, uid, gid)
            os.chmod(dest_path, 0o664)
        return True
    else:
        root_dirname = get_root_dirname_from_zip(module, plugin_path)
        plugin_dir = os.path.join(plugins_dir, root_dirname)

        if os.path.exists(plugin_dir):
            return False

        if not module.check_mode:
            extract_zip(module, plugins_dir, plugin_path, uid, gid)
        return True


def run_module():

    module_args = dict(
        plugin_manager_url=dict(type='str', required=True),
        intellij_home=dict(type='path', required=True),
        intellij_user_dir=dict(type='path', required=True),
        owner=dict(type='str', required=True),
        group=dict(type='str', required=True),
        plugin_id=dict(type='str', required=True),
        download_cache=dict(type='path', required=True))

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    plugin_manager_url = module.params['plugin_manager_url']
    intellij_home = os.path.expanduser(module.params['intellij_home'])
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
    plugin_id = module.params['plugin_id']
    download_cache = os.path.expanduser(module.params['download_cache'])

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

    changed = install_plugin(module, plugin_manager_url, intellij_home,
                             intellij_user_dir, uid, gid, plugin_id,
                             download_cache)

    if changed:
        msg = 'Plugin %s has been installed' % username
    else:
        msg = 'Plugin %s was already installed' % username

    module.exit_json(changed=changed, msg=msg)


def main():
    run_module()


if __name__ == '__main__':
    main()
