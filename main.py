"""
AinaDigit-Music — Guitar Capo & Keyboard Transpose Calculator
Compatible avec Flet 0.82.2

Corrections appliquées :
  - ft.padding.symmetric()  → ft.Padding.symmetric()
  - ft.padding.only()       → ft.Padding.only()
  - ft.padding.all()        → ft.Padding.all()
  - ft.border.only()        → ft.Border.only()
  - ft.border.all()         → ft.Border.all()
  - ft.margin.symmetric()   → ft.Margin.symmetric()
  - Text(letter_spacing=…)  → Text(style=ft.TextStyle(letter_spacing=…))
  - ft.app()                → ft.run()
  - ft.ElevatedButton       → ft.Button
  - ft.icons.*              → ft.Icons.*
  - page.window_width       → page.window.width

Lancer :
    pip install flet==0.82.2
    python ainadigit_music.py
"""

import flet as ft

# ── Music theory ──────────────────────────────────────────────────────────────
NOTES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

# ── Design tokens ─────────────────────────────────────────────────────────────
BG_COLOR     = "#080d1a"
CARD_COLOR   = "#0f1929"
BTN_IDLE     = "#1a2540"
BTN_ACTIVE   = "#2563eb"
TEXT_PRIMARY = "#f1f5f9"
TEXT_SUB     = "#64748b"
ACCENT       = "#3b82f6"
BORDER_COL   = "#1e2d45"


# ── Helpers ───────────────────────────────────────────────────────────────────
def note_idx(note: str) -> int:
    return NOTES.index(note)

def ordinal(n: int) -> str:
    return f"{n}{'st' if n==1 else 'nd' if n==2 else 'rd' if n==3 else 'th'}"

def calc_capo(song: str, play: str) -> int:
    diff = (note_idx(play) - note_idx(song)) % 12
    return (12 - diff) % 12

def calc_keyboard(song: str, play: str) -> int:
    return (note_idx(play) - note_idx(song)) % 12

def chord_conversions(song: str, play: str):
    si   = note_idx(song)
    diff = (note_idx(play) - si) % 12
    pairs = [
        (NOTES[si],             "Major"),
        (NOTES[(si + 9) % 12], "Minor"),
        (NOTES[(si + 5) % 12], "Major"),
        (NOTES[(si + 7) % 12], "Major"),
        (NOTES[(si + 4) % 12], "Minor"),
        (NOTES[(si + 2) % 12], "Minor"),
    ]
    return [(f"{n} {t}", f"{NOTES[(note_idx(n)+diff)%12]} {t}") for n, t in pairs]


