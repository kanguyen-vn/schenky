#(set! paper-alist (cons '("snippet" . (cons (* 190 mm) (* 70 mm))) paper-alist))
\paper {
    #(set-paper-size "snippet")
    indent = 0
    tagline = ##f
}

\version "2.20.0"

\pointAndClickTypes #'note-event
I = \once \override NoteColumn.ignore-collision = ##t

staffPiano = \new PianoStaff {
    \set Score.timing = ##f
    \set PianoStaff.followVoice = ##t
    <<
        \new Staff = "RH" {
            \clef treble
            \key f \major
            \mergeDifferentlyHeadedOn
            <<
                {
                    \hide Stem
                    \override Stem.length = #0
                    a'4 g'4 f'4 s4
                    \undo \hide Stem
                    \revert Stem.length
                }
            >>
            \bar "|."
        }
        \new Staff = "LH" {
            \clef bass
            \key f \major
            \mergeDifferentlyHeadedOn
            <<
                {
                    \hide Stem
                    \override Stem.length = #0
                    f4 c4 f4 s4
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
