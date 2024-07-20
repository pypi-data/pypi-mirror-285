#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple viewer for collections - provide the root and we display the hierarchy

"""

import argparse

from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.tree import Tree
from rich.console import Console
from pyegeria import (UserNotAuthorizedException, PropertyServerException,
                      InvalidParameterException, AutomatedCuration)
from pyegeria._exceptions import (
    print_exception_response,
)

console = Console()
disable_ssl_warnings = True

platform = "https://127.0.0.1:9443"
user = "erinoverview"
view_server = "view-server"


def tech_viewer(tech: str, server_name:str, platform_url:str, user:str):

    def view_tech_details(a_client: AutomatedCuration, root_collection_name: str, tree: Tree) -> Tree:
        l2: Tree = None
        tech_details = a_client.get_technology_type_detail(tech)
        if (type(tech_details) is dict) and (len(tech_details)>0):
            name = tech_details.get('name','---')
            qualified_name = tech_details.get('qualifiedName',"---")
            category = tech_details.get('category','---')
            description = tech_details.get('description','---')

            style = ""
            l2 = tree.add(Text(f"Name: {name}", "bold red"))
            l2 = tree.add(Text(f"* QualifiedName: {qualified_name}","bold white"))
            l2 = tree.add(Text(f"* Category: {category}", "bold white"))
            l2 = tree.add(Text(f"* Technology Description: {description}", "bold white"))
            ext_ref = tech_details.get('externalReferences', None)

            if ext_ref is not None:
                uri = ext_ref[0]["properties"].get("uri", "---")
                # console.print(f" {type(ext_ref)}, {len(ext_ref)}")
                l2 = tree.add(Text(f'* URI: {uri}', "bold white"))

            resource_list = tech_details.get('resourceList',None)
            if resource_list:
                t_r = tree.add("Resource List[bold red]")
                for resource in resource_list:
                    resource_use = Text(f"[bold white]{resource.get('resourceUse','---')}", "")
                    resource_use_description = Text(f"[bold white]{resource.get('resourceUseDescription','---')}", "")
                    type_name = Text(f"[bold white]{resource['relatedElement']['type'].get('typeName','---')}", "")
                    unique_name = Text(f"[bold white]{resource['relatedElement'].get('uniqueName','---')}", "")
                    related_guid = Text(f"[bold white]{resource['relatedElement'].get('guid','---')}", "")
                    resource_text = (f"[bold red]Resource\n"
                                     f"[white]Resource use: {resource_use}[white]\nDescription: "
                                     f"{resource_use_description}\nType Name: {type_name}\n"
                                     f"[white]Unique Name: {unique_name}\n[white]Related GUID: {related_guid}\n")
                    p = Panel.fit(resource_text)
                    tt = t_r.add(p, style=style)

        else:
            tt = tree.add(f"Tech type {tech} was not found - please check the tech type name")

        return tt

    try:
        tree = Tree(f"[bold bright green]{tech}", guide_style="bold bright_blue")
        a_client = AutomatedCuration(view_server, platform,
                                     user_id=user)

        token = a_client.create_egeria_bearer_token(user, "secret")
        view_tech_details(a_client,tech,tree)
        print(tree)

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException
    ) as e:
        print_exception_response(e)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'erinoverview'

    tech = Prompt.ask("Enter the Technology to start from:", default="PostgreSQL Server")
    tech_viewer(tech,server, url, userid)

if __name__ == "__main__":
    main()