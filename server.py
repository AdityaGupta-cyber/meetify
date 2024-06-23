from flask import Flask,request,jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timezone
import pytz
from dateutil import parser
from flask_migrate import Migrate
from croniter import croniter
from apscheduler.schedulers.background import BackgroundScheduler
import requests

app = Flask(__name__)
import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')  or 'sqlite:///site.db'
db  = SQLAlchemy(app) 
migrate = Migrate(app, db)
scheduler = BackgroundScheduler()
scheduler.start()

# OUR DATABASE MODELS
class Users(db.Model):
        id = db.Column(db.Integer,primary_key = True)
        name  = db.Column(db.String(20),unique=False,nullable=False)
        email = db.Column(db.String(50),unique=True,nullable=False) 
        dnd_end_time= db.Column(db.DateTime,unique=False,nullable=False)
        dnd_start_time = db.Column(db.DateTime,unique=False,nullable=False)
        preferred_timezone= db.Column(db.String(10),unique=False,nullable=False)
        meetings = db.relationship('Meetings',back_populates = 'users',cascade="all, delete-orphan")

class Meetings(db.Model):
        id = db.Column(db.Integer,primary_key = True)
        user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
        meeting_type =  db.Column(db.String,unique=False,nullable=False)
        start_time = db.Column(db.DateTime,nullable = False)
        end_time =  db.Column(db.DateTime,nullable = False)
        timezone = db.Column(db.String(20),nullable = False)
        notification_interval =db.Column(db.String(20),nullable = False)
        users = db.relationship('Users',back_populates='meetings')

#scheduler functions -

def notify_user(user, meeting): #this func will check if the user is inthe dnd mode and if he is not then it will send a notification
    print("user notification!")
    now = datetime.now(pytz.timezone(user.preferred_timezone))
    if user.dnd_start_time and user.dnd_end_time:
        dnd_start = user.dnd_start_time.astimezone(pytz.timezone(user.preferred_timezone))
        dnd_end = user.dnd_end_time.astimezone(pytz.timezone(user.preferred_timezone))
        if dnd_start <= now <= dnd_end:
            return

    
    requests.post('https://webhook.site', data={
        'user': user.email,
        'meeting': meeting.id,
        'meeting_type':meeting.meeting_type,
        'timezone':meeting.timezone,
        'start_time':meeting.start_time,
        'end_time':meeting.end_time,
        'message': 'You have a meeting scheduled.'
    })

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
    
def scheduler_notification():
     with app.app_context():
          meetings = Meetings.query.all()

          for meeting in meetings:
               user = Users.query.get(meeting.user_id)
               cron_args = cron_parser(meeting.notification_interval)
               scheduler.add_job(
                notify_user,
                'cron',
                [user,meeting],
               **cron_args
               )

#Our Routes to server the requests
@app.route("/",methods=["GET"])
def home():
     return render_template('index.html')


@app.route('/create-user',methods=['POST'])
def create_user():
    data = request.json

    if not data:
         return jsonify({"error":"No input data!"})
    name = data.get('name')
    email = data.get('email')
    dnd_start_time = data.get('dnd_start_time')
    dnd_end_time = data.get('dnd_end_time')
    print(dnd_end_time)
    preferred_timezone = data.get('preferred_timezone')
    if preferred_timezone.lower()  == "ist":
          preferred_timezone = "Asia/Kolkata"
    if preferred_timezone not in pytz.all_timezones:
        return jsonify({'error': 'Invalid timezone'}), 400
    if not name or not email or not dnd_start_time or not dnd_end_time or not preferred_timezone:
        return jsonify({'error': 'Missing required fields'}), 400
    try:
        # temp = Users.query.all()
        # print(temp[1].dnd_end_time)
        user = Users(name = data['name'],email =data['email'],
        dnd_start_time = datetime.fromisoformat(data['dnd_start_time'] ),dnd_end_time = datetime.fromisoformat(data['dnd_end_time']),preferred_timezone = "IST")
        db.session.add(user)
        db.session.commit()
      
        return jsonify({"message":"User has been created"}),201
    except ValueError as error:
        return f"{error}"



