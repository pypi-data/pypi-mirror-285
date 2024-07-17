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

import os
from typing import Any

from qctrlclient import ApiKeyAuth
from qctrlclient.defaults import (
    get_default_api_url,
    get_default_cli_auth,
)
from qctrlclient.exceptions import GraphQLQueryError
from qctrlclient.globals import (
    global_value,
    update_global_value,
)
from qctrlworkflowclient import (
    ApiRouter,
    CoreClientSettings,
    LocalRouter,
    Product,
    get_authenticated_client_for_product,
)

from boulderopal._configuration.constants import (
    API_KEY_NAME,
    BOULDER_OPAL_CONFIGURATION_NAME,
    BOULDER_OPAL_USER_ROLE,
    INVALID_SUBSCRIPTION_ERROR,
    PACKAGE_INFO,
)
from boulderopal._configuration.verbosity import MESSAGE_PRINTER


def get_default_router() -> ApiRouter:
    """
    Return the default router that the Boulder Opal client uses.
    """
    api_key = os.getenv(API_KEY_NAME)
    if api_key is not None:
        auth = get_default_api_key_auth(api_key)
    else:
        auth = get_default_cli_auth()

    client = get_authenticated_client_for_product(
        product_access_required=BOULDER_OPAL_USER_ROLE,
        package_name=PACKAGE_INFO.install_name,
        api_url=get_default_api_url(),
        auth=auth,
        invalid_access_error_message=INVALID_SUBSCRIPTION_ERROR,
    )
    settings = get_configuration()

    return ApiRouter(client, settings)


def get_default_api_key_auth(api_key: str) -> ApiKeyAuth:
    """
    Return a token-based authentication handler
    pointed to the default API URL.
    """
    auth = ApiKeyAuth(get_default_api_url(), api_key)

    # Check the API key.
    # Fetching user roles requires exchanging the API key for an access token.
    # We can thus infer that the API key is invalid if roles cannot be fetched.
    try:
        auth.user_roles()
    except GraphQLQueryError as error:
        raise RuntimeError(
            f"Invalid API key ({api_key}). Please check your key "
            "or visit https://accounts.q-ctrl.com to generate a new one."
        ) from error

    return auth


@global_value(BOULDER_OPAL_CONFIGURATION_NAME)
def get_configuration() -> CoreClientSettings:
    """
    Return the global Boulder Opal settings.
    """
    return CoreClientSettings(
        router=get_default_router,
        product=Product.BOULDER_OPAL,
        event_listeners=[MESSAGE_PRINTER],
    )


def configure(**kwargs: Any) -> None:
    """
    Update the global Boulder Opal settings. See :class:`CoreClientSettings`
    for details on which fields can be updated.
    """
    configuration = get_configuration()
    configuration.update(**kwargs)
    update_global_value(BOULDER_OPAL_CONFIGURATION_NAME, configuration)


def set_local(resolver: "BaseResolver") -> None:  # type: ignore
    """
    Configure Boulder Opal for local routing.

    Parameters
    ----------
    resolver : BaseResolver
        A local implementation of a workflow resolver which uses
        a registry that implements all of the available Boulder Opal
        workflows.
    """
    configure(router=LocalRouter(resolver))


def in_local_mode() -> bool:
    """
    Check if client is in local mode.
    """
    return isinstance(get_configuration().get_router(), LocalRouter)


def is_async(result: Any) -> bool:
    """
    Check if we get async result back from the server.
    """
    return isinstance(result, dict) and result.get("async_result") is not None


def set_local_mode() -> None:
    """
    Set the Boulder Opal client to operate in local mode.

    Local mode requires a Boulder Opal Core installation.
    """
    try:
        is_boulder_dev = os.environ.get("BOULDER_OPAL_LOCAL_DEV", "0") != "0"

        # Disable debug log from TensorFlow at CPP level by default.
        # Note that this needs to be done before TensorFlow is imported.
        if not is_boulder_dev:
            os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

        import tensorflow as tf  # pylint: disable=import-outside-toplevel

        # Disable WARNING/INFO from TensorFlow at Python level by default.
        if not is_boulder_dev:
            tf.get_logger().setLevel("ERROR")

        from boulderopalcore.api import (  # pylint: disable=import-outside-toplevel
            SynchronousResolver,
            get_boulder_core_api,
        )

    except ImportError as exc:
        raise ImportError(
            "Cannot find a Boulder Opal Core installation. "
            "Contact us at https://q-ctrl.com/contact if you need assistance."
        ) from exc

    set_local(SynchronousResolver(get_boulder_core_api()))


def set_cloud_mode() -> None:
    """
    Set the Boulder Opal client to operate in cloud mode.
    """
    configure(router=get_default_router())
