from flask import render_template, flash, redirect, url_for, request, jsonify
from app import db, app
from flask_login import current_user, login_required
from app.models import User, Post, Trip, Notification, Notice
from app.main.forms import EditProfileForm, PostForm, SendFeedbackForm
from werkzeug.urls import url_parse
from datetime import datetime
from app.main import bp
from app.email import send_email

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', form=form,
                            posts=posts.items, next_url=next_url,
                            prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    trips = user.all_trips().order_by(Trip.trip_time.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=trips.next_num) \
        if trips.has_next else None
    prev_url = url_for('main.user', username=user.username, page=trips.prev_num) \
        if trips.has_prev else None
    return render_template('user.html', user=user, trips=trips.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Изменить профиль', form=form)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user=User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('main.user', username=username))

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Обзор', posts=posts.items,
                            next_url=next_url, prev_url=prev_url)

       
@bp.route('/notifications')
@login_required
def notifications():
    current_user.last_notification_read_time = datetime.utcnow()
    current_user.add_notice('unread_notification_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    notifications = current_user.notifications.order_by(
        Notification.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.notifications', page=notifications.next_num) \
        if notifications.has_next else None
    prev_url = url_for('main.notifications', page=notifications.prev_num) \
        if notifications.has_prev else None
    return render_template('notifications.html', notifications=notifications.items,
                            next_url=next_url, prev_url=prev_url)

@bp.route('/notices')
@login_required
def notices():
    since = request.args.get('since', 0.0, type=float)
    notices = current_user.notices.filter(Notice.timestamp > since).order_by(Notice.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
        } for n in notices])

@bp.route('/sw.js', methods=['GET'])
def sw():
    return app.send_static_file('sw.js')

@bp.route('/options', methods=['GET', 'POST'])
@login_required
def options():
    return render_template('options.html', title="Настройки")

@bp.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    form = SendFeedbackForm();
    if form.validate_on_submit():
        send_email('Отзыв',
                sender=app.config['ADMINS'][0],
                recipients=['kvyatkovsky@mail.ru'],
                text_body='Отправитель:{}, текст:{}'.format(current_user.email, form.body.data),
                html_body='Отправитель:{}, текст:{}'.format(current_user.email, form.body.data))
        flash('Ваше сообщение отправлено')
        return redirect(url_for('main.index'))
    return render_template('feedback.html', form=form)
