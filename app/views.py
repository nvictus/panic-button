from datetime import datetime
import os
import calendar
import itertools
import requests

from flask import Flask, session, request, flash, jsonify
from flask import render_template, make_response, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required, current_user

from .models import User, ButtonPress
from .forms import SigninForm, RegistrationForm
from . import app, db


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash("Invalid user name", "error")
            return redirect(url_for('signin'))
        if user.check_password(form.password.data):
            login_user(user)
            flash("Signed in successfully.", "success")
            return redirect(request.args.get("next") or url_for("index"))
        else:
            flash("Invalid password", "error")
            return redirect(url_for('signin'))

    return render_template('signin.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        user = User.query.filter_by(username=form.username.data).first()

        if user is not None:
            flash("Username is already taken", "error")
            return render_template('register.html', form=form)

        if password != password2:
            flash("Error - passwords did not match!", "error")
            return render_template('register.html', form=form)

        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('signin'))

    return render_template('register.html', form=form)


@app.route('/signout')
def signout():
    logout_user()
    flash("Signed out successfully", "info")
    return redirect(url_for('signin'))


@app.route('/')
@login_required
def index():
    return render_template('index.html')


# @app.route('/plot')
# def plot():
#     time_stamps = [bp.time_stamp for bp in ButtonPress.query.all()]
#     gby = itertools.groupby(time_stamps, lambda x: (x.hour, x.minute))
#     data = []
#     for item, group in gby:
#         items = [item for item in group]
#         x = calendar.timegm(items[0].timetuple())*1000
#         y = len(items)
#         data.append( [x,y] )
#     return render_template('plot.html', data=data)




@app.route('/panic', methods=['POST'])
def on_press():
    user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()

    now = datetime.utcnow()
    new_press = ButtonPress(user, now)
    db.session.add(new_press)
    db.session.commit()

    now_formatted = calendar.timegm(now.timetuple())*1000
    return jsonify( {"timestamp": now_formatted, "count" : 1} )


@app.route('/panic', methods=['GET'])
def on_data_request():
    # user_id = current_user.id
    # user = User.query.filter_by(id=user_id).first()

    time_stamps = [bp.time_stamp for bp in ButtonPress.query.all()]
    gby = itertools.groupby(time_stamps, lambda x: (x.hour, x.minute))
    series = []
    for item, group in gby:
        items = [item for item in group]
        x = calendar.timegm(items[0].timetuple())*1000
        y = len(items)
        series.append( [x, y] )
    series = sorted(series, key=lambda x: x[0])

    return jsonify({'series': series})





