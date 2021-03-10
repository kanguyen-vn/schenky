from .constants import Accidental, VoiceType, NoteName, NoteType, MinorAccidentals, MajorAccidentals, StemType
from .skip import Skip
from .note import Note


class Voice:
    def __init__(self, key, quality, voice_type, note_input=None, new_notes=None, slurs=None, unfoldings=None):
        self.key = key
        self.voice_type = voice_type
        self.quality = quality
        self.slurs = slurs
        self.unfoldings = unfoldings
        if new_notes:
            self.notes = new_notes
            return
        self.notes = []
        if note_input:
            note_list = []
            if isinstance(note_input, str):
                note_list = note_input.split()
            elif isinstance(note_input, list):
                note_list = note_input
            for entry in note_list:
                if entry == "skip":
                    self.notes.append(Skip())
                    continue
                if entry in Accidental and len(self.notes) > 0:
                    self.notes[-1].accidental = Accidental[entry]
                    continue
                name = entry[0]
                first_digit = 0
                for index, _ in enumerate(entry):
                    if _.isdigit():
                        first_digit = index
                        register = int(entry[first_digit:])
                        break
                else:
                    register = 3
                if first_digit > 1:
                    accidental = Accidental[entry[1:first_digit]]
                else:
                    accidental = (MajorAccidentals[key][NoteName[name]]
                                  if self.quality == "major" else MinorAccidentals[key][NoteName[name]])

                in_main_voice = voice_type == VoiceType.MAIN
                self.notes.append(
                    Note(
                        name=name,
                        accidental=accidental,
                        register=register,
                        in_main_voice=in_main_voice
                    )
                )

    def __str__(self):
        notes = " ".join([str(note) for note in self.notes])
        return f"Voice type: {self.voice_type}\n{notes}"

    def __getitem__(self, key):
        return self.notes[key]

    def __len__(self):
        return len(self.notes)

    def changeKey(self, newKey, newQuality):
        self.key = newKey
        self.quality = newQuality

    def index(self, value):
        try:
            return self.notes.index(value)
        except ValueError:
            return -1

    def code(self):
        lines = ["{"]
        if self.voice_type == VoiceType.MAIN or self.voice_type == VoiceType.URLINIE:
            lines.extend([
                "\\hide Stem",
                "\\override Stem.length = #0"
            ])
            line = " ".join([note.code(self.voice_type)
                             for note in self.notes])
            if self.voice_type == VoiceType.MAIN:
                line += " s4"
            lines.extend(line.split("\n") + [
                "\\undo \\hide Stem",
                "\\revert Stem.length"
            ])
        elif self.voice_type == VoiceType.BEAM_LEFT or self.voice_type == VoiceType.BEAM_RIGHT:
            if self.voice_type == VoiceType.BEAM_LEFT:
                lines.extend([
                    "\\override Beam.positions = #'(-8 . -8)",
                    "\\stemDown"
                ])
            else:
                lines.extend([
                    "\\override Beam.positions = #'(8 . 8)",
                    "\\stemUp"
                ])
            lines.extend([
                "\\override NoteHead.duration-log = #1",
                "\\hide NoteHead"
            ])

            def is_urlinie_note(note):
                return isinstance(note, Note) and note.note_type == NoteType.URLINIE
            urlinie_notes = list(
                filter(lambda note: is_urlinie_note(note), self.notes))
            line = ""
            for note in self.notes:
                if note == urlinie_notes[0]:
                    line += f"\\I {note.code(self.voice_type)}[ "
                    continue
                if note == urlinie_notes[-1]:
                    line += f"\\I {note.code(self.voice_type)}] "
                    continue
                if is_urlinie_note(note):
                    line += "\\I "
                line += f"{note.code(self.voice_type)} "
            lines.extend(line.split("\n") + [
                "\\revert Beam.positions",
                "\\undo \\hide NoteHead",
                "\\revert NoteHead.duration-log"
            ])
        elif self.voice_type == VoiceType.SLURS:
            lines.extend([
                "\\hide Stem",
                "\\hide NoteHead",
                "\\override Stem.length = #2"
            ])
            line = ""
            for note in self.notes:
                start = next(filter(lambda slur: note ==
                                    slur.before, self.slurs), None)
                start_slur = False
                if start:
                    start_slur = True
                    pos_char = "_" if start.down else "^"
                end_slur = any(note == each.after for each in self.slurs)
                if start_slur and end_slur:
                    line += f"\\I {note.code(self.voice_type)}){pos_char}("
                elif start_slur:
                    line += f"\\I {note.code(self.voice_type)}{pos_char}("
                elif end_slur:
                    line += f"\\I {note.code(self.voice_type)}) "
                else:
                    line += f"\\I {note.code(self.voice_type)} "
            lines.extend([
                line,
                "\\revert Stem.length",
                "\\undo \\hide NoteHead"
                "\\undo \\hide Stem"
            ])
        elif self.voice_type == VoiceType.UNFOLDINGS:
            line = ""
            for note in self.notes:
                check = False
                for unfolding in note.unfoldings:
                    if unfolding in self.unfoldings:
                        check = True
                        if len(line):
                            lines.append(line)
                        if unfolding.higher() == note:
                            lines.append("\\stemDown")
                            bracket = "]" if note == unfolding.after else "["
                            line = f"\\I {note.code(self.voice_type, 8)}{bracket} s8"
                        elif unfolding.lower() == note:
                            lines.append("\\stemUp")
                            bracket = "]" if note == unfolding.after else "["
                            line = f"\\I {note.code(self.voice_type, 8)}{bracket} s8"
                if not check:
                    line += " s4"
            if len(line):
                lines.append(line)
        elif self.voice_type == VoiceType.STEMS:
            # lines.extend([
            #     "\\hide NoteHead",
            #     "\\override Stem.length = #2"
            # ])
            line = ""
            for note in self.notes:
                if not note.stem:
                    line += "s4 "
                    continue
                if len(line):
                    lines.append(line)
                if note.stem.up:
                    lines.append("\\stemUp")
                else:
                    lines.append("\\stemDown")
                if note.stem.stem_type == StemType.QUARTER:
                    line = f"\\I {note.code(self.voice_type, 4)} "
                elif note.stem.stem_type == StemType.EIGHTH:
                    line = f"\\I {note.code(self.voice_type, 8)} s8"
            if len(line):
                lines.append(line)
            # lines.extend([
            #     line,
            #     "\\revert Stem.length",
            #     "\\undo \\hide NoteHead"
            # ])

        lines.append("}")
        return lines
