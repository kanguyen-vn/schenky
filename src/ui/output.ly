\version "2.20.0"

\pointAndClickTypes #'note-event
I = \once \override NoteColumn.ignore-collision = ##t
Binv = \bar ""
B = \bar "|"

staffPiano = \new PianoStaff {
    \set Score.timing = ##f
    \set PianoStaff.followVoice = ##t
    \override Score.BarNumber.break-visibility = ##(#f #t #t)
    \set Score.barNumberVisibility = #all-bar-numbers-visible
    <<
        \new Staff = "RH" {
            \clef treble
            \key c \major
            \mergeDifferentlyHeadedOn
            <<
                {
                    \hide Stem
                    \override Stem.length = #0
                    a4 s4 b4 s4
                    \undo \hide Stem
                    \revert Stem.length
                }
            >>
            \bar "|."
        }
        \new Staff = "LH" {
            \clef bass
            \key c \major
            \mergeDifferentlyHeadedOn
            <<
                {
                    \hide Stem
                    \override Stem.length = #0
                    s4 s4 s4 s4
                    \undo \hide Stem
                    \revert Stem.length
                }
            >>
            \bar "|."
        }
    >>
}

\score {
<< \staffPiano >>
    \layout {
        indent = 0.0
        ragged-right = ##t
        \context {
            \Staff \remove "Time_signature_engraver"
        }
    }
}
