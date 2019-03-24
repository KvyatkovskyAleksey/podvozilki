from flask import Blueprint

bp = Blueprint('trip', __name__, template_folder='templates')

from app.trip import routes, forms
