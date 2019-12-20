# Forked from https://github.com/jayrav13/ical_dict

###
#   Imports
#
import urllib.request
import re
from collections import defaultdict

###
#   class iCalDict
#
#   Convert a .ics file into a Dictionary object.
#
class iCalDict():

    ###
    #   __init__
    #
    #   Create a new iCalDict instance with a string representing a url to an .ics file
    #
    def __init__(self, ical_url: str):
        self.__ical_url = ical_url
        self.__data_dict = self.__load_data()


    ###
    #   refresh
    #
    #   Get the latest version of the ics_file
    #
    def refresh(self):
        self.__data_dict = self.__file_get_contents()


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
    ical = iCalDict(ical_url)
    print(ical)
