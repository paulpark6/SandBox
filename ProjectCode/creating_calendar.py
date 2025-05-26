# creating_calendar.py
# file should have functions to create calendar
from methods import load_recent_keys, save_recent_keys, create_single_event, generate_event_key
from llm_methods import store_response
from auth import get_user_service
import pandas as pd


def create_schedule(service, calendar_id, df_calendar, recent_keys_stack):
    ## FUNCTION_PURPOSE: adding user's schedule to google calendar
    # arguments:
    #       service -> contains the service from auth.py
    #       calendar_id -> contains information about which calendar user wants to edit. This calendar should be created by user in google calendar first and user should give the calendar id of the created calendar
    #       df_calendar -> output from conver_response() function (df should have 3 columns: 'title', 'description', 'event_date')
    #       stack -> stores all events created as a stack, this is a list of dictionary
    # Effects: the function will modify google calendar and create non duplicate events
    # returns: will return the updated version of the stack
    for _, row in df_calendar.iterrows():
        title = row['title']  # Corrected from 'Activity Description' to 'title'
        description = row.get('description', '')  # Ensure this matches your DataFrame column names
        event_date = row.get('event_date', None)  # Ensure this matches your DataFrame column names
        # adding single rows as events from df_calendar to google calendar
        # generating unique key for indvidual events
        unique_key = generate_event_key(title=title, description=description, calendar_id=calendar_id, event_date=event_date)
        key_count = 0
        for tuples in recent_keys_stack:
            if tuples[0] == unique_key: 
                key_count += 1 
            else: 
                continue
        # only create if key is unique
        if key_count == 0: 
            mapping = create_single_event(service, calendar_id=calendar_id, title=title, description=description, event_date=event_date, mapping = recent_keys_stack)
            recent_keys_stack += [mapping] # updating stack
        return recent_keys_stack

    ## deleting google calendar events
    # there is a delete function in methods.py that will delete the events
    # it will delete the most recently created event first.
    # user will have two options, delete one event at a time or delete all events created by automation



# ----------------------------------------------------------------------------------------------------------------
# below is an example main file
# def main():
# INITIALIZATIONS
# recent_keys_dic   = load_recent_keys() # might not need this line

recent_keys_stack = [] # basically list of tuples (key, value)
# getting user's calendar id and service
service = get_user_service() # this will authenticate the user with their email
calendar_id = '2806f05d02c1bbdf138214309fef8f6c1066b1aa071308257a51ca49eedd2497@group.calendar.google.com' # this should be given by the user, this stores which calendar you want to create the schedule with.
# Need to read in data for calendar events to dictionary format or pd dataframe, lets call this event_data
#user_response = "path_to_txt" # will store the user's given path to txt file. User should give the full path location to the txt file.
# given the text file this is what the output of store_response(user_response) should look like
user_response = {
    "title": [
        "Textbook Reading : Chapter 1",
        "Case Study Assignment 1 Available"
    ],
    "event_date": [
        "2025-05-09",  # Fri
        "2025-05-23",  # Fri
    ],
    "description": [
        "Week 1,\nDue Date = Friday, May 09, 2025: 11:55 PM",
        "Week 3,\nAvailable = Friday, May 23, 2025: 12:05 AM"
    ]
}
# df_calendar = pd.DataFrame(store_response(user_response))# store user's response into pd dataframe
df_calendar = pd.DataFrame(user_response)
# creating new schedule for specified calendar id
recent_keys_stack = create_schedule(service, calendar_id, df_calendar, recent_keys_stack)
# save all keys in stack
for tuples in recent_keys_stack:
    save_recent_keys({tuples[0]:tuples[1]}) # this function takes in dictionaries and will save into json file
# after saving empty stack
recent_keys_stack = []

# if __name__ == "__main__":
#     main()
