from pathlib import Path
import subprocess
# import webbrowser
import popplerqt5
import re
from .note import Note
from .slur import Slur
from .unfolding import Unfolding
from .stem import Stem
from .constants import StemType


class Score:
    def __init__(self, key, quality, staves=None):
        self.key = key
        self.quality = quality
        self.staves = staves  # top staff first
        self.slur_from = None
        if staves and len(staves[-1].main_voice) > 0:
            self.current = {
                "note": staves[-1].main_voice[-1],
                "staff": staves[-1]
            }
        else:
            self.current = None

    def __str__(self):
        staves = "\n".join([str(staff) for staff in self.staves])
        return f"Key: {self.key} {self.quality}\n{staves}"
    
    def changeKey(self, newKey, newQuality):
        self.key = newKey
        self.quality = newQuality
        if self.staves:
            for staff in self.staves:
                staff.changeKey(newKey, newQuality)
    
    # def addNote(self, staffIndex, note, index=False):
    #     if not index:
    #         index = len(self.staves[staffIndex])
    #     self.staves[staffIndex].insert

    def code(self):
        lines = [
            # """#(set! paper-alist (cons '("snippet" . (cons (* 190 mm) (* 70 mm))) paper-alist))""",
            # "\\paper {",
            # '#(set-paper-size "snippet")',
            # "indent = 0",
            # "tagline = ##f",
            # "}\n",
            # "\\header{",
            # 'title = "Schenky example"',
            # 'composer = "Entered by: Kiet Nguyen"',
            # "}\n",
            "\\version \"2.20.0\"\n",
            "\\pointAndClickTypes #'note-event",
            "I = \\once \\override NoteColumn.ignore-collision = ##t",
            "Binv = \\bar \"\"",
            "B = \\bar \"|\"\n",
            "staffPiano = \\new PianoStaff {",
            "\\set Score.timing = ##f",
            "\\set PianoStaff.followVoice = ##t",
            "\\override Score.BarNumber.break-visibility = ##(#f #t #t)",
            "\\set Score.barNumberVisibility = #all-bar-numbers-visible",
            "<<"
        ]
        for staff in self.staves:
            lines.extend(staff.code())
        lines.extend([
            ">>",
            "}\n",
            "\\score {",
            "<< \\staffPiano >>",
            "\\layout {",
            "indent = 0.0",
            "ragged-right = ##t",
            "\\context {",
            "\\Staff \\remove \"Time_signature_engraver\"",
            "}",
            "}",
            "}"
        ])
        return lines

    def process(self):
        for staff in self.staves:
            staff.generate_urlinie()
            staff.generate_slurs()
            staff.generate_unfoldings()
            staff.generate_stems()

    def add_indentation(self, old_lines):
        lines = [line for possible_lines in old_lines
                 for line in possible_lines.split("\n")]
        indent = 0
        INDENT_SPACES = 4
        for i in range(len(lines)):
            if "}" in lines[i] or ">>" in lines[i]:
                indent -= 1
            lines[i] = " " * (INDENT_SPACES * indent) + lines[i]
            if "{" in lines[i] or "<<" in lines[i]:
                indent += 1
        return lines

    def write(self):
        path = Path(__file__).parent.parent / "ui" / "output.ly"
        with open(path, "w") as f:
            code = self.add_indentation(self.code())
            for line in code:
                f.write(line + "\n")
        return path

    def extract_args(self, command):
        args = re.findall(r"\[[0-9]+:[0-9]+\]", command)
        if not args:
            return []
        parsed = []
        for arg in args:
            staff, note = arg[1:-1].split(":")
            parsed.append({
                "note_index": int(note),
                "staff_index": int(staff)
            })
        return parsed

    def valid_indices(self, staff, note):
        return 0 <= staff < len(self.staves) and 0 <= note < len(self.staves[staff].main_voice)
    
    def engrave(self):
        self.process()
        ly_path = self.write()
        lilypond_run = subprocess.run(["lilypond", ly_path.absolute()], check=True)
        print("LilyPond executed with exit code", lilypond_run.returncode)

    def cmd(self, command):
        current_note, current_staff = self.current["note"], self.current["staff"]
        assert current_note == None or isinstance(current_note, Note)
        current_staff_index = self.staves.index(current_staff)
        current_note_index = current_staff.main_voice.index(current_note)
        if command == "staffDown":
            new_staff_index = (current_staff_index + 1) % len(self.staves)
            new_staff = self.staves[new_staff_index]
            self.current["staff"] = new_staff
            return
        if command == "staffUp":
            new_staff_index = (len(self.staves) +
                               current_staff_index - 1) % len(self.staves)
            new_staff = self.staves[new_staff_index]
            self.current["staff"] = new_staff
            return
        if command == "left":
            len_notes = len(current_staff)
            new_note_index = (len_notes + current_note_index - 1) % len_notes
            new_note = current_staff.main_voice[new_note_index]
            self.current["note"] = new_note
            return
        if command == "right":
            len_notes = len(current_staff)
            new_note_index = (current_note_index + 1) % len_notes
            new_note = current_staff.main_voice[new_note_index]
            self.current["note"] = new_note
            return
        if command.startswith("navigateTo"):
            args = self.extract_args(command)
            if len(args) != 1:
                print("Usage navigateTo[staff_index:note_index]")
                return
            staff_index, note_index = args[0]["staff_index"], args[0]["note_index"]
            if not self.valid_indices(staff_index, note_index):
                print("Invalid indices")
                return
            self.current["staff"] = self.staves[staff_index]
            self.current["note"] = self.staves[staff_index].main_voice[note_index]
        if command.startswith("makeUrlinie"):
            current_note.make_urlinie()
            return
        if command.startswith("startSlur"):
            if self.slur_from:
                print("endSlur required")
                return
            args = self.extract_args(command)
            if len(args) > 1:
                print("Usage startSlur or startSlur[staff_index:note_index]")
            elif len(args) == 0:
                self.slur_from = {
                    "note": current_note,
                    "staff": current_staff
                }
            else:
                staff_index, note_index = args[0]["staff_index"], args[0]["note_index"]
                if not self.valid_indices(staff_index, note_index):
                    print("Invalid indices")
                    return
                self.slur_from = {
                    "note": self.staves[staff_index].main_voice[note_index],
                    "staff": self.staves[staff_index]
                }
            return
        if command.startswith("endSlur"):
            args = self.extract_args(command)
            slur_end = None
            if len(args) == 0:
                slur_end = self.current
            else:
                if len(args) != 1:
                    print("Usage endSlur[staff_index:note_index]")
                    return
                staff_index, note_index = args[0]["staff_index"], args[0]["note_index"]
                if not self.valid_indices(staff_index, note_index):
                    print("Invalid indices")
                    return
                slur_end = {
                    "note": self.staves[staff_index].main_voice[note_index],
                    "staff": self.staves[staff_index]
                }
            if not self.slur_from:
                print("startSlur required")
                return
            if self.slur_from == slur_end:
                print("Cannot slur one note to itself")
                return
            if self.slur_from["staff"] != slur_end["staff"]:
                print("Unable to slur between different voices")
                return
            if slur_end["note"] in self.slur_from["note"].slurs:
                print("Slur already available")
                return
            new_slur = Slur(
                self.slur_from["note"], slur_end["note"], slur_end["staff"].main_voice)
            self.slur_from["note"].slurs.append(new_slur)
            slur_end["note"].slurs.append(new_slur)
            return
        if command.startswith("slur"):
            args = self.extract_args(command)
            if len(args) != 2:
                print(
                    "Usage slur[start_staff_index:start_note_index][end_staff_index:end_note_index]")
                return
            start_staff_index, start_note_index = args[0]["staff_index"], args[0]["note_index"]
            end_staff_index, end_note_index = args[1]["staff_index"], args[1]["note_index"]
            if not self.valid_indices(start_staff_index, start_note_index) or not self.valid_indices(end_staff_index, end_note_index):
                print("Invalid indices")
                return
            start_note = self.staves[start_staff_index].main_voice[start_note_index]
            end_note = self.staves[end_staff_index].main_voice[end_note_index]
            if start_note in end_note.slurs or end_note in start_note.slurs:
                print("Slur already exists")
                return
            new_slur = Slur(start_note, end_note,
                            self.staves[start_staff_index].main_voice)
            start_note.slurs.append(new_slur)
            end_note.slurs.append(new_slur)
        if command.startswith("cancelSlur"):
            args = self.extract_args(command)
            if len(args) != 2:
                print(
                    "Usage cancelSlur[start_staff_index:start_note_index][end_staff_index:end_note_index]")
                return
            start_staff_index, start_note_index = args[0]["staff_index"], args[0]["note_index"]
            end_staff_index, end_note_index = args[1]["staff_index"], args[1]["note_index"]
            if not self.valid_indices(start_staff_index, start_note_index) or not self.valid_indices(end_staff_index, end_note_index):
                print("Invalid indices")
                return
            start_note = self.staves[start_staff_index].main_voice[start_note_index]
            end_note = self.staves[end_staff_index].main_voice[end_note_index]
            to_remove = Slur(start_note, end_note,
                             self.staves[start_staff_index].main_voice)
            to_remove_from_start = next(
                filter(lambda slur: slur == to_remove, start_note.slurs), None)
            to_remove_from_end = next(
                filter(lambda slur: slur == to_remove, end_note.slurs), None)
            if not to_remove_from_start or not to_remove_from_end:
                print("Slur not available")
                return
            # start_note.slurs.remove(end_note)
            # end_note.slurs.remove(start_note)
            start_note.slurs.remove(to_remove_from_start)
            end_note.slurs.remove(to_remove_from_end)
        if command.startswith("unfolding"):
            args = self.extract_args(command)
            if len(args) != 2:
                print(
                    "Usage unfolding[start_staff_index:start_note_index][end_staff_index:end_note_index]")
                return
            start_staff_index, start_note_index = args[0]["staff_index"], args[0]["note_index"]
            end_staff_index, end_note_index = args[1]["staff_index"], args[1]["note_index"]
            if not self.valid_indices(start_staff_index, start_note_index) or not self.valid_indices(end_staff_index, end_note_index):
                print("Invalid indices")
                return
            start_note = self.staves[start_staff_index].main_voice[start_note_index]
            end_note = self.staves[end_staff_index].main_voice[end_note_index]
            unfolding = Unfolding(start_note, end_note,
                                  self.staves[start_staff_index].main_voice)
            start_note.unfoldings.append(unfolding)
            end_note.unfoldings.append(unfolding)
            return
        if command.startswith("quarter_stem"):
            args = self.extract_args(command)
            if len(args) != 1:
                print("Usage stem[staff_index:note_index]")
                return
            staff_index, note_index = args[0]["staff_index"], args[0]["note_index"]
            if not self.valid_indices(staff_index, note_index):
                print("Invalid indices")
                return
            stem_up = staff_index == 0
            note = self.staves[staff_index].main_voice[note_index]
            note.stem = Stem(note, StemType.QUARTER, stem_up)
            return
        if command.startswith("eighth_stem"):
            args = self.extract_args(command)
            if len(args) != 1:
                print("Usage stem[staff_index:note_index]")
                return
            staff_index, note_index = args[0]["staff_index"], args[0]["note_index"]
            if not self.valid_indices(staff_index, note_index):
                print("Invalid indices")
                return
            stem_up = staff_index == 0
            note = self.staves[staff_index].main_voice[note_index]
            note.stem = Stem(note, StemType.EIGHTH, stem_up)
            return
        if command == "engrave":
            self.process()
            self.write()
            ly_path = Path(__file__).parent.parent / "ui" / "output.ly"
            lilypond_run = subprocess.run(["lilypond", ly_path.absolute()], check=True)
            print("LilyPond executed with exit code", lilypond_run.returncode)
            return
