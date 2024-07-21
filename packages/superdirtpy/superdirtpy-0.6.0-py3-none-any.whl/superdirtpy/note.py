from __future__ import annotations

import random
from enum import IntEnum


class PitchClass(IntEnum):
    C = 0
    Cs = 1
    D = 2
    Ds = 3
    E = 4
    F = 5
    Fs = 6
    G = 7
    Gs = 8
    A = 9
    As = 10
    B = 11

    @classmethod
    def random(cls) -> tuple[str, PitchClass]:
        pitch_classes = []
        for k, v in cls.__members__.items():
            pitch_classes.append((k, v))
        return random.choice(pitch_classes)


class Note:
    def __init__(self, pc: PitchClass, octave: int) -> None:
        midi_number = self.__to_midi_number(pc, octave)

        self.pc = pc
        self.octave = octave
        self.midi_number = midi_number

    def __repr__(self) -> str:
        class_name = type(self).__name__
        return f"{class_name}(pc={self.pc!r}, octave={self.octave!r}, midi_number={self.midi_number!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Note):
            return NotImplemented
        return self.midi_number == other.midi_number

    def __lt__(self, other: Note) -> bool:
        return self.midi_number < other.midi_number

    def __le__(self, other: Note) -> bool:
        return self.midi_number <= other.midi_number

    def __hash__(self) -> int:
        return hash(self.midi_number)

    def transpose(self, n: int) -> Note:
        midi_number = self.midi_number + n
        pc, octave = self.__from_midi_number(midi_number)
        return Note(pc, octave)

    @classmethod
    def __to_midi_number(cls, pc: PitchClass, octave: int) -> int:
        return pc + octave * 12

    @classmethod
    def __from_midi_number(cls, midi_number: int) -> tuple[PitchClass, int]:
        pc = PitchClass(midi_number % 12)
        octave = int(midi_number / 12)
        return pc, octave
