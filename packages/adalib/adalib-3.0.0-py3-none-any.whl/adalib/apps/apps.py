import requests

from .. import adaboard
from ..utils import validate_acl

PRIVILEGED_ROLES = ["Curator", "PlatformAdmin"]


def delete_app(app_id: str) -> None:
    """
    Delete a deployed app from AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/delete_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    """

    adaboard.request_adaboard(path=f"apps/{app_id}/", method=requests.delete)
    return None


def deploy_app(
    name: str,
    description: str,
    metadata_id: int,
    url_path_prefix: str,
    stripped_prefix: bool = True,
    port: int = 80,
    replicas: int = 1,
    environment_variables: dict = {},
    max_cpu: float = 1.0,
    min_cpu: float = 0.0,
    max_ram: int = 500,
    min_ram: int = 20,
    command: str = "",
    acl_type: str = "public",
    acl_userlist: list[str] = [],
    acl_group_names: list[str] = [],
    idp_enabled: bool = False,
    idp_scope: str = "",
) -> str:
    """
    Deploy an app to AdaLab from an existing metadata object.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/deploy_app.ipynb) to test this function or build upon it.

    :param name: the app's name
    :type name: str
    :param description: the app's description
    :type description: str
    :param metadata_id: the ID of the metadata object
    :type metadata_id: int
    :param url_path_prefix: URL endpoint to deploy the app to
    :type url_path_prefix: str
    :param stripped_prefix: whether to strip the apps/{app_url} prefix from the URL, defaults to True
    :type stripped_prefix: bool, optional
    :param port: the port where the app is served from, defaults to 80
    :type port: int, optional
    :param replicas: number of replicas to deploy, defaults to 1
    :type replicas: int, optional
    :param environment_variables: environment variables to pass to the app, defaults to {}
    :type environment_variables: dict, optional
    :param max_cpu: maximum CPU usage allowed (vCPU), defaults to 1.0
    :type max_cpu: float, optional
    :param min_cpu: minimum CPU usage allowed (vCPU), defaults to 0.0
    :type min_cpu: float, optional
    :param max_ram: maximum RAM usage allowed (Mb), defaults to 500
    :type max_ram: int, optional
    :param min_ram: minimum RAM usage allowed (Mb), defaults to 20
    :type min_ram: int, optional
    :param command: command to start up the app, defaults to ""
    :type command: str, optional
    :param acl_type: type of access control list, defaults to "public"
    :type acl_type: str, optional
    :param acl_userlist: list of users allowed to access the app when acl_type="userlist", defaults to []
    :type acl_userlist: list, optional
    :param acl_group_names: list of groups allowed to access the app when acl_type="group", defaults to []
    :type acl_group_names: list, optional
    :param idp_enabled: whether to enable IdP token in app headers, defaults to False
    :type idp_enabled: bool, optional
    :param idp_scope: IdP token scope, defaults to ""
    :type idp_scope: str, optional
    :return: the app's ID
    :rtype: str
    """

    # Build the payload for the request
    payload = {
        "name": name,
        "description": description,
        "metadata_id": metadata_id,
        "url_path_prefix": url_path_prefix,
        "stripped_prefix": stripped_prefix,
        "port": port,
        "replicas": replicas,
        "environment_variables": environment_variables,
        "max_cpu": max_cpu,
        "min_cpu": min_cpu,
        "max_ram": max_ram,
        "min_ram": min_ram,
        "command": command,
        "acl_type": acl_type,
        "acl_userlist": acl_userlist,
        "acl_group_names": acl_group_names,
        "idp_enabled": idp_enabled,
        "idp_scope": idp_scope,
    }

    # Check that the app configuration is valid and update payload
    validate_acl("app", False, acl_type)
    if acl_type == "public":
        payload.pop("acl_userlist")
        payload.pop("acl_group_names")
    elif acl_type == "userlist":
        assert (
            isinstance(acl_userlist, list) and len(acl_userlist) > 0
        ), "ACL type is userlist but no users were specified."
        payload.pop("acl_group_names")
    elif acl_type == "group":
        assert (
            isinstance(acl_group_names, list) and len(acl_group_names) > 0
        ), "ACL type is group but no groups were specified."
        payload.pop("acl_userlist")

    # Deploy the app
    response = adaboard.request_adaboard(
        path="apps/", method=requests.post, json=payload
    ).json()

    # Return the ID of the deployed app
    return response["id"]


