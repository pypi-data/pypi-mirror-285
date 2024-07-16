#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020-2023 (c) Randy W @xtdevs, @xtsea
#
# from : https://github.com/TeamKillerX
# Channel : @RendyProjects
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

from typing import List, Optional, Union

import requests


class SibylBan:
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def _make_request(self, method: str, url: str, params: dict = None, json_data: dict = None):
        headers = {"accept": "application/json", "api-key": self.api_key}
        try:
            response = requests.request(
                method, url, headers=headers, params=params, json=json_data
            )
            return response.json()
        except requests.RequestException:
            pass

    def add_ban(self, user_id: int = None, reason: str = None, is_banned: bool = False) -> str:
        if is_banned:
            url = "https://randydev-ryuzaki-api.hf.space/sibylban"
            payload = {"user_id": user_id, "reason": reason}
            response = self._make_request("POST", url, json_data=payload)
            return response.get("randydev", {}).get(
                "message", response.get("message", "Unknown error")
            )
        else:
            raise ValueError("Error: is_banned must be True")

    def get_ban(self, user_id: int = None, banlist: bool = False) -> Union[dict, str]:
        if banlist:
            url = "https://randydev-ryuzaki-api.hf.space/ryuzaki/sibyl"
            payload = {"user_id": user_id}
            return self._make_request("GET", url, json_data=payload)
        else:
            raise ValueError("Error: banlist must be True")

    def unban_del(self, user_id: int = None, delete: bool = False) -> Union[dict, str]:
        if delete:
            url = "https://randydev-ryuzaki-api.hf.space/ryuzaki/sibyldel"
            payload = {"user_id": user_id}
            return self._make_request("DELETE", url, json_data=payload)
        else:
            raise ValueError("Error: delete must be True")

    def get_all_banlist(self) -> Union[dict, str]:
        url = "https://randydev-ryuzaki-api.hf.space/ryuzaki/getbanlist"
        return self._make_request("GET", url)
