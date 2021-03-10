from .constants import Clef, KeyCode, NoteType, VoiceType
from .voice import Voice
from .skip import Skip
from .note import Note


class Staff:
    def __init__(self, name, clef, key, quality, main_voice=None):
        self.name = name
        self.clef = clef
        self.key = key
        self.quality = quality
        self.main_voice = main_voice
        self.extra_voices = []

    def __len__(self):
        return len(self.main_voice.notes)

    def __str__(self):
        extra_voices = "\n".join([str(voice) for voice in self.extra_voices])
        return f"Name: {self.name}, clef: {self.clef}\nMain voice:\n{str(self.main_voice)}\nExtra voices:\n{extra_voices}"

    def __eq__(self, other):
        return self is other

    def changeKey(self, newKey, newQuality):
        self.key = newKey
        self.quality = newQuality
        if self.main_voice:
            self.main_voice.changeKey(newKey, newQuality)
        for voice in self.extra_voices:
            voice.changeKey(newKey, newQuality)

    def code(self):
        lines = [
            f"\\new Staff = \"{self.name}\" {{",
            f"\\clef {'treble' if self.clef == Clef.TREBLE else 'bass'}",
            f"\\key {KeyCode[self.key]} \\{self.quality}",
            "\\mergeDifferentlyHeadedOn",
            "<<"
        ]
        lines.extend(self.main_voice.code())
        for voice in self.extra_voices:
            lines.append("\\\\")
            lines.extend(voice.code())
        lines.extend([
            ">>",
            "\\bar \"|.\"",
            "}"
        ])
        return lines

    def generate_urlinie(self):
        for note in self.main_voice.notes:
            if note.note_type == NoteType.URLINIE:
                break
        else:
            return
        urlinie_even_and_odd = [[], [Skip()]]
        beams = []
        for index, note in enumerate(self.main_voice.notes):
            if note.note_type == NoteType.URLINIE:
                urlinie_even_and_odd[index % 2].append(note)
                beams.extend([
                    Note(
                        name=note.name,
                        accidental=note.accidental,
                        register=note.register,
                        in_main_voice=True,
                        note_type=note.note_type,
                        duration=8
                    ),
                    Skip(8)
                ])
                continue
            if index == len(self.main_voice.notes) - 1:
                urlinie_even_and_odd[index % 2].append(Skip())
            else:
                urlinie_even_and_odd[index % 2].append(Skip(duration=2))
            beams.append(Skip())

        for voice in urlinie_even_and_odd:
            if len(voice) > 0:
                self.extra_voices.append(
                    Voice(key=self.key, quality=self.quality,
                          voice_type=VoiceType.URLINIE, new_notes=voice)
                )

        self.extra_voices.append(
            Voice(
                key=self.key,
                quality=self.quality,
                voice_type=VoiceType.BEAM_RIGHT if self.name == "RH" else VoiceType.BEAM_LEFT,
                new_notes=beams
            )
        )

    def generate_slurs(self):
        slurs_by_length = [None] * len(self.main_voice)
        for slur_length in range(1, len(self.main_voice)):
            slurs_with_duplicates = [slur for note in self.main_voice.notes for slur in note.slurs if len(
                slur) == slur_length]
            if len(slurs_with_duplicates) == 0:
                continue
            slurs = []
            for slur in slurs_with_duplicates:
                if slur not in slurs:
                    slurs.append(slur)
            slurs.sort(key=lambda slur: self.main_voice.index(slur.before))
            slurs_by_length[slur_length] = slurs

        for length, slurs in enumerate(slurs_by_length):
            if not slurs:
                continue
            for slur in slurs:
                left_slurs_to_increment = [
                    longer_slur for longer_slur in slur.after.slurs if len(longer_slur) > length and longer_slur.after == slur.after]
                right_slurs_to_increment = [
                    longer_slur for longer_slur in slur.before.slurs if len(longer_slur) > length and longer_slur.before == slur.before]
                for slur_to_increment in left_slurs_to_increment + right_slurs_to_increment:
                    slur_to_increment.level += 1

        for slurs in slurs_by_length:
            if not slurs:
                continue
            for slur in slurs:
                if slur.level % 2 != 0:
                    slur.down = False

        self.extra_voices.extend([
            Voice(
                key=self.key,
                quality=self.quality,
                voice_type=VoiceType.SLURS,
                new_notes=self.main_voice.notes,
                slurs=slurs
            )
            for slurs in slurs_by_length if slurs
        ])

    def generate_unfoldings(self):
        all_unfoldings = []
        for note in self.main_voice.notes:
            for unfolding in note.unfoldings:
                if unfolding not in all_unfoldings:
                    all_unfoldings.append(unfolding)
        if len(all_unfoldings) == 0:
            return
        self.extra_voices.append(
            Voice(
                key=self.key,
                quality=self.quality,
                voice_type=VoiceType.UNFOLDINGS,
                new_notes=self.main_voice.notes,
                unfoldings=all_unfoldings
            )
        )

    def generate_stems(self):
        for note in self.main_voice.notes:
            if note.stem:
                break
        else:
            return
        self.extra_voices.append(
            Voice(
                key=self.key,
                quality=self.quality,
                voice_type=VoiceType.STEMS,
                new_notes=self.main_voice.notes,
            )
        )
