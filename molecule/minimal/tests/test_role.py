def test_idea_installed(host):
    assert host.run('which idea').rc == 0
