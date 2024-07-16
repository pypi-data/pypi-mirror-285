# © Copyright 2023-2024 Hewlett Packard Enterprise Development LP
from argparse import Namespace
from typing import Any, List

import aiolirest
from aioli import cli
from aioli.cli import errors, render
from aioli.common import api
from aioli.common.api import authentication
from aioli.common.api.errors import NotFoundException
from aioli.common.declarative_argparse import Arg, ArgsDescription, Cmd, Group
from aioli.common.util import (
    construct_arguments,
    construct_environment,
    launch_dashboard,
)
from aiolirest.models.autoscaling import Autoscaling
from aiolirest.models.deployment import Deployment, DeploymentState
from aiolirest.models.deployment_request import DeploymentRequest
from aiolirest.models.event_info import EventInfo
from aiolirest.models.security import Security


@authentication.required
def dashboard(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.DeploymentsApi(session)

    deployment: Deployment = lookup_deployment(args.name, api_instance)

    observability = api_instance.deployments_id_observability_get(deployment.id)
    launch_dashboard(args, observability.dashboard_url)


@authentication.required
def show_deployment(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.DeploymentsApi(session)

    deployment: Deployment = lookup_deployment(args.name, api_instance)

    # For a more useful display, replace the model ID with its name
    packaged_models_api = aiolirest.PackagedModelsApi(session)
    deployment.model = packaged_models_api.models_id_get(deployment.model).name

    d = deployment.to_dict()
    # Remove clusterName for now - INF-243
    d.pop("clusterName")

    # Get the model version for the deployment
    deployment_model_versions = packaged_models_api.models_versions_get(deployment.model)
    for r in deployment_model_versions:
        if r.deployment_id == d["id"]:
            d["version"] = r.mdl_version
    if args.json:
        render.print_json(d)
    else:
        print(render.format_object_as_yaml(d))


@authentication.required
def list_deployments(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.DeploymentsApi(session)
        response = api_instance.deployments_get()
    model_api = aiolirest.PackagedModelsApi(session)

    if args.json:
        format_json(response, model_api)
    else:
        format_deployments(response, args, model_api)


def format_json(response: List[Deployment], model_api: aiolirest.PackagedModelsApi) -> None:
    deps = []
    for d in response:
        # Don't use the d.to_json() method as it adds backslash escapes for double quote
        m_dict = d.to_dict()
        m_dict.pop("modifiedAt")
        # Use model name instead of id
        model = model_api.models_id_get(d.model)
        deployment_model_versions = model_api.models_versions_get(model.name)
        for r in deployment_model_versions:
            if r.deployment_id == m_dict["id"]:
                m_dict["version"] = r.mdl_version
        m_dict.pop("id")
        m_dict["model"] = model.name
        m_dict.pop("clusterName", None)
        deps.append(m_dict)
    render.print_json(deps)


def format_deployments(
    response: List[Deployment],
    args: Namespace,
    packaged_models_api: aiolirest.PackagedModelsApi,
) -> None:
    def format_deployment(e: Deployment, models_api: aiolirest.PackagedModelsApi) -> List[Any]:
        model = models_api.models_id_get(e.model)
        state = e.state
        total_failures = 0

        if state is None:
            state = DeploymentState()
        else:
            failure_info = state.failure_info
            if failure_info:
                total_failures = len(failure_info)

        secondary_state = e.secondary_state
        if secondary_state is None:
            secondary_state = DeploymentState()

        assert e.security is not None

        auto_scaling = e.auto_scaling
        if auto_scaling is None:
            auto_scaling = Autoscaling()

        if total_failures > 1:
            e.status = f"{e.status}\n({total_failures} errors)"
        elif total_failures == 1:
            e.status = f"{e.status}\n({total_failures} error)"

        deployment_model_versions = models_api.models_versions_get(model.name)
        version = next(r.mdl_version for r in deployment_model_versions if r.deployment_id == e.id)
        result = [
            e.name,
            model.name,
            version,
            e.namespace,
            e.status,
            e.security.authentication_required,
            state.status,
            state.traffic_percentage,
        ]

        return result

    headers = [
        "Name",
        "Model",
        "Version",
        "Namespace",
        "Status",
        "Auth Required",
        "State",
        "Traffic %",
    ]

    values = [format_deployment(r, packaged_models_api) for r in response]
    render.tabulate_or_csv(headers, values, args.csv)


@authentication.required
def create(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.DeploymentsApi(session)

        sec = Security(authenticationRequired=False)
        if args.authentication_required is not None:
            val = args.authentication_required.lower() == "true"
            sec.authentication_required = val

        auto = Autoscaling(
            metric=args.autoscaling_metric,
        )

        if args.autoscaling_target is not None:
            auto.target = args.autoscaling_target

        if args.autoscaling_max_replicas is not None:
            auto.max_replicas = args.autoscaling_max_replicas

        if args.autoscaling_min_replicas is not None:
            auto.min_replicas = args.autoscaling_min_replicas

        r = DeploymentRequest(
            name=args.name,
            model=args.model,
            security=sec,
            namespace=args.namespace,
            autoScaling=auto,
            canaryTrafficPercent=args.canary_traffic_percent,
            environment=construct_environment(args),
            arguments=construct_arguments(args),
        )
        api_instance.deployments_post(r)


def lookup_deployment(name: str, api: aiolirest.DeploymentsApi) -> Deployment:
    for r in api.deployments_get():
        if r.name == name:
            return r
    raise NotFoundException(f"deployment {name} not found")


@authentication.required
def update(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.DeploymentsApi(session)
        found = lookup_deployment(args.deploymentname, api_instance)
        request = DeploymentRequest(
            name=found.name,
            namespace=found.namespace,
            security=found.security,
            model=found.model,
            autoScaling=found.auto_scaling,
            canaryTrafficPercent=found.canary_traffic_percent,
            goalStatus=found.goal_status,
        )

        if request.auto_scaling is None:
            # Not likely, but testing these prevents complaints from mypy
            raise api.errors.BadResponseException("Unexpected null result")

        if args.pause and args.resume:
            raise errors.CliError("--pause and --resume cannot be specified at the same time")

        if args.pause:
            request.goal_status = "Paused"

        if args.resume:
            request.goal_status = "Ready"

        if args.name is not None:
            request.name = args.name

        if args.model is not None:
            request.model = args.model

        if args.namespace is not None:
            request.namespace = args.namespace

        if args.autoscaling_min_replicas is not None:
            request.auto_scaling.min_replicas = args.autoscaling_min_replicas

        if args.autoscaling_max_replicas is not None:
            request.auto_scaling.max_replicas = args.autoscaling_max_replicas

        if args.autoscaling_metric is not None:
            request.auto_scaling.metric = args.autoscaling_metric

        if args.autoscaling_target is not None:
            request.auto_scaling.target = args.autoscaling_target

        if args.canary_traffic_percent is not None:
            request.canary_traffic_percent = args.canary_traffic_percent

        assert request.security is not None

        if args.authentication_required is not None:
            val = args.authentication_required.lower() == "true"
            request.security.authentication_required = val

        if args.env is not None:
            request.environment = construct_environment(args)

        if args.arg is not None:
            request.arguments = construct_arguments(args)

        headers = {"Content-Type": "application/json"}
        assert found.id is not None
        api_instance.deployments_id_put(found.id, request, _headers=headers)


@authentication.required
def delete_deployment(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.DeploymentsApi(session)
        found = lookup_deployment(args.name, api_instance)
        assert found.id is not None
        api_instance.deployments_id_delete(found.id)


@authentication.required
def get_deployment_events(args: Namespace) -> None:
    def format_events(event: EventInfo) -> List[Any]:
        result = [
            event.reason,
            event.message,
            event.time,
            event.event_type,
        ]
        return result

    with cli.setup_session(args) as session:
        api_instance = aiolirest.DeploymentsApi(session)
        found = lookup_deployment(args.name, api_instance)
        assert found.id is not None
        events = api_instance.deployments_id_events_get(found.id)
        headers = [
            "Reason",
            "Message",
            "Time",
            "Event Type",
        ]
        values = [format_events(r) for r in events]
        render.tabulate_or_csv(headers, values, args.csv)


common_deployment_args: ArgsDescription = [
    Arg(
        "--authentication-required",
        help="Deployed model requires callers to provide authentication",
    ),
    Arg("--namespace", help="The Kubernetes namespace to be used for the deployment"),
    Arg("--autoscaling-min-replicas", help="Minimum number of replicas", type=int),
    Arg(
        "--autoscaling-max-replicas",
        help="Maximum number of replicas created based upon demand",
        type=int,
    ),
    Arg("--autoscaling-metric", help="Metric name which controls autoscaling"),
    Arg("--autoscaling-target", help="Metric target value", type=int),
    Arg(
        "--canary-traffic-percent",
        help="Percent traffic to pass to new model version",
        type=int,
    ),
    Arg(
        "-a",
        "--arg",
        help="Argument to be added to the service command line. "
        "If specifying an argument that starts with a '-', use the form --arg=<your-argument>",
        action="append",
    ),
    Arg(
        "-e",
        "--env",
        help="Specifies an environment variable & value as name=value, "
        "to be passed to the launched container",
        action="append",
    ),
]

main_cmd = Cmd(
    "d|eployment|s",
    None,
    "manage trained deployments",
    [
        # Inspection commands.
        Cmd(
            "list ls",
            list_deployments,
            "list deployments",
            [
                Arg("--csv", action="store_true", help="print as CSV"),
                Arg("--json", action="store_true", help="print as JSON"),
            ],
            is_default=True,
        ),
        # Create command.
        Cmd(
            "create",
            create,
            "create a deployment",
            [
                Arg(
                    "name",
                    help="The name of the deployment. Must begin with a letter, but may contain "
                    "letters, numbers, and hyphen",
                ),
                Arg(
                    "--model",
                    help=(
                        "The package model id, name or versioned-name (evaluated in that "
                        "order) to be deployed"
                    ),
                    required="true",
                ),
            ]
            + common_deployment_args,
        ),
        # dashboard command.
        Cmd(
            "dashboard",
            dashboard,
            "launch the deployment dashboard",
            [
                Arg(
                    "name",
                    help="The name of the deployment.",
                ),
            ],
        ),
        # Show command.
        Cmd(
            "show",
            show_deployment,
            "show a deployment",
            [
                Arg(
                    "name",
                    help="The name of the deployment.",
                ),
                Group(
                    Arg("--yaml", action="store_true", help="print as YAML", default=True),
                    Arg("--json", action="store_true", help="print as JSON"),
                ),
            ],
        ),
        # Update command
        Cmd(
            "update",
            update,
            "modify a deployment",
            [
                Arg("deploymentname", help="The name of the deployment"),
                Arg(
                    "--name",
                    help="The new name of the deployment. Must begin with a letter, but may "
                    "contain letters, numbers, and hyphen",
                ),
                Arg(
                    "--model",
                    help=(
                        "The package model id, name or versioned-name (evaluated in that "
                        "order) to be deployed"
                    ),
                ),
                Arg("--pause", action="store_true", help="Pause the deployment"),
                Arg("--resume", action="store_true", help="Resume the deployment"),
            ]
            + common_deployment_args,
        ),
        Cmd(
            "delete",
            delete_deployment,
            "delete a deployment",
            [
                Arg("name", help="The name of the deployment"),
            ],
        ),
        Cmd(
            "event|s",
            get_deployment_events,
            "get deployment events",
            [
                Arg("name", help="The name of the deployment"),
                Arg("--csv", action="store_true", help="print as CSV"),
            ],
        ),
    ],
)

args_description = [main_cmd]  # type: List[Any]
