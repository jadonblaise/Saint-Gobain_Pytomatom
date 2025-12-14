import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import httpx
import numpy as np
from msal import ConfidentialClientApplication

from django.conf import settings
from django.db import transaction
from django.utils import timezone

import apps.ordermanagement.views as ordermanagement_views
from apps.ordermanagement.models import OrderBookEntry
from apps.resources import read
from core.cypher import security
from core.inout import files

from .exceptions import DownloadException
from .models import (
    CoaterProductionPlanner,
    FloaterProductionPlanner,
    SharepointFile,
)


log = logging.getLogger("django.sharepoint")


class PorzProductionPlanners(NamedTuple):
    floater: FloaterProductionPlanner | None
    coater: CoaterProductionPlanner | None


@dataclass
class Sharepoint:
    """
    Sharepoint information. Holds objects for site, drive and files returned by
    the graph api get-info requests.
    """

    site: dict = field(default_factory=dict)
    drive: dict = field(default_factory=dict)
    files: list = field(default_factory=list)

    @property
    def site_id(self) -> str:
        """
        for instance:
        saintgobain.sharepoint.com,edcdc2bb-bdd3-4872-9d74-189a6f275301,f03f506d-25f9-4a84-a3e1-fe04018ca2df
        """
        return self.site["id"]

    @property
    def drive_id(self) -> str:
        return self.drive["id"]

    def search(self, name: str) -> dict | None:
        """
        Filter files by a matching name.
        """
        matches = [f for f in self.files if f["name"] == name]
        if len(matches) > 1:
            raise ValueError(f"Multiple files with the name '{name}' found.")
        try:
            file = matches[0]
            return file
        except IndexError:
            return None


def _get_authorized_app():
    """
    The "app" (misleading caled 'the service principal by some sg-teams'
    a confidential client application using the 'client secret' method.
    """
    tenant_id = settings.SHAREPOINT_TENANT_ID
    client_secret = settings.SHAREPOINT_CLIENT_SECRET
    client_id = settings.SHAREPOINT_CLIENT_ID
    authority = f"{settings.SHAREPOINT_AUTHORITY_ENDPOINT}/{tenant_id}"
    return ConfidentialClientApplication(client_id=client_id, authority=authority, client_credential=client_secret)


def _request_auth_headers() -> dict:
    """
    Request an access token from the app and return it as a headers-dict
    directly usable by the httpx.Client.
    """
    app = _get_authorized_app()
    r: dict = app.acquire_token_for_client(scopes=[f"{settings.SHAREPOINT_GRAPH_BASE}/.default"])  # type: ignore
    token: str | None = r.get("access_token")
    token_type: str | None = r.get("token_type")
    assert token is not None, "No access token available."
    assert token_type is not None, "Token type invalid."
    headers = {"Authorization": f"{token_type} {token}"}
    return headers


def gather_sharepoint_information(client):
    """
    Gather all available information about the sharepoint site, drive and files.
    """
    sharepoint = Sharepoint()
    sharepoint.site = get_site(client=client)
    drives = get_drives(client=client, sharepoint=sharepoint)
    sharepoint.drive = get_named_drive(drives=drives, drive_name="Documents")
    sharepoint.files = get_all_files(client=client, sharepoint=sharepoint)
    return sharepoint


def download_files_from_sharepoint(filenames: list[str]) -> dict[str, SharepointFile]:
    """
    download named files from sharepoint.
    - return dict with filename as key and SharepointFile object as value (e.g. to get path to storage)
    """
    downloaded = {}
    headers = _request_auth_headers()
    with httpx.Client() as client:
        client.headers.update(headers)
        sharepoint = gather_sharepoint_information(client=client)
        for filename in filenames:
            file = sharepoint.search(name=filename)
            if file is None:
                log.error(f"File '{filename=}' not found on sharepoint.")
                continue
            downloaded[filename] = download_file(client=client, sharepoint=sharepoint, file=file)
    return downloaded


def from_excel(path: Path, sheet_name: str) -> list[dict]:
    """
    - load excel
    - return each row as JsON entry
    - first row in Excel defines attribute names for JSON entries
    """
    df = read.as_df(path=path, sheet_name=sheet_name)
    return serialize(df.to_dict(orient="records"))


def serialize(records: list[dict]) -> list[dict]:
    """
    Serialize the record entries to be json serializable.

    - datetime objects
    """
    serialized = [serialize_row(r) for r in records]
    return serialized


def serialize_row(d: dict) -> dict:
    """
    Serialize a single row.
    - Convert Nans to None.
    - Convert datetime objects to ISO format strings.

    If value itself is dictionary, call recursively.
    """
    for k, v in d.items():
        if isinstance(v, float) and np.isnan(v):
            d[k] = None
        if isinstance(v, datetime):
            d[k] = v.isoformat()
        if isinstance(v, dict):
            d[k] = serialize_row(v)
    return d