def edit_app(
    app_id: str,
    name: str = None,
    description: str = None,
    metadata_id: int = None,
    url_path_prefix: str = None,
    stripped_prefix: bool = None,
    port: int = None,
    replicas: int = None,
    environment_variables: dict = None,
    max_cpu: float = None,
    min_cpu: float = None,
    max_ram: int = None,
    min_ram: int = None,
    command: str = None,
    acl_type: str = None,
    acl_userlist: list[str] = None,
    acl_group_names: list[str] = None,
    idp_enabled: bool = None,
    idp_scope: str = None,
) -> None:
    """
    Edit a deployed app's configuration.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/edit_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :param name: the app's name, defaults to None (old one)
    :type name: str, optional
    :param description: the app's description, defaults to None (old one)
    :type description: str, optional
    :param metadata_id: the ID of the metadata object, defaults to None (old one)
    :type metadata_id: int, optional
    :param url_path_prefix: URL endpoint to deploy the app to, defaults to None (old one)
    :type url_path_prefix: str, optional
    :param stripped_prefix: whether to strip the apps/{app_url} prefix from the URL, defaults to None (old one)
    :type stripped_prefix: bool, optional
    :param port: the port where the app is served from, defaults to None (old one)
    :type port: int, optional
    :param replicas: number of replicas to deploy, defaults to None (old one)
    :type replicas: int, optional
    :param environment_variables: environment variables to pass to the app, defaults to None (old one)
    :type environment_variables: dict, optional
    :param max_cpu: maximum CPU usage allowed (vCPU), defaults to None (old one)
    :type max_cpu: float, optional
    :param min_cpu: minimum CPU usage allowed (vCPU), defaults to None (old one)
    :type min_cpu: float, optional
    :param max_ram: maximum RAM usage allowed (Mb), defaults to None (old one)
    :type max_ram: int, optional
    :param min_ram: minimum RAM usage allowed (Mb), defaults to None (old one)
    :type min_ram: int, optional
    :param command: command to start up the app, defaults to None (old one)
    :type command: str, optional
    :param acl_type: type of access control list, defaults to None (old one)
    :type acl_type: str, optional
    :param acl_userlist: list of users allowed to access the app when acl_type="userlist", defaults to None (old one)
    :type acl_userlist: list, optional
    :param acl_group_names: list of groups allowed to access the app when acl_type="group", defaults to None (old one)
    :type acl_group_names: list, optional
    :param idp_enabled: whether to enable IdP token in app headers, defaults to None (old one)
    :type idp_enabled: bool, optional
    :param idp_scope: IdP token scope, defaults to None (old one)
    :type idp_scope: str, optional
    :return: nothing
    :rtype: None
    """

    # Collect configuration options
    app_config = {
        "name": name,
        "description": description,
        "metadata_id": metadata_id,
        "url_path_prefix": url_path_prefix,
        "stripped_prefix": stripped_prefix,
        "port": port,
        "replicas": replicas,
        "environment_variables": environment_variables,
        "max_cpu": max_cpu,
        "min_cpu": min_cpu,
        "max_ram": max_ram,
        "min_ram": min_ram,
        "command": command,
        "acl_type": acl_type,
        "acl_userlist": acl_userlist,
        "acl_group_names": acl_group_names,
        "idp_enabled": idp_enabled,
        "idp_scope": idp_scope,
    }

    # Check that the app configuration is valid and update payload
    if acl_type:
        validate_acl("app", True, acl_type)
        if acl_type == "public":
            app_config.pop("acl_userlist")
            app_config.pop("acl_group_names")
        elif acl_type == "userlist":
            assert (
                isinstance(acl_userlist, list) and len(acl_userlist) > 0
            ), "ACL type is userlist but no users were specified."
            app_config.pop("acl_group_names")
        elif acl_type == "group":
            assert (
                isinstance(acl_group_names, list) and len(acl_group_names) > 0
            ), "ACL type is group but no groups were specified."
            app_config.pop("acl_userlist")

    # Fetch old configuration
    old_config = adaboard.request_adaboard(
        path=f"apps/{app_id}/", method=requests.get
    ).json()

    # Build request payload combining new and old options
    payload = {
        k: v if v is not None else old_config[k] for k, v in app_config.items()
    }

    adaboard.request_adaboard(
        path=f"apps/{app_id}/", method=requests.put, json=payload
    )

    return None


def get_all_apps() -> (
    list[dict[str, str | int | bool | dict[str, str] | list[str]]]
):
    """
    Get information for all the apps deployed in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_all_apps.ipynb) to test this function or build upon it.

    :return: list with all the information of each app
    :rtype: list
    """

    # If the user is privileged enough, get all apps
    response_roles = adaboard.request_adaboard(path="users/self").json()
    include_all = any(
        role in PRIVILEGED_ROLES
        for role in response_roles["roles"]["adaboard"]
    )
    # Get the list of all apps
    response = adaboard.request_adaboard(
        path=f"apps/?all={include_all}", method=requests.get
    ).json()

    return response


