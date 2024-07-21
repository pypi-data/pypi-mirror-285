import copy
from datetime import timedelta

from .params import Params
from .superdirt_client import SuperDirtClient
from .temporal_context import TemporalContext


class Pattern:
    def __init__(self, client: SuperDirtClient, params: dict) -> None:
        Event.validate(params)
        params_list = self.__prepare(params)
        events_list = self.__make_events_list(params_list)

        self.client = client
        self.events_list = events_list

    def __prepare(self, params: dict) -> list[dict]:
        longest = 0
        params2 = {}
        for k, v in params.items():
            if not isinstance(v, list):
                v = [v]
            if len(v) > longest:
                longest = len(v)
            params2[k] = v

        params_list = []
        for i in range(longest):
            params3 = {}
            for k, v in params2.items():
                params3[k] = v[i % len(v)]
            params_list.append(params3)
        return params_list

    def __make_events_list(
        self, params_list: list[dict]
    ) -> list[tuple[timedelta, list[dict]]]:
        events_list = []
        for params in params_list:
            delta = timedelta(seconds=params[Params.delta])
            events = Event.make_events(params)
            events_list.append((delta, events))
        return events_list

    def play(self, tctx: TemporalContext) -> None:
        for delta, events in self.events_list:
            for event in events:
                self.client.send(event, tctx.now(), tctx.is_dryrun())
            tctx.sleep(delta)


class Event:
    @classmethod
    def validate(cls, params: dict) -> None:
        if Params.s not in params and Params.sound not in params:
            raise ValueError(
                f"{Params.s} or {Params.sound} is required, params={params}"
            )
        if Params.delta not in params:
            raise ValueError(f"{Params.delta} is required, params={params}")

    @classmethod
    def make_events(cls, params: dict) -> list[dict]:
        # rest note
        s = params.get(Params.s)
        sound = params.get(Params.sound)
        if s is None and sound is None:
            return []

        # chord
        n = params.get(Params.n)
        chord = []
        if n is not None and isinstance(n, list):
            for note in params[Params.n]:
                note_params = copy.deepcopy(params)
                note_params[Params.n] = note
                chord.append(note_params)
            return chord

        # single note
        return [params]
