#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for glossary terms
"""

import time
import json
import argparse
from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    AssetCatalog
)
# import pyegeria.X_asset_catalog_omvs
from rich.table import Table
from rich.live import Live
from rich import box
from rich.prompt import Prompt
from rich.tree import Tree
from rich import print
from rich.console import Console


from pyegeria.server_operations import ServerOps
from pyegeria._deprecated_gov_engine import GovEng
from pyegeria.glossary_browser_omvs import GlossaryBrowser
disable_ssl_warnings = True

def display_assets(search_string: str, guid: str, server: str, url: str, username: str):

    g_client = AssetCatalog(server, url, username)
    token = g_client.create_egeria_bearer_token(username, "secret")


    def generate_table(search_string:str = 'Enter Your Tech Type') -> Table:
        """Make a new table."""
        table = Table(
            title=f"Asset Definitions contining the string  {search_string} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{server}' @ Platform - {url}",
            expand=True
        )
        table.add_column("Display Name")
        table.add_column("Type Name")
        table.add_column("GUID", no_wrap=True)
        table.add_column("Technology Type")
        table.add_column("Path")
        table.add_column("Qualified Name")


        assets = g_client.find_assets_in_domain(search_string, starts_with=True,
                                             ends_with=False, ignore_case=True, page_size=10)
        if type(assets) is str:
            return table

        for element in assets:
            display_name = element.get("resourceName",'---')
            qualified_name = element["qualifiedName"]
            type_name = element["type"]["typeName"]
            tech_type = element.get("deployedImplementationType",'---')
            guid = element["guid"]
            path_name = element.get("extendedProperties", None)
            if path_name:
                path = path_name.get("pathName"," ")
            else:
                path = " "



            table.add_row(
                display_name, type_name,guid, tech_type, path, qualified_name
            )

        g_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console()
        with console.pager():
            console.print(generate_table(search_string))


    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
        assert e.related_http_code != "200", "Invalid parameters"

def main():
    sus_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--guid", help="GUID of glossary to search")
    parser.add_argument("--sustainability", help="Set True for Sustainability Glossary")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'
    guid = args.guid if args.guid is not None else None
    guid = sus_guid  if args.sustainability else None

    search_string = Prompt.ask("Enter a search string:", default="*")
    display_assets(search_string, guid,server, url, userid)

if __name__ == "__main__":
    main()