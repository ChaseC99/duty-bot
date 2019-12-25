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
    #   returns a dict containing changes, additions, and deletions
    #
    #   [(time_checked, ADDITION/REMOVAL, event_time, event_summary),
    #    (time_checked, UPDATED, event_time, event_summary, prev_event_summary)]
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
                difference.append(("time", "ADDITION", day, event["SUMMARY"]))
        
        # Find changes
        for day in days_shared:
            difference += self.__compare_days(day, self[day], old_cal[day])

        # Find removals
        for day in days_removed:
            for event in old_cal.get_events(day):
                difference.append(("time", "REMOVAL", day, event["SUMMARY"]))

        return difference


    ###
    #   compare days
    #
    #   Given two days, in the following dict format
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
            difference.append(("time", "ADDITION", time, day1[event_id]["SUMMARY"]))

        # Find changes
        for event_id in events_shared:
            new_summary = day1[event_id]["SUMMARY"]
            old_summary = day2[event_id]["SUMMARY"]

            if new_summary != day2[event_id]["SUMMARY"]:
                difference.append(("time", "UPDATED", time, new_summary, old_summary))

        # Find removals
        for event_id in events_removed:
            difference.append(("time", "REMOVAL", time, day2[event_id]["SUMMARY"]))

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
            
            # Get the start date and unique id of the event
            start_date = event_dict["DTSTART;VALUE=DATE"]
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
