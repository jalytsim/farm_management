"""Serialized IDs: WR-00001, W-00007, B-00012…

The number is the row's primary key, zero-padded. Unique by construction, with
no counter table and no race condition between two simultaneous inserts.
"""

SERIAL_WIDTH = 5


def serial_from_id(prefix, id_, width=SERIAL_WIDTH):
    """serial_from_id('WR-', 7) -> 'WR-00007'"""
    if id_ is None:
        raise ValueError("The row has no id yet: call db.session.flush() first.")
    return f"{prefix}{id_:0{width}d}"