Ansible Role: IntelliJ
======================

[![Build Status](https://travis-ci.org/gantsign/ansible-role-intellij.svg?branch=master)](https://travis-ci.org/gantsign/ansible-role-intellij)
[![Ansible Galaxy](https://img.shields.io/badge/ansible--galaxy-gantsign.intellij-blue.svg)](https://galaxy.ansible.com/gantsign/intellij)

Role to download, install and configure the IntelliJ IDEA IDE
[https://www.jetbrains.com/idea](https://www.jetbrains.com/idea).

Requirements
------------

* Ubuntu
* Java JDK
* Apache Maven

Role Variables
--------------

The following variables will change the behavior of this role (default values
are shown below):

```yaml
# IntelliJ IDEA version number
intellij_version: '2016.2.2'

# Mirror where to dowload IntelliJ IDEA redistributable package from
# Using HTTP because of https://github.com/ansible/ansible/issues/11579
intellij_mirror: "http://download.jetbrains.com/idea"

# Edition to install (community or ultimate)
intellij_edition: community

# Base installation directory for any IntelliJ IDEA distribution
intellij_install_dir: /opt/idea/idea-{{ intellij_edition }}-{{ intellij_version }}

# Location of the default JDK for IntelliJ IDEA projects
intellij_default_jdk_home: "{{ ansible_local.java.general.home }}"

# Location of the default Apache Maven installation for IntelliJ IDEA projects
intellij_default_maven_home: "{{ ansible_local.maven.general.home }}"

# List of users to configure IntelliJ IDEA for
users: []

# Directory to store files downloaded for IntelliJ IDEA installation
intellij_download_dir: "{{ x_ansible_download_dir | default('~/.ansible/tmp/downloads') }}"
```

### Supported IntelliJ IDEA Versions

The following versions of IntelliJ IDEA are supported without any additional
configuration (for other versions follow the Advanced Configuration
instructions):

* `2016.1.1`
* `2016.1.3`
* `2016.2`
* `2016.2.1`
* `2016.2.2`

Advanced Configuration
----------------------

The following role variable is dependent on the IntelliJ IDEA version; to use a
IntelliJ IDEA version **not pre-configured by this role** you must configure the
variable below:

```yaml
# SHA256 sum for the redistributable package
# i.e. ideaIC-{{ intellij_version }}.tar.gz for the Community Edition
# or ideaIU-{{ intellij_version }}.tar.gz for the Ultimate Edition
intellij_redis_sha256sum: d1cd3f9fd650c00ba85181da6d66b4b80b8e48ce5f4f15b5f4dc67453e96a179
```

Example Playbook
----------------

```yaml
- hosts: servers
  roles:
    - role: gantsign.intellij
      intellij_default_jdk_home: '/opt/java/oracle/jdk1.8.0_66'
      intellij_default_maven_home: '/opt/maven/apache-maven-3.3.9'
      users:
        - username: vagrant
          intellij_disabled_plugins:
            - org.jetbrains.plugins.gradle
            - CVS
            - com.intellij.uiDesigner
            - org.jetbrains.android
            - TestNG-J
            - hg4idea
            - Subversion
            - AntSupport
            - DevKit
```

Role Facts
----------

This role exports the following Ansible facts for use by other roles:


* `ansible_local.intellij.general.home`

    * e.g. `/opt/idea/idea-community-2016.2.2`
    
* `ansible_local.intellij.general.desktop_file`

    * e.g. `/usr/share/applications/jetbrains-idea-ce.desktop`

More Roles From GantSign
------------------------

You can find more roles from GantSign on [Ansible Galaxy](https://galaxy.ansible.com/gantsign).

Development & Testing
---------------------

This project uses [Molecule](http://molecule.readthedocs.io/) to aid in the
development and testing; the role is unit tested using
[Testinfra](http://testinfra.readthedocs.io/) and
[pytest](http://docs.pytest.org/).

To develop or test you'll need to have installed the following:

* Linux (e.g. [Ubuntu](http://www.ubuntu.com/))
* [Docker](https://www.docker.com/)
* [Python](https://www.python.org/) (including python-pip)
* [Ansible](https://www.ansible.com/)
* [Molecule](http://molecule.readthedocs.io/)

To run the role (i.e. the `tests/test.yml` playbook), and test the results
(`tests/test_role.py`), execute the following command from the project root
(i.e. the directory with `molecule.yml` in it):

```bash
molecule test
```

License
-------

MIT

Author Information
------------------

John Freeman

GantSign Ltd.
Company No. 06109112 (registered in England)
