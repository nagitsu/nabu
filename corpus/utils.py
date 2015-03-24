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
