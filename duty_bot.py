# Duty Bot

# Imports
import slack
from ical_dict import iCalDict
from datetime import date
import time
import schedule

from config import SECRETS
from config import MEMBER_IDS

# Global Variables
channel = "#bot-playground"
ical_url = SECRETS.get("ical_url")
oauth_token = SECRETS.get("oauth_token")
slack_client = slack.WebClient(token=oauth_token)

# Post Slack Message
#   Posts a message to the channel set in global variables
#   Sending it as an attachment with the color #1f4387,
#       posts the message with the mesa blue line next to it
def post_duty_slack_message(message: str):
    parsed_message = parse_for_users(message)
    slack_client.chat_postMessage(
        channel = channel,
        attachments = [
		    {
                "color": "#1f4387",
                "text": "*" + parsed_message + "*"
		    }
        ]
    )

# Parse For User
#   Given a str, parse it and swap out any user names with user IDS
#   This will @ the person when the message is posted
def parse_for_users(text: str):
    parsed_text = []
    
    for word in text.split(" "):
        if word in MEMBER_IDS:
            parsed_text.append(f"<@{MEMBER_IDS[word]}>")
        else:
            parsed_text.append(word)

    return " ".join(parsed_text)  


def post_daily_duty_schedule():
    # Generate Calendar Dictionary
    #   {str : [dict]}
    #   key => date string (ex. "20191208")
    #   value => list of dicts for each event
    cal_dict = iCalDict(ical_url).convert()

    # Get today's date
    today = date.today()
    today_str = f"{today.year}{today.month:02d}{today.day:02d}"
    
    # Find duty team for today
    today_team = cal_dict[today_str]
    duty_members = [duty_member["summary"] for duty_member in today_team]
    duty_members.sort()
    print(duty_members)
    
    # Post duty team on slack
    for member in duty_members:
        post_duty_slack_message(member)


# Main
if __name__ == "__main__":
    # Schedule jobs
    schedule.every().day.at("16:00").do(post_daily_duty_schedule)

    while True:
        schedule.run_pending()
        time.sleep(1)    
