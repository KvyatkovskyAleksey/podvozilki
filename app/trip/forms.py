from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, BooleanField, RadioField
from wtforms.fields.html5 import DateTimeLocalField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from app.models import User, Trip
from datetime import datetime

# string to datetime i
def str_date(string):
    sec = ':1'
    string = string + sec
    date = datetime.strptime(string, '%d.%m.%Y %H:%M')
    return date

class MakeTripForm(FlaskForm):
    trip_from = StringField('Откуда', validators=[DataRequired()])
    trip_to = StringField('Куда', validators=[DataRequired()])
    trip_time = DateTimeField('Во сколько', validators=[DataRequired()], id='datepick', format = '%d.%m.%Y %H:%M')
    free_seats = IntegerField('Количество свободных мест', default=1,validators=[DataRequired(), NumberRange(min=1, max=4)])
    comment = StringField('Комментарий')
    driver_or_passenger = RadioField('Label', choices=[('value1','Я водитель'),('value2','Я пассажир')], default='value1',validators=[DataRequired()])
    submit = SubmitField('Поехали!')

class FilterForm(FlaskForm):
    trip_from_filter = StringField('Откуда')
    trip_to_filter = StringField('Куда')
    trip_start_filter = DateTimeField('Начало интервала', id='datepick', format='%d.%m.%Y %H:%M')
    trip_end_filter = DateTimeField('Конец интервала', id='datepick2', format='%d.%m.%Y %H:%M')
    free_seats_filter = IntegerField('Количество свободных мест', default=1, validators=[NumberRange(min=1, max=4)])
    driver_or_passenger = RadioField('Label', choices=[('value1','Я пассажир'),('value2','Я водитель')], default='value1',validators=[DataRequired()])
    submit = SubmitField('Найти поездки')

class PassengerCountForm(FlaskForm):
    free_seats = IntegerField('Изменить количество мест', default=1, validators=[DataRequired(), NumberRange(min=1, max=4)])
    submit = SubmitField('Изменить')
