# Duty Bot

# Imports
import slack
from ical import iCal
from datetime import date
import time
import schedule
import traceback

from config import SECRETS
from config import MEMBER_IDS
from config import TESTING_MODE

# Global Variables
duty_channel = "#duty"
trade_channel = "#duty-trade-tracker"
if TESTING_MODE: duty_channel = trade_channel = "#bot-playground"

ical_url = SECRETS.get("ical_url")
oauth_token = SECRETS.get("oauth_token")
slack_client = slack.WebClient(token=oauth_token)


# Post Slack Message (attachment)
#   Sending it as an attachment with the color #1f4387,
#       posts the message with the mesa blue line next to it
def post_attachment_slack_message(channel: str, pretext: str, message: str, color="1f4387"):
    slack_client.chat_postMessage(
        channel = channel,
        attachments = [
            {
                "color": color,
                "pretext": pretext,
                "text": message
            }
        ]
    )


# Post Slack Message
#   Post a normal slack message to the specified channel
def post_slack_message(channel: str, text: str):
    slack_client.chat_postMessage(
        channel = channel,
        text = text
    )


# Post Exception Message
#   Given an exception, it will post the exceptions information to Slack
def post_exception():
    post_slack_message("#bot-playground", "*Duty Bot has crashed!* :rotating_light: <!channel>")
    post_attachment_slack_message(
        "#bot-playground", 
        "The following error was detected:",
        traceback.format_exc(),
        "ff0000"
    )


# Parse For User
#   Given a str, parse it and swap out any user names with user IDS
#   This will @ the person when the message is posted
def parse_for_users(text: str) -> str:
    parsed_text = []
    
    for word in text.split(":"):
        word = word.strip()
        if word in MEMBER_IDS:
            parsed_text.append(f"<@{MEMBER_IDS[word]}>")
        else:
            parsed_text.append(word)

    return ": ".join(parsed_text)  


# Date to String
#   Given a str in ical date format (YYYYMMDD),
#   Return it in a readable format (Month DD, YYYY)
months = {  '01':'January', '02':'February', '03':'March',
            '04': 'April',  '05':'May',      '06':'June',
            '07':'July',    '08':'August',   '09':'September', 
            '10':'October', '11':'November', '12':'December' }

def date_to_string(date: str) -> str:
    year = date[0:4]
    month = date[4:6]
    day = date[6:]
    return f"{months[month]} {day}, {year}"


# Post Daily Duty Schedule
def post_daily_duty_schedule():
    # Generate Calendar Dictionary
    #   {str : [dict]}
    #   key => date string (ex. "20191208")
    #   value => list of dicts for each event
    cal = iCal(ical_url)

    # Get today's date
    today = date.today()
    today_str = f"{today.year}{today.month:02d}{today.day:02d}"
    
    # Find duty team for today
    today_team = cal.get_events(today_str)
    duty_members = [duty_member["SUMMARY"] for duty_member in today_team]
    duty_members.sort()
    print(duty_members)
    
    # Post duty team on slack
    for member in duty_members:
        parsed_message = parse_for_users(member)
        formatted_message = "*" + parsed_message + "*"
        post_attachment_slack_message(duty_channel, None, formatted_message)


# Check for Calendar Updates
#   Call refresh on calendar, 
#   Check to see if there are differences between prev and current version,
#   Post the differences to Slack,
#   TODO: Log the differences (to a text file?)  
#
#   Note: Since python paramaters are `pass-by-object-reference`,
#   calling refresh on calendar updates the variable in __main__.
def check_for_calendar_updates(calendar):
    # Get a list of differences between the current and previous versions
    # List format: [{ change_type: str, event: dict, previous: ?dict }]
    differences = calendar.refresh(compare=True)
    
    if not len(differences) == 0:
        for difference in differences:
            # Pull some variables out of `difference
            change_type = difference["change_type"]
            event = difference["event"]
            event_summary = event["SUMMARY"]
            event_date = date_to_string(event["DTSTART;VALUE=DATE"])   

            # Post messages to slack, depending on the change_type
            if change_type == "ADDITION":
                post_attachment_slack_message(
                    trade_channel,
                    "Calendar event was added :rotating_light:",
                    "*{event_title}*\n{date}".format(
                        event_title = parse_for_users(event_summary),
                        date = event_date
                    )
                )
            elif change_type == "UPDATE":
                post_attachment_slack_message(
                    trade_channel,
                    "Calendar event was updated",
                    "*~{old_event}~*\n*{new_event}*\n{date}".format(
                        old_event = parse_for_users(difference["previous_event"]["SUMMARY"]),
                        new_event = parse_for_users(event_summary),
                        date = event_date
                    )
                )
            elif change_type == "REMOVAL":
                post_attachment_slack_message(
                    trade_channel,
                    "Calendar event was deleted :rotating_light:",
                    "*~{event_title}~*\n{date}".format(
                        event_title = parse_for_users(event_summary),
                        date = event_date
                    )
                )


# Main
if __name__ == "__main__":
    # Create calendar ref
    calendar = iCal(ical_url)

    # Schedule jobs
    schedule.every(5).minutes.do(check_for_calendar_updates, calendar)
    schedule.every().day.at("16:00").do(post_daily_duty_schedule)    

    # Wrap main loop in a try statement
    try:
        # Notify Slack that Duty Bot has been activated
        if not TESTING_MODE:
            post_slack_message("#bot-playground", "Duty Bot activated and reporting for duty :salute:")

        while True:
            schedule.run_pending()
            time.sleep(20)    

    except KeyboardInterrupt:
        if not TESTING_MODE: 
            post_slack_message("#bot-playground", "Duty Bot has been deactivated :sleeping:")
    except:
        # Notify slack that an exception occured
        if not TESTING_MODE: post_exception()
        raise