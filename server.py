from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import pytz
from dateutil import parser
from datetime import datetime, timezone
from urllib.parse import unquote
from croniter import croniter
from models import db, Users, Meetings
from scheduler import init_scheduler, scheduler_notification

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
db.init_app(app)
migrate = Migrate(app, db)
scheduler = init_scheduler(app)



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
        check_usr = Users.query.filter_by(email=email).first()
        print(check_usr)
        if check_usr is not None:
            return jsonify({"error":"User with email already exists!"})

        user = Users(name = data['name'],email = data['email'],
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
    
     if dnd_end_time<=dnd_start_time:
         return jsonify({'error': 'Invalid time'}), 400
     
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




@app.route('/create-meeting', methods=['POST'])
def create_meeting():
    data = request.json
    if not data:
        return jsonify({"error": "Missing required fields!"}), 400

    user_id = data.get('user_id')
    user = Users.query.get(user_id)
    if not user:
        return jsonify({"error": f"Meeting cannot be scheduled as the User with ID {user_id} does not exist"}), 400

    meeting_type = data.get('meeting_type')
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    timezone_str = data.get("timezone")
    notification_interval = data.get("notification_interval")

    if start_time > end_time:
        return jsonify({"error": "Invalid Time!"}), 400



    if not all([user_id, meeting_type, start_time, end_time, timezone_str, notification_interval]):
        return jsonify({"error": "Missing required fields!"}), 400

    if timezone_str.lower() == "ist":
        timezone_str = "Asia/Kolkata"

    if timezone_str not in pytz.all_timezones:
        return jsonify({'error': 'Invalid timezone'}), 400

    try:
        croniter(notification_interval)
    except ValueError as e:
        return jsonify({"error": "Invalid cron expression"}), 400

    try:
        tz = pytz.timezone(timezone_str)
        
        
        new_start_time = parser.parse(start_time)
        new_end_time = parser.parse(end_time)
        if new_start_time.tzinfo is None:
            new_start_time = tz.localize(new_start_time)
        if new_end_time.tzinfo is None:
            new_end_time = tz.localize(new_end_time)

        new_start_time = new_start_time.astimezone(tz)
        new_end_time = new_end_time.astimezone(tz)

        if new_end_time <= new_start_time:
            return jsonify({"error": "End time must be after start time"}), 400

        conflicting_meet = Meetings.query.filter(
            Meetings.user_id == user_id
        ).filter(
            ((Meetings.start_time <= new_start_time) & (Meetings.end_time > new_start_time)) |
            ((Meetings.start_time < new_end_time) & (Meetings.end_time >= new_end_time)) |
            ((Meetings.start_time >= new_start_time) & (Meetings.end_time <= new_end_time))
        ).first()

        if conflicting_meet:
            return jsonify({"error": "Cannot create a new meeting. There is a scheduling conflict with an existing meeting."}), 400

        if meeting_type.lower() not in ["online", "offline"]:
            return jsonify({"error": "Invalid meeting type. It should be either ONLINE or OFFLINE"}), 400

        meeting = Meetings(
            user_id=user_id,
            meeting_type=meeting_type.lower(),
            start_time=new_start_time,
            end_time=new_end_time,
            timezone=timezone_str,
            notification_interval=notification_interval
        )
        db.session.add(meeting)
        db.session.commit()

        scheduler_notification(app,new_meeting_id=meeting.id)
        return jsonify({"message": "Meeting has been successfully scheduled"}), 201

    except ValueError as e:
        return jsonify({"error": f"Error while creating the meeting: {str(e)}"}), 400




@app.route("/meetings/<int:user_id>", methods=['GET'])
def time_slots(user_id):
    start_time_str = request.args.get('start_time')
    print(start_time_str)
    end_time_str = request.args.get('end_time')
    print(end_time_str)
    if not start_time_str or not end_time_str:
        return jsonify({"error": "Start time and end time are required as query parameters"}), 400

    try:
        start_time = datetime.fromisoformat(unquote(start_time_str))
        end_time = datetime.fromisoformat(unquote(end_time_str))
    except ValueError:
        return jsonify({"error": "Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400

    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)    

    if end_time < start_time:
        return jsonify({"error": "Requested end time is invalid!"})
    
    user = Users.query.get(user_id)
    if not user:
        return jsonify({"error": f"User with User ID {user_id} does not exist!"}), 400
    
    user_meetings = Meetings.query.filter_by(user_id=user_id).filter(
        Meetings.start_time >= start_time,
        Meetings.end_time <= end_time
    ).all()

    booked_slots = []
    free_slots = []
    current_time = start_time

    for meet in user_meetings:
        meet_start = meet.start_time
        meet_end = meet.end_time
        
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
            'meeting_type': meet.meeting_type,
            'timezone': meet.timezone
        })

        current_time = meet_end
 
    if current_time < end_time:
        free_slots.append({
            'start_time': current_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration': int((end_time - current_time).total_seconds() / 60)
        })

    return jsonify({"free_slots": free_slots, "booked_slots": booked_slots})

# I am creating this for docker (as we need to initialise database and create tables in it before running)
def create_tables():
    with app.app_context():
        db.create_all()

if(__name__ == "__main__"):
    with app.app_context():
        db.create_all()
    app.run()