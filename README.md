Ansible Role: IntelliJ
======================

[![Tests](https://github.com/gantsign/ansible-role-intellij/workflows/Tests/badge.svg)](https://github.com/gantsign/ansible-role-intellij/actions?query=workflow%3ATests)
[![Ansible Galaxy](https://img.shields.io/badge/ansible--galaxy-gantsign.intellij-blue.svg)](https://galaxy.ansible.com/ui/standalone/roles/gantsign/intellij/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/gantsign/ansible-role-intellij/master/LICENSE)

Role to download, install and configure the IntelliJ IDEA IDE
[https://www.jetbrains.com/idea](https://www.jetbrains.com/idea).

While this role can install IntelliJ plugins, if you want to conditionally
install particular plugins take a look at our companion role:
[gantsign.intellij-plugins](https://galaxy.ansible.com/ui/standalone/roles/gantsign/intellij-plugins).

Requirements
------------

* Ansible Core >= 2.17

* Linux Distribution

    * Debian Family

        * Ubuntu

            * Jammy (22.04)
            * Noble (24.04)

    * RedHat Family

        * Rocky Linux

            * 9

    * Note: other versions are likely to work but have not been tested.

* Java JDK

    * You need to install the JDK src as well as the JDK.
    * When using Java > 9 you also need to install the jmods.

    e.g. the following is required if using OpenJDK 17 with Rocky Linux:

    ```yml
    - name: Install OpenJDK 17
      become: true
      yum:
        name:
          - java-17-openjdk-devel
          - java-17-openjdk-jmods
          - java-17-openjdk-src
        state: present
    ```

* Apache Maven

Role Variables
--------------

The following variables will change the behavior of this role (default values
are shown below):

```yaml
# IntelliJ IDEA version number
intellij_version: '2024.3.5'

# Mirror where to dowload IntelliJ IDEA redistributable package from
# Using HTTP because of https://github.com/ansible/ansible/issues/11579
intellij_mirror: 'http://download.jetbrains.com/idea'

# Edition to install (community or ultimate)
intellij_edition: community

# Base installation directory for any IntelliJ IDEA distribution
intellij_install_dir: /opt/idea/idea-{{ intellij_edition }}-{{ intellij_version }}

# Owner of the installation files
intellij_install_user: root

# Location of the default Apache Maven installation for IntelliJ IDEA projects
# Defaults to value of ansible_local.maven.general.home (see gantsign.maven role)
intellij_default_maven_home: '{{ ((((ansible_local | default(dict())).maven | default(dict())).general | default(dict())).home | default(None)) }}'

# URL for IntelliJ IDEA plugin manager web service
intellij_plugin_manager_url: 'https://plugins.jetbrains.com/pluginManager/'

# List of users to configure IntelliJ IDEA for
users: []

# Directory to store files downloaded for IntelliJ IDEA installation
intellij_download_dir: "{{ x_ansible_download_dir | default(ansible_facts.env.HOME + '/.ansible/tmp/downloads') }}"

# Timeout for IntelliJ IDEA download response in seconds
intellij_idea_download_timeout_seconds: 600
```

Users are configured as follows:

```yaml
users:
  - username: # Unix user name
    intellij_group: # Unix group for the user's files/directories (optional - defaults to username)
    intellij_jdks:
      - name: # The name use want to use for this JDK
        home: # The path to the JDK home.
    # The name of the JDK you want to be the default for new projects.
    # Required if you specify `intellij_jdks`.
    # Must match the name given to one of the `intellij_jdks`.
    intellij_default_jdk:
    intellij_disabled_plugins: # see ~/.config/JetBrains/*Idea*/disabled_plugins.txt
      - # Plugin ID
    intellij_codestyles:
      # List of codestyles (each XML location may be specified by URL or filesystem path)
      - name: # Name (must match the value in the XML file /code_scheme/@name)
        url: # URL to download the codestyles XML from
      - name: # Name (must match the value in the XML file /code_scheme/@name)
        src: # path to the codestyles XML file (may be absolute or relative, relative paths are evaluated the same way as the Ansible copy module)
        remote_src: # yes/no, wether to copy from the remote filesystem (default no)
    intellij_default_codestyle: # Name (must match the value in the XML file /code_scheme/@name)
    intellij_inspection_profiles:
      # List of inspection profiles (each XML location may be specified by URL or filesystem path)
      - name: # Name (must match the value in the XML file /profile/option[@name='myName']/@value)
        url: # URL to download the inspection profile XML from
      - name: # Name (must match the value in the XML file /profile/option[@name='myName']/@value)
        src: # path to the inspection profile XML file (may be absolute or relative, relative paths are evaluated the same way as the Ansible copy module)
        remote_src: # yes/no, wether to copy from the remote filesystem (default no)
    intellij_default_inspection_profile: # Name (must match the value in the XML file /profile/option[@name='myName']/@value)
    intellij_plugins:
      - # Plugin ID of plugin to install
    # Ultimate Edition only: location of the IntelliJ license key on the Ansible master.
    # Your license key can be found at ~/.config/JetBrains/*Idea*/idea.key
    intellij_license_key_path: # e.g. '/vagrant/idea.key'
```

**Warning:** the feature for installing additional plugins relies on internal
IntelliJ IDEA APIs and should be considered experimental at this time.

### Supported IntelliJ IDEA Versions

The following versions of IntelliJ IDEA are supported without any additional
configuration (for other versions follow the Advanced Configuration
instructions):

* `2024.3.5`
* `2024.3.4.1`
* `2024.3.4`
* `2024.3.3`
* `2024.3.2.2`
* `2024.3.2.1`
* `2024.3.2`
* `2024.3.1.1`
* `2024.3.1`
* `2024.3`
* `2024.2.5`
* `2024.2.4`
* `2024.2.3`
* `2024.2.2`
* `2024.2.1`
* `2024.2`
* `2024.1.4`
* `2024.1.3`
* `2024.1.2`
* `2024.1.1`
* `2024.1`
* `2023.3.6`
* `2023.3.5`
* `2023.3.4`
* `2023.3.3`
* `2023.3.2`
* `2023.3.1`
* `2023.3`
* `2023.2.5`
* `2023.2.4`
* `2023.2.3`
* `2023.2.2`
* `2023.2.1`
* `2023.2`
* `2023.1.5`
* `2023.1.4`
* `2023.1.3`
* `2023.1.2`
* `2023.1.1`
* `2023.1`
* `2022.3.3`
* `2022.3.2`
* `2022.3.1`
* `2022.3`
* `2022.2.4`
* `2022.2.3`
* `2022.2.2`
* `2022.2.1`
* `2022.2`
* `2022.1.4`
* `2022.1.3`
* `2022.1.2`
* `2022.1.1`
* `2022.1`
* `2021.3.3`
* `2021.3.2`
* `2021.3.1`
* `2021.3`
* `2021.2.3`
* `2021.2.2`
* `2021.2.1`
* `2021.2`
* `2021.1.3`
* `2021.1.2`
* `2021.1.1`
* `2021.1`
* `2020.3.3`
* `2020.3.2`
* `2020.3.1`
* `2020.3`
* `2020.2.4`
* `2020.2.3`
* `2020.2.2`
* `2020.2.1`
* `2020.2`
* `2020.1.2`
* `2020.1.1`
* `2020.1`
* `2019.3.4`
* `2019.3.3`
* `2019.3.2`
* `2019.3.1`
* `2019.3`
* `2019.2.4`
* `2019.2.3`
* `2019.2.2`
* `2019.2.1`
* `2019.2`
* `2019.1.3`
* `2019.1.2`
* `2019.1.1`
* `2019.1`
* `2018.3.6`
* `2018.3.5`
* `2018.3.4`
* `2018.3.3`
* `2018.3.2`
* `2018.3.1`
* `2018.3`
* `2018.2.5`
* `2018.2.4`
* `2018.2.3`
* `2018.2.2`
* `2018.2.1`
* `2018.2`
* `2018.1.6`
* `2018.1.5`
* `2018.1.4`
* `2018.1.3`
* `2018.1.2`
* `2018.1.1`
* `2018.1`
* `2017.3.5`
* `2017.3.4`
* `2017.3.3`
* `2017.3.2`
* `2017.3.1`
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

IntelliJ Plugin IDs
-------------------

JetBrains doesn't make the IntelliJ Plugin IDs visible on their marketplace
website
([https://plugins.jetbrains.com/idea](https://plugins.jetbrains.com/idea)). But
it's relatively easy to get the ID with a little JavaScript.

1. Search JetBrains Marketplace for a plugin you want to install and navigate to it's overview page
   (e.g. https://plugins.jetbrains.com/plugin/12195-concise-assertj-optimizing-nitpicker-cajon-).

2. Type `javascript:` into your browser address bar (don't press enter yet).

    Note: for security reasons you can't paste `javascript:` into the address
    bar (the browser won't let you), you have to type it.

3. Paste the following after `javascript:` followed by enter/return:

    ```
    fetch(window.location.pathname.replace(/\/plugin\/(\d+).*/, "/api/plugins/$1"))
        .then((response) => response.json())
        .then((data) => alert(`Plugin ID: "${data.xmlId}"`));
    ```

    This uses a RegEx to alter the path of the URL, and the
    [fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
    to make a request to the JetBrains plugins REST API. It then displays an
    alert showing the Plugin ID (`xmlId` from the JSON response).

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
      intellij_default_maven_home: '/opt/maven/apache-maven-3.9.4'
      users:
        - username: vagrant
          intellij_jdks:
            - name: '17'
              home: '/usr/lib/jvm/java-17-openjdk-amd64'
            - name: '11'
              home: '/usr/lib/jvm/java-11-openjdk-amd64'
            - name: '1.8'
              home: '/usr/lib/jvm/java-8-openjdk-amd64'
          intellij_default_jdk: '17'
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
            - name: Example1
              src: Example-style1.xml
            - name: Example2
              src: /example/Example-style2.xml
              remote_src: true
            - name: GoogleStyle
              url: 'https://raw.githubusercontent.com/google/styleguide/gh-pages/intellij-java-google-style.xml'
          intellij_default_codestyle: GoogleStyle
          intellij_inspection_profiles:
            - name: Example1
              src: Example1.xml
            - name: Example2
              src: /example/Example2.xml
              remote_src: true
            - name: GantSign
              url: 'https://raw.githubusercontent.com/gantsign/inspection-profile-intellij/master/GantSign.xml'
          intellij_default_inspection_profile: GantSign
          intellij_plugins:
            - CheckStyle-IDEA
```

Role Facts
----------

This role exports the following Ansible facts for use by other roles:


* `ansible_local.intellij.general.home`

    * e.g. `/opt/idea/idea-community-2024.3.5`

* `ansible_local.intellij.general.desktop_filename`

    * e.g. `jetbrains-idea-ce.desktop`

* `ansible_local.intellij.general.desktop_file`

    * e.g. `/usr/share/applications/jetbrains-idea-ce.desktop`

* `ansible_local.intellij.general.user_config_dir`

    * e.g. `.config/JetBrains/IntelliJIdea2023.2`

* `ansible_local.intellij.general.user_plugins_dir`

    * e.g. `.local/share/JetBrains/IntelliJIdea2023.2`

More Roles From GantSign
------------------------

You can find more roles from GantSign on
[Ansible Galaxy](https://galaxy.ansible.com/ui/standalone/namespaces/2463/).

Development & Testing
---------------------

This project uses the following tooling:
* [Molecule](http://molecule.readthedocs.io/) for orchestrating test scenarios
* [Testinfra](http://testinfra.readthedocs.io/) for testing the changes on the
  remote
* [pytest](http://docs.pytest.org/) the testing framework
* [Tox](https://tox.wiki/en/latest/) manages Python virtual
  environments for linting and testing
* [pip-tools](https://github.com/jazzband/pip-tools) for managing dependencies

A Visual Studio Code
[Dev Container](https://code.visualstudio.com/docs/devcontainers/containers) is
provided for developing and testing this role.

License
-------

MIT

Author Information
------------------

John Freeman

GantSign Ltd.
Company No. 06109112 (registered in England)
