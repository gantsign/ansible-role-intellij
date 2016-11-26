import pytest

from testinfra.utils.ansible_runner import AnsibleRunner

testinfra_hosts = AnsibleRunner('.molecule/ansible_inventory').get_hosts('all')


def test_idea_installed(Command):
    assert Command('which idea').rc == 0


@pytest.mark.parametrize('file_path,expected_text', [
    ('disabled_plugins.txt', 'org.jetbrains.plugins.gradle'),
    ('options/jdk.table.xml', '/usr/lib/jvm/java-1.8.0-openjdk'),
    ('options/jdk.table.xml', '/usr/lib/jvm/java-1.7.0-openjdk'),
    ('options/project.default.xml', '/test/maven/home'),
    ('codestyles/GoogleStyle.xml', 'code_scheme name="GoogleStyle"'),
    ('options/code.style.schemes',
     'name="PREFERRED_PROJECT_CODE_STYLE" value="GoogleStyle"'),
    ('options/code.style.schemes.xml',
     'name="CURRENT_SCHEME_NAME" value="GoogleStyle"')
])
def test_config_files(Command, File, file_path, expected_text):
    config_dir_pattern = '\\.(IdeaIC|IntelliJIdea)[0-9]+\\.[0-9]/config$'
    config_home = Command.check_output('find %s | grep --color=never -E %s',
                                       '/home/test_usr',
                                       config_dir_pattern)
    assert File(config_home + '/' + file_path).contains(expected_text)


@pytest.mark.parametrize('plugin_dir_name', [
    'google-java-format',
    'lombok-plugin',
    'Go'
])
def test_plugins_installed(Command, File, plugin_dir_name):
    config_dir_pattern = '\\.(IdeaIC|IntelliJIdea)[0-9]+\\.[0-9]/config$'
    config_home = Command.check_output('find %s | grep --color=never -E %s',
                                       '/home/test_usr',
                                       config_dir_pattern)
    plugin_dir = File(config_home + '/plugins/' + plugin_dir_name)

    assert plugin_dir.exists
    assert plugin_dir.is_directory
    assert plugin_dir.user == 'test_usr'
    assert plugin_dir.group == 'test_usr'
    assert oct(plugin_dir.mode) == '0755'