@app.route("/update/<int:user_id>",methods =["PUT"])
def update_user(user_id):
     data = request.json
     user = Users.query.get(user_id)
     
     if not user:
            return jsonify({"error":f"User cannot be updated as the User with {user_id} does not exists"})
     if not data:
            return jsonify({"error":f"No data received to update the User ID- {user_id}"})

     dnd_start_time = data.get('dnd_start_time')
     dnd_end_time = data.get('dnd_end_time')
     preferred_timezone = data.get('preferred_timezone')
     print(dnd_end_time)

     if preferred_timezone.lower()  == "ist":
          preferred_timezone = "Asia/Kolkata"

     if preferred_timezone not in pytz.all_timezones:
        return jsonify({'error': 'Invalid timezone'}), 400
     
     if not dnd_end_time or not dnd_end_time or not preferred_timezone:
        return jsonify({'error': 'Missing required fields'}), 400 
    
     try:
          
          user.dnd_start_time = datetime.fromisoformat(dnd_start_time)
          user.dnd_end_time =  datetime.fromisoformat(dnd_end_time)
          user.preffered_timezone = preferred_timezone
          db.session.commit()
          print(user.dnd_end_time)

     except ValueError as e:
          return jsonify({"Error":f"Error {e} occured while updating the user details!"})
     
     return jsonify({"Message":"User details updated!"})

@app.route('/create-meeting',methods=['POST'])
def create_meeting():
     
     data = request.json
    #check if the user exists or not - 
     user = Users.query.get(data['user_id'])

     if not user:
          return jsonify({"error":f"Meeting cannot be scheduled as the User with {data.get('user_id')} does not exists"})
     
     # is data not null and if itsi then returns error
     if not data:
          return jsonify({"error":"Missing Required fields!"})
     
     user_id = data.get('user_id')
     meeting_type = data.get('meeting_type')
     start_time = data.get("start_time")
     end_time = data.get("end_time")
     timezone = data.get("timezone")
     notification_interval = data.get("notification_interval")

     
     if timezone.lower()  == "ist":
          timezone = "Asia/Kolkata"

     if timezone not in pytz.all_timezones:
        return jsonify({'error': 'Invalid timezone'}), 400
     
     if not user_id or not meeting_type or not start_time or not end_time or not timezone or not notification_interval:
          return jsonify({"error":"Missing Required Fields!"}),400
     
     try:
        croniter(notification_interval)
     except ValueError as e:
        return jsonify({"error": "Invalid cron expression"}), 400
     
     try:
        
        if meeting_type.lower() == "online" or meeting_type.lower() == "offline":
            meeting = Meetings(user_id = user_id,meeting_type=meeting_type,start_time=datetime.fromisoformat(start_time),end_time=datetime.fromisoformat(end_time),timezone=timezone,notification_interval=notification_interval)
            db.session.add(meeting)
            db.session.commit()
        else:
            return"Invalid Meeting type if should be either ONLINE or OFFLINE"
        
        scheduler_notification()
        return jsonify({"mesage":"Meeting has been sucessfully scheduled"})
     
     except ValueError as e:
          return f"Error while creating the meet - {e}"    


@app.route("/meetings/<int:user_id>",methods = ['POST'])
def time_slots(user_id):
    data = request.json
    start_time = datetime.fromisoformat(data['start_time'])
    end_time  =  datetime.fromisoformat(data['end_time'])

    #the requested method might contain an offest i.e +0000 etc, so checking is imp
    if start_time.tzinfo is None:
         start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
         end_time = end_time.replace(tzinfo=timezone.utc)    

    if end_time<start_time:
         return jsonify({"error":"Requested end time is invalid!"})
    user = Users.query.get(user_id)
    if not user:
         return jsonify({"error":f"User with User ID {user_id} does not exists!"}),400
    
    user_meetings = Meetings.query.filter_by(user_id = user_id).filter(
         Meetings.start_time >= start_time,
         Meetings.end_time <= end_time
    ).all()


    booked_slots =[]
    free_slots =[]
    current_time = start_time
    print(parser.parse(data['start_time']))
    for meet in user_meetings:
        meet_start = meet.start_time
        meet_end = meet.end_time
        
        #the offset naive error is fixed this way
        if meet_start.tzinfo is None:
            meet_start = meet_start.replace(tzinfo=timezone.utc)
        if meet_end.tzinfo is None:
            meet_end = meet_end.replace(tzinfo=timezone.utc)
        

        if current_time < meet_start:
            free_slots.append({
                'start_time': current_time.isoformat(),
                'end_time': meet_start.isoformat(),
                'duration': int((meet_start - current_time).total_seconds() / 60)
            })

        booked_slots.append({
             'start_time': meet.start_time.isoformat(),
             'end_time': meet.end_time.isoformat(),
             'meeting_type':meet.meeting_type,
             'timezone': meet.timezone
        })


        current_time = meet_end


    if current_time < end_time:
        free_slots.append({
            'start_time': current_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration': int((end_time - current_time).total_seconds() / 60)
        })

    return {"free_slots": free_slots,"booked_slots":booked_slots}
if(__name__ == "__main__"):
    with app.app_context():
        db.create_all()
    app.run()