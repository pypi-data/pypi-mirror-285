# © Copyright 2024 Hewlett Packard Enterprise Development LP

import argparse
from typing import Any, List

import aioli
import aioli.cli
import aioli.cli.errors
import aioli.cli.render
import aioli.common.api.authentication
import aioli.common.declarative_argparse
import aiolirest


def format_token(t: aiolirest.DeploymentToken) -> List[Any]:
    result = [t.id, t.description, t.username, t.deployment, t.expiration, t.revoked]
    return result


@aioli.common.api.authentication.required
def create_token(parsed_args: argparse.Namespace) -> None:
    """Create a deployment token with the provided arguments.

    Invoke the Aioli Tokens API to create the deployment token. Print the ID of the deployment
    token created on the console.

    Args:
        parsed_args: command line arguments provided by the user. The deployment name argument
        is required, and the description and expiration arguments are optional.
    """
    with aioli.cli.setup_session(parsed_args) as session:
        tokens_api = aiolirest.TokensApi(session)

    token_request = aiolirest.DeploymentTokenRequest(
        user=parsed_args.username,
        deployment=parsed_args.deployment,
        description=parsed_args.description,
        expiration=parsed_args.expiration,
    )
    token = tokens_api.tokens_post(request=token_request)
    print(token.id)


@aioli.common.api.authentication.required
def list_tokens(parsed_args: argparse.Namespace) -> None:
    """List active deployment tokens accessible to the current user.

    Invoke the Aioli Tokens API and fetch deployment tokens accessible to the current user.
    Only active tokens are listed by default. Adding the all flag will get all tokens for the
    all users if the user is has an admin role and all tokens for the current user otherwise.
    Format and display the deployment tokens on the console as a table by default. Output can be
    formatted as JSON or CSV based on the json or csv flag provided by the user.

    Args:
        parsed_args: command line arguments provided by the user. Includes json or csv flag to
        indicating output format. Includes all flag indicating token list should
        include all tokens for all users for admin users and all tokens for current user for other
        users.
    """
    with aioli.cli.setup_session(parsed_args) as session:
        tokens_api = aiolirest.TokensApi(session)
        if parsed_args.all:
            response = tokens_api.tokens_get(all="")
        else:
            response = tokens_api.tokens_get()

    if parsed_args.json:
        tokens = [token.to_dict() for token in response]
        aioli.cli.render.print_json(tokens)
    else:
        headers = ["ID", "Description", "Username", "Deployment", "Expiration", "Revoked"]
        values = [format_token(t) for t in response]
        aioli.cli.render.tabulate_or_csv(headers, values, parsed_args.csv)


@aioli.common.api.authentication.required
def get_token(parsed_args: argparse.Namespace) -> None:
    """Get the deployment token with the provided ID.

    Invoke the Aioli Tokens API to get the deployment token with the provided ID. Display the
    deployment token details in JSON format on the console.

    Args:
        parsed_args: command line arguments provided by the user. Includes ID for the deployment
        token.
    """
    with aioli.cli.setup_session(parsed_args) as session:
        tokens_api = aiolirest.TokensApi(session)
        token = tokens_api.tokens_id_get(parsed_args.id)
        if parsed_args.json:
            aioli.cli.render.print_json(token.to_json())
        else:
            token_yaml = aioli.cli.render.format_object_as_yaml(token.to_dict())
            print(token_yaml)


@aioli.common.api.authentication.required
def delete_token(parsed_args: argparse.Namespace) -> None:
    """Delete the deployment token with the provided ID.

    Invoke the Aioli Tokens API to delete the deployment token with the provided ID.

    Args:
        parsed_args: command line arguments provided by the user. Includes ID for the deployment
        token.
    """
    with aioli.cli.setup_session(parsed_args) as session:
        tokens_api = aiolirest.TokensApi(session)
        tokens_api.tokens_id_delete(parsed_args.id)


