![PyPI - License](https://img.shields.io/pypi/l/taiga-contrib-ldap-auth-ext.svg?style=flat-square)

# Taiga contrib ldap auth ext²

Extended [Taiga.io](https://taiga.io/) plugin for LDAP authentication.

This is a fork of [Monogramm/taiga-contrib-ldap-auth-ext](https://github.com/Monogramm/taiga-contrib-ldap-auth-ext), which, in turn, is a fork of [ensky/taiga-contrib-ldap-auth](https://github.com/ensky/taiga-contrib-ldap-auth).

Compared to Monogramm/taiga-contrib-ldap-auth-ext, this repo has the following changes:

* Sanitize the username before using it in an LDAP filter, preventing LDAP injection (feature branch [`sanitize-data-before-passing-to-ldap`](https://github.com/TuringTux/taiga-contrib-ldap-auth-ext/tree/sanitize-data-before-passing-to-ldap), [PR #47 in the Monogramm repo](https://github.com/Monogramm/taiga-contrib-ldap-auth-ext/pull/47))
* Updated README: Explanations for Docker added, sample configuration adjusted

You can always also [compare the changes in-depth on GitHub](https://github.com/Monogramm/taiga-contrib-ldap-auth-ext/compare/master...TuringTux:taiga-contrib-ldap-auth-ext:master).

## Installation

You can use pip to install this fork directly from Git in your `taiga-back` environment:

```bash
pip install git+https://github.com/TuringTux/taiga-contrib-ldap-auth-ext.git
```

🐋 If you use the Taiga Docker setup, see the “Installation & Configuration with Docker“ section below.

## Configuration

### taiga-back

Add the following settings. You can either insert them into `settings/common.py` or append them to `settings/config.py` – both worked in our tests.

```python
INSTALLED_APPS += ["taiga_contrib_ldap_auth_ext"]

LDAP_SERVER = "ldaps://ldap.example.com"
LDAP_PORT = 636

# Note (1): This uses an encrypted ldap connection (like https:// in the browser) and
# should be safe by default.

# Note (2): If you want to use unencrypted, insecure LDAP instead, use the following:
# LDAP_SERVER = "ldap://ldap.example.com"
# LDAP_PORT = 389

# Note (3): If you want to use LDAP with STARTTLS before bind, use the following:
# LDAP_SERVER = "ldap://ldap.example.com"
# LDAP_PORT = 389
# LDAP_START_TLS = True

# Note (4): Specifying multiple LDAP servers is currently not supported, see
# https://github.com/Monogramm/taiga-contrib-ldap-auth-ext/issues/16

# Full DN of the service account use to connect to LDAP server and search for login user's account entry
# If LDAP_BIND_DN is not specified, or is blank, then an anonymous bind is attempated
LDAP_BIND_DN = 'CN=SVC Account,OU=Service Accounts,OU=Servers,DC=example,DC=com'
LDAP_BIND_PASSWORD = '<REPLACE_ME>'

# Starting point within LDAP structure to search for login user
LDAP_SEARCH_BASE = 'OU=DevTeam,DC=example,DC=net'

# Additional search criteria to the filter (will be ANDed)
#LDAP_SEARCH_FILTER_ADDITIONAL = '(mail=*)'

# Names of attributes to get username, e-mail and full name values from
# These fields need to have a value in LDAP 
LDAP_USERNAME_ATTRIBUTE = 'uid'
LDAP_EMAIL_ATTRIBUTE = 'mail'
LDAP_FULL_NAME_ATTRIBUTE = 'displayName'

LDAP_SAVE_LOGIN_PASSWORD = False
# Note: If you want to store the passwords in the local database as well, remove
# the line above.

LDAP_MAP_USERNAME_TO_UID = None
# Note: This means "use the entered username as LDAP uid as-is, do not use any mapping"
# Sanitization of the username is nevertheless performed, so don't worry.
# This only fixes a bug (if left out, the plugin would try to use a mapping function
# that cannot be used for this purpose).

# ... A few more options can be found in the Monogramm repository
```

A dedicated domain service account user (specified by `LDAP_BIND_DN`)
performs a search on LDAP for an account that has a
`LDAP_USERNAME_ATTRIBUTE` or `LDAP_EMAIL_ATTRIBUTE` matching the
user-provided login.

If the search is successful, then the returned entry and the
user-provided password are used to attempt a bind to LDAP. If the bind is
successful, then we can say that the user is authorised to log in to
Taiga.

If the `LDAP_BIND_DN` configuration setting is not specified or is
blank, then an anonymous bind is attempted to search for the login
user's LDAP account entry.

**RECOMMENDATION**: for security reasons, if you are using a service
account for performing the LDAP search, it should be configured to only
allow reading/searching the LDAP structure. No other LDAP (or wider
network) permissions should be granted for this user because you need
to specify the service account password in the configuration file. A
suitably strong password should be chosen, eg. VmLYBbvJaf2kAqcrt5HjHdG6


**Notes:**
* if you are using the Taiga's built-in `USER_EMAIL_ALLOWED_DOMAINS` config option, all LDAP email addresses will still be filtered through this list. Ensure that if `USER_EMAIL_ALLOWED_DOMAINS` != `None`, that your corporate LDAP email domain is also listed there. This is due to the fact that LDAP users are automatically "registered" behind the scenes on their first login.
* if you plan to only allow your LDAP users to access Taiga, set the `PUBLIC_REGISTER_ENABLED` config option to `False`. This will prevent any external user to register while still automatically register LDAP users on their first login.

### taiga-front

Change the `loginFormType` setting to `"ldap"` in `dist/conf.json`:

```json
    ...
    "loginFormType": "ldap",
    ...
```

## Installation & Configuration with Docker

### taiga-back

If you installed Taiga using the [`taiga-docker`](https://github.com/kaleidos-ventures/taiga-docker) repository, try the following:

1. Edit the `taiga-back` section in the `docker-compose.yml`: Replace `image: taigaio/taiga-back:latest` with `build: ./custom-back`
2. Create a folder `custom-back` next to the `docker-compose.yml` file
3. In this folder, create a file `config.append.py` with the added configuration for `taiga-back` (the one we described above).
4. In this folder, also create a `Dockerfile` with the following content:

    ```Dockerfile
    FROM taigaio/taiga-back:latest

    # Insert custom configuration into the taiga configuration file
    COPY config.append.py /taiga-back/settings
    RUN cat /taiga-back/settings/config.append.py >> /taiga-back/settings/config.py && rm /taiga-back/settings/config.append.py
 
    # Install git, because we need it to install the taiga-ldap-contrib-auth-ext package
    RUN apt-get update \
        && apt-get install -y git \
        && rm -rf /var/lib/apt/lists/*

    RUN pip install git+https://github.com/TuringTux/taiga-contrib-ldap-auth-ext.git

    RUN apt-get purge -y git \
        && apt-get autoremove -y
    ```

If you now start Taiga like you would normally in the Docker setup, the `taiga-back` image will not be pulled directly from Docker Hub, instead, the `Dockerfile` you just specified will be built:

- This image is based on the latest `taigaio/taiga-back` image.
- It however, also inserts the relevant configuration.
- Furthermore, it fetches the apt package lists, installs Git and removes the lists again (to save some space)
- It then installs this plugin directly from GitHub
- Afterwards, Git is removed from the image because it isn't needed in production.
