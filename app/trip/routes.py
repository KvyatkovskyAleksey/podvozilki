from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.main import bp
from flask_login import current_user, login_required
from app.models import Post, Trip, Notification
from app.trip import bp
from app.trip.forms import MakeTripForm , FilterForm, PassengerCountForm
from datetime import datetime
from app.main.forms import PostForm

#дельта времени для utc
delta = datetime.now() - datetime.utcnow()


@bp.route('/make_trip', methods=['GET', 'POST'])
@login_required
def make_trip():
    form = MakeTripForm()
    passenger = current_user
    if form.validate_on_submit():
        if form.driver_or_passenger.data == 'value2':
            trip = Trip(trip_from=form.trip_from.data, trip_to=form.trip_to.data, 
                    trip_time=form.trip_time.data-delta, free_seats=form.free_seats.data, 
                    passengers=[passenger], comment=form.comment.data )
            db.session.add(trip)
            db.session.commit()
            flash('Поездка создана')
        else:
            trip = Trip(trip_from=form.trip_from.data, trip_to=form.trip_to.data, 
                    trip_time=form.trip_time.data-delta, free_seats=form.free_seats.data,
                    driver_id = current_user.id, comment=form.comment.data)
            db.session.add(trip)
            db.session.commit()
            flash('Поездка создана')
            return redirect(url_for('trip.trip', trip_id=trip.id))
    return render_template('trip/make_trip.html', title='Создать поездку', form=form)

@bp.route('/my_trips')
@login_required
def my_trips():
    trips = current_user.all_trips()
    return render_template('trip/index.html', title='Мои поездки', trips=trips)
    
