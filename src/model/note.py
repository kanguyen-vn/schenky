from .skip import Skip
from .constants import NoteType, NoteValue, VoiceType


class Note:
    def __init__(self, name, accidental, register, in_main_voice, note_type=NoteType.BLACK, duration=4, scale_degree=0):
        self.name = name
        self.accidental = accidental
        self.register = register
        self.duration = duration
        self.in_main_voice = in_main_voice
        self.note_type = note_type
        self.scale_degree = scale_degree
        self.slurs = []
        self.unfoldings = []
        self.stem = None

    def __str__(self):
        qualities = ["bb", "b", "", "#", "##"]
        return f"{self.name.upper()}{qualities[self.accidental + 2]}{self.register}"

    def __eq__(self, other):
        return self is other

    def __gt__(self, other):
        self_value = NoteValue[self.name] + \
            self.accidental + 12 * self.register
        other_value = NoteValue[other.name] + \
            other.accidental + 12 * other.register
        return self_value > other_value

    def updateNote(self, name, accidental, register=None):
        self.name = name
        self.accidental = accidental
        if register:
            self.register = register

    def code(self, voice_type, duration=None):
        if voice_type == VoiceType.MAIN and self.note_type == NoteType.URLINIE:
            return "s4"
        qualities = ["eses", "es", "", "is", "isis"]
        if self.register > 3:
            register = "".join(["'" for _ in range(self.register - 3)])
        else:
            register = "".join(["," for _ in range(3 - self.register)])
        if not duration:
            if voice_type == VoiceType.SLURS:
                duration = 4
            else:
                duration = self.duration
        return f"{self.name}{qualities[self.accidental + 2]}{register}{duration}"

    def make_urlinie(self, scale_degree=0):
        self.note_type = NoteType.URLINIE
        self.duration = 2
        self.scale_degree = scale_degree
