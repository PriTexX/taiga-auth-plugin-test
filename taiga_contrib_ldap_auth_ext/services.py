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
import logging

from django.db import transaction as tx
from django.apps import apps

from taiga.base.connectors.exceptions import ConnectorBaseException, BaseException
from taiga.auth.services import send_register_email
from taiga.auth.services import make_auth_response_data
from taiga.auth.signals import user_registered as user_registered_signal

from . import connector


def ldap_login_func(request):
    """
    Login a user using LDAP.

    This will first try to authenticate user against LDAP.
    If authentication is succesful, it will register user in Django DB from LDAP data.
    If LDAP authentication fails, it will either use FALLBACK login or crash.

    Can raise `ConnectorBaseException` exceptions in case of authentication failure.
    Can raise `exc.IntegrityError` exceptions in case of conflict found.

    :returns: User
    """
    # although the form field is called 'username', it can be an e-mail
    # (or any other attribute)

    login_input = request.DATA.get('username', None)
    password_input = request.DATA.get('password', None)
    logger = logging.getLogger("auth")

    logger.info(f"{login_input} fgdfggrg")


    username, email, full_name = connector.login(
        username=login_input, password=password_input)

    user = register_or_update(
        username=username, email=email, full_name=full_name, password=password_input)
    data = make_auth_response_data(user)
    return data


@tx.atomic
def register_or_update(username: str, email: str, full_name: str, password: str):
    """
    Register new or update existing user in Django DB from LDAP data.

    Can raise `exc.IntegrityError` exceptions in case of conflict found.

    :returns: User
    """
    user_model = apps.get_model('users', 'User')

    username_unique = username

    # TODO https://github.com/Monogramm/taiga-contrib-ldap-auth-ext/issues/15
    # TODO https://github.com/Monogramm/taiga-contrib-ldap-auth-ext/issues/17
    superuser = False

    try:
        # has user logged in before?
        user = user_model.objects.get(username=username_unique)
    except user_model.DoesNotExist:
        # create a new user
        user = user_model.objects.create(username=username_unique,
                                         email=email,
                                         full_name=full_name,
                                         is_superuser=superuser)
        user.save()

        user_registered_signal.send(sender=user.__class__, user=user)
        send_register_email(user)
    else:
        user.set_password(None)

        user.save()
        # update DB entry if LDAP field values differ
        if user.email != email or user.full_name != full_name:
            user_object = user_model.objects.filter(pk=user.pk)
            user_object.update(email=email, full_name=full_name)
            user.refresh_from_db()

    return user
