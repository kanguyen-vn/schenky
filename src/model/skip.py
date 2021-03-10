from .constants import NoteType


class Skip:
    def __init__(self, duration=4):
        self.duration = duration
        self.note_type = NoteType.SKIP
        self.slurs = []
        self.unfoldings = []
        self.stem = None

    def code(self, in_main_voice):
        return f"s{self.duration}"

    def __str__(self):
        # return f"S{self.duration}"
        return "  "
