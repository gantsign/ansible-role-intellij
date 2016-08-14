Ansible Role: IntelliJ
======================

[![Build Status](https://travis-ci.org/gantsign/ansible-role-intellij.svg?branch=master)](https://travis-ci.org/gantsign/ansible-role-intellij)

Role to download, install and configure the IntellJ IDEA IDE
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
intellij_version: '2016.2.1'

# Mirror where to dowload IntelliJ IDEA redistributable package from
# Using HTTP because of https://github.com/ansible/ansible/issues/11579
intellij_mirror: "http://download.jetbrains.com/idea"

# Edition to install (community or ultimate)
intellij_edition: community

# Base installation directory for any IntelliJ IDEA distribution
intellij_install_dir: /opt/idea/idea-{{ intellij_edition }}-{{ intellij_version }}

# Location of the default JDK for IntelliJ IDEA projects
intellij_default_jdk_home: "{{ ansible_local.java.general.java_home }}"

# Location of the default Apache Maven installation for IntelliJ IDEA projects
intellij_default_maven_home: "{{ ansible_local.maven.general.maven_home }}"

# List of users to configure IntelliJ IDEA for
users: []

# path for Ansible to store downloaded files
local_ansible_data_path: '/tmp/ansible/data'

# SHA256 sum for the redistributable package
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

License
-------

MIT

Author Information
------------------

John Freeman

GantSign Ltd.
Company No. 06109112 (registered in England)
