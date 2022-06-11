# Duty Bot

# Imports
import slack
from ical import iCal
from datetime import date
import traceback
import requests

from config import SECRETS
from config import TESTING_MODE
from config import ROOMPACT

# Global Variables
duty_channel = "#duty"
trade_channel = "#duty-trade-tracker"
log_channel = "#bot-log"
if TESTING_MODE: duty_channel = trade_channel = log_channel

# Secrets
ical_url = SECRETS.get("ical_url")          # Duty Schedule from DUTY 1920
rlc_ical_url = SECRETS.get("rlc_ical_url")  # RLC Duty Schedule from URL DUTY 1920
oauth_token = SECRETS.get("oauth_token")    # Duty Bot OAuth Token for slack

# Slack Client
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
    post_slack_message(log_channel, "*Duty Bot has crashed!* :rotating_light: <!channel>")
    post_attachment_slack_message(
        log_channel, 
        "The following error was detected:",
        traceback.format_exc(),
        "ff0000"
    )


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


# Get Today
#   Return today's date as a string `YYYY-MM-DD`
def get_today() -> str:
    today = date.today()
    today_str = f"{today.year}-{today.month:02d}-{today.day:02d}"
    return today_str


# Fetch the duty members from roompact
#   Sends a request to the download schedule url for a specific day.
#   Takes the emails of the people assigned to that day and fetches their user id from Slack
#   Returns a list of user ids
def fetch_duty_members_from_roompact():
    # Roompact Config values
    cookie = ROOMPACT.get("cookie")
    region_id = ROOMPACT.get("region_id")
    timezone = ROOMPACT.get("timezone")

    # Get today's date
    today_str = get_today()

    # Construct the request to Roompact
    #   Should return a CSV of "First name", "Last name", "Email", etc.
    url = f"https://roompact.com/schedule/download?start={today_str}&end={today_str}&region_id={region_id}&tz={timezone}"
    r = requests.get(url, cookies=cookie)

    if(r.status_code == 200):
        decoded_content = r.content.decode("utf-8")
        
        # If the token is expired, the response will be a login page
        if decoded_content.startswith("<!DOCTYPE"):
            raise ValueError("Expired token")

        # Convert the decoded content to rows
        rows = decoded_content.split('\n')[:-1]
        
        # Pull out the header row
        header = rows[0].split(",")
        rows = rows[1:]

        # Find the index of the email column
        email_index = header.index("Email")
        
        # Construct a list slack ids for the duty members for that day
        duty_members = []
        for row in rows:
            row_values = row.split(",")
            email = row_values[email_index]

            try:
                # Take the email of the member and find the related slack user id
                response = slack_client.users_lookupByEmail(email=email)
                duty_members.insert(0, f"<@{response.data['user']['id']}>")
            except:
                # Print first and last name if the user can't be found
                name = row_values[0] + " " + row_values[1]
                name = name.replace('"', '')
                duty_members.insert(0, name)
        
        return duty_members
    else:
        raise Exception(f"Roompact request failed. Status Code: {r.status_code}. Error Message {r.text}")


# Post Daily RLC Schedule
def post_daily_rlc_schedule():
    # Load RLC calendar
    cal = iCal(rlc_ical_url)

    # Get today's date
    today_str = get_today().replace('-', '')
    
    # Find rlcs on duty for today
    rlcs = cal.get_event_summaries(today_str)

    # Post rlcs on slack
    if len(rlcs) > 0:
        formatted_message = "*" +  "* | *".join(rlcs) + "*"
        post_attachment_slack_message(duty_channel, None, formatted_message, "87693b")


# Post Daily Duty Schedule
def post_daily_duty_schedule():
    # Find duty team for today
    duty_members = fetch_duty_members_from_roompact()

    # Post duty team on slack
    for index, member in enumerate(duty_members):
        duty_number = f"D{index}" if index != 0 else "DC" 
        formatted_message = f"*{duty_number}: {member}*"
        post_attachment_slack_message(duty_channel, None, formatted_message)

    # Post RLCs on duty
    # post_daily_rlc_schedule()


# AWS Handler
#   This is the entry point for the AWS lambda function
def aws_handler(event, lambda_context):
    try:
        post_daily_duty_schedule()
    except:
        # Notify slack that an exception occured
        if not TESTING_MODE: post_exception()
        raise


# Main
if __name__ == "__main__":
    try:
        post_daily_duty_schedule()
    except:
        # Notify slack that an exception occured
        if not TESTING_MODE: post_exception()
        raise
