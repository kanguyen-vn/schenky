from enum import Enum


class Clef(Enum):
    TREBLE = 0
    BASS = 1


class NoteType(Enum):
    BLACK = 0
    URLINIE = 1
    SKIP = 2


class VoiceType(Enum):
    MAIN = 0
    URLINIE = 1
    BEAM_LEFT = 2
    BEAM_RIGHT = 3
    SLURS = 4
    UNFOLDINGS = 5
    STEMS = 6


class StemType(Enum):
    QUARTER = 0
    EIGHTH = 1


Accidental = {
    "double_flat": -2,
    "bb": -2,
    "flat": -1,
    "b": -1,
    "natural": 0,
    "n": 0,
    "sharp": 1,
    "#": 1,
    "double_sharp": 2,
    "x": 2
}


NoteName = {
    "f": 0,
    "c": 1,
    "g": 2,
    "d": 3,
    "a": 4,
    "e": 5,
    "b": 6
}


NoteValue = {
    "c": 0,
    "d": 2,
    "e": 4,
    "f": 5,
    "g": 7,
    "a": 9,
    "b": 11
}


MajorAccidentals = {
    "c_flat": [-1, -1, -1, -1, -1, -1, -1],
    "g_flat": [0, -1, -1, -1, -1, -1, -1],
    "d_flat": [0, 0, -1, -1, -1, -1, -1],
    "a_flat": [0, 0, 0, -1, -1, -1, -1],
    "e_flat": [0, 0, 0, 0, -1, -1, -1],
    "b_flat": [0, 0, 0, 0, 0, -1, -1],
    "f": [0, 0, 0, 0, 0, 0, -1],
    "c": [0, 0, 0, 0, 0, 0, 0],
    "g": [1, 0, 0, 0, 0, 0, 0],
    "d": [1, 1, 0, 0, 0, 0, 0],
    "a": [1, 1, 1, 0, 0, 0, 0],
    "e": [1, 1, 1, 1, 0, 0, 0],
    "b": [1, 1, 1, 1, 1, 0, 0],
    "f_sharp": [1, 1, 1, 1, 1, 1, 0],
    "c_sharp": [1, 1, 1, 1, 1, 1, 1],
}


MinorAccidentals = {
    "a_flat": [-1, -1, -1, -1, -1, -1, -1],
    "e_flat": [0, -1, -1, -1, -1, -1, -1],
    "b_flat": [0, 0, -1, -1, -1, -1, -1],
    "f": [0, 0, 0, -1, -1, -1, -1],
    "c": [0, 0, 0, 0, -1, -1, -1],
    "g": [0, 0, 0, 0, 0, -1, -1],
    "d": [0, 0, 0, 0, 0, 0, -1],
    "a": [0, 0, 0, 0, 0, 0, 0],
    "e": [1, 0, 0, 0, 0, 0, 0],
    "b": [1, 1, 0, 0, 0, 0, 0],
    "f_sharp": [1, 1, 1, 0, 0, 0, 0],
    "c_sharp": [1, 1, 1, 1, 0, 0, 0],
    "g_sharp": [1, 1, 1, 1, 1, 0, 0],
    "d_sharp": [1, 1, 1, 1, 1, 1, 0],
    "a_sharp": [1, 1, 1, 1, 1, 1, 1],
}


KeyCode = {
    "c_flat": "ces",
    "g_flat": "ges",
    "d_flat": "des",
    "a_flat": "aes",
    "e_flat": "ees",
    "b_flat": "bes",
    "f": "f",
    "c": "c",
    "g": "g",
    "d": "d",
    "a": "a",
    "e": "e",
    "b": "b",
    "f_sharp": "fis",
    "c_sharp": "cis",
    "g_sharp": "gis",
    "d_sharp": "dis",
    "a_sharp": "ais"
}
