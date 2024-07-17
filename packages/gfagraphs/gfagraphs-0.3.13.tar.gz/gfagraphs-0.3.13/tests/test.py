from enum import Enum


class Orientation(Enum):
    """Describes the way a node is read. Minus is reversecomp and plus is forward.
    Please refer to http://gfa-spec.github.io/GFA-spec/GFA1.html for examples and full description of the format.

    Parameters
    ----------
    Enum : str
        Could be a GFA-compatible tag (+ or -) or ? to specify 'Any' or = to specify 'both'.
    """
    FORWARD = '+'
    REVERSE = '-'
    ANY = '?'
    BOTH = '='


dic: dict = {Orientation.FORWARD: 'test'}


print(dic[Orientation.FORWARD])