@aioli.common.api.authentication.required
def update_token(parsed_args: argparse.Namespace) -> None:
    """Update the description for the deployment token with the provided ID.

    Invoke the Aioli Tokens API to update the description for the deployment token with the
    provided ID.

    Args:
        parsed_args: command line arguments provided by the user. Includes ID for the deployment
        token and the updated description.
    """
    with aioli.cli.setup_session(parsed_args) as session:
        tokens_api = aiolirest.TokensApi(session)
        token_patch_request = aiolirest.DeploymentTokenPatchRequest(
            description=parsed_args.description,
        )
        tokens_api.tokens_id_patch(parsed_args.id, token_patch_request)


@aioli.common.api.authentication.required
def revoke_token(parsed_args: argparse.Namespace) -> None:
    """Revoke the deployment token with the provided ID.

    Invoke the Aioli Tokens API to revoke the deployment token with the provided ID.

    Args:
        parsed_args: command line arguments provided by the user. Includes ID for the deployment
        token to be revoked.
    """
    with aioli.cli.setup_session(parsed_args) as session:
        tokens_api = aiolirest.TokensApi(session)
        token_patch_request = aiolirest.DeploymentTokenPatchRequest(
            revoked=True,
        )
        tokens_api.tokens_id_patch(parsed_args.id, token_patch_request)


# fmt: off

args_description = [
    aioli.common.declarative_argparse.Cmd("t|oken|s", None, "manage deployment tokens", [
        aioli.common.declarative_argparse.Cmd("create", create_token, "create deployment token", [
            aioli.common.declarative_argparse.Arg(
                "deployment", help="The deployment for which the token will be created.",
            ),
            aioli.common.declarative_argparse.Arg(
                "--username",
                help="The username for whom the token will be created. "
                "If no username is provided, the current user's username will be used."
            ),
            aioli.common.declarative_argparse.Arg(
                "--description", help="Description for the deployment token."
            ),
            aioli.common.declarative_argparse.Arg(
                "--expiration",
                help="Expiration date for the token. For example, 2024-06-28T18:41:52-05:00",
            ),
        ]),
        aioli.common.declarative_argparse.Cmd(
            "list ls",
            list_tokens,
            "list the deployment tokens",
            [
                aioli.common.declarative_argparse.Group(
                    aioli.common.declarative_argparse.Arg(
                        "--json", action="store_true",
                        help="Print the tokens in JSON format.",
                    ),
                    aioli.common.declarative_argparse.Arg(
                        "--csv", action="store_true",
                        help="Print the tokens in CSV format.",
                    ),
                ),
                aioli.common.declarative_argparse.Arg(
                    "--all", action="store_true",
                    help="Get all tokens for all users for admin roles and all tokens for current "
                    "user otherwise.",
                ),
            ],
            is_default=True,
        ),
        aioli.common.declarative_argparse.Cmd(
            "show", get_token, "show the details of the deployment token with given ID", [
                aioli.common.declarative_argparse.Arg("id", help="ID of the token"),
                aioli.common.declarative_argparse.Arg(
                    "--json", action="store_true",
                    help="Print the token in JSON format.",
                ),
            ]
        ),
        aioli.common.declarative_argparse.Cmd(
            "update", update_token, "update the description for deployment token with given ID", [
                aioli.common.declarative_argparse.Arg("id", help="ID of the token"),
                aioli.common.declarative_argparse.Arg(
                    "description", help="New description for the deployment token."
                ),
            ]
        ),
        aioli.common.declarative_argparse.Cmd(
            "revoke", revoke_token, "revoke the deployment token with given ID", [
                aioli.common.declarative_argparse.Arg("id", help="ID of the token"),
            ]
        ),
        aioli.common.declarative_argparse.Cmd(
            "delete", delete_token, "delete the deployment token with given ID", [
                aioli.common.declarative_argparse.Arg("id", help="ID of the token"),
            ]
        ),
    ])
]  # type: List[Any]

# fmt: on