# ── Main ──────────────────────────────────────────────────────────────────────
def main(page: ft.Page):
    page.title      = "AinaDigit-Music"
    page.bgcolor    = BG_COLOR
    page.padding    = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width  = 420
    page.window.height = 880

    # ── State ─────────────────────────────────────────────────────────────────
    state = {"song": "C", "play": "G"}
    song_btns: dict[str, ft.Button] = {}
    play_btns: dict[str, ft.Button] = {}

    # ── Live-update refs ──────────────────────────────────────────────────────
    r_capo_num  = ft.Ref[ft.Text]()
    r_capo_suf  = ft.Ref[ft.Text]()
    r_capo_desc = ft.Ref[ft.Text]()
    r_kb_num    = ft.Ref[ft.Text]()
    r_kb_desc   = ft.Ref[ft.Text]()
    r_conv_col  = ft.Ref[ft.Column]()

    # ── Refresh logic ─────────────────────────────────────────────────────────
    def refresh():
        sk, pk = state["song"], state["play"]
        capo   = calc_capo(sk, pk)
        kbt    = calc_keyboard(sk, pk)

        r_capo_num.current.value  = str(capo)
        r_capo_suf.current.value  = f"{ordinal(capo)} Fret"
        r_capo_desc.current.value = f"Place capo on {ordinal(capo)} of the neck"
        for r in (r_capo_num, r_capo_suf, r_capo_desc):
            r.current.update()

        sign = "+" if kbt >= 0 else ""
        r_kb_num.current.value  = f"{sign}{kbt}"
        r_kb_desc.current.value = (
            f"Shift settings by {abs(kbt)} semitones "
            f"{'up' if kbt >= 0 else 'down'}"
        )
        for r in (r_kb_num, r_kb_desc):
            r.current.update()

        r_conv_col.current.controls = [
            conv_row(o, n) for o, n in chord_conversions(sk, pk)
        ]
        r_conv_col.current.update()

    def on_song(e, note):
        state["song"] = note
        for n, b in song_btns.items():
            b.bgcolor = BTN_ACTIVE if n == note else BTN_IDLE
            b.update()
        refresh()

    def on_play(e, note):
        state["play"] = note
        for n, b in play_btns.items():
            b.bgcolor = BTN_ACTIVE if n == note else BTN_IDLE
            b.update()
        refresh()

    # ── Widget factories ──────────────────────────────────────────────────────
    def note_btn(note: str, key_type: str) -> ft.Button:
        is_song = key_type == "song"
        active  = note == state[key_type]
        handler = (lambda e, n=note: on_song(e, n)) if is_song \
                  else (lambda e, n=note: on_play(e, n))
        btn = ft.Button(
            content=ft.Text(
                note, size=13, color=TEXT_PRIMARY,
                weight=ft.FontWeight.W_600,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=BTN_ACTIVE if active else BTN_IDLE,
            width=52, height=52,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                elevation=0,
                overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            ),
            on_click=handler,
        )
        (song_btns if is_song else play_btns)[note] = btn
        return btn

    def notes_grid(key_type: str) -> ft.Column:
        return ft.Column(controls=[
            ft.Row(
                controls=[note_btn(n, key_type) for n in NOTES[:6]],
                spacing=6, scroll=ft.ScrollMode.AUTO,
            ),
            ft.Row(
                controls=[note_btn(n, key_type) for n in NOTES[6:]],
                spacing=6, scroll=ft.ScrollMode.AUTO,
            ),
        ], spacing=6)

    def sec_header(left: str, right: str = "", italic: bool = False) -> ft.Row:
        return ft.Row(controls=[
            ft.Text(
                left, size=13, weight=ft.FontWeight.BOLD,
                color=TEXT_PRIMARY, expand=True,
            ),
            ft.Text(
                right, size=12,
                color=TEXT_SUB if italic else ACCENT,
                italic=italic,
            ),
        ])

    def conv_row(orig: str, new: str) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(orig, color=TEXT_SUB, size=15, expand=True),
                    ft.Text(new,  color=ACCENT,   size=15,
                            weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding.symmetric(vertical=13),
            border=ft.Border.only(bottom=ft.BorderSide(0.5, BORDER_COL)),
        )

    def result_card(
        label:     str,
        icon,
        num_ref,
        suf_ref,
        init_num:  str,
        init_suf:  str,
        desc_ref,
        init_desc: str,
        deco_icon,
    ) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(icon, color=ACCENT, size=17),
                                    # ✅ letter_spacing via TextStyle (Text n'a plus cet arg)
                                    ft.Text(
                                        label,
                                        style=ft.TextStyle(
                                            size=11,
                                            color=ACCENT,
                                            weight=ft.FontWeight.BOLD,
                                            letter_spacing=1.2,
                                        ),
                                    ),
                                ],
                                spacing=6,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        init_num, ref=num_ref, size=54,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        init_suf, ref=suf_ref, size=22,
                                        color=ACCENT,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.END,
                                spacing=4,
                            ),
                            ft.Text(init_desc, ref=desc_ref, size=13, color=TEXT_SUB),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.Icon(
                        deco_icon,
                        color=ft.Colors.with_opacity(0.12, TEXT_PRIMARY),
                        size=64,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=CARD_COLOR,
            border_radius=16,
            padding=ft.Padding.all(20),
            border=ft.Border.all(1, BORDER_COL),
        )

    # ── Static widgets ────────────────────────────────────────────────────────
    top_bar = ft.Container(
        content=ft.Row(controls=[
            ft.IconButton(
                icon=ft.Icons.SETTINGS_OUTLINED,
                icon_color=TEXT_PRIMARY, icon_size=22,
            ),
            ft.Text(
                "AinaDigit-Music", size=19, weight=ft.FontWeight.BOLD,
                color=TEXT_PRIMARY, expand=True,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.IconButton(
                icon=ft.Icons.INFO_OUTLINE,
                icon_color=TEXT_PRIMARY, icon_size=22,
            ),
        ]),
        padding=ft.Padding.symmetric(horizontal=8, vertical=6),
        border=ft.Border.only(bottom=ft.BorderSide(0.5, BORDER_COL)),
    )

    # Separate suf_ref for keyboard (static "st", no need to update)
    r_kb_suf = ft.Ref[ft.Text]()

    capo_card_widget = result_card(
        label="GUITAR CAPO",
        icon=ft.Icons.TUNE,
        num_ref=r_capo_num, suf_ref=r_capo_suf,
        init_num="5",       init_suf="th Fret",
        desc_ref=r_capo_desc,
        init_desc="Place capo on 5th fret of the neck",
        deco_icon=ft.Icons.MUSIC_NOTE,
    )

    kb_card_widget = result_card(
        label="KEYBOARD TRANSPOSE",
        icon=ft.Icons.TUNE,
        num_ref=r_kb_num,  suf_ref=r_kb_suf,
        init_num="+7",     init_suf="st",
        desc_ref=r_kb_desc,
        init_desc="Shift settings by 7 semitones up",
        deco_icon=ft.Icons.PIANO,
    )

    conv_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "COMMON CONVERSIONS",
                    style=ft.TextStyle(
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_SUB,
                        letter_spacing=1.5,
                    ),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Row(controls=[
                                    ft.Text(
                                        "Original", color=TEXT_PRIMARY,
                                        size=14, weight=ft.FontWeight.BOLD,
                                        expand=True,
                                    ),
                                    ft.Text(
                                        "New Chord", color=TEXT_PRIMARY,
                                        size=14, weight=ft.FontWeight.BOLD,
                                    ),
                                ]),
                                padding=ft.Padding.only(bottom=10),
                                border=ft.Border.only(
                                    bottom=ft.BorderSide(1, BORDER_COL)
                                ),
                            ),
                            ft.Column(
                                ref=r_conv_col,
                                controls=[
                                    conv_row(o, n)
                                    for o, n in chord_conversions("C", "G")
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=0,
                    ),
                    bgcolor=CARD_COLOR,
                    border_radius=14,
                    padding=ft.Padding.all(16),
                    border=ft.Border.all(1, BORDER_COL),
                ),
            ],
            spacing=10,
        ),
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
    )

    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        bgcolor=CARD_COLOR,
        indicator_color=ft.Colors.with_opacity(0.15, ACCENT),
        border=ft.Border.only(top=ft.BorderSide(0.5, BORDER_COL)),
        destinations=[
            ft.NavigationBarDestination(
                label="Calculator",
                icon=ft.Icons.CALCULATE_OUTLINED,
                selected_icon=ft.Icons.CALCULATE,
            ),
            ft.NavigationBarDestination(
                label="Saved",
                icon=ft.Icons.BOOKMARK_OUTLINE,
                selected_icon=ft.Icons.BOOKMARK,
            ),
        ],
    )

    page.add(
        ft.Column(
            controls=[
                top_bar,
                ft.ListView(
                    controls=[
                        ft.Container(
                            content=ft.Column(controls=[
                                sec_header("SONG KEY (ORIGINALE)", "Select One"),
                                notes_grid("song"),
                            ], spacing=12),
                            padding=ft.Padding.symmetric(horizontal=16, vertical=16),
                        ),
                        ft.Container(
                            content=ft.Column(controls=[
                                sec_header(
                                    "PLAYING KEY (JOUÉE)",
                                    "Relative to neck", italic=True,
                                ),
                                notes_grid("play"),
                            ], spacing=12),
                            padding=ft.Padding.symmetric(horizontal=16, vertical=16),
                        ),
                        ft.Container(
                            content=capo_card_widget,
                            padding=ft.Padding.symmetric(horizontal=16, vertical=6),
                        ),
                        ft.Container(
                            content=kb_card_widget,
                            padding=ft.Padding.symmetric(horizontal=16, vertical=6),
                        ),
                        conv_section,
                        ft.Container(height=20),
                    ],
                    expand=True,
                    padding=0,
                    spacing=0,
                ),
            ],
            expand=True,
            spacing=0,
        )
    )


ft.run(main)
