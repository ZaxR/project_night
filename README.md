# project_night

A collection of scripts useful for hosting/managing Chicago Python User Group (ChiPy)'s Project Night, which is also pip installable. While this project was inspired by the needs of ChiPy's Project Nights, the scripts are easily generalizable for other purposes.

Scripts:
 - challenge.grouper: creates groups of participants based on an "experience level."
 - meetup.meetup: Meetup endpoint to track group members/event attendees.

## Set up Environment

1. Setup and activate Python version environment
1. `pip install -r requirements.txt`

## Running Challenge Helper

1. `python challenge_helpers/grouper.py`
1. Use `add`, `bulk add`, or `google add` commands to add folks to Project Night roster
1. `group` to split into teams of 4.
