import datetime
from flask import jsonify, request
from app import app, db
from app.models import User, Subscribe
from app.api import bp
from flask_login import current_user, login_required
from pywebpush import webpush, WebPushException
import json

WEBPUSH_VAPID_PRIVATE_KEY = app.config['WEBPUSH_VAPID_PRIVATE_KEY']

@bp.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    data = request.get_json('subscription_info')
    # if is_active=False == unsubscribe
    subscription_info = request.json.get('subscription_info')
    is_active = request.json.get('is_active')
    subscription_info = json.dumps(subscription_info)

    try:
        deactivated = Subscribe.query.filter(Subscribe.is_active == 0).first()
        db.session.delete(deactivated)
        db.session.commit
    except:
        print("User have not deactivated subscription")

    # we assume subscription_info shall be the same
    item = Subscribe.query.filter(Subscribe.subscription_info == subscription_info).first()

    if not item:
        item = Subscribe()
        item.created = datetime.datetime.utcnow()
        item.subscription_info = subscription_info
        item.user_id = current_user.id

    item.is_active = is_active
    item.modified = datetime.datetime.utcnow()
    db.session.add(item)
    db.session.commit()

    return jsonify({ 'id': item.id })

@bp.route('/notify')
def notify():
    items = Subscribe.query.filter(Subscribe.is_active == True).all()
    count = 0
    for _item in items:
        try:
            webpush(
                    subscription_info=json.loads(_item.subscription_info),
                    data="Test 123",
                    vapid_private_key=WEBPUSH_VAPID_PRIVATE_KEY,
                    vapid_claims={
                        "sub": "mailto:kvyatkovsky@mail.ru"
                    }
                )
            count += 1
        except WebPushException as ex:
            logging.exception("webpush fail")


    return "{} notification(s) sent".format(count)