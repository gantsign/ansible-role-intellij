Ansible Role: IntelliJ
======================

[![Build Status](https://travis-ci.org/gantsign/ansible-role-intellij.svg?branch=master)](https://travis-ci.org/gantsign/ansible-role-intellij)
[![Ansible Galaxy](https://img.shields.io/badge/ansible--galaxy-gantsign.intellij-blue.svg)](https://galaxy.ansible.com/gantsign/intellij)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/gantsign/ansible-role-intellij/master/LICENSE)

Role to download, install and configure the IntelliJ IDEA IDE
[https://www.jetbrains.com/idea](https://www.jetbrains.com/idea).

Requirements
------------

* Ansible

    * Minimum 2.3

* Linux Distribution

    * Debian Family

        * Ubuntu

            * Trusty (14.04)
            * Xenial (16.04)

    * RedHat Family

        * CentOS

            * 7

    * Note: other versions are likely to work but have not been tested.

* Java JDK

* Apache Maven

Role Variables
--------------

The following variables will change the behavior of this role (default values
are shown below):

```yaml
# IntelliJ IDEA version number
intellij_version: '2017.3'

# Mirror where to dowload IntelliJ IDEA redistributable package from
# Using HTTP because of https://github.com/ansible/ansible/issues/11579
intellij_mirror: 'http://download.jetbrains.com/idea'

# Edition to install (community or ultimate)
intellij_edition: community

# Base installation directory for any IntelliJ IDEA distribution
intellij_install_dir: /opt/idea/idea-{{ intellij_edition }}-{{ intellij_version }}

# Deprecated: use users.intellij_jdks and users.intellij_default_jdk instead
# Location of the default JDK for IntelliJ IDEA projects
intellij_default_jdk_home: '{{ ansible_local.java.general.home }}'

# Location of the default Apache Maven installation for IntelliJ IDEA projects
intellij_default_maven_home: '{{ ansible_local.maven.general.home }}'

# URL for IntelliJ IDEA plugin manager web service
intellij_plugin_manager_url: 'https://plugins.jetbrains.com/pluginManager/'

# List of users to configure IntelliJ IDEA for
users: []

# Directory to store files downloaded for IntelliJ IDEA installation
intellij_download_dir: "{{ x_ansible_download_dir | default(ansible_env.HOME + '~/.ansible/tmp/downloads') }}"

# Timeout for IntelliJ IDEA download response in seconds
intellij_idea_download_timeout_seconds: 600
```

Users are configured as follows:

```yaml
users:
  - username: # Unix user name
    intellij_jdks:
      - name: # The name use want to use for this JDK
        home: # The path to the JDK home.
    # The name of the JDK you want to be the default for new projects.
    # Required if you specify `intellij_jdks`.
    # Must match the name given to one of the `intellij_jdks`.
    intellij_default_jdk:
    intellij_disabled_plugins: # see ~/.*Idea*/config/disabled_plugins.txt
      - # Plugin ID
    intellij_codestyles:
      - name: # Name (must match the value in the XML file /code_scheme/@name)
        url: # URL to download the codestyles XML from
    intellij_active_codestyle: # Name (must match the value in the XML file /code_scheme/@name)
    intellij_plugins:
      - # Plugin ID of plugin to install
    # Ultimate Edition only: location of the IntelliJ license key on the Ansible master.
    # Your license key can be found at ~/.IntelliJIdea2017.1/config/idea.key
    intellij_license_key_path: # e.g. '/vagrant/idea.key'
```

**Warning:** the feature for installing additional plugins relies on internal
IntelliJ IDEA APIs and should be considered experimental at this time.

### Supported IntelliJ IDEA Versions

The following versions of IntelliJ IDEA are supported without any additional
configuration (for other versions follow the Advanced Configuration
instructions):

* `2017.3`
* `2017.2.6`
* `2017.2.5`
* `2017.2.4`
* `2017.2.3`
* `2017.2.2`
* `2017.2.1`
* `2017.2`
* `2017.1.5`
* `2017.1.4`
* `2017.1.3`
* `2017.1.2`
* `2017.1.1`
* `2017.1`
* `2016.3.5`
* `2016.3.4`
* `2016.3.3`
* `2016.3.2`
* `2016.3.1`
* `2016.3`
* `2016.2.5`
* `2016.2.4`
* `2016.2.3`
* `2016.2.2`
* `2016.2.1`
* `2016.2`
* `2016.1.3`
* `2016.1.1`

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

Example Playbooks
-----------------

Minimal playbook:

```yaml
- hosts: servers
  roles:
    - role: gantsign.intellij
```

Playbook with user specific configuration (Default JDK, Maven, disabled plugins
and code style):

```yaml
- hosts: servers
  roles:
    - role: gantsign.intellij
      intellij_default_maven_home: '/opt/maven/apache-maven-3.3.9'
      users:
        - username: vagrant
          intellij_jdks:
            - name: '1.8'
              home: '/usr/lib/jvm/java-8-openjdk-amd64'
            - name: '1.7'
              home: '/usr/lib/jvm/java-7-openjdk-amd64'
            - name: '1.6'
              home: '/usr/lib/jvm/java-6-openjdk-amd64'
          intellij_default_jdk: '1.8'
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
          intellij_codestyles:
            - name: GoogleStyle
              url: 'https://raw.githubusercontent.com/google/styleguide/gh-pages/intellij-java-google-style.xml'
          intellij_active_codestyle: GoogleStyle
          intellij_plugins:
            - CheckStyle-IDEA
```

Role Facts
----------

This role exports the following Ansible facts for use by other roles:


* `ansible_local.intellij.general.home`

    * e.g. `/opt/idea/idea-community-2016.2.2`

* `ansible_local.intellij.general.desktop_filename`

    * e.g. `jetbrains-idea-ce.desktop`

* `ansible_local.intellij.general.desktop_file`

    * e.g. `/usr/share/applications/jetbrains-idea-ce.desktop`

* `ansible_local.intellij.general.user_dirname`

    * e.g. `.IdeaIC2016.2`

More Roles From GantSign
------------------------

You can find more roles from GantSign on
[Ansible Galaxy](https://galaxy.ansible.com/gantsign).

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
