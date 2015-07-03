# coding: utf-8
import asyncio
import functools
import re
import requests

from datetime import datetime

from dateutil.parser import parse, parserinfo

from nabu.core import settings


@asyncio.coroutine
def get(*args, **kwargs):
    """
    Performs a request in an asyncio-aware manner using the `requests` library.
    """
    loop = asyncio.get_event_loop()
    with (yield from loop.request_semaphore):
        make_request = functools.partial(requests.get, *args, **kwargs)
        future = asyncio.wait_for(
            loop.run_in_executor(None, make_request),
            settings.REQUEST_TIMEOUT
        )
        return (yield from future)


def custom_encoder(obj):
    """
    Custom encoder for `json` module in order to serialize datetimes into
    seconds since Unix Epoch Time.
    """
    if isinstance(obj, datetime):
        epoch = datetime(1970, 1, 1)
        # TODO: Manage TZ info correctly; we're just removing it for now.
        since_epoch = obj.replace(tzinfo=None) - epoch.replace(tzinfo=None)
        return since_epoch.total_seconds()
    else:
        msg = "Object of type {} with value of {} is not JSON serializable"
        raise TypeError(msg.format(type(obj), repr(obj)))


def was_redirected(response, regexp=r'.*/(\d+)/'):
    """
    Checks whether the request was redirected to a different article.

    Assumes that the first and final redirection *both* have a numeric ID.
    """
    # Now check if the redirection history changed our ID.
    if response.history:
        original_url = response.history[0].url
        current_url = response.url

        id_regexp = re.compile(regexp)
        m_original = id_regexp.match(original_url)
        m_current = id_regexp.match(current_url)

        # No ID on the new URL.
        if not m_current:
            return True

        if m_original and m_current:
            if m_original.group(1) != m_current.group(1):
                return True

    return False


class CustomParser(parserinfo):
    JUMP = [
        " ", ".", ",", ";", "-", "/", "'", "|",
        "at", "on", "and", "ad", "m", "t", "of",
        "st", "nd", "rd", "th",
        "y", "el", "a", "las", "de", "del",
    ]

    WEEKDAYS = [
        ("Mon", "Monday", "Lun", "Lunes"),
        ("Tue", "Tuesday", "Martes"),
        ("Wed", "Wednesday", "Mie", "Miercoles", u"Mié", u"Miércoles"),
        ("Thu", "Thursday", "Jue", "Jueves"),
        ("Fri", "Friday", "Vie", "Viernes"),
        ("Sat", "Saturday", "Sab", "Sabado", u"Sáb", u"Sábado"),
        ("Sun", "Sunday", "Dom", "Domingo")
    ]

    MONTHS = [
        ("Jan", "January", "Ene", "Enero"),
        ("Feb", "February", "Febrero"),
        ("Mar", "March", "Marzo"),
        ("Apr", "April", "Abr", "Abril"),
        ("May", "May", "Mayo"),
        ("Jun", "June", "Junio"),
        ("Jul", "July", "Julio"),
        ("Aug", "August", "Ago", "Agosto"),
        ("Sep", "Sept", "September", "Set", "Setiembre", "Septiembre"),
        ("Oct", "October", "Octubre"),
        ("Nov", "November", "Noviembre"),
        ("Dec", "December", "Dic", "Diciembre")
    ]

    HMS = [
        ("h", "hour", "hours", "hrs", "hs"),
        ("m", "minute", "minutes"),
        ("s", "second", "seconds")
    ]

    AMPM = [
        ("am"),
        ("pm")
    ]

    UTCZONE = ["UTC", "GMT", "Z"]

    PERTAIN = ["of", "de", "del"]


def parse_date(text):
    """
    Uses a localized version of the python-dateutil library to parse a date.

    Note that it's not perfect; it still needs some help to reduce the search
    string as much as possible beforehand.
    """
    parser = CustomParser(dayfirst=True, yearfirst=True)
    try:
        date = parse(text, parserinfo=parser, fuzzy=True)
    except:
        date = None
    return date
