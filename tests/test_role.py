import pytest

from testinfra.utils.ansible_runner import AnsibleRunner

testinfra_hosts = AnsibleRunner('.molecule/ansible_inventory').get_hosts('all')


def test_idea_installed(Command):
    assert Command('which idea').rc == 0


@pytest.mark.parametrize('file_path,expected_text', [
    ('disabled_plugins.txt', 'org.jetbrains.plugins.gradle'),
    ('options/jdk.table.xml', '/usr/lib/jvm/java-1.8.0-openjdk-amd64'),
    ('options/project.default.xml', '/test/maven/home')
])
def test_config_files(Command, File, file_path, expected_text):
    config_home = Command.check_output('find %s | grep --color=never -E %s',
                                       '/home/test_usr',
                                       '\\.IdeaIC[0-9]+\\.[0-9]/config$')
    assert File(config_home + '/' + file_path).contains(expected_text)
