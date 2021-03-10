class Stem:
    def __init__(self, note, stem_type, up):
        self.note = note
        self.stem_type = stem_type
        self.up = up

    def toggle_direction(self):
        self.up = not self.up
