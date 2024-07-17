# Copyright 2024 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from __future__ import annotations

from typing import ContextManager

from qctrlcommons.exceptions import QctrlException
from qctrlworkflowclient import (
    ApiRouter,
    LocalRouter,
    get_authenticated_client_for_product,
)
from qctrlworkflowclient.router.api import Action
from rich.console import Console
from rich.table import Table

from boulderopal._configuration.configuration import (
    configure,
    get_configuration,
)
from boulderopal._configuration.constants import (
    BOULDER_OPAL_USER_ROLE,
    INVALID_SUBSCRIPTION_ERROR,
    PACKAGE_INFO,
)
from boulderopal._core.formatter import (
    async_result_formatter,
    metadata_formatter,
)
from boulderopal._validation import (
    Checker,
    ScalarT,
)


def get_cloud_router(on_fail_message: str) -> ApiRouter:
    """
    Return the current cloud router.

    Parameters
    ----------
    on_fail_message : str
        Message to throw when running locally.

    Returns
    -------
    ApiRouter
        The current ApiRouter object.

    Raises
    ------
    QctrlException
        If running in local mode.
    """
    router = get_configuration().get_router()
    if isinstance(router, LocalRouter):
        raise QctrlException(f"{on_fail_message} is not supported in local mode.")
    return router


def get_result(action_id: int | str) -> dict:
    """
    Retrieve the result of a previously run calculation.

    Parameters
    ----------
    action_id : int or str
        The ID associated to the calculation.
        You can get the ID of your calculations from the activity monitor.

    Returns
    -------
    dict
        A dictionary containing the calculation result.
    """
    Checker.TYPE(
        str(action_id).isnumeric(),
        "The calculation id must be an integer.",
        {"action_id": action_id},
    )
    action = Action(action_id=str(action_id))
    return metadata_formatter(
        get_cloud_router("Retrieving results").get_result(action)
    ).decoded


def request_machines(machine_count: int) -> None:
    """
    Request a minimum number of machines to be online.

    Parameters
    ----------
    machine_count : int
        The minimum number of machines requested to be online.

    Notes
    -----
    This command is blocking until the specified amount of machines
    have been observed in your environment. It only attempts to ensure
    the requested amount are online, not necessarily starting up that
    amount if some machines are already online.
    """
    machine_count = ScalarT.INT("machine_count").ge(1)(machine_count)
    get_cloud_router("Requesting machines").request_machines(machine_count)


def group_requests() -> ContextManager:
    """
    Create a context manager for executing multiple function calls over available machines.

    Returns
    -------
    ContextManager
        A context manager to collect and run computation requests.

    Notes
    -----
    All grouped calculations must be independent from each other.

    Within the context manager, the object returned from each request is a placeholder.
    When exiting, the context manager waits until all calculations have finished,
    hence this command blocks execution.
    When all results are received, the placeholders are replaced with them.

    Read the `Computational resources in Boulder Opal
    <https://docs.q-ctrl.com/boulder-opal/topics/computational-resources-in-boulder-opal>`_
    topic for more information about this feature.
    """
    return get_cloud_router("Grouping requests").enable_parallel(
        callback=async_result_formatter
    )


def set_organization(organization_slug: str) -> None:
    """
    Set the organization for Boulder Opal cloud calls.

    Parameters
    ----------
    organization_slug : str
        Unique slug for the organization.
    """
    configure(organization=organization_slug)


def set_api(api_url: str, oidc_url: str) -> None:
    """
    Configure Boulder Opal for API routing.

    Parameters
    ----------
    api_url : str
        URL of the GraphQL schema.
    oidc_url : str
        Base URL of the OIDC provider, e.g. Keycloak.
    """
    client = get_authenticated_client_for_product(
        product_access_required=BOULDER_OPAL_USER_ROLE,
        package_name=PACKAGE_INFO.install_name,
        api_url=api_url,
        auth=oidc_url,
        invalid_access_error_message=INVALID_SUBSCRIPTION_ERROR,
    )
    settings = get_configuration()

    configure(router=ApiRouter(client, settings))


def show_machine_status() -> None:
    """
    Print the current machine status in Boulder Opal cloud environment for your organization.
    """

    status_map = {
        "Online": "online",
        "Starting up": "initializing",
        "Pending": "pending",
        "Shutting down": "terminating",
        "Offline": "offline",
    }

    status = get_cloud_router("Machine status").get_machine_status()

    table = Table(title="Machine status", show_lines=True)
    console = Console()

    for header in ["Status", "Count"]:
        table.add_column(header, justify="center")

    for state, key in status_map.items():
        number = status.get(key)
        if number is None:
            raise RuntimeError(
                f"Unknown machine state. Expected {list(status.keys())}, got {key}."
            )
        table.add_row(state, str(number))

    console.print(table)
