"""The Apps sub-package exposes the core integrations of the deployed apps in AdaLab."""

from .apps import (
    delete_app,
    deploy_app,
    edit_app,
    get_all_apps,
    get_app,
    get_app_id,
    get_app_logs,
    get_apps_by_author,
    get_apps_status,
    restart_app,
    start_app,
    stop_app,
)

__all__ = [
    "delete_app",
    "deploy_app",
    "edit_app",
    "get_all_apps",
    "get_app",
    "get_app_id",
    "get_app_logs",
    "get_apps_by_author",
    "get_apps_status",
    "restart_app",
    "start_app",
    "stop_app",
]
__title__ = "adalib Apps"
