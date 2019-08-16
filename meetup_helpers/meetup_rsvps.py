import copy
import os
from datetime import datetime

import meetup.api
import numpy as np
import pandas as pd
import requests
from natsort import humansorted, ns
from prompt_toolkit import prompt
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError


API_URL = "https://api.meetup.com"
URLNAME = "_ChiPy_"
MEETUP_API_KEY = os.getenv('MEETUP_API_KEY', None)  # In the process of being deprecated?
QUERY = {"sign": True, "key": MEETUP_API_KEY}


def get_summary_event_list(group_urlname='_ChiPy_', client=None):
    """ Gets a list of all future events for `group_urlname`.

    Args:
        group_urlname (str): The meetup group's unique identifier.
        client: Meetup API client connection.

    Returns:
        A pd.DataFrame of all future events for `group_urlname` with
        the event id, name, human-readable datetime, and url.

    """
    client = client if client else meetup.api.Client(MEETUP_API_KEY)
    events = client.GetEvents(parameters={"group_urlname": group_urlname})

    pretty_events = [{'name': e['name'],
                      'time': datetime.fromtimestamp(e['time'] / 1000.0).strftime("%Y-%m-%d %H:%M:%S"),
                      'id': e['id'],
                      'event_url': e['event_url']}
                     for e in events.results]
    pretty_events = pd.DataFrame(pretty_events).set_index('id')[['name', 'time', 'event_url']]

    return pretty_events


def get_rsvps(event_id):
    url = f"{API_URL}/{URLNAME}/events/{event_id}/rsvps"
    query = copy.copy(QUERY)
    query["fields"] = "rsvp"
    response = requests.get(url, params=query)
    if not response.ok:
        status = interpret_status(response.status_code)
        print(f"Failed with status: {status}. URL :\n{url}")
        exit(1)
    else:
        return response.json()


def get_given_name(member_id):
    query = copy.copy(QUERY)
    query["fields"] = "group_profile"
    url = f"{API_URL}/{URLNAME}/members/{member_id}/#get"
    response = requests.get(url, params=query)
    try:
        return response.json()["group_profile"]["answers"][0]["answer"]
    except (IndexError, KeyError):
        return ""


def summarize_rsvps(rsvps):
    attendees = [{'User ID': rsvp['member']['id'],
                  'Name': rsvp['member']['name'],
                  'RSVP Last Updated': datetime.fromtimestamp(rsvp['updated'] / 1000.0).strftime("%Y-%m-%d %H:%M:%S"),
                  'RSVP': rsvp['response'],
                  'Given Name': get_given_name(member_id=rsvp['member']['id']),
                  # 'Guests': rsvp['guests'],
                  }
                 for rsvp in rsvps]

    return attendees


def get_valid_attendee_names(attendees):
    """ Gets a list of valid RSVPs, in alphabetical order by first name.

    Only includes yes/maybe registrants who have a first and last name.
    Names are taken from the better of the given name or the meetup account name.

    Args:
        attendees (ldjson): A list of dicts, where each dict is an RSVP'd person's info.

    Returns:
        A pd.DataFrame of all event attendees, in alphabetical order by first name.
        The attendee's meetup id, name, and RSVPed on are all included.

    """
    df = pd.DataFrame(attendees)
    df = df[df['RSVP'] != 'no']
    df['Security Name'] = df['Given Name'].replace('', np.nan).combine_first(df['Name'])

    # Only keep rows where there's at least a first and last name
    mask = [True if len(x) > 1 else False for x in df['Security Name'].str.findall(r'\w+')]
    df = df[mask]

    # Human sort the names
    df['Security Name'] = humansorted(df['Security Name'].tolist(), alg=ns.IGNORECASE)

    info_for_security = df[['User ID', 'Security Name', 'RSVP Last Updated']]
    info_for_security.set_index('User ID', inplace=True)

    return info_for_security


class SingleFieldValidator(Validator):
    def __init__(self, completer):
        self.completer = completer

    def validate(self, field):
        field = field.text

        if field not in self.completer.words:
            raise ValidationError(message=f"The following option isn't valid: {field}. "
                                  f"Please select from {self.completer.words}. "
                                  f"Selections should NOT be enclosed in quotes.")


if __name__ == '__main__':
    client = meetup.api.Client(MEETUP_API_KEY)

    event_list = get_summary_event_list(client=client)
    print(event_list)

    while True:
        valid_selections = WordCompleter(event_list.index.tolist(), ignore_case=True)
        event_id = prompt('Select the event id from which you want attendees from the above table: ',
                          completer=valid_selections,
                          complete_while_typing=False,
                          validate_while_typing=True,
                          validator=SingleFieldValidator(valid_selections),
                          mouse_support=True)
        break

    event_name = event_list[event_list.index == event_id]['name'][0]
    event_date = event_list[event_list.index == event_id]['time'][0]

    urlname = '_ChiPy_'
    rsvps = get_rsvps(event_id=event_id)
    summary_rsvps = summarize_rsvps(rsvps)

    attendee_df = get_valid_attendee_names(summary_rsvps)
    attendee_df.to_csv(f"{event_date}_{event_name}.csv")
