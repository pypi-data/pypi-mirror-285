# © Copyright 2024 Hewlett Packard Enterprise Development LP
from argparse import Namespace
from typing import Any, List

import aiolirest
from aioli import cli
from aioli.cli import render
from aioli.common.api import authentication
from aioli.common.declarative_argparse import Arg, Cmd
from aiolirest.models.role import Role
from aiolirest.models.role_assignment import RoleAssignment
from aiolirest.models.role_assignments import RoleAssignments


@authentication.required
def list_roles(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RolesApi(session)
        response = api_instance.roles_get()

    def format_roles(r: Role) -> List[Any]:
        result = [
            r.id,
            r.role_name,
        ]
        return result

    headers = [
        "ID",
        "Role Name",
    ]

    values = [format_roles(r) for r in response]
    render.tabulate_or_csv(headers, values, args.csv)


@authentication.required
def list_user_roles(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RolesApi(session)
        response = api_instance.roles_assignments_get(args.username)

    def format_assignments(r: RoleAssignment) -> List[Any]:
        result = [
            r.user_name,
            r.role_name,
        ]
        return result

    headers = [
        "User Name",
        "Role Name",
    ]

    values = [format_assignments(r) for r in response]
    render.tabulate_or_csv(headers, values, args.csv)


@authentication.required
def assign_role(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RolesApi(session)

    assignments = []
    assignments.append(RoleAssignment(userName=args.u, roleName=args.role))

    api_instance.roles_add_assignments_post(RoleAssignments(userRoleAssignments=assignments))


@authentication.required
def unassign_role(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RolesApi(session)

    assignments = []
    assignments.append(RoleAssignment(userName=args.u, roleName=args.role))

    api_instance.roles_remove_assignments_post(RoleAssignments(userRoleAssignments=assignments))


main_cmd = Cmd(
    "rbac",
    None,
    "role management",
    [
        Cmd(
            "list-roles ls",
            list_roles,
            "list roles",
            [
                Arg("--csv", action="store_true", help="print as CSV"),
            ],
            is_default=True,
        ),
        Cmd(
            "list-user-roles lu",
            list_user_roles,
            "list roles for a user",
            [
                Arg("username", help="The name of the user"),
                Arg("--csv", action="store_true", help="print as CSV"),
            ],
        ),
        Cmd(
            "assign-role",
            assign_role,
            "assign a role to a user",
            [
                Arg(
                    "role",
                    help="role name",
                ),
                Arg("-u", help="The name of the user", required="true"),
            ],
        ),
        Cmd(
            "unassign-role",
            unassign_role,
            "unassign a role for a user",
            [
                Arg(
                    "role",
                    help="role name",
                ),
                Arg("-u", help="The name of the user", required="true"),
            ],
        ),
    ],
)


args_description = [main_cmd]  # type: List[Any]
