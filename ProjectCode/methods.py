import json
import datetime
from pathlib import Path
from googleapiclient.discovery import build
from typing import Any, Dict, List, Optional
import datetime
import hashlib

# Constants
BASE_DIR    = Path(__file__).resolve().parent
MAPPING_FILE = BASE_DIR / "Data" / "mapping_file.json"

def _ensure_mapping_dir_and_file(path: Path) -> None:
    """
    Ensure that the mapping file and its parent directory exist.

    - Creates the parent directory if it does not exist.
    - Creates the file with an empty JSON object if the file is missing or has zero size.

    Args:
        path (Path): Full path to the mapping JSON file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size == 0:
        path.write_text(json.dumps({}, indent=2))


def load_recent_keys(path: Path = MAPPING_FILE) -> Dict[str, Any]:
    """
    Load key mappings from a JSON file, creating or initializing it if needed.

    - Ensures the mapping file and its parent directory exist.
    - Returns the parsed JSON content as a dictionary.
    - If the file contains invalid JSON, returns an empty dictionary.

    Args:
        path (Path, optional): Path to the mapping file. Defaults to MAPPING_FILE.

    Returns:
        Dict[str, Any]: Parsed key-value mappings from the file.
    """
    _ensure_mapping_dir_and_file(path)
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}

## need to crate a function that turns tuples into json file type opposite of load_recent_keys
def save_recent_keys(d):
    # functionw ill take in singl dictionary d and add it to the mapping_file.json
    # given the path to the mapping file (like above function) it will append a single dictionary to this json file.
    return None
## function to create a hash key
def generate_event_key(
    title: str                  = "",
    description: str            = "",
    calendar_id: str            = "",
    event_date: str             = "",
    event_time: Optional[str]   = "",
    end_date: str               = "",
    timezone: str               = "",
    notifications: Optional[List[Dict[str, Any]]] = None,
    invitees: Optional[List[str]]               = None
) -> str:
    """
    Generate a deterministic unique key for an event based only on its input parameters.
    """
    # Normalize parameters
    event_time_part = event_time or ""
    notifications_part = (
        "|".join([f"{n['method']}@{n['minutes']}" for n in notifications])
        if notifications else ""
    )
    invitees_part = ",".join(sorted(invitees)) if invitees else ""

    # Create a single string from all parts
    key_string = "\x1F".join([
        "automated",
        title,
        description,
        calendar_id,
        event_date,
        event_time_part,
        end_date,
        timezone,
        notifications_part,
        invitees_part
    ])

    # Hash the combined string to keep keys short
    key_hash = hashlib.sha1(key_string.encode('utf-8')).hexdigest()

    return key_hash

## function to create single event
def create_single_event(
    service,
    calendar_id: str = 'primary',
    title: str = 'title',
    description: str = 'description',
    event_date: str = None,
    event_time: str = None,
    end_date: str = None,
    timezone: str = 'America/Toronto',
    notifications: list = None,
    invitees: list = None,
) -> tuple:
    """
    Create a single Google Calendar event with optional reminders and invitees,
    and return a unique key paired with the actual event ID.

    This function builds a complete event object based on the provided inputs and
    inserts it into the specified Google Calendar. A unique hash-based key is generated
    to support cross-session deduplication and tracking. Reminder defaults are automatically
    applied based on whether the event is timed or all-day.

    Parameters
    ----------
    service : googleapiclient.discovery.Resource
        Authenticated Google Calendar API service instance.
    calendar_id : str, optional
        The ID of the calendar to insert the event into. Defaults to 'primary'.
    title : str, optional
        The title of the event. Defaults to 'title'.
    description : str, optional
        A description of the event. Defaults to 'description'.
    event_date : str, optional
        Event start date in 'YYYY-MM-DD' format. Defaults to today if not provided.
    event_time : str, optional
        Event start time in 'HH:MM' format. If omitted, the event is treated as all-day.
    end_date : str, optional
        End date of the event. Defaults to `event_date` if not provided.
    timezone : str, optional
        IANA time zone string. Defaults to 'America/Toronto'.
    notifications : list of dict, optional
        List of custom notification dictionaries, each with 'method' and 'minutes'.
        If omitted, default reminders are used based on event type (timed or all-day).
    invitees : list of str, optional
        List of email addresses to invite to the event.

    Returns
    -------
    tuple
        A tuple containing:
        - `key` (str): A deterministic, hash-based key representing the event identity.
        - `event_id` (str): The ID assigned by Google Calendar for the created event.

    Notes
    -----
    - This function assumes `service` is pre-authenticated and valid.
    - The generated key can be used for deduplication or tracking events across sessions.
    """
    # Default dates to today
    today = datetime.date.today().strftime('%Y-%m-%d')
    event_date = event_date or today
    end_date = end_date or event_date

    # Decide which reminders to use
    if notifications is None:
        if event_time:                 # timed (date‑time) events
            overrides = [
                {'method': 'email',  'minutes': 24 * 60},     # 1 day before (same clock time)
                {'method': 'popup',  'minutes': 7  * 24 * 60},# 1 week before
                {'method': 'popup',  'minutes': 2  * 60},     # 2 hours before
                {'method': 'popup',  'minutes': 24 * 60},     # 1 day before
                {'method': 'popup',  'minutes': 2  * 24 * 60} # 2 days before
            ]
        else:                           # all‑day events (start = 00:00)
            #H9 = 9 * 60                 # 9 a.m. offset
            overrides = [
                {'method': 'popup',  'minutes': 7  * 24 * 60}, # 1 week before @ 00:00
                {'method': 'email',  'minutes': 1  * 24 * 60}, # 1 day  before @ 00:00 (email)
                {'method': 'popup',  'minutes': 1  * 24 * 60}, # 1 day  before @ 00:00
                {'method': 'popup',  'minutes': 2  * 24 * 60},  # 2 days before @ 00:00
                {'method': 'popup',  'minutes': 3  * 24 * 60},  # 3 days before @ 00:00
            ]
    else:
        overrides = notifications

    # generate a unique key for the event using its parameters
    key = generate_event_key(
        title,
        description,
        calendar_id,
        event_date,
        event_time,
        end_date,
        timezone,
        notifications,
        invitees
    )

    # Build the event object
    event = {
        'summary': title,
        'description': description,
        'start':  (
            {'dateTime': f"{event_date}T{event_time}", 'timeZone': timezone}
            if event_time else {'date': event_date}
        ),
        'end':    (
            {'dateTime': f"{end_date}T{event_time}", 'timeZone': timezone}
            if event_time else {'date': end_date}
        ),
        'reminders': {
            'useDefault': False,
            'overrides': overrides
        },
        'attendees': [{'email': e} for e in (invitees or [])]
    }

    # Create event
    created = service.events().insert(calendarId=calendar_id, body=event).execute()

    # creates a tulple/pair of key and id
    mapping = (key,  created['id'])
    return mapping


def delete_event(
    service,
    calendar_id='primary',
    mapping=()
) -> str:
    """
    Delete an event from Google Calendar using its event ID.

    Parameters
    ----------
    service : googleapiclient.discovery.Resource
        Authenticated Google Calendar API service instance.
    calendar_id : str, optional
        The ID of the calendar from which to delete the event. Defaults to 'primary'.
    mapping : tuple
        A 2-element tuple containing:
        - key (str): A unique event hash (not used in deletion).
        - event_id (str): The Google Calendar event ID to be deleted.

    Returns
    -------
    str
        The event ID of the deleted event.

    Raises
    ------
    googleapiclient.errors.HttpError
        If the event could not be deleted due to an API error.
    """
    key, event_id = mapping
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
    return mapping

