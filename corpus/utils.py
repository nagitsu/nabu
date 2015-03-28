import re

from datetime import datetime


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


def was_redirected(response):
    """
    Checks whether the request was redirected to a different article.

    Assumes that the first and final redirection *both* have a numeric ID.
    """
    # Now check if the redirection history changed our ID.
    if response.history:
        original_url = response.history[0].url
        current_url = response.url

        id_regexp = re.compile(r'.*/(\d+)/')
        m_original = id_regexp.match(original_url)
        m_current = id_regexp.match(current_url)

        # No ID on the new URL.
        if not m_current:
            return True

        if m_original and m_current:
            if m_original.group(1) != m_current.group(1):
                return True

    return False