def get_app(
    app_id: str,
) -> dict[str, str | int | bool | dict[str, str] | list[str]]:
    """
    Get the information of a specific deployed app in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :return: app's information
    :rtype: dict
    """

    response = adaboard.request_adaboard(
        path=f"apps/{app_id}/", method=requests.get
    ).json()

    return response


def get_app_id(
    app_name: str = "", author_id: str = "", app_url: str = ""
) -> str:
    """
    Get the ID of a deployed app in AdaLab. Either app_url, or app_name and author_id, must be specified.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_app_id.ipynb) to test this function or build upon it.

    :param app_name: name of the app, defaults to ""
    :type app_name: str, optional
    :param author_id: author of the app, defaults to ""
    :type author_id: str, optional
    :param app_url: endpoint of the app's URL, defaults to ""
    :type app_url: str, optional
    :return: the app's ID
    :rtype: str
    """

    # Check that enough information is provided to find the app
    assert (
        app_name and author_id
    ) or app_url, (
        "Either app_url, or app_name and author_id, must be specified."
    )
    # If the user is privileged enough, get all apps
    response_roles = adaboard.request_adaboard(path="users/self").json()
    include_all = any(
        role in PRIVILEGED_ROLES
        for role in response_roles["roles"]["adaboard"]
    )
    # Get the list of all apps
    response = adaboard.request_adaboard(
        path=f"apps/?all={include_all}", method=requests.get
    ).json()

    # Return the ID of the requested app
    try:
        if app_url:
            return [
                app["app_id"]
                for app in response
                if app["url_path_prefix"] == app_url
            ][0]
        else:
            return [
                app["app_id"]
                for app in response
                if app["name"] == app_name and app["user_id"] == author_id
            ][0]
    except IndexError:
        raise ValueError("No app found with the specified parameters.")


def get_app_logs(
    app_id: str, system: bool = False
) -> str | list[dict[str, str]]:
    """
    Get the execution or deployment logs of a deployed app in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_app_logs.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :param system: whether to get the system logs or the deployment logs, defaults to False
    :type system: bool, optional
    :return: deployment logs
    :rtype: str
    """

    response = adaboard.request_adaboard(
        path=f"apps/{app_id}/logs/?system={system}", method=requests.get
    ).json()

    if system:
        return response
    else:
        return response["log"]


def get_apps_by_author(
    author_id: str,
) -> list[dict[str, str | int | bool | dict[str, str] | list[str]]]:
    """
    Get information for all the apps deployed in AdaLab by a specific author.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_apps_by_author.ipynb) to test this function or build upon it.

    :param author_id: the ID of the app's author
    :type author_id: str
    :return: list with all the information of each app
    :rtype: list
    """

    # If the user is privileged enough, get all apps
    response_roles = adaboard.request_adaboard(path="users/self").json()
    include_all = any(
        role in PRIVILEGED_ROLES
        for role in response_roles["roles"]["adaboard"]
    )
    # Get the list of all apps
    response = adaboard.request_adaboard(
        path=f"apps/?all={include_all}", method=requests.get
    ).json()

    return [app for app in response if app["user_id"] == author_id]


def get_apps_status() -> dict[str, str]:
    """
    Get the status of all the apps deployed in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_apps_status.ipynb) to test this function or build upon it.

    :return: dictionary with the status of each app
    :rtype: dict
    """

    # Get status report for all apps
    response_stats = adaboard.request_adaboard(
        path="apps/status/", method=requests.get
    ).json()

    # If the user is privileged enough, get all apps
    response_roles = adaboard.request_adaboard(path="users/self").json()
    include_all = any(
        role in PRIVILEGED_ROLES
        for role in response_roles["roles"]["adaboard"]
    )
    # Get the list of all apps
    response_apps = adaboard.request_adaboard(
        path=f"apps/?all={include_all}", method=requests.get
    ).json()

    # Build dictionary with the status of each app
    apps_status = [
        {
            "name": app["name"],
            "author": app["user_id"],
            "URL": app["url_path_prefix"],
            "status": response_stats[str(app["status"])],
        }
        for app in response_apps
    ]
    return apps_status


def restart_app(app_id: str) -> None:
    """
    Restart a deployed app in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/restart_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :return: nothing
    :rtype: None
    """

    adaboard.request_adaboard(
        path=f"apps/{app_id}/restart/", method=requests.put
    )
    return None


def start_app(app_id: str) -> None:
    """
    Start a deployed app in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/start_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :return: nothing
    :rtype: None
    """

    adaboard.request_adaboard(
        path=f"apps/{app_id}/start/", method=requests.put
    )

    return None


def stop_app(app_id: str) -> None:
    """
    Stop a deployed app in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/stop_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :return: nothing
    :rtype: None
    """

    adaboard.request_adaboard(path=f"apps/{app_id}/stop/", method=requests.put)
    return None
