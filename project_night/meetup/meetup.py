import os

import meetup.api
import numpy as np
import pandas as pd
from natsort import humansorted, ns


MEETUP_API_KEY = os.getenv('MEETUP_API_KEY', None)


def get_valid_attendee_names(event_id=None, urlname='_ChiPy_', client=None, offset=0):
    client = client if client else meetup.api.Client(MEETUP_API_KEY)
    event_id = event_id if event_id else get_summary_event_list(client=client)[0]['id']

    rsvps = client.GetRsvps(event_id=event_id, urlname=urlname, offset=offset)
    # check whether all pertinent data has been retrieved
    all_data_flag = len(rsvps.results) < 200

    attendees = [{'Name': person['member']['name'],
                  'RSVP': person['response'],
                  'Given Name': person['answers'][0]}
                 for person in rsvps.results]

    df = pd.DataFrame(attendees)
    df = df[df['RSVP'] != 'no']
    df['Security Name'] = df['Given Name'].replace('', np.nan).combine_first(df['Name'])

    # Only keep rows where there's at least a first and last name
    mask = [True if len(x) > 1 else False for x in df['Security Name'].str.findall(r'\w+')]
    df = df[mask]

    # Human sort the names
    df['Security Name'] = humansorted(df['Security Name'].tolist(), alg=ns.IGNORECASE)

    return df['Security Name'], all_data_flag


def get_summary_event_list(client=None):
    client = client if client else meetup.api.Client(MEETUP_API_KEY)

    events = client.GetEvents(group_urlname='_ChiPy_')

    # todo time needs to be formatted into a readable form
    return [{'name': e['name'], 'time': e['time'], 'id': e['id'], 'event_url': e['event_url']}
            for e in events.results]


# # To match the csv output for event attendees, use:
    # rsvps = client.GetRsvps(event_id=event_id, urlname=urlname)
    # member_ids = [person['member']['member_id'] for person in rsvps.results]
    # members = client.GetMembers(member_id=member_ids)
    # mem_id_to_link = [{m['id']: m['link']}for m in members.results]

#     attendees = []
#     for person in rsvps.results:
#         d = {'Name': person['member']['name'],
#              # 'User ID': person['member']['member_id'],
#              # 'Title': ,
#              # 'Event Host': ,
#              'RSVP': person['response'],
#              # 'Guests': person['guests'],
#              # 'RSVPed on': ,
#              # 'Joined Group on': person['mtime'] ?
#              # 'URL of Member Profile': mem_id_to_link[person['member']['member_id']]
#              'Given Name': person['answers'][0]}

#         attendees.append(d)
