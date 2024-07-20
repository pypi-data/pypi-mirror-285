from typing import List
from ..types.nosql import (
    NoSqlDeleteItemReq,
    NoSqlFetchItemReq,
    NoSqlInsertItemReq,
    NoSqlQueryItemReq,
    NoSqlTableResourceRes,
    NoSqlTableResponse,
    NoSqlUpdateItemReq,
)
from ..types import Component
from .._http_client import AuthorizedHttpClient
from .._constants import RequestMethod, CredentialUser, Components


class TableItem(Component):
    def __init__(self, nosql_instance, table_id) -> None:
        self._requester: AuthorizedHttpClient = nosql_instance._requester
        self.base_path = f"/nosqltable/{table_id}"

    def get_component_name(self):
        return Components.NOSQL

    def insert_items(self, input_data: NoSqlInsertItemReq):
        input_data_list = [input_data]
        resp = self._requester.request(
            method=RequestMethod.POST,
            path=self.base_path + "/item",
            json=input_data_list,
            user=CredentialUser.ADMIN,
        )
        res = resp.response_json.get("data")
        item_res = res.get("create")[0]
        insert_res = {**item_res, "size": res.get("size")}
        return insert_res

    def fetch_item(self, input_data: NoSqlFetchItemReq) -> NoSqlTableResourceRes:
        resp = self._requester.request(
            method=RequestMethod.POST,
            path=self.base_path + "/item/fetch",
            json=input_data,
            user=CredentialUser.ADMIN,
        )
        res = resp.response_json.get("data")
        return res

    def update_items(self, input_data: NoSqlUpdateItemReq) -> List[NoSqlTableResponse]:
        input_data = [input_data]
        print(input_data)
        resp = self._requester.request(
            method=RequestMethod.PUT,
            path=self.base_path + "/item",
            json=input_data,
            user=CredentialUser.ADMIN,
        )
        res = resp.response_json.get("data")
        return res

    def delete_items(self, input_data: NoSqlDeleteItemReq) -> NoSqlTableResourceRes:
        input_data = [input_data]
        resp = self._requester.request(
            method=RequestMethod.DELETE,
            path=self.base_path + "/item",
            json=input_data,
            user=CredentialUser.ADMIN,
        )
        res = resp.response_json.get("data")
        return res

    def query_table(self, input_data: NoSqlQueryItemReq) -> List[NoSqlTableResponse]:
        resp = self._requester.request(
            method=RequestMethod.POST,
            path=self.base_path + "/item/query",
            json=input_data,
            user=CredentialUser.ADMIN,
        )
        res = resp.response_json.get("data")
        return res

    def query_index(
        self, index_id, input_data: NoSqlQueryItemReq
    ) -> NoSqlTableResourceRes:
        resp = self._requester.request(
            method=RequestMethod.POST,
            path=self.base_path + f"/index/{index_id}/item/query",
            json=input_data,
            user=CredentialUser.ADMIN,
        )
        res = resp.response_json.get("data")
        return res
