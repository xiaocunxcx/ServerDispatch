from __future__ import annotations

from dataclasses import dataclass

from ldap3 import Connection, Server

from internal.config.settings import Settings


@dataclass
class LdapClient:
    settings: Settings

    def authenticate(self, ldap_id: str, password: str) -> bool:
        user_dn = self.settings.ldap_user_dn_template.format(ldap_id=ldap_id)
        server = Server(self.settings.ldap_uri, get_info=None)
        connection = None
        try:
            connection = Connection(server, user=user_dn, password=password, auto_bind=True)
        except Exception:
            return False
        finally:
            if connection:
                connection.unbind()
        return True
