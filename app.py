import os
from datetime import datetime
import calendar
import itertools

from flask import Flask, session, request, flash, jsonify
from flask import render_template, make_response, redirect, url_for
import requests

from models import db, Person, ButtonPress

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
DB_PATH = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'test.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{0}'.format(DB_PATH)
db.init_app(app)

def init_db():
    with app.app_context():
        db.create_all()

# Login page
@app.route('/', methods=['GET'])
def login():
    return render_template('login.html')

# Check login
@app.route('/', methods=['POST'])
def do_login():
    #db = get_db()
    username = request.form['username']
    password = request.form['password']
    #user = db.execute('SELECT id_person FROM person WHERE username=? AND password=?', [username, password]).fetchone()
    user = Person.query.filter_by(username=username, password=password).first()
    if user is None:
        flash("Invalid Log In")
        return render_template('login.html')
    else:
        session['logged_in'] = True
        session['username'] = username
        session['user_id'] = user.id
        return redirect(url_for('home'))

# Logout Page
@app.route('/logout')
def logout():
    if 'username' not in session:
        return redirect(url_for('login'))
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out')
    return redirect(url_for('login'))
	
# Page for registration
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def do_register():
    #db = get_db()
    username = request.form['username']
    password = request.form['password']
    password2 = request.form['password2']
    #user = db.execute("SELECT * FROM person WHERE username=?", [username])
    #if user != None:
    #    flash("Username is already taken")
    #    return render_template('register.html')
    if password != password2:
        flash('Error - passwords did not match!')
        return render_template('register.html')
    else:
        #db.execute('INSERT INTO person (username, password) VALUES (?, ?)', (username, password))
        #db.commit()
        new = Person(username, password)
        db.session.add(new)
        db.session.commit()
        return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')
 

@app.route('/press', methods=['POST'])
def press():
    user_id = session['user_id']
    user = Person.query.filter_by(id=user_id).first()
    now = datetime.utcnow()
    now_formatted = calendar.timegm(now.timetuple())
    press = ButtonPress(user, now)
    db.session.add(press)
    db.session.commit()
    return jsonify( {"timestamp": now_formatted, "user_id" : user_id})

@app.route('/ajax/data')
def get_data():
    time_stamps = [bp.time_stamp for bp in ButtonPress.query.all()]
    gby = itertools.groupby(time_stamps, lambda x: (x.hour, x.minute))
    data = []
    for item, group in gby:
        items = [item for item in group]
        x = calendar.timegm(items[0].timetuple())*1000
        y = len(items)
        data.append( [x,y] )
    return jsonify({'series': data}) 

@app.route('/plot')
def plot():
    time_stamps = [bp.time_stamp for bp in ButtonPress.query.all()]
    gby = itertools.groupby(time_stamps, lambda x: (x.hour, x.minute))
    data = []
    for item, group in gby:
        items = [item for item in group]
        x = calendar.timegm(items[0].timetuple())*1000
        y = len(items)
        data.append( [x,y] )
    return render_template('plot.html', data=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
