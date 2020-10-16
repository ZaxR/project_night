from collections import defaultdict

import pandas as pd
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter


class Challenge(object):
    """Challenge instance for grouping challenge participants based on experience.

    Commands:
        'add': Adds participants one at a time in a , format.
        'bulk add': Loads participants and their experience levels from a csv file at the given path.
        'clear': Clears all participants.
        'group': Creates groups of a given size (default 4), evenly distributing experience levels (any int) across groups.
        'list': Displays a list of participants.
        'remove': Removes one or more participants, separating with commas.
        'save': Saves the list of participants and their experience scores to a csv at the given path.

    """
    def __init__(self, name: str):
        self.name = name
        df = pd.DataFrame(columns=['Name', 'Experience Score'])
        self.participants = df.set_index("Name")

    def add_participant(self, no_cmd_msg: str):
        """Add participants one at a time in a <name>, <int> format."""
        try:
            name = no_cmd_msg.split(',')[0].strip()
            experience_score = int(no_cmd_msg.split(',')[1].strip())
        except:
            print("Invalid addition. Please enter a name, integter only.")
            return

        new_df = pd.DataFrame([[name, experience_score]], columns=["Name", "Experience Score"])
        new_df = new_df.set_index('Name')

        self.participants = pd.concat([self.participants[~self.participants.index.isin(new_df.index)], new_df])

        print(f"{name} added.")

    def bulk_add_participants(self, no_cmd_msg: str):
        """Loads participants from a csv file at the given path."""
        path = no_cmd_msg.strip()
        columns = ["Name", "Experience Score"]
        new_df = pd.read_csv(path, skiprows=1, names=columns)
        new_df = new_df.set_index("Name")

        self.participants = pd.concat([self.participants[~self.participants.index.isin(new_df.index)], new_df])

        print(f"Participants from {path} added.")

    def bulk_add_participants_google_form(self, no_cmd_msg: str):
        """Loads participants from a csv file at the given path."""
        path = no_cmd_msg.strip()
        columns = ["ts", "Name", "Experience Score"]
        new_df = pd.read_csv(path, skiprows=1, usecols=[1,2], names=columns)
        new_df = new_df.set_index("Name")

        self.participants = pd.concat([self.participants[~self.participants.index.isin(new_df.index)], new_df])

        print(f"Participants from {path} added.")

    def clear_participants(self, no_cmd_msg: str):
        """Clear all participants."""
        clear_y_n = prompt("Are you sure you want to remove all participants? ")
        if str(clear_y_n).lower() in ["y", "yes"]:
            self.participants = pd.DataFrame(columns=['Experience Score'])
            print("Aaaall gone.")
        elif str(clear_y_n).lower() in ["n", "no"]:
            print("Ok - we didn't touch anything.")
        else:
            print(f" '{clear_y_n}'' is not a valid command.")

    def create_groups(self, no_cmd_msg: str):
        """Creates groups with one participant per quantile by any numeric scores.

        Example:
                Typing `group` alone or with non-integers will create groups of 4.
                An integer can optionally be added to change group size. E.g. `group 3`

        """
        no_cmd_msg = no_cmd_msg.strip()
        df = self.participants.copy()
        df['Experience Score'] = df['Experience Score'].astype('int32')
        # todo handle group_size of 0 and empty df

        try:
            group_size = 4 if not no_cmd_msg else int(no_cmd_msg)
        except ValueError:
            print(f"group_size expects an integer. You input the string {no_cmd_msg}.")
            return

        if group_size > df.shape[0]:
            print(f"Group 1 {list(df.index)}")
            return

        # Quantiles are derived from ranked experience_score to break ties.
        # Specifically, method='first' is used to break the ties
        df['rank'] = df['Experience Score'].rank(method='first', ascending=False)
        df['quantile'] = pd.qcut(df['rank'], group_size, labels=False)

        # Shuffle the dataframe
        df = df.sample(frac=1)
        df.index.name = 'Name'

        # Create groups
        groups = defaultdict(list)
        for name, group in df.groupby('quantile'):
            c = 0
            for i, r in group.iterrows():
                c += 1
                groups[f"Group {c}"].append(r.name)

        # Identify small groups
        small_groups = []
        for group_name, group_members in groups.items():
            if len(group_members) < group_size - 1:
                small_groups.append(group_name)

        # Redistribute members of small groups to the larger groups
        to_redistribute = []
        for group_name in small_groups:
            to_redistribute.extend(groups.pop(group_name))

        while to_redistribute:
            for group_name, group_members in groups.items():
                if not to_redistribute:
                    break
                group_members.append(to_redistribute.pop())

        for k, v in groups.items():
            print(f"{k}: {', '.join(v)}")

    def list_participants(self, no_cmd_msg: str):
        print(self.participants)

    def remove_participants(self, no_cmd_msg: str):
        """Remove one or more participants, separating with commas."""
        participant_names = [i.strip() for i in no_cmd_msg.split(",")]

        removed_list = []
        for name in participant_names:
            if name in self.participants.index:
                removed_list.append(name)

        if removed_list:
            self.participants = self.participants[~self.participants.index.isin(participant_names)]
            print(f"{removed_list} removed.")
        else:
            print(f"No valid names to remove.")

    def save_participants_list(self, no_cmd_msg: str):
        """Save the list of participants and their experience scores to a csv at the given path."""
        path = no_cmd_msg.strip()
        try:
            self.participants.to_csv(path)
            print(f"Participants saved to {path}.")
        except FileNotFoundError:
            print("Please enter a valid path name.")

    def parse_event(self, event_data):
        """Routes commands to the proper function."""
        message = event_data.strip()

        valid_commands = {"add ": self.add_participant,
                          "bulk add ": self.bulk_add_participants,
                          "google add ": self.bulk_add_participants_google_form,
                          "clear": self.clear_participants,
                          "group": self.create_groups,
                          "list": self.list_participants,
                          "remove ": self.remove_participants,
                          "save": self.save_participants_list}

        for command in valid_commands:
            if message.lower().startswith(command):
                valid_commands[command](message.lower()[len(command):])
                break
        else:
            return f"{message} is an invalid command. Please choose from: {', '.join([c for c in valid_commands])}."


def grouper():
    command_completer = WordCompleter(['add', 'bulk add', 'google add', 'clear', 'group', 'list', 'remove', 'save'], ignore_case=True)
    history = InMemoryHistory()
    challenge = Challenge('Current')

    while True:
        try:
            event_data = prompt('> ',
                                completer=command_completer,
                                history=history)
            challenge.parse_event(event_data)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break  # Control-D pressed.

    print('GoodBye!')


if __name__ == '__main__':
    grouper()
