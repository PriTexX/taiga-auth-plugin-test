![PyPI - License](https://img.shields.io/pypi/l/taiga-contrib-ldap-auth-ext.svg?style=flat-square)

# Taiga contrib ldap auth

Extended [Taiga.io](https://taiga.io/) plugin for LDAP authentication.

This is a fork of [Monogramm/taiga-contrib-ldap-auth-ext](https://github.com/Monogramm/taiga-contrib-ldap-auth-ext), which, in turn, is a fork of [ensky/taiga-contrib-ldap-auth](https://github.com/ensky/taiga-contrib-ldap-auth).

Compared to Monogramm/taiga-contrib-ldap-auth-ext, this repo has the following changes:

* Sanitize the username before using it in an LDAP filter, preventing LDAP injection (feature branch [`sanitize-data-before-passing-to-ldap`](https://github.com/TuringTux/taiga-contrib-ldap-auth-ext/tree/sanitize-data-before-passing-to-ldap), [PR #47 in the Monogramm repo](https://github.com/Monogramm/taiga-contrib-ldap-auth-ext/pull/47))
* Updated README

## Installation

Install using pip in the `taiga-back` environment. If you are using the dockerized version, you might want to create a custom image based on the taiga-back image, which has Git and this package installed.

```bash
pip install git+https://github.com/TuringTux/taiga-contrib-ldap-auth-ext.git
```

## Configuration

### taiga-back

Add the following to `settings/common.py` (for Taiga >5.0). Note that changing `settings/config.py` does not work, you have to change `settings/common.py`:

```python
INSTALLED_APPS += ["taiga_contrib_ldap_auth_ext"]

# TODO https://github.com/Monogramm/taiga-contrib-ldap-auth-ext/issues/16
LDAP_SERVER = 'ldap://ldap.example.com'
LDAP_PORT = 389

# Flag to enable LDAP with STARTTLS before bind
LDAP_START_TLS = False

# Support of alternative LDAP ciphersuites
#from ldap3 import Tls
#import ssl

#LDAP_TLS_CERTS = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1, ciphers='RSA+3DES')

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

# Option to not store the passwords in the local db
#LDAP_SAVE_LOGIN_PASSWORD = False

# TODO https://github.com/Monogramm/taiga-contrib-ldap-auth-ext/issues/15
# Group search filter where $1 is the project slug and $2 is the role slug
#LDAP_GROUP_SEARCH_FILTER = 'CN=$2,OU=$1,OU=Groups,DC=example,DC=net'

# TODO https://github.com/Monogramm/taiga-contrib-ldap-auth-ext/issues/15
# Use an attribute in the user entry for membership
#LDAP_USER_MEMBER_ATTRIBUTE = 'memberof,primaryGroupID'

# TODO https://github.com/Monogramm/taiga-contrib-ldap-auth-ext/issues/15
# Starting point within LDAP structure to search for login group
#LDAP_GROUP_SEARCH_BASE = 'OU=Groups,DC=example,DC=net'
# Group classes filter
#LDAP_GROUP_FILTER = '(|(objectclass=group)(objectclass=groupofnames)(objectclass=groupofuniquenames))'
# Group member attribute
#LDAP_GROUP_MEMBER_ATTRIBUTE = 'memberof,primaryGroupID'

# TODO https://github.com/Monogramm/taiga-contrib-ldap-auth-ext/issues/17
# Taiga super users group id
#LDAP_GROUP_ADMIN = 'OU=TaigaAdmin,DC=example,DC=net'

# Fallback on normal authentication method if LDAP auth fails. Uncomment to disable and only allow LDAP login.
#LDAP_FALLBACK = ""

# Function to map LDAP username to local DB user unique identifier.
# Upon successful LDAP bind, will override returned username attribute
# value. May result in unexpected failures if changed after the database
# has been populated.
# 
def _ldap_slugify(uid: str) -> str:
    # example: force lower-case
    #uid = uid.lower()
    return uid
    
# To enable the function above, uncomment the line below to store the function in the variable
#LDAP_MAP_USERNAME_TO_UID = _ldap_slugify

# Similarly, you can apply filters to the email and name by defining functions and specifying them here in the same way
#LDAP_MAP_EMAIL = _ldap_map_email
#LDAP_MAP_NAME = _ldap_map_name


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
