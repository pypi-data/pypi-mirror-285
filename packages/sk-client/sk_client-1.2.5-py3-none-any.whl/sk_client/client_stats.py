#!/usr/bin/python3

from http import HTTPStatus
from typing import List

from requests import Response

from sk_schemas.stats import (
    API_STATS_V1,
    API_STATS_V2,
    DpStats,
    FileDataModel,
    StatsStringModel,
)

from .client_base import HttpClient


class ClientStatsMgr:
    def __init__(self, http_client: HttpClient) -> None:
        self.http_client = http_client

    def get_hw_stats(self, iface_name=None) -> tuple[Response, StatsStringModel | None]:

        iface_ep = ""
        if iface_name:
            iface_ep = f"/{iface_name}"

        resp = self.http_client.http_get(API_STATS_V1 + "/hw" + iface_ep)

        if resp and resp.status_code == HTTPStatus.OK:
            stats_json = resp.json()
            return resp, StatsStringModel(**stats_json)

        return resp, None

    def get_ipsec_stats(self) -> tuple[Response, StatsStringModel | None]:

        resp = self.http_client.http_get(API_STATS_V1 + "/ipsec")

        if resp and resp.status_code == HTTPStatus.OK:
            stats_json = resp.json()
            return resp, StatsStringModel(**stats_json)

        return resp, None

    def get_ipsec_counter_history(
        self,
    ) -> tuple[Response, list[DpStats]]:

        resp = self.http_client.http_get(API_STATS_V1 + "/history/ipsec")

        ret = []
        if resp and resp.status_code == HTTPStatus.OK:
            for k in resp.json():
                ret.append(DpStats(**k))
            return resp, ret
        return resp, ret

    def get_error_counter_history(
        self,
    ) -> tuple[Response, list[DpStats]]:

        resp = self.http_client.http_get(API_STATS_V1 + "/history/errors")

        ret = []
        if resp and resp.status_code == HTTPStatus.OK:
            for k in resp.json():
                ret.append(DpStats(**k))
            return resp, ret
        return resp, ret

    def get_iface_counter_history(
        self,
    ) -> tuple[Response, list[DpStats]]:

        resp = self.http_client.http_get(API_STATS_V1 + "/history/iface")

        ret = []
        if resp and resp.status_code == HTTPStatus.OK:
            for k in resp.json():
                ret.append(DpStats(**k))
            return resp, ret
        return resp, ret

    def get_sa_counter_history(
        self,
    ) -> tuple[Response, list[DpStats]]:

        resp = self.http_client.http_get(API_STATS_V1 + "/history/sas")

        ret = []
        if resp and resp.status_code == HTTPStatus.OK:
            for k in resp.json():
                ret.append(DpStats(**k))
            return resp, ret
        return resp, ret

    def get_runtime_stats(self) -> tuple[Response, StatsStringModel | None]:

        resp = self.http_client.http_get(API_STATS_V1 + "/runtime")

        if resp and resp.status_code == HTTPStatus.OK:
            stats_json = resp.json()
            return resp, StatsStringModel(**stats_json)

        return resp, None

    def get_error_stats(
        self,
    ) -> tuple[Response, StatsStringModel | None]:

        resp = self.http_client.http_get(API_STATS_V1 + "/errors")

        if resp and resp.status_code == HTTPStatus.OK:
            stats_json = resp.json()
            return resp, StatsStringModel(**stats_json)

        return resp, None

    def get_error_stats_v2(
        self,
    ) -> tuple[Response, DpStats | None]:

        resp = self.http_client.http_get(API_STATS_V2 + "/errors")

        if resp and resp.status_code == HTTPStatus.OK:
            stats_json = resp.json()
            return resp, DpStats(**stats_json)

        return resp, None

    def get_iface_stats(self) -> tuple[Response, DpStats | None]:

        resp = self.http_client.http_get(API_STATS_V1 + "/iface")

        if resp and resp.status_code == HTTPStatus.OK:
            stats_json = resp.json()
            return resp, DpStats(**stats_json)

        return resp, None

    def get_crypto_stats(self) -> tuple[Response, List[FileDataModel]]:

        resp = self.http_client.http_get(API_STATS_V1 + "/crypto")

        resp_list = []
        if resp and resp.status_code == HTTPStatus.OK:
            data = resp.json()
            for k in data:
                resp_list.append(FileDataModel(**k))
        return resp, resp_list
