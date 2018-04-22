import os
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_idea_installed(Command):
    assert Command('which idea').rc == 0


def test_config_files(Command, File):
    file_path = 'options/project.default.xml'
    expected_text = '/test/maven/home'

    config_dir_pattern = '\\.(IdeaIC|IntelliJIdea)[0-9]+\\.[0-9]/config$'
    config_home = Command.check_output('find %s | grep --color=never -E %s',
                                       '/home/test_usr',
                                       config_dir_pattern)
    assert File(config_home + '/' + file_path).contains(expected_text)
