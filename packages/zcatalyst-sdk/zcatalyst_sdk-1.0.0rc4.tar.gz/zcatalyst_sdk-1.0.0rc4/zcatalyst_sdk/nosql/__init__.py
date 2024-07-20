from typing import List

from ..exceptions import CatalystNoSqlError
from .. import validator
from ..types.nosql import NoSqlTableResourceRes, NoSqlTableResponse
from ..types import Component
from .._http_client import AuthorizedHttpClient
from .._constants import RequestMethod, CredentialUser, Components
from ._table_items import TableItem


class NoSql(Component):
    def __init__(self, app) -> None:
        self._app = app
        self._requester = AuthorizedHttpClient(self._app)

    def get_component_name(self):
        return Components.NOSQL

    def get_all_tables(self) -> List[NoSqlTableResponse]:
        resp = self._requester.request(
            method=RequestMethod.GET, path="/nosqltable", user=CredentialUser.ADMIN
        )
        res = resp.response_json.get("data")
        return res

    def get_table_resources(self, table_name) -> NoSqlTableResourceRes:
        resp = self._requester.request(
            method=RequestMethod.GET,
            path=f"/nosqltable/{table_name}",
            user=CredentialUser.ADMIN,
        )
        res = resp.response_json.get("data")
        return res

    def get_table(self, table_id):
        validator.is_non_empty_string_or_number(
            table_id, "table_id", CatalystNoSqlError
        )
        try:
            return TableItem(self, int(table_id))
        except ValueError:
            return TableItem(self, str(table_id))
