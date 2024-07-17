from datetime import datetime, timezone


def log(message: str, *args):
    return  # no logging
    """Prints a message with some extra information."""
    now = datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()
    extra = (
        "\n".join(["", *[str(arg) for arg in args]]).replace("\n", "\n | ")
        if len(args) > 0
        else ""
    )
    print("%s -- %s %s" % (now, message, extra))
