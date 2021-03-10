class Unfolding:
    def __init__(self, first, second, voice):
        self.voice = voice
        if first == second:
            raise ValueError("Cannot unfold single note")
        if not (first in voice and second in voice):
            raise ValueError("Notes have to be part of voice")
        if voice.index(first) < voice.index(second):
            self.before, self.after = first, second
        else:
            self.before, self.after = second, first

    def lower(self):
        return self.before if self.before < self.after else self.after

    def higher(self):
        return self.before if self.before > self.after else self.after

    def index_before(self):
        return self.voice.index(self.before)

    def index_after(self):
        return self.voice.index(self.after)
