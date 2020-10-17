# project_night

A collection of scripts useful for hosting/managing Chicago Python User Group (ChiPy)'s Project Night, which is also pip installable. While this project was inspired by the needs of ChiPy's Project Nights, the scripts are easily generalizable for other purposes.

Scripts:
 - challenge.grouper: creates groups of participants based on an "experience level."
 - meetup.meetup: Meetup endpoint to track group members/event attendees.

## Set up Environment

1. Setup and activate Python virtual environment
1. `pip install -r requirements.txt`

## Running Challenge Helper

1. `python challenge_helpers/grouper.py`
1. Use `add`, `bulk add`, or `google add` commands to add folks to Project Night roster
1. `group` to split into teams of 4.

### Bulk Add

Use the `bulk add [path-to-file]` command to add multiple participants to the program.

File format:

```csv
Name, Experience Score
Bobby,3
Jill,9
```

### Add Users Submitted via Google Forms

With the move to virtual events, we have a Google Forms link to get experience information.
Use the `google add [path-to-file]` command to add multiple participants to the program.

File format:

```csv
Timestamp,Your Name,How much experience do you have with Python?
10/15/2020 18:21:24,Bobby,3
10/15/2020 18:21:29,Jill,9
```

