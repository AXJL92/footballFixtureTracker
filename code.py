import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import schedule
import time

# Football Data API Configuration
API_TOKEN = 'API_TOKEN'
TEAM_ID = 57  # XXX FC ID in Football-Data API

# Email Configuration
SENDER_EMAIL = 'EMAIL_ADDRESS'
SENDER_APP_PASSWORD = 'PASSWORD'  # App-Specific Password
RECIPIENT_EMAIL = 'EMAIL_ADDRESS'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Fetch upcoming fixtures for Arsenal
def fetch_fixtures():
    url = f'https://api.football-data.org/v4/teams/{TEAM_ID}/matches?status=SCHEDULED'
    headers = {'X-Auth-Token': API_TOKEN}
    response = requests.get(url, headers=headers)
    data = response.json()

    upcoming_fixtures = []
    now = datetime.now()
    next_monday = now + timedelta(days=(7 - now.weekday()))  # Calculate next Monday
    next_sunday = next_monday + timedelta(days=6)

    # Filter fixtures between next Monday and Sunday
    for match in data['matches']:
        match_date = datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%SZ')
        if next_monday <= match_date <= next_sunday:
            upcoming_fixtures.append({
                'home_team': match['homeTeam']['name'],
                'away_team': match['awayTeam']['name'],
                'date': match_date.strftime('%Y-%m-%d %H:%M:%S'),
                'competition': match['competition']['name']
            })
    
    return upcoming_fixtures

# Send email with fixtures
def send_email(fixtures):
    if not fixtures:
        message_body = "No upcoming Arsenal matches for the next week."
    else:
        message_body = "Mikel Arteta's Tricky Reds have the following fixtures:\n\n"
        for fixture in fixtures:
            message_body += f"• {fixture['home_team']} vs {fixture['away_team']} - {fixture['date']} - {fixture['competition']}\n"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = 'Upcoming Fixtures'

    msg.attach(MIMEText(message_body, 'plain'))

    # Sending the email
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)  # Use the App-Specific Password
    server.send_message(msg)
    server.quit()

# Job to fetch fixtures and send email
def job():
    fixtures = fetch_fixtures()
    send_email(fixtures)

# Schedule the job to run every Monday at 9:00 AM
schedule.every().monday.at("08:00").do(job)


# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute for scheduled jobs
