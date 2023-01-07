from datetime import datetime, date, timedelta
import re


def get_elapsed_date_from_now(reference_datetime):
    now_datetime = datetime.now()
    delta = now_datetime - reference_datetime
    return delta.days


def get_now_text():
    return datetime_to_text(datetime.now())


def get_today_text():
    return date_to_text(date.today())


def get_yesterday_text():
    yesterday = date.today() - timedelta(days=1)
    return date_to_text(yesterday)


def text_to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date()


def date_to_text(date_obj):
    return date_obj.strftime("%Y-%m-%d")


def text_to_datetime(datetime_str):
    datetime_str = re.sub(r".\d\d\d\d\d\d+$", "", datetime_str)
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")


def datetime_to_text(datetime_obj, ignore_none=True, return_for_none=None):
    """
    If ignore_none == True then returns value 'return_for_none' if datetime_obj is None
    """
    if ignore_none:
        if datetime_obj is None:
            return return_for_none

    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")


def date_obj_unk_to_text(date_obj_or_str):
    """
    Allows to convert datetime, date or str => string
    """
    date_str = date_obj_or_str
    if type(date_obj_or_str) is date:
        date_str = date_to_text(date_obj_or_str)
    elif type(date_obj_or_str) is datetime:
        date_str = date_to_text(datetime.date(date_obj_or_str))
    return date_str
