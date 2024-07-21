class Params:
    """SuperDirt parameters used by this library.

    This library handles only the following values.
    But, other parameters are available. e.g. amp, room.
    See: https://github.com/musikinformatik/SuperDirt/blob/develop/used-parameters.scd
    """

    s = "s"  # sound
    sound = "sound"  # sound="bd:1" equals s="bd" and n=1
    n = "n"  # note
    delta = "delta"  # Time until next event
