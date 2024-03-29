# Forked from https://github.com/jayrav13/ical_dict

###
#   Imports
#
import urllib.request
import re
from collections import defaultdict

###
#   class iCal
#
#   Convert a .ics file into a Dictionary object.
#
class iCal():

    ###
    #   __init__
    #
    #   Create a new iCal instance with a string representing a url to an .ics file
    #
    def __init__(self, ical_url: str):
        self.__ical_url = ical_url
        self.__data_dict = self.__load_data()


    ###
    #   get events
    #
    #   Get events for a given day
    #
    #   params: day (str with the format "YYYYMMDD")
    #   returns: list of event_dicts
    #   
    def get_events(self, day: str) -> [dict]:
        # Assert that there are events on the given day
        # If no events, return an empty list
        if not day in self.__data_dict:
            return []

        # Get the events for the day
        return self.__data_dict[day].values()
        

    ###
    #   get event summaries
    #
    #   Get the summary for each event on a given day
    #
    #   params: day (str with the format "YYYYMMDD")
    #   returns: list of event summaries (str0
    #
    def get_event_summaries(self, day: str) -> [str]:
        # Get events for the day
        events = self.get_events(day)

        # Get summaries from each event
        event_summaries = [event["SUMMARY"] for event in events]
        event_summaries.sort()

        return event_summaries


    ###
    #   refresh
    #
    #   Get the latest version of the ics_file
    #   If `compare` is set to true,
    #       then it will return the difference between the old and new cals
    #
    def refresh(self, compare=False):
        if compare:
            temp = iCal(self.__ical_url)
            difference = temp.compare(self)
            self.__data_dict = temp.__data_dict
            return difference
        else:
            self.__data_dict = self.__load_data()


    ###
    #   compare
    #
    #   Compares two calendars
    #   Returns a list of dicts containing changes, additions, and deletions
    #       [{ change_type: str, event: dict, previous: ?dict }]
    #
    def compare(self, old_cal):
        # Assert that other is of type ical        
        if not type(old_cal) == iCal: raise TypeError("other must be of type `iCal`") 

        difference = []

        # Get the days for the current calendar and old calendar
        new_days = self.__data_dict.keys()
        old_days = old_cal.__data_dict.keys()

        # Compare the dict_keys to get the days added, removed, and shared
        # Set operations can be used on the dict_key class
        days_added = new_days - old_days
        days_removed = old_days - new_days
        days_shared = new_days & old_days
        
        # Find additions
        for day in days_added:
            for event in self.get_events(day):
                difference.append({ "change_type": "ADDITION", "event": event })
        
        # Find changes
        for day in days_shared:
            difference += self.__compare_days(day, self[day], old_cal[day])

        # Find removals
        for day in days_removed:
            for event in old_cal.get_events(day):
                difference.append({ "change_type": "REMOVAL", "event": event })

        return difference


    ###
    #   compare days
    #
    #   Given two days, find all added, removed, and updated events
    #   Return a list of dicts in the following format
    #       [{ change_type: str, event: dict, previous: ?dict }]
    #
    def __compare_days(self, time: str, day1: dict, day2: dict):
        difference = []    

        # Get all event_ids from the new and old days        
        new_events = day1.keys()
        old_events = day2.keys()

        # Compare the dict_keys to get the events added, removed, and shared
        # Set operations can be used on the dict_key class
        events_added = new_events - old_events
        events_removed = old_events - new_events
        events_shared = new_events & old_events

        # Find additions
        for event_id in events_added:
            difference.append({ "change_type": "ADDITION", "event": day1[event_id] })

        # Find changes
        for event_id in events_shared:
            current_event = day1[event_id]
            previous_event = day2[event_id]

            if current_event["SUMMARY"] != previous_event["SUMMARY"]:
                difference.append({ "change_type": "UPDATE", "event": current_event,  "previous_event": previous_event })

        # Find removals
        for event_id in events_removed:
            difference.append({ "change_type": "REMOVAL", "event": day2[event_id] })

        return difference


    ###
    #   load data
    #
    #   load the calendar from the url and store it as a dict
    #
    def __load_data(self) -> dict:
        # Fetch ical from url
        #   content: str = the ical file, with every newline indicated by "\r\n"
        content = urllib.request.urlopen(self.__ical_url).read().decode()

        # Dict for the calendar
        #   structure of ouput:
        #   { date (str YYYYMMDD):
        #       { unique_id (str): 
        #           { event_dict }
        #       }
        #   }
        output = defaultdict(dict)
        
        # Regex Expression to match events
        #   This captures all of the content of the vevent as a str, 
        #   with each vevent value on a newline (\r\n)
        event_regex = r"BEGIN:VEVENT\r\n(.+?(?=END:VEVENT))"
        event_matches = re.finditer(event_regex, content, re.MULTILINE | re.DOTALL)
        
        # Iterate over matches 
        for event in event_matches:
            # Split the vevent str by its lines,
            # so that each line contains a value
            #   ex: ['DTSTART;VALUE=DATE:20191221', 'DTEND;VALUE=DATE:20191222', 'UID:0aolsmdd0eufajj0', 'SUMMARY:D1:Chase'] 
            event_list = event.group(1).split("\r\n")
            
            # Convert that list into a dict
            #   ex: ['SUMMARY:D1:Chase', 'UID:0aolsmdd0eufajj0'] -> { 'SUMMARY': 'D1:Chase', 'UID': '0aolsmdd0eufajj0' }
            event_dict = self.__list_to_dict(event_list)
            
            # Get the start date of the event
            # If the key is not in the event dict,
            #   then it is not an all day event.
            #   Handle this cause by get the `DTSTART` and taking the substring to remove the time, leaving only the date.
            #   Add this start date to the dict with key `DTSTART;VALUE=DATE`, so there won't be other errors later on.
            if "DTSTART;VALUE=DATE" in event_dict:
                start_date = event_dict["DTSTART;VALUE=DATE"]
            else:
                start_date = event_dict["DTSTART;TZID=America/Los_Angeles"][0:8]
                event_dict["DTSTART;VALUE=DATE"] = start_date

            # Get event's unique id
            unique_id = event_dict["UID"]

            # Add the event to the output
            output[start_date][unique_id] = event_dict
            

        # Return the calendar dict object
        return output


    ###
    #   __list_to_dict
    #
    #   Given a list of .ics lines, return the list as a Dictionary object.
    #
    def __list_to_dict(self, data: list) -> dict:
        
        # Assert that data is of type list
        if not isinstance(data, list): raise Exception(self.__error_messages("array_required"))

        # Event dict
        event_dict = {}

        # Iterate over all ical values
        for line in data:
            # Split line into key and value
            #   ex: "SUMMARY:D1: Chase" -> ["SUMMARY", "D1: Chase"]
            elements = line.split(':', 1)

            # Assert that elements has a key and a pair
            #   If it doesn't, ignore the line
            if len(elements) != 2: 
                continue

            # Add the key/value pair to the event_dict
            #   elements[0] is the key.     ex: "SUMMARY"
            #   elements[1] is the value.   ex: "D1: Chase"
            event_dict[elements[0]] = elements[1]

        return event_dict

    
    ###
    #   __error_messages
    #
    #   Return an error message given an identifying key.
    #
    def __error_messages(self, key):

        messages = {
            "invalid_file":     "This file is invalid. A .ics file is identified as a file in which the first line is \"BEGIN:VCALENDAR\".",
            "no_events":        "No Events, identified by the \"BEGIN:VEVENT\" line, have been found.",
            "array_required":   "An array is required to convert data to JSON. A non-array parameter has been provided.",
            "invalid_element":  "The following line does not follow expected convention"
        }

        if key not in messages: return "An unknown error has occured."

        return messages[key]


    ###
    #   override getitem
    #
    #   Add ability to use the [] operator
    #   Returns the value for key in self.__data_dict
    def __getitem__(self, key):
        return self.__data_dict[key]

    ###
    #   override str
    #
    #   return the dict as a str
    def __str__(self) -> str:
        return str(self.__data_dict)
    
###
#   Testing the above.
#
if __name__ == '__main__':
    ical_url = "https://calendar.google.com/calendar/ical/uci.edu_5jklevjtcuktlt4ltl8mlfc3eo%40group.calendar.google.com/private-0b64929a1db93a0150220deec82a9e3a/basic.ics"
    ical = iCal(ical_url)
    print(ical)
