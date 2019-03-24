from datetime import datetime
from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
import json
from pywebpush import webpush, WebPushException
import logging

WEBPUSH_VAPID_PRIVATE_KEY = app.config['WEBPUSH_VAPID_PRIVATE_KEY']

users_trips = db.Table('users_trips',
    db.Column('user', db.Integer, db.ForeignKey('user.id')),
    db.Column('trip', db.Integer, db.ForeignKey('trip.id'))
)

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

notifications_trips = db.Table('notifications_trips',
	db.Column('trip_id', db.Integer, db.ForeignKey('trip.id')),
	db.Column('notification_id', db.Integer, db.ForeignKey('notification.id'))
	)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    passenger_trips = db.relationship('Trip', secondary=users_trips, 
        backref=db.backref('passengers', lazy='select'), lazy='dynamic')
    driver_trips = db.relationship('Trip', backref = 'driver', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    notifications = db.relationship('Notification', backref='recipient', lazy='dynamic')
    last_notification_read_time=db.Column(db.DateTime)
    notices = db.relationship('Notice', backref='user', lazy='dynamic')
    subscribes = db.relationship('Subscribe', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def all_trips(self):
        d_trips = Trip.query.filter_by(driver_id=self.id)
        p_trips = Trip.query.join(users_trips, (users_trips.c.trip == Trip.id)).filter(users_trips.c.user == self.id)
        return p_trips.union(d_trips).order_by(Trip.trip_time.desc())

    def join_as_passenger(self, trip):
        if not self.joined_as_passenger(trip):
            self.passenger_trips.append(trip)

    def leave_as_passenger(self, trip):
    	if self.joined_as_passenger(trip):
    		self.passenger_trips.remove(trip)

    def joined_as_passenger(self, trip):
        return self.passenger_trips.filter(
            users_trips.c.trip == trip.id).count() > 0

    def leave_as_driver(self, trip):
    	if self.joined_as_driver:
    		trip.driver = None

    def joined_as_driver(self, trip):
    	return self == trip.driver\

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def new_notifications(self):
    	last_read_time = self.last_notification_read_time or datetime(1900, 1, 1)
    	return Notification.query.filter_by(user_id=self.id).filter(
    		Notification.timestamp > last_read_time).count()

    def add_notice(self, name, data):
        self.notices.filter_by(name=name).delete()
        n = Notice(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def send_notify(self, text):
        subscribes = self.subscribes.filter_by(is_active=True).all()
        data = json.dumps({
        'title': 'Подвозилки',
        'body': text,
    })
        for subscribe in subscribes:
            try:
                webpush(
                        subscription_info=json.loads(subscribe.subscription_info),
                        data=data,
                        vapid_private_key=WEBPUSH_VAPID_PRIVATE_KEY,
                        vapid_claims={
                            "sub": "mailto:kvyatkovsky@mail.ru"
                        }
                    )
            except WebPushException as ex:
                logging.exception("webpush fail")
                db.session.delete(subscribe)
                db.session.commit()




    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_from = db.Column(db.String(120))
    trip_to = db.Column(db.String(120))
    trip_time = db.Column(db.DateTime, index=True)
    free_seats = db.Column(db.Integer)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    posts = db.relationship('Post', backref='trip', lazy='dynamic')
    comment = db.Column(db.String(120))

    def __repr__(self):
        return '<{} поедет: откуда {}, куда {} в {}>'.format(self.driver_id,
                                                       self.trip_from,
                                                       self.trip_to,
                                                       self.trip_time)

class Notification(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	trip_id = db.Column(db.Integer)
	body = db.Column(db.String(120))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))

class Subscribe(db.Model):
    id = db.Column(db.Integer(), primary_key=True, default=None)
    created = db.Column(db.DateTime())
    modified = db.Column(db.DateTime())
    subscription_info = db.Column(db.Text())
    is_active = db.Column(db.Boolean(), default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def subscription_info_json(self):
        return json.loads(self.subscription_info)

    @subscription_info_json.setter
    def subscription_info_json(self, value):
        self.subscription_info = json.dumps(value)

