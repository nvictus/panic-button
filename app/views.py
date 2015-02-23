from datetime import datetime
import os
import calendar
import itertools
import requests

from flask import Flask, session, request, flash, jsonify
from flask import render_template, make_response, redirect, url_for
from flask.ext.login import login_user, logout_user, login_required, current_user

from .models import User, Room, Guest, Panic
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
            Room.query.filter_by(name='default').first().add_guest(user)

            flash("Signed in successfully.", "success")
            return redirect(form.next.data or url_for("index"))
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
    for g in Guest.query.filter_by(user_id=current_user.id):
        g.leave_room()
    logout_user()
    flash("Signed out successfully", "info")
    return redirect(url_for('signin'))


# Rely on /, which will redirect to appropriate place:
#   - signin if not logged in
#   - guest page if a guest
#   - admin page if an admin
@app.route('/')
@login_required
def index():
    return render_template('index.html')




# CRUD routes

@app.route('/panic', methods=['POST'])
def on_press():
    user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()
    room = Room.query.filter_by(name='default').first()

    now = datetime.utcnow()
    new_press = Panic(user, room, now)
    db.session.add(new_press)
    db.session.commit()

    now_formatted = calendar.timegm(now.timetuple())*1000
    return jsonify( {"timestamp": now_formatted, "count" : 1} )


@app.route('/panic', methods=['GET'])
def on_data_request():
    user_id = current_user.id
    room_id = Room.query.filter_by(name='default').first().id
    guest = Guest.query.filter_by(user_id=user_id, room_id=room_id).first()
    times = [p.time_stamp for p in Panic.query.filter_by(guest=guest)]

    gby = itertools.groupby(times, lambda x: (x.hour, x.minute))
    series = []
    for item, group in gby:
        items = [item for item in group]
        x = calendar.timegm(items[0].timetuple())*1000
        y = len(items)
        series.append( [x, y] )
    series = sorted(series, key=lambda x: x[0])

    return jsonify( {'series': series} )


# New CRUD API

# Resource: PANIC
# create: /guest/rooms/<room_id> POST : sign user into room
# read:   /guest/rooms/<room_id> GET : goes to guest view
# create: /guest/rooms/<room_id>/panics POST : guest sends new panic
# read:   /guest/rooms/<room_id>/panics GET  : guest retrieves panics
#   params: since, until, window
#   returns: list of time_stamps

# Resource: ROOM
# create: /admin/rooms POST : create new room and become admin
# read:   /admin/rooms/<room_id> GET : goes to room dashboard
# read:   /admin/rooms/<room_id>/panics GET : retieve panics from all users, aggregated
#   params: since, until, window
#   returns: list of (time_stamp, count)


# These are resource routes that return json: no redirects, no html
# On fail: send error json

# @app.route('/guest/<room_id>', methods=['GET', 'POST'])
# def guest_room(room_id):
#     if method == POST:
#         if user is already a guest/admin of a room -> fail
#         else join user to room
#         return confirmation
#     if method == GET:
#         if user is not a guest of this room -> fail
#         else return room info

# @app.route('/guest/<room_id>/panics', methods=['GET', 'POST'])
# def guest_panic(room_id):
#     if method == POST:
#         if user is not a guest of this room -> fail
#         else add a panic to this room
#         return confirmation
#     if method == GET:
#         if user is not a guest of this room -> fail
#         else query this user's past panics (see get params)
#         return results

# @app.route('/admin', methods=['POST'])
# def create_room():
#     if user is already a guest/admin of a room -> fail
#     else create new room and make user admin
#     return confirmation with room_id

# @app.route('/admin/<room_id>', methods=['GET'])
# def admin_room(room_id):
#     if user is not admin of this room -> fail
#     else return room info

# @app.route('/admin/<room_id>/panics', methods=['GET'])
# def get_panics(room_id):
#     if user is not admin of this room -> fail
#     else query and return aggregated panic counts (see get params)






