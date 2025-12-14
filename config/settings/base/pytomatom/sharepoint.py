# -- Modular settings ---------------------------------------------------------
# These settings are imported in the __init__.py of the base directory explicitly.
# To add a new setting, also edit the __init__.py
# -----------------------------------------------------------------------------
from environs import Env


def read_sharepoint_secrets(env: Env) -> dict:
    """
    Read sharepoint access secrets from environment.
    will be read from .env files or the environment provided.
    """
    # pylint: disable=invalid-name
    # pylint: disable=possibly-unused-variable
    SHAREPOINT_TENANT_ID = env.str("SHAREPOINT_TENANT_ID")
    SHAREPOINT_CLIENT_SECRET = env.str("SHAREPOINT_CLIENT_SECRET")
    SHAREPOINT_CLIENT_ID = env.str("SHAREPOINT_CLIENT_ID")

    # ! shall not return the env, we didn't want to modify
    del env
    return locals()


SHAREPOINT_GRAPH_BASE = "https://graph.microsoft.com"
SHAREPOINT_GRAPH_ENDPOINT = f"{SHAREPOINT_GRAPH_BASE}/v1.0"
SHAREPOINT_AUTHORITY_ENDPOINT = "https://login.microsoftonline.com"

SHAREPOINT_HOST_NAME = "saintgobain.sharepoint.com"
SHAREPOINT_TARGET = "PPSPorz"

# SHAREPOINT_MEDIA -> is defined in base.static

SHAREPOINT_PRODUCTION_PLANNER_PORZ_FLOATER_FILENAME = "Produktionsprogramm G035 Float.xlsx"
SHAREPOINT_PRODUCTION_PLANNER_PORZ_COATER_FILENAME = "Produktionsprogramm G035 MAG.xlsx"
SHAREPOINT_PRODUCTION_PLANNER_PORZ_SHEET_NAME = "Planung"

SHAREPOINT_ORDERMANAGEMENT_EXPORT_NAME = "G035 Auftragsbestand"
