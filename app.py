import os
from datetime import datetime
import calendar
import itertools

from flask import Flask, session, request, flash, jsonify
from flask import render_template, make_response, redirect, url_for
import requests

from models import db, Person, Button

app = Flask(__name__)
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
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
    db = get_db()
    username = request.form['username']
    password = request.form['password']
    credentials = db.execute('SELECT id_person FROM person WHERE username=? AND password=?', [username, password]).fetchone()
    if credentials == None:
        flash("Invalid Log In")
        return render_template('login.html')
    else:
        session['logged_in'] = True
        session['username'] = username
        session['user_id'] = credentials[0]
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
    db = get_db()
    username = request.form['username']
    password = request.form['password']
    password2 = request.form['password2']
    user = db.execute("SELECT * FROM person WHERE username=?", [username])
    #if user != None:
    #    flash("Username is already taken")
    #    return render_template('register.html')
    if password != password2:
        flash('Error - passwords did not match!')
        return render_template('register.html')
    else:
        db.execute('INSERT INTO person (username, password) VALUES (?, ?)', (username, password))
        db.commit()
        return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')
 
# Page for users to see their history
@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_id = str(session['user_id'])
    db = get_db()
    cur = db.execute('SELECT * FROM button WHERE trackperson=? ORDER BY id_button', [user_id])
    entries = cur.fetchall()
    return render_template('history.htm', entries=entries)

@app.route('/press', methods=['POST'])
def press():
    #return jsonify({"timestamp": datetime.utcnow()})
    user_id = str(session['user_id'])
    bla = "opi"
    now = datetime.utcnow()
    now_formatted = calendar.timegm(now.timetuple())

    db = get_db()
    db.execute( 'INSERT INTO button(trackperson, time_stamp) VALUES (?,?)', (user_id, now_formatted) )
    db.commit()

    return jsonify( {"timestamp": now_formatted, "user_id" : user_id})

@app.route('/plot')
def plot():
    db = get_db()
    d1 = db.execute('SELECT time_stamp FROM button ORDER BY time_stamp')
    d2 = d1.fetchall()
    d3 = [ datetime.fromtimestamp(int(x[0])) for x in d2 ]
    gby = itertools.groupby(d3, lambda x: (x.hour, x.minute))
    data = []
    for item, group in gby:
        items = [item for item in group]
        x = calendar.timegm(items[0].timetuple())*1000
        y = len(items)
        data.append( [x,y] )
    print data
    #data = [ [int(x[0]),1] for x in d2 ]
    #print data
    #data = [ [[0, 0], [1, 1]] ]
    return render_template('plot.html', data=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
