class Slur:
    def __init__(self, first, second, voice):
        self.voice = voice
        if first == second:
            raise ValueError("Cannot slur a note to itself")
        if not (first in voice and second in voice):
            raise ValueError("Notes have to be part of voice")
        if voice.index(first) < voice.index(second):
            self.before, self.after = first, second
        else:
            self.before, self.after = second, first
        self.down = True
        self.level = 0

    def __eq__(self, other):
        return ((self.before == other.before and self.after == other.after) or (self.before == other.after and self.after == other.before)) and self.voice == other.voice

    def __len__(self):
        return abs(self.voice.index(self.before) - self.voice.index(self.after))

    def other(self, note):
        if note == self.before:
            return self.after
        if note == self.after:
            return self.before
        return None
