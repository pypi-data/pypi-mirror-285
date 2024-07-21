# superdirtpy
superdirtpy is a client library for Super Dirt written in python.

## features
- timing control
- no framework or DSL
- can be used for algorithmic composition, live coding, integration with python libraries such as numpy and scipy and developing tools for your own use.

## prerequisite
Install Tidal Cycles. Especially Super Dirt.  
https://tidalcycles.org/

## examples
```py
import logging

import numpy as np

import superdirtpy as sd

rng = np.random.default_rng()
client = sd.SuperDirtClient()
p = {"s": "mydevice", "midichan": 0}


def main():
    tctx = sd.TemporalContext()
    scale = sd.Scale(sd.PitchClass.C, sd.Scales.messiaen3)
    for _ in range(16):
        n = rng.integers(1, 5, endpoint=True)
        chord = rng.choice(10, n, replace=False).tolist()
        chord = scale.bind(degrees=chord)
        params = p | {
            "n": [chord],
            "amp": rng.uniform(0.4, 0.9),
            "delta": rng.uniform(0.8, 2.0),
        }
        sd.Pattern(client=client, params=params).play(tctx)


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.DEBUG)
        main()
    except KeyboardInterrupt:
        pass
```
See more [examples](./examples/).

## parameters
This library internally handles only `s`, `sound`, `n`, and `delta`, but you can also use parameters such as `amp` and `room`. ([source](./superdirtpy/params.py))