@bp.route('/<trip_id>', methods=['GET', 'POST'])
@login_required
def trip(trip_id):
    user = current_user
    trip = Trip.query.filter_by(id=trip_id).first_or_404()
    form = PostForm()
    if form.validate_on_submit():
        post=Post(author=current_user, trip_id=trip.id, body=form.post.data)
        db.session.add(post)
        db.session.commit()
        flash('Сообщение отправлено.')
        if trip.driver and trip.driver!=current_user:
            trip.driver.send_notify("У Вас новое сообщение")
            notification = Notification(body='{} написал новое сообщение'.format(current_user.username), user_id = trip.driver_id, trip_id = trip.id)
            db.session.add(notification)
            db.session.commit()
            trip.driver.add_notice('unread_notification_count', trip.driver.new_notifications())
            db.session.commit()
        if trip.passengers:
            for passenger in trip.passengers:
                if passenger != current_user:
                    passenger.send_notify("У вас новое сообщение")
                    notification = Notification(body='{} написал новое сообщение'.format(current_user.username), user_id = passenger.id, trip_id = trip.id)
                    db.session.add(notification)
                    db.session.commit()
                    passenger.add_notice('unread_notification_count', passenger.new_notifications())
                    db.session.commit()
        return redirect(url_for('trip.trip', trip_id=trip.id))
    count_form = PassengerCountForm()
    if count_form.validate_on_submit():
        p = 0
        for passenger in trip.passengers:
            p +=1
        trip.free_seats=count_form.free_seats.data-p
        if trip.free_seats < 0:
            flash('Вы не можете сделать количество свободных мест меньше чем пассажиров в поездке.')
        else:
            db.session.commit()
    page = request.args.get('page', 1, type=int)
    posts = trip.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('trip.trip', page=posts.next_num, trip_id=trip.id) \
        if posts.has_next else None
    prev_url = url_for('trip.trip', page=posts.prev_num, trip_id=trip.id) \
        if posts.has_prev else None
    return render_template('trip/trip.html', title='Детали поездки', trip=trip, user=user, form=form, count_form=count_form, posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    trips = Trip.query.order_by(Trip.trip_time.desc()).paginate(
        page, app.config['TRIPS_PER_PAGE'], False)
    next_url = url_for('trip.explore', page=trips.next_num) \
        if trips.has_next else None
    prev_url = url_for('trip.explore', page=trips.prev_num) \
        if trips.has_prev else None
    return render_template('trip/index.html', title='Обзор', trips=trips.items, 
                            next_url=next_url, prev_url=prev_url)

@bp.route('/trip_filter', methods=['GET','POST'])
@login_required
def trip_filter():
    form=FilterForm()
    if form.validate_on_submit():
        start_time = form.trip_start_filter.data
        # func.lower made lower register
        # ilike - filter without rergister
        if form.driver_or_passenger.data == 'value1':
            trips = Trip.query.filter(Trip.trip_from.ilike('%{}%'.format(form.trip_from_filter.data))).filter(
                Trip.trip_to.ilike('%{}%'.format(form.trip_to_filter.data))).filter(
                (Trip.trip_time) >= start_time-delta).filter(
                Trip.free_seats >= form.free_seats_filter.data).all()
        else:
            trips = Trip.query.filter(Trip.trip_from.ilike('%{}%'.format(form.trip_from_filter.data))).filter(
                Trip.trip_to.ilike('%{}%'.format(form.trip_to_filter.data))).filter(
                Trip.trip_time >= form.trip_start_filter.data-delta).filter(
                Trip.free_seats >= form.free_seats_filter.data).filter(
                Trip.driver==None).all()
        return render_template('trip/index.html', title='Обзор', trips = trips)
    return render_template('trip/trip_filter.html', title='Обзор', form=form, delta=delta)


@bp.route('/passenger_join/<trip_id>', methods=['GET','POST'])
@login_required
def passenger_join(trip_id):
    user = current_user
    trip=Trip.query.filter_by(id=trip_id).first()
    if trip is None:
        flash('Такой поездки не существует.')
        return redirect(url_for('trip.explore'))
    if trip.free_seats<1:
        flash('Свободных мест нет.')
        return redirect(url_for('trip.trip', trip_id=trip.id))
    if user.joined_as_driver(trip):
        flash('Вы уже присоединились к поездке как водитель.')
        return redirect(url_for('trip.trip', trip_id=trip.id))
    if user.joined_as_passenger(trip):
        flash('Вы уже присоединились к поездке.')
        return redirect(url_for('trip.trip', trip_id=trip.id))
    if trip.driver:
        trip.driver.send_notify("К вашей поездке присоединился пассажир")
        notification = Notification(body='Пассажир {} присоединился к поездке от {} в {}'.format(current_user.username, trip.trip_from, (trip.trip_time+delta).strftime("%H:%M %d-%m-%Y")), user_id = trip.driver_id, trip_id = trip.id)
        db.session.add(notification)
        db.session.commit()
        trip.driver.add_notice('unread_notification_count', trip.driver.new_notifications())
        db.session.commit()
    if trip.passengers:
        for passenger in trip.passengers:
            passenger.send_notify("К вашей поездке присоединился пассажир")
            notification = Notification(body='Пассажир {} присоединился к поездке {} в {}'.format(current_user.username, trip.trip_from, (trip.trip_time+delta).strftime("%H:%M %d-%m-%Y")), user_id = passenger.id, trip_id = trip.id)
            db.session.add(notification)
            db.session.commit()
            passenger.add_notice('unread_notification_count', passenger.new_notifications())
            db.session.commit()
    user.join_as_passenger(trip)
    trip.free_seats -= 1
    db.session.commit()
    flash('Вы присоединились к поездке')
    return redirect(url_for('trip.trip', trip_id=trip.id))

@bp.route('/passenger_leave/<trip_id>', methods=['GET','POST'])
@login_required
def passenger_leave(trip_id):
    user = current_user
    trip=Trip.query.filter_by(id=trip_id).first()
    if trip is None:
        flash('Такой поездки не существует.')
        return redirect(url_for('trip.explore'))
    if not user.joined_as_passenger(trip):
        flash('Вы ещё не присоединялись к этой поездке.')
        return redirect(url_for('trip.trip', trip_id=trip.id))
    user.leave_as_passenger(trip)
    trip.free_seats += 1
    db.session.commit()
    if trip.driver:
        trip.driver.send_notify("Вашу поездку покинул пассажир")
        notification = Notification(body='Пассажир {} покинул поездку от {} в {}'.format(current_user.username, trip.trip_from, (trip.trip_time+delta).strftime("%H:%M %d-%m-%Y")),
                                    user_id = trip.driver_id, trip_id = trip.id)
        db.session.add(notification)
        db.session.commit()
        trip.driver.add_notice('unread_notification_count', trip.driver.new_notifications())
        db.session.commit()
    if trip.passengers:
        for passenger in trip.passengers:
            passenger.send_notify("Вашу поездку покинул пассажир")
            notification = Notification(body='Пассажир {} покинул поездку от {} в {}'.format(current_user.username, trip.trip_from, (trip.trip_time+delta).strftime("%H:%M %d-%m-%Y")), user_id = passenger.id, trip_id = trip.id)
            db.session.add(notification)
            db.session.commit()
            passenger.add_notice('unread_notification_count', passenger.new_notifications())
            db.session.commit()
    flash('Вы покинули поездку')
    if not trip.driver_id and not trip.passengers:
        db.session.delete(trip)
        db.session.commit()
        return redirect(url_for('trip.explore'))
    return redirect(url_for('trip.trip', trip_id=trip.id))

@bp.route('/driver_join/<trip_id>', methods=['GET','POST'])
@login_required
def driver_join(trip_id):
    user = current_user
    trip=Trip.query.filter_by(id=trip_id).first()
    if trip is None:
        flash('Такой поездки не существует.')
        return redirect(url_for('trip.explore'))
    if trip.driver is not None:
        flash('У данной поездки уже есть водитель.')
        return redirect(url_for('trip.trip', trip_id=trip.id))
    if user.joined_as_driver(trip):
        flash('Вы уже присоединились к поездке.')
        return redirect(url_for('trip.trip', trip_id=trip.id))
    if user.joined_as_passenger(trip):
        flash('Вы уже присоедились к поездке как пассажир.')
        return redirect(url_for('trip.trip', trip_id=trip.id))
    if trip.passengers:
        for passenger in trip.passengers:
            passenger.send_notify("К вашей поездке присоединился водитель")
            notification = Notification(body='Водитель {} присоединился к поездке {} в {}'.format(current_user.username, trip.trip_from, (trip.trip_time+delta).strftime("%H:%M %d-%m-%Y")), user_id = passenger.id, trip_id = trip.id)
            db.session.add(notification)
            db.session.commit()
            passenger.add_notice('unread_notification_count', passenger.new_notifications())
            db.session.commit()
    trip.driver = user
    db.session.add(trip)
    db.session.commit()
    flash('Вы присоединились к поездке')
    return redirect(url_for('trip.trip', trip_id=trip.id))

@bp.route('/driver_leave/<trip_id>', methods=['GET','POST'])
@login_required
def driver_leave(trip_id):
    user = current_user
    trip=Trip.query.filter_by(id=trip_id).first()
    if trip is None:
        flash('Такой поездки не существует.')
        return redirect(url_for('trip.explore'))
    if not user.joined_as_driver(trip):
        flash('Вы ещё не присоединялись к этой поездке.')
        return redirect(url_for('trip.trip', trip_id=trip.id))
    user.leave_as_driver(trip)
    if trip.passengers:
        for passenger in trip.passengers:
            passenger.send_notify("Вашу поездку покинул водитель")
            notification = Notification(body='Водитель {} покинул поездку от {} в {}'.format(current_user.username, trip.trip_from, (trip.trip_time+delta).strftime("%H:%M %d-%m-%Y")), user_id = passenger.id, trip_id = trip.id)
            db.session.add(notification)
            db.session.commit()
            passenger.add_notice('unread_notification_count', passenger.new_notifications())
            db.session.commit()
    db.session.add(trip)
    db.session.commit()
    flash('Вы покинули поездку')
    if not trip.driver_id and not trip.passengers:
        db.session.delete(trip)
        db.session.commit()
        return redirect(url_for('trip.explore'))
    return redirect(url_for('trip.trip', trip_id=trip.id))




