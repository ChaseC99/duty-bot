# Rename this to "config.py"
import os
roompact_token = os.environ.get("roompact_token")

TESTING_MODE = False

SECRETS = dict(
    oauth_token = "Get this token from api.slack.com/apps",
    
    # If the Duty Calendar or RLC Calendar use Google Calendar instead of roompact, add the url's below.
    # Duty Calendar
    ical_url = "",
    # URL Duty Calendar
    rlc_ical_url = ""
)

ROOMPACT = dict(
    cookie = {"roompact": roompact_token},
    region_id = "7eYYeA",
    timezone = "-07%3A00"
)