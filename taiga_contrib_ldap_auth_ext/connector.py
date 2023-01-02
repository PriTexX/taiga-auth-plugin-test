# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import requests
from django.conf import settings
from taiga.base.connectors.exceptions import ConnectorBaseException

headers = {"accept": "application/json"}

class CooonnectionError(ConnectorBaseException):
    pass


# TODO https://github.com/Monogramm/taiga-contrib-ldap-auth-ext/issues/16

def login(username: str, password: str) -> tuple:
    """
    Connect to LDAP server, perform a search and attempt a bind.

    Can raise `exc.LDAPConnectionError` exceptions if the
    connection to LDAP fails.

    Can raise `exc.LDAPUserLoginError` exceptions if the
    login to LDAP fails.

    :param username: a possibly unsanitized username
    :param password: a possibly unsanitized password
    :returns: tuple (username, email, full_name)

    """

    try:
        response = requests.post("http://auth-service/login", data={"username": username, "password": password}, headers=headers)

        if(response.status_code != 200):
            raise Exception("fff")

        body = response.json()

        full_name = body["fullname"]
        email = body["email"]

    except Exception as ex:
        raise CooonnectionError(ex)

    return (username, email, full_name)
