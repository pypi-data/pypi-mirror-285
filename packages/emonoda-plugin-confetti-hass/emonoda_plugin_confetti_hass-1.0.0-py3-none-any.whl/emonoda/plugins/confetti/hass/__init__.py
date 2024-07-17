"""
    Emonoda -- A set of tools to organize and manage your torrents

    hass.py -- create notifications via home assistant
    Copyright (C) 2024  Pavel Pletenev <cpp.create@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import asyncio

from typing import List
from typing import Dict
from typing import Any

from emonoda.optconf import Option
from emonoda.optconf import SecretOption
from emonoda.optconf.converters import as_string_list
from emonoda.optconf.converters import as_path_or_empty


from emonoda.plugins.confetti import ResultsType
from emonoda.plugins.confetti import WithStatuses
from emonoda.plugins.confetti import STATUSES

try:
    from homeassistant_api import Client  # pylint: disable=import-error
except ImportError:
    Client = None


# =====
class Plugin(WithStatuses):  # pylint: disable=too-many-instance-attributes
    PLUGIN_NAMES = ["hass"]

    def __init__(  # pylint: disable=super-init-not-called,too-many-arguments
        self,
        api_url: str,
        token: str,
        title: str,
        template: str,
        **kwargs: Any,
    ) -> None:

        self._init_bases(**kwargs)

        self.__api_url = api_url
        self.__token = token
        self.__title = title
        self.__template_path = template

    @classmethod
    def get_options(cls) -> Dict[str, Option]:
        return cls._get_merged_options({
            "api_url":  SecretOption(default="http://localhost:8123/api", help="HomeAssistant server api url"),
            "token":    SecretOption(default="CHANGE_ME",  help="Refresh or long lived access token"),
            "title":    Option(default="{source} report for {name}", help="Title of the notification"),
            "template": Option(default="", type=as_path_or_empty, help="Mako template file name")
        })

    def send_results(self, source: str, results: ResultsType) -> None:
        messages = [
            {
                "message": Plugin.templated(
                    name=(self.__template_path if self.__template_path else "hass.{source}.mako").format(source=source),
                    built_in=(not self.__template_path),
                    source=source,
                    file_name=file_name,
                    status=status,
                    status_msg=STATUSES[status],
                    result=result,
                ),
                "title": self.__title.format(source=source, name=result.torrent.get_name())
            }
            for status in self._statuses
            for (file_name, result) in results[status].items()
        ]
        with Client(
            self.__api_url, self.__token,
        ) as client:
            pn = client.get_domain("persistent_notification")
            create_pn = pn.get_service("create")
            for msg in messages:
                create_pn.trigger(**msg)

