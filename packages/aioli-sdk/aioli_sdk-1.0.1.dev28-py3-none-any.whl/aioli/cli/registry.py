# © Copyright 2023-2024 Hewlett Packard Enterprise Development LP
from argparse import Namespace
from typing import Any, List, Optional

import aiolirest
from aioli import cli
from aioli.cli import render
from aioli.common.api import authentication
from aioli.common.api.errors import NotFoundException
from aioli.common.declarative_argparse import Arg, Cmd, Group
from aiolirest.models.trained_model_registry import TrainedModelRegistry
from aiolirest.models.trained_model_registry_request import TrainedModelRegistryRequest

# Avoid reporting BrokenPipeError when piping `tabulate` output through
# a filter like `head`.
FLUSH = False


@authentication.required
def list_registries(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RegistriesApi(session)
        response = api_instance.registries_get()

    if args.json:
        format_json(response)
    else:
        format_deployment(response, args)


def format_json(response: List[TrainedModelRegistry]) -> None:
    regs = []
    for r in response:
        # Don't use the r.to_json() method as it adds backslash escapes for double quote
        d = r.to_dict()
        d.pop("id")
        d.pop("modifiedAt")
        regs.append(d)

    render.print_json(regs)


def format_deployment(response: List[TrainedModelRegistry], args: Namespace) -> None:
    def format_registry(e: TrainedModelRegistry) -> List[Any]:
        result = [
            e.name,
            e.type,
            e.access_key,
            e.bucket,
            e.secret_key,
            e.endpoint_url,
        ]
        return result

    headers = [
        "Name",
        "Type",
        "Access Key",
        "Bucket",
        "Secret Key",
        "Endpoint URL",
    ]

    values = [format_registry(r) for r in response]
    render.tabulate_or_csv(headers, values, args.csv)


@authentication.required
def create(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RegistriesApi(session)

        r = TrainedModelRegistryRequest(
            name=args.name,
            accessKey=args.access_key,
            bucket=args.bucket,
            endpointUrl=args.endpoint_url,
            secretKey=args.secret_key,
            type=args.type,
            insecureHttps=args.insecure_https,
        )
        api_instance.registries_post(r)


def lookup_registry(name: str, api: aiolirest.RegistriesApi) -> TrainedModelRegistry:
    for r in api.registries_get():
        if r.name == name:
            return r
    raise NotFoundException(f"registry {name} not found")


def lookup_registry_by_id(
    ident: Optional[str], api: aiolirest.RegistriesApi
) -> TrainedModelRegistry:
    for r in api.registries_get():
        if r.id == ident:
            return r
    raise NotFoundException(f"registry with ID {ident} not found")


def lookup_registry_name_by_id(ident: Optional[str], api: aiolirest.RegistriesApi) -> Any:
    if not ident:
        return ""
    r = lookup_registry_by_id(ident, api)
    if r:
        return r.name
    raise NotFoundException(f"registry with ID {ident} not found")


@authentication.required
def show_registry(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RegistriesApi(session)

    registry = lookup_registry(args.name, api_instance)

    d = registry.to_dict()
    if args.json:
        render.print_json(d)
    else:
        print(render.format_object_as_yaml(d))


@authentication.required
def update(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RegistriesApi(session)
        found = lookup_registry(args.registryname, api_instance)
        request = TrainedModelRegistryRequest(
            accessKey=found.access_key,
            bucket=found.bucket,
            endpointUrl=found.endpoint_url,
            name=found.name,
            secretKey=found.secret_key,
            type=found.type,
        )

        if args.name is not None:
            request.name = args.name

        if args.type is not None:
            request.type = args.type

        if args.access_key is not None:
            request.access_key = args.access_key

        if args.bucket is not None:
            request.bucket = args.bucket

        if args.secret_key is not None:
            request.secret_key = args.secret_key

        if args.endpoint_url is not None:
            request.endpoint_url = args.endpoint_url

        headers = {"Content-Type": "application/json"}
        assert found.id is not None
        api_instance.registries_id_put(found.id, request, _headers=headers)


@authentication.required
def delete_registry(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RegistriesApi(session)
        found = lookup_registry(args.name, api_instance)
        assert found.id is not None
        api_instance.registries_id_delete(found.id)


main_cmd = Cmd(
    "registries r|egistry",
    None,
    "manage packaged model registries",
    [
        # Inspection commands.
        Cmd(
            "list ls",
            list_registries,
            "list registries",
            [
                Group(
                    Arg("--csv", action="store_true", help="print as CSV"),
                    Arg("--json", action="store_true", help="print as JSON"),
                )
            ],
            is_default=True,
        ),
        # Create command.
        Cmd(
            "create",
            create,
            "create a registry",
            [
                Arg(
                    "name",
                    help="The name of the model registry. Must begin with a letter, but may "
                    "contain letters, numbers, and hyphen",
                ),
                Arg("--type", help="The type of this model registry", required="true"),
                Arg("--bucket", help="S3 Bucket name"),
                Arg("--access-key", help="S3 access key/username"),
                Arg("--secret-key", help="secret key/password", required="true"),
                Arg("--endpoint-url", help="S3 endpoint URL"),
                Arg(
                    "--insecure-https",
                    help="Allow insecure HTTPS connections to S3",
                    action="store_true",  # prefer argparse.BooleanOptionalAction
                ),
            ],
        ),
        # Show command.
        Cmd(
            "show",
            show_registry,
            "show a registry",
            [
                Arg(
                    "name",
                    help="The name of the registry.",
                ),
                Group(
                    Arg("--yaml", action="store_true", help="print as YAML", default=True),
                    Arg("--json", action="store_true", help="print as JSON"),
                ),
            ],
        ),
        # Update command.
        Cmd(
            "update",
            update,
            "modify a registry",
            [
                Arg("registryname", help="The name of the model registry"),
                Arg(
                    "--name",
                    help="The new name of the model registry. Must begin with a letter, but may "
                    "contain letters, numbers, and hyphen",
                ),
                Arg("--type", help="The type of this model registry"),
                Arg("--bucket", help="S3 Bucket name"),
                Arg("--access-key", help="S3 access key/username"),
                Arg("--secret-key", help="S3 secret key/password"),
                Arg("--endpoint-url", help="S3 endpoint URL"),
                Arg(
                    "--insecure-https",
                    help="Allow insecure HTTPS connections to S3",
                    action="store_true",  # prefer argparse.BooleanOptionalAction
                ),
            ],
        ),
        Cmd(
            "delete",
            delete_registry,
            "delete a registry",
            [
                Arg("name", help="The name of the model registry"),
            ],
        ),
    ],
)

args_description = [main_cmd]  # type: List[Any]
