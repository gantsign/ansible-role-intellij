import pytest


def test_idea_installed(host):
    assert host.run('which idea').rc == 0


@pytest.mark.parametrize('file_path,expected_text', [
    ('disabled_plugins.txt', 'org.jetbrains.plugins.gradle'),
    ('options/jdk.table.xml', '/usr/lib/jvm/java-1.8.0-openjdk'),
    ('options/jdk.table.xml', '/opt/java/jdk-11.0.6+10'),
    ('options/project.default.xml', '/test/maven/home'),
    ('codestyles/GoogleStyle.xml', 'code_scheme name="GoogleStyle"'),
    ('options/code.style.schemes',
     'name="PREFERRED_PROJECT_CODE_STYLE" value="GoogleStyle"'),
    ('options/code.style.schemes.xml',
     'name="CURRENT_SCHEME_NAME" value="GoogleStyle"'),
    ('inspection/GantSign.xml', 'value="GantSign"'),
    ('options/editor.codeinsight.xml',
     'component name="DaemonCodeAnalyzerSettings" profile="GantSign"'),
    ('options/project.default.xml',
     'option name="PROJECT_PROFILE" value="GantSign"')
])
def test_config_files(host, file_path, expected_text):
    config_dir_pattern = (
        '\\.config/JetBrains/(IdeaIC|IntelliJIdea)[0-9]+\\.[0-9]$')
    config_home = host.check_output('find %s | grep --color=never -E %s',
                                    '/home/test_usr',
                                    config_dir_pattern)
    assert host.file(config_home + '/' + file_path).contains(expected_text)


@pytest.mark.parametrize('plugin_dir_name', [
    'google-java-format',
    'lombok-plugin'
])
def test_plugins_installed(host, plugin_dir_name):
    plugins_dir_pattern = (
        '\\.local/share/JetBrains/(IdeaIC|IntelliJIdea)[0-9]+\\.[0-9]$')
    plugins_path = host.check_output('find %s | grep --color=never -E %s',
                                     '/home/test_usr',
                                     plugins_dir_pattern)

    plugin_dir = host.file(plugins_path + '/' + plugin_dir_name)
    assert plugin_dir.exists
    assert plugin_dir.is_directory
    assert plugin_dir.user == 'test_usr'
    assert plugin_dir.group == 'test_usr'
    assert plugin_dir.mode == 0o755


def test_jar_plugin_installed(host):
    plugins_dir_pattern = (
        '\\.local/share/JetBrains/(IdeaIC|IntelliJIdea)[0-9]+\\.[0-9]$')
    plugins_path = host.check_output('find %s | grep --color=never -E %s',
                                     '/home/test_usr',
                                     plugins_dir_pattern)

    plugin_path = host.check_output('find %s | grep --color=never -E %s',
                                    plugins_path,
                                    'save-actions.*\\.jar')

    plugin_file = host.file(plugin_path)

    assert plugin_file.exists
    assert plugin_file.is_file
    assert plugin_file.user == 'test_usr'
    assert plugin_file.group == 'test_usr'
    assert plugin_file.mode == 0o664
