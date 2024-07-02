from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz
from models import Users, Meetings

scheduler = BackgroundScheduler()

def notify_user(user, meeting): #this func will check if the user is inthe dnd mode and if he is not then it will send a notification
    print("user notification!")
    user_tmz = user.preferred_timezone
    print(user_tmz)
    if user_tmz.lower() == 'ist':
        now = datetime.now(pytz.timezone("Asia/Kolkata"))
    else:
         now = datetime.now(pytz.timezone(user.preferred_timezone))
    if user.dnd_start_time and user.dnd_end_time:
        if user.preferred_timezone.lower() == 'ist':
            print("Create")
            dnd_start = user.dnd_start_time.astimezone(pytz.timezone("Asia/Kolkata"))
            dnd_end = user.dnd_end_time.astimezone(pytz.timezone("Asia/Kolkata"))
        else:
            dnd_start = user.dnd_start_time.astimezone(pytz.timezone(user.preferred_timezone))
            dnd_end = user.dnd_end_time.astimezone(pytz.timezone(user.preferred_timezone))
        if dnd_start <= now <= dnd_end:
            return

    print("requesting webhook")
    # try:
    #     requests.post('https://webhook.site', json={
    #     'user': user.email,
    #     'meeting': meeting.id,
    #     'meeting_type':meeting.meeting_type,
    #     'timezone':meeting.timezone,
    #     'start_time':meeting.start_time,
    #     'end_time':meeting.end_time,
    #     'message': 'You have a meeting scheduled.'
    # })
    # except ValueError as e:
    #      jsonify({"error":f"Please check the error {e} and try again! "})

def cron_parser(cron_expression):
    cron_parts = cron_expression.split()


    if len(cron_parts) == 5:
        return {
            'minute': cron_parts[0],
            'hour': cron_parts[1],
            'day': cron_parts[2],
            'month': cron_parts[3],
            'day_of_week': cron_parts[4]
        }
    else:
        raise ValueError("Invalid cron expression")
    
def scheduler_notification(app,new_meeting_id = None):
     with app.app_context():
        if new_meeting_id is None:
            print("No meeting ID provided")
            return

        meeting = Meetings.query.get(new_meeting_id)
        if not meeting:
            print(f"No meeting found with ID {new_meeting_id}")
            return

        user = Users.query.get(meeting.user_id)
        if not user:
            print(f"No user found for meeting ID {new_meeting_id}")
            return

        try:
            cron_args = cron_parser(meeting.notification_interval)
        except ValueError as e:
            print(f"Invalid cron expression: {str(e)}")
            return

        existing_job = scheduler.get_job(str(new_meeting_id))
        if existing_job:
            print(f"Removing existing job for meeting ID {new_meeting_id}")
            scheduler.remove_job(str(new_meeting_id))

        print(f"Scheduling new job for meeting ID {new_meeting_id}")
        scheduler.add_job(
            notify_user,
            'cron',
            args=[user, meeting],
            id=str(new_meeting_id),
            **cron_args
        )

        print(f"Notification scheduled for meeting ID {new_meeting_id}")


def init_scheduler(app):
    scheduler.start()
    return scheduler