@transaction.atomic
def coater_to_db(file: SharepointFile) -> CoaterProductionPlanner:
    """
    Insert new entity of 'CoaterProductionPlanner' as JSON in DB with timestamp (traceability).
    """
    path = Path(f"{file.file.path}")
    sha256 = security.hashme(path, hexme=True)
    sheet_name = settings.SHAREPOINT_PRODUCTION_PLANNER_PORZ_SHEET_NAME
    plan = from_excel(path=path, sheet_name=sheet_name)
    planner, _ = CoaterProductionPlanner.objects.get_or_create(sha256=sha256, defaults={"plan": plan})
    return planner


@transaction.atomic
def float_to_db(file: SharepointFile) -> FloaterProductionPlanner:
    """
    Insert new entity of 'FloatProductionPlanner' as JSON in DB with timestamp (traceability).
    """
    path = Path(f"{file.file.path}")
    sha256 = security.hashme(path, hexme=True)
    sheet_name = settings.SHAREPOINT_PRODUCTION_PLANNER_PORZ_SHEET_NAME
    plan = from_excel(path=path, sheet_name=sheet_name)
    planner, _ = FloaterProductionPlanner.objects.get_or_create(sha256=sha256, defaults={"plan": plan})
    return planner


def import_porz_plans_from_sharepoint() -> PorzProductionPlanners:
    """
    import of production plans od Porz from Sharepoint
    - save files in media folder
    - transform content into json strings and store it on DB
    """

    floater_file_name = settings.SHAREPOINT_PRODUCTION_PLANNER_PORZ_FLOATER_FILENAME
    coater_file_name = settings.SHAREPOINT_PRODUCTION_PLANNER_PORZ_COATER_FILENAME

    downloads = download_files_from_sharepoint(
        filenames=[
            floater_file_name,
            coater_file_name,
        ]
    )

    coater = coater_to_db(file=downloads[coater_file_name])
    floater = float_to_db(file=downloads[floater_file_name])
    return PorzProductionPlanners(floater=floater, coater=coater)


def feedback_to_db(file: SharepointFile):
    """
    Read the planner feedback from a downloaded ordermanagement file.
    Add the planner feedback to the matching OrderBookEntry.
    """
    log.debug("Start of 'sharepoint.access.feedback_to_db()'.")

    df = read.as_df(path=Path(settings.MEDIA_ROOT, file.file.path))

    for _, entity in df.iterrows():
        # Hardcoded the columns found in the translation here.
        # See: -> apps.ordermanagement.models.OrderBookEntry.column_translation()
        ob_uid = entity.get("ob_UID", None)
        comment = entity.get("Comment", "")
        status = entity.get("Status", "")
        np_cw = entity.get("NP CW", "")
        etd = entity.get("ETD", "")

        if ob_uid is None:
            log.critical(f"The entity {entity=} for df {df.head()=} has no {ob_uid=}. This should not happen.")
            continue

        try:
            obe = OrderBookEntry.objects.get(pk=ob_uid)
            log.debug(f"Get OrderBookEntry with {ob_uid=}.")
        except OrderBookEntry.DoesNotExist:
            log.warning(f"OrderBookEntry with {ob_uid=} not found.")
            continue

        with transaction.atomic():
            obe.planner_status = status
            obe.planner_comment = comment
            obe.planner_new_production_calender_week = np_cw
            obe.planner_estimation_or_task = etd
            obe.save()


def _get_filename_of_last_existing_om_file(
    prefix: str = f"{settings.SHAREPOINT_ORDERMANAGEMENT_EXPORT_NAME}-TEST",
) -> str:
    """
    Get filename of last existing file (if entry exist in DB)
    or return filename from settings instead.
    """
    filename = f"{prefix}.xlsx"
    last: SharepointFile | None = (
        SharepointFile.objects.filter(file__startswith=prefix).order_by("-lastmodified_at").first()
    )
    return str(last.file).lstrip("sharepoint/") if last else filename


def rewrite_latest_orderbook_from_and_to_sharepoint(division):
    """
    Rewrite the latest orderbook from and to the sharepoint.
    - Download the latest orderbook from the sharepoint, to include planner-feedback.
    """
    log.debug(
        f"Rewrite latest Orderbook from and to Sharepoint (start function). {division=}"
    )

    today: str = timezone.localtime().date().strftime("%Y-%m-%d")
    last_name = _get_filename_of_last_existing_om_file()
    headers = _request_auth_headers()

    with httpx.Client() as client:
        log.debug(f"Starting rewrite of orderbook from and to sharepoint {today=} {last_name=}")

        client.headers.update(headers)
        sharepoint = gather_sharepoint_information(client=client)
        url = (
            f"{settings.SHAREPOINT_GRAPH_ENDPOINT}"  # The base url to post the file to.
            f"/sites/{sharepoint.site_id}"
            f"/drives/{sharepoint.drive_id}"
        )

        file_info = sharepoint.search(name=last_name)
        if file_info is not None:
            log.debug(f"Integrating planer-feedback from {file_info=}")
            feedback_to_db(file=download_file(client=client, sharepoint=sharepoint, file=file_info))

        # Generate the new orderbook - writing new content to disc
        log.debug(f"Generating and writing (to disc) new ordermanagement upload media for {division=}. ")
        spf: SharepointFile = generate_ordermanagement_upload_media(division=division, filename=last_name)

        if file_info is not None:
            log.debug(f"Prepare upload of '{spf.file.name}' uploaded {today=} to sharepoint.")

            # uri to existing file on SharePoint - # ! file will be overwritten
            url += f"/items/{file_info['id']}/content"

            # TBD: do we really need this? Might be redundant.
            headers = _request_auth_headers()
            client.headers.update(headers)

            # read new generated Ordermanagement.
            content = files.read_from_disk(path=settings.SHAREPOINT_MEDIA / last_name, mode="rb")
            data: bytes = content  # type: ignore[annotation-unchecked]  # content mode rb will always be bytes

            # write new generated Ordermanagement to Sharepoint.
            r = client.put(url, data=data, follow_redirects=True)  # type: ignore[assignment]
            r.raise_for_status()
            log.info(f"Orderbook '{spf.file.name}' uploaded {today=} to sharepoint {r.status_code=}.")
        else:
            log.warning(f"File does not exist: {last_name=}")
            # # create new
            # url += f"/items/{spf.file.name}:/content"
            # r = client.post(url, data=data, follow_redirects=True)  # type: ignore[assignment]

    return spf


def generate_ordermanagement_upload_media(division: str, filename: str):
    # today: str = timezone.localtime().date().strftime("%Y-%m-%d")  # type: ignore[annotation-unchecked]

    plant_ids = ordermanagement_views.get_plant_ids(divisions=[division])
    buffer = ordermanagement_views.generate_order_management_buffer(plant_ids=plant_ids)

    # receive filename from the outside
    # filename = f"{settings.SHAREPOINT_ORDERMANAGEMENT_EXPORT_NAME}-TEST.xlsx"

    if not files.write_to_disk(path=settings.SHAREPOINT_MEDIA / filename, content=buffer.read()):
        raise DownloadException(f"Could not write ordermanagement file to disk: {filename=}")
    log.info(f"Write new generated Ordermanagement to disc: {filename=}")

    return db_entry_from_media(file=f"sharepoint/{filename}")


def get_site(client: httpx.Client):
    url = (
        f"{settings.SHAREPOINT_GRAPH_ENDPOINT}"
        f"/sites/{settings.SHAREPOINT_HOST_NAME}"
        f":/sites/{settings.SHAREPOINT_TARGET}/"
    )
    r = client.get(url)
    r.raise_for_status()
    return r.json()


def get_drives(client: httpx.Client, sharepoint: Sharepoint):
    """
    Get drives and their IDs
    """
    url = f"{settings.SHAREPOINT_GRAPH_ENDPOINT}/sites/{sharepoint.site_id}/drives"
    r = client.get(url)
    r.raise_for_status()
    return r.json()


def get_named_drive(drives: dict, drive_name: str) -> dict:
    matches = [d for d in drives["value"] if d["name"] == drive_name]
    if len(matches) > 1:
        raise ValueError(f"Multiple drives with the name '{drive_name}' found.")
    elif len(matches) == 0:
        raise ValueError(f"No drive with the name '{drive_name}' found.")
    return matches[0]


def get_children(client: httpx.Client, sharepoint: Sharepoint, root: str):
    """
    Get the contents of a directory.
    root: "root" or "items/{id}"
    """
    url = (
        f"{settings.SHAREPOINT_GRAPH_ENDPOINT}/sites/{sharepoint.site_id}/drives/{sharepoint.drive_id}/{root}/children"
    )
    r = client.get(url)
    r.raise_for_status()
    return r.json()


def tree_walk_children(client: httpx.Client, sharepoint: Sharepoint, children: list):
    files = []
    for child in children:
        if child.get("folder") is None:
            files.append(child)
            continue

        root = f"items/{child.get('id')}"
        _children = get_children(client=client, sharepoint=sharepoint, root=root)
        files.extend(tree_walk_children(client=client, sharepoint=sharepoint, children=_children["value"]))
    return files


def get_all_files(client: httpx.Client, sharepoint: Sharepoint):
    root_children = get_children(client=client, sharepoint=sharepoint, root="root")
    return tree_walk_children(client=client, sharepoint=sharepoint, children=root_children["value"])


@transaction.atomic
def db_entry_from_media(file: str):
    spf, created = SharepointFile.objects.get_or_create(file=file)
    if not created:
        spf.lastmodified_at = timezone.now()
        spf.save()
    return spf


def download_file(client: httpx.Client, sharepoint: Sharepoint, file: dict) -> SharepointFile:
    """
    Download a file from sharepoint.
    """
    url = (
        f"{settings.SHAREPOINT_GRAPH_ENDPOINT}"
        f"/sites/{sharepoint.site_id}"
        f"/drives/{sharepoint.drive_id}"
        f"/items/{file['id']}/content"
    )

    # Microsoft graph api sends: 302 - preauthorized redirection link (valid for a short time period)
    r = client.get(url, follow_redirects=True)
    r.raise_for_status()

    if not files.write_to_disk(path=settings.SHAREPOINT_MEDIA / file["name"], content=r.content):
        raise DownloadException(f"Could not write file to disk: {file['name']}")
    return db_entry_from_media(file=f"sharepoint/{file['name']}")
