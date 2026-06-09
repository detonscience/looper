

import base64
import io
import math
import random
import wave
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import streamlit as st
import streamlit.components.v1 as components

try:
    import mido
    MIDO_AVAILABLE = True
except Exception:
    MIDO_AVAILABLE = False


APP_TITLE = "PadLoop Lab"
APP_SUBTITLE = "Sample-to-pad looper + MIDI note engine for techno, house, ambient, IDM, and dub textures."
SAMPLE_RATE = 44100


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

    :root {
        --bg: #070912;
        --panel: rgba(18, 23, 42, 0.92);
        --panel2: rgba(28, 36, 64, 0.88);
        --text: #f4f7ff;
        --muted: #aeb9d6;
        --cyan: #6ee7ff;
        --pink: #ff66c4;
        --lime: #b8ff6a;
        --amber: #ffd166;
        --border: rgba(255,255,255,0.14);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: var(--text) !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 12%, rgba(110,231,255,0.18), transparent 34%),
            radial-gradient(circle at 84% 8%, rgba(255,102,196,0.17), transparent 28%),
            radial-gradient(circle at 50% 92%, rgba(184,255,106,0.10), transparent 36%),
            linear-gradient(135deg, #050610 0%, #0b1020 52%, #12091d 100%);
    }

    .hero {
        border: 1px solid var(--border);
        background: linear-gradient(135deg, rgba(110,231,255,0.11), rgba(255,102,196,0.09));
        border-radius: 28px;
        padding: 28px 30px;
        box-shadow: 0 24px 80px rgba(0,0,0,0.34);
        margin-bottom: 20px;
    }

    .hero h1 {
        font-size: 3.0rem;
        line-height: 1.02;
        margin: 0;
        letter-spacing: -0.06em;
        color: #ffffff !important;
    }

    .hero p {
        margin-top: 12px;
        color: var(--muted) !important;
        font-size: 1.05rem;
        max-width: 980px;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
    }

    .badge {
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 999px;
        padding: 8px 12px;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem;
        color: #eaf7ff;
        background: rgba(255,255,255,0.06);
    }

    .panel {
        border: 1px solid var(--border);
        background: var(--panel);
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 18px 54px rgba(0,0,0,0.26);
        margin-bottom: 18px;
    }

    .panel h3 {
        margin-top: 0;
        letter-spacing: -0.03em;
        color: #ffffff !important;
    }

    .mini-card {
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 14px;
        min-height: 96px;
    }

    .mini-card b {
        display: block;
        color: #ffffff;
        margin-bottom: 6px;
    }

    .mini-card span {
        color: var(--muted);
        font-size: 0.92rem;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    div[data-testid="stMetricLabel"] {
        color: #cdd8ff !important;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        background: linear-gradient(135deg, rgba(110,231,255,0.22), rgba(255,102,196,0.20)) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        min-height: 44px;
    }

    .stSelectbox label, .stSlider label, .stNumberInput label, .stFileUploader label, .stCheckbox label {
        color: #eff5ff !important;
        font-weight: 700 !important;
    }

    input, textarea, select, [data-baseweb="select"] * {
        color: #ffffff !important;
    }

    [data-baseweb="select"] > div {
        background: rgba(8, 12, 24, 0.98) !important;
        border: 1px solid rgba(255,255,255,0.22) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        color: #ffffff !important;
        font-weight: 800;
        padding: 10px 18px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(110,231,255,0.32), rgba(255,102,196,0.28)) !important;
        color: #ffffff !important;
    }

    .loop-audio-card {
        border: 1px solid rgba(255,255,255,0.14);
        background: rgba(255,255,255,0.055);
        border-radius: 18px;
        padding: 14px;
        margin: 12px 0 18px 0;
    }

    .loop-audio-card b {
        color: #ffffff;
        display: block;
        margin-bottom: 10px;
    }

    .loop-audio-card audio {
        width: 100%;
        filter: drop-shadow(0 8px 24px rgba(0,0,0,0.24));
    }

    .wave-player-note {
        color: #aeb9d6;
        font-size: 0.88rem;
        margin-top: -4px;
        margin-bottom: 12px;
    }

    .drop-zone-panel {
        border: 1px dashed rgba(110,231,255,0.42);
        background: linear-gradient(135deg, rgba(110,231,255,0.10), rgba(255,102,196,0.08));
        border-radius: 24px;
        padding: 20px;
        margin-bottom: 14px;
        box-shadow: inset 0 0 32px rgba(110,231,255,0.05), 0 18px 54px rgba(0,0,0,0.20);
    }

    .drop-zone-panel h3 {
        color: #ffffff !important;
        margin: 0 0 8px 0;
        letter-spacing: -0.03em;
    }

    .drop-zone-panel p {
        color: #cdd8ff !important;
        margin: 0;
    }

    .drop-zone-panel b {
        color: #6ee7ff !important;
    }

    /* High-contrast Streamlit overrides for sidebar, labels, tables, captions, and upload widgets */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #07101f 0%, #0b1224 55%, #12091d 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.14) !important;
    }

    section[data-testid="stSidebar"] * {
        color: #f6f9ff !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #f6f9ff !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    section[data-testid="stSidebar"] .stSlider [data-testid="stTickBar"],
    section[data-testid="stSidebar"] .stSlider span,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stCheckbox label {
        color: #ffffff !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea {
        background: #070b16 !important;
        color: #ffffff !important;
        border: 1px solid rgba(110,231,255,0.42) !important;
        box-shadow: 0 0 0 1px rgba(110,231,255,0.10) !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] span,
    section[data-testid="stSidebar"] [data-baseweb="select"] div {
        color: #ffffff !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label,
    section[data-testid="stSidebar"] [role="radiogroup"] span,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        opacity: 1 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stCaptionContainer"],
    div[data-testid="stCaptionContainer"] p,
    div[data-testid="stCaptionContainer"] span {
        color: #dfe8ff !important;
        opacity: 1 !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.16) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
    }

    div[data-testid="stDataFrame"] * {
        color: #06101c !important;
    }

    div[data-testid="stDataFrame"] [role="columnheader"] * {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetric"] label,
    [data-testid="stMetric"] p,
    [data-testid="stMetric"] span {
        color: #eaf0ff !important;
        opacity: 1 !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        text-shadow: 0 0 18px rgba(110,231,255,0.20) !important;
    }

    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span {
        color: #ffffff !important;
        opacity: 1 !important;
    }

    .stFileUploader,
    .stFileUploader * {
        color: #ffffff !important;
        opacity: 1 !important;
    }

    .stFileUploader section {
        background: rgba(5,8,18,0.72) !important;
        border: 1px dashed rgba(110,231,255,0.50) !important;
        border-radius: 18px !important;
    }

    .stFileUploader button {
        color: #ffffff !important;
        background: linear-gradient(135deg, rgba(110,231,255,0.24), rgba(255,102,196,0.22)) !important;
        border: 1px solid rgba(255,255,255,0.22) !important;
        font-weight: 800 !important;
    }

    .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
/* --- Streamlit Cloud uploader white-box fix v1.6.1 --- */
div[data-testid="stFileUploader"] {
    background: rgba(5,8,18,0.90) !important;
    border: 1px solid rgba(110,231,255,0.42) !important;
    border-radius: 18px !important;
    padding: 10px !important;
}

div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploader"] section > div,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
    background: #07101f !important;
    color: #ffffff !important;
    border: 1px dashed rgba(110,231,255,0.65) !important;
    border-radius: 16px !important;
}

div[data-testid="stFileUploader"] label,
div[data-testid="stFileUploader"] p,
div[data-testid="stFileUploader"] span,
div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] div {
    color: #ffffff !important;
    opacity: 1 !important;
}

div[data-testid="stFileUploader"] button,
div[data-testid="stFileUploader"] button span,
div[data-testid="stFileUploader"] [role="button"],
div[data-testid="stFileUploader"] [role="button"] * {
    color: #ffffff !important;
    background: linear-gradient(135deg, rgba(110,231,255,0.30), rgba(255,102,196,0.26)) !important;
    border: 1px solid rgba(255,255,255,0.26) !important;
    border-radius: 12px !important;
    font-weight: 900 !important;
    opacity: 1 !important;
}

div[data-testid="stFileUploader"] svg,
div[data-testid="stFileUploader"] svg * {
    color: #6ee7ff !important;
    fill: #6ee7ff !important;
    stroke: #6ee7ff !important;
    opacity: 1 !important;
}

div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"],
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] *,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] * {
    color: #f7fbff !important;
    opacity: 1 !important;
}

div[data-testid="stAlert"] {
    background: rgba(10,18,38,0.96) !important;
    color: #ffffff !important;
    border: 1px solid rgba(110,231,255,0.25) !important;
}

div[data-testid="stAlert"] *,
div[data-testid="stNotification"] *,
div[data-testid="stStatusWidget"] * {
    color: #ffffff !important;
    opacity: 1 !important;
}


/* --- Upload chip / file-name dark-mode fix v1.7.1 --- */
div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] *,
div[data-testid="stFileUploader"] li,
div[data-testid="stFileUploader"] li *,
div[data-testid="stFileUploader"] ul,
div[data-testid="stFileUploader"] ul *,
div[data-testid="stFileUploader"] [class*="uploadedFile"],
div[data-testid="stFileUploader"] [class*="uploadedFile"] *,
div[data-testid="stFileUploader"] [class*="fileName"],
div[data-testid="stFileUploader"] [class*="fileName"] * {
    background: #07101f !important;
    color: #06101c !important;
    opacity: 1 !important;
}

/* The actual white chip sometimes uses generic button/span classes on Streamlit Cloud. */
div[data-testid="stFileUploader"] div[role="button"],
div[data-testid="stFileUploader"] div[role="button"] *,
div[data-testid="stFileUploader"] button[kind],
div[data-testid="stFileUploader"] button[kind] * {
    color: #ffffff !important;
    opacity: 1 !important;
}

/* If Streamlit insists on a white file chip, force dark visible text inside it. */
div[data-testid="stFileUploader"] [style*="background-color: rgb(255"],
div[data-testid="stFileUploader"] [style*="background-color: rgb(255"] *,
div[data-testid="stFileUploader"] [style*="background: rgb(255"],
div[data-testid="stFileUploader"] [style*="background: rgb(255"] * {
    background: #07101f !important;
    color: #ffffff !important;
    border-color: rgba(110,231,255,0.65) !important;
    opacity: 1 !important;
}

/* Keep uploader helper text bright but not washed out. */
div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] small {
    color: #cdd8ff !important;
    opacity: 1 !important;
}


/* --- Final uploader readability fix v1.7.2 --- */
/* Hide Streamlit's unreadable white uploaded-file chip on Cloud */
div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
div[data-testid="stFileUploader"] ul,
div[data-testid="stFileUploader"] li {
    display: none !important;
}

/* Keep the dropzone itself dark and readable */
div[data-testid="stFileUploader"],
div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
    background: #050914 !important;
    color: #ffffff !important;
    border-color: rgba(110,231,255,0.65) !important;
}

/* Force every remaining uploader text element readable */
div[data-testid="stFileUploader"] *,
div[data-testid="stFileUploader"] label,
div[data-testid="stFileUploader"] p,
div[data-testid="stFileUploader"] span,
div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] button,
div[data-testid="stFileUploader"] button * {
    color: #ffffff !important;
    opacity: 1 !important;
}

/* Custom readable file status panel */
.upload-status-card {
    border: 1px solid rgba(110,231,255,0.35);
    background: linear-gradient(135deg, rgba(7,16,31,0.96), rgba(18,9,29,0.92));
    border-radius: 18px;
    padding: 14px 16px;
    margin: 12px 0 16px 0;
    color: #ffffff !important;
    box-shadow: 0 12px 32px rgba(0,0,0,0.24);
}

.upload-status-card b {
    color: #6ee7ff !important;
}

.upload-status-card span {
    color: #f7fbff !important;
}

</style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Music theory / MIDI helpers
# -----------------------------
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
ROOT_TO_MIDI = {name: 60 + i for i, name in enumerate(NOTE_NAMES)}

SCALES: Dict[str, List[int]] = {
    "Minor / Deep": [0, 2, 3, 5, 7, 8, 10],
    "Dorian / House": [0, 2, 3, 5, 7, 9, 10],
    "Phrygian / Dark Techno": [0, 1, 3, 5, 7, 8, 10],
    "Major / Warm": [0, 2, 4, 5, 7, 9, 11],
    "Lydian / Floating": [0, 2, 4, 6, 7, 9, 11],
    "Whole Tone / IDM Glass": [0, 2, 4, 6, 8, 10],
}

PROGRESSION_RECIPES: Dict[str, List[List[int]]] = {
    "Dub Techno Fog": [[0, 2, 4, 6], [5, 0, 2, 4], [3, 5, 0, 2], [6, 1, 3, 5]],
    "Maya Songs Warm House": [[0, 2, 4, 6], [3, 5, 0, 2], [4, 6, 1, 3], [5, 0, 2, 4]],
    "Boards Memory Drift": [[0, 2, 4], [5, 0, 2], [2, 4, 6], [3, 5, 0]],
    "Alva Noto Glass": [[0, 4, 6], [1, 4, 6], [0, 3, 6], [2, 5, 6]],
    "Underworld Motion Pad": [[0, 2, 4], [0, 3, 5], [5, 0, 2], [3, 5, 1]],
    "Autechre Fragment Bed": [[0, 1, 4], [6, 2, 5], [3, 1, 6], [5, 0, 4]],
}

MODE_DESCRIPTIONS = {
    "Dub Chord Cloud": "Turns notes into smoky filtered chords with delay-friendly long tails.",
    "Ambient Freeze": "Creates long frozen drones from MIDI notes and future sample freeze points.",
    "IDM Fragment": "Breaks notes into unstable micro-loops, reverse ghosts, and pitch scatter.",
    "Micronaut in Detroit": "Warm David Alvarado / deep house inspired pad bed with soft pump and smooth sample tone.",
    "Techno Pressure": "Dark pressure layer for warehouse techno, rumble, and low-mid movement.",
}


@dataclass
class PadNote:
    name: str
    midi: int
    frequency: float
    velocity: int
    start_bar: int
    length_bars: int


def midi_to_frequency(midi_note: int) -> float:
    return 440.0 * (2 ** ((midi_note - 69) / 12))


def midi_to_name(midi_note: int) -> str:
    return f"{NOTE_NAMES[midi_note % 12]}{(midi_note // 12) - 1}"


def generate_pad_notes(root: str, scale_name: str, progression_name: str, bars: int, density: str, octave_shift: int) -> List[PadNote]:
    root_midi = ROOT_TO_MIDI[root] + octave_shift * 12
    scale = SCALES[scale_name]
    progression = PROGRESSION_RECIPES[progression_name]
    notes: List[PadNote] = []

    chord_count = max(1, bars // 2)
    for chord_index in range(chord_count):
        degrees = progression[chord_index % len(progression)]
        start_bar = chord_index * 2
        length_bars = 2

        if density == "Thin":
            selected_degrees = degrees[:2]
        elif density == "Medium":
            selected_degrees = degrees[:3]
        else:
            selected_degrees = degrees[:4]

        for degree in selected_degrees:
            scale_degree = degree % len(scale)
            octave = degree // len(scale)
            midi_note = root_midi + scale[scale_degree] + octave * 12
            midi_note += random.choice([-12, 0, 0, 12]) if density == "Thick" else 0
            velocity = random.randint(70, 108)
            notes.append(
                PadNote(
                    name=midi_to_name(midi_note),
                    midi=midi_note,
                    frequency=midi_to_frequency(midi_note),
                    velocity=velocity,
                    start_bar=start_bar,
                    length_bars=length_bars,
                )
            )
    return notes


def create_midi_file(notes: List[PadNote], bpm: int, bars: int) -> bytes:
    if not MIDO_AVAILABLE:
        return b""

    ticks_per_beat = 480
    mid = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage("track_name", name="PadLoop Lab MIDI Notes", time=0))
    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))

    events: List[Tuple[int, mido.Message]] = []
    for note in notes:
        start_tick = int(round(float(note.start_bar) * 4 * ticks_per_beat))
        end_tick = start_tick + int(round(float(note.length_bars) * 4 * ticks_per_beat))
        events.append((start_tick, mido.Message("note_on", note=note.midi, velocity=note.velocity, time=0)))
        events.append((end_tick, mido.Message("note_off", note=note.midi, velocity=0, time=0)))

    final_tick = bars * 4 * ticks_per_beat
    events.append((final_tick, mido.MetaMessage("end_of_track", time=0)))
    events.sort(key=lambda item: item[0])

    current_tick = 0
    for tick, message in events:
        message.time = int(max(0, tick - current_tick))
        track.append(message)
        current_tick = tick

    output = io.BytesIO()
    mid.save(file=output)
    return output.getvalue()


# -----------------------------
# MIDI piano-roll visualizer/editor helpers
# -----------------------------

def render_midi_piano_roll_svg(notes: List[PadNote], bars: int, width: int = 1100, height: int = 320) -> str:
    """Render an SVG piano-roll style MIDI note visualizer."""
    if not notes:
        return ""

    min_midi = min(note.midi for note in notes) - 2
    max_midi = max(note.midi for note in notes) + 2
    midi_range = max(1, max_midi - min_midi + 1)

    left_pad = 72
    right_pad = 20
    top_pad = 28
    bottom_pad = 34
    grid_w = width - left_pad - right_pad
    grid_h = height - top_pad - bottom_pad

    def x_for_bar(bar_value: float) -> float:
        return left_pad + (bar_value / max(1, bars)) * grid_w

    def y_for_midi(midi_value: int) -> float:
        return top_pad + ((max_midi - midi_value) / midi_range) * grid_h

    grid_lines = []
    for bar in range(bars + 1):
        x = x_for_bar(bar)
        opacity = "0.28" if bar % 4 == 0 else "0.13"
        grid_lines.append(f'<line x1="{x:.2f}" y1="{top_pad}" x2="{x:.2f}" y2="{top_pad + grid_h}" stroke="rgba(255,255,255,{opacity})" stroke-width="1" />')
        if bar < bars:
            grid_lines.append(f'<text x="{x + 4:.2f}" y="{height - 10}" fill="#aeb9d6" font-size="11" font-family="monospace">{bar + 1}</text>')

    note_lines = []
    for midi in range(min_midi, max_midi + 1):
        y = y_for_midi(midi)
        note_lines.append(f'<line x1="{left_pad}" y1="{y:.2f}" x2="{left_pad + grid_w}" y2="{y:.2f}" stroke="rgba(255,255,255,0.08)" stroke-width="1" />')
        if midi % 12 in [0, 2, 4, 5, 7, 9, 11]:
            note_lines.append(f'<text x="10" y="{y + 4:.2f}" fill="#cdd8ff" font-size="10" font-family="monospace">{midi_to_name(midi)}</text>')

    note_rects = []
    for index, note in enumerate(notes):
        x = x_for_bar(float(note.start_bar))
        y = y_for_midi(int(note.midi)) - 7
        w = max(8, (float(note.length_bars) / max(1, bars)) * grid_w)
        velocity_alpha = 0.45 + min(0.45, note.velocity / 127 * 0.45)
        color = "#6ee7ff" if index % 3 == 0 else "#ff66c4" if index % 3 == 1 else "#b8ff6a"
        note_rects.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="14" rx="6" fill="{color}" opacity="{velocity_alpha:.2f}" />'
            f'<text x="{x + 5:.2f}" y="{y + 10:.2f}" fill="#06101c" font-size="9" font-weight="800" font-family="monospace">{note.name}</text>'
        )

    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="24" fill="rgba(5,8,18,0.84)" />'
        f'<text x="18" y="20" fill="#ffffff" font-size="13" font-weight="800" font-family="Inter, sans-serif">MIDI Piano Roll · notes driving the sampler</text>'
        + "".join(grid_lines)
        + "".join(note_lines)
        + "".join(note_rects)
        + "</svg>"
    )


def show_midi_piano_roll(notes: List[PadNote], bars: int, title: str = "MIDI Piano Roll") -> None:
    svg = render_midi_piano_roll_svg(notes, bars)
    if svg:
        st.markdown(
            f"""
            <div class="panel">
                <h3>{title}</h3>
                {svg}
            </div>
            """,
            unsafe_allow_html=True,
        )


def notes_to_editor_rows(notes: List[PadNote]) -> List[Dict[str, float]]:
    return [
        {
            "Note Name": note.name,
            "MIDI": int(note.midi),
            "Start Bar": float(note.start_bar + 1),
            "Length Bars": float(note.length_bars),
            "Velocity": int(note.velocity),
        }
        for note in notes
    ]


def editor_rows_to_notes(rows, bars: int) -> List[PadNote]:
    edited_notes: List[PadNote] = []

    for row in rows:
        try:
            midi_note = int(row.get("MIDI", 60))
            midi_note = max(12, min(120, midi_note))

            start_bar = float(row.get("Start Bar", 1.0)) - 1.0
            start_bar = max(0.0, min(float(bars) - 0.25, start_bar))

            length_bars = float(row.get("Length Bars", 1.0))
            length_bars = max(0.25, min(float(bars), length_bars))

            velocity = int(row.get("Velocity", 90))
            velocity = max(1, min(127, velocity))

            edited_notes.append(
                PadNote(
                    name=midi_to_name(midi_note),
                    midi=midi_note,
                    frequency=midi_to_frequency(midi_note),
                    velocity=velocity,
                    start_bar=start_bar,
                    length_bars=length_bars,
                )
            )
        except Exception:
            continue

    return edited_notes


# -----------------------------
# Audio synthesis / preview helpers
# -----------------------------
def soft_clip(signal: np.ndarray, drive: float) -> np.ndarray:
    return np.tanh(signal * drive) / np.tanh(drive)


def one_pole_lowpass(signal: np.ndarray, cutoff_hz: float, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    cutoff_hz = max(40.0, min(cutoff_hz, sample_rate * 0.45))
    x = math.exp(-2.0 * math.pi * cutoff_hz / sample_rate)
    y = np.zeros_like(signal)
    y[0] = signal[0]
    for i in range(1, len(signal)):
        y[i] = (1.0 - x) * signal[i] + x * y[i - 1]
    return y


# --- waveform/audio helpers ---

def audio_to_wav_bytes(audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> bytes:
    """Convert mono or stereo float audio into 16-bit WAV bytes."""
    if audio.ndim == 1:
        stereo = np.column_stack([audio, audio])
    else:
        stereo = audio

    peak = float(np.max(np.abs(stereo))) if len(stereo) else 0.0
    if peak > 1.0:
        stereo = stereo / peak

    pcm = (np.clip(stereo, -1.0, 1.0) * 32767).astype(np.int16)
    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes())
    return output.getvalue()


def read_wav_bytes_to_audio(wav_bytes: bytes) -> Tuple[Optional[np.ndarray], str]:
    """Read WAV bytes into stereo float32 audio for waveform display."""
    try:
        with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_count = wav_file.getnframes()
            raw = wav_file.readframes(frame_count)
    except Exception as exc:
        return None, f"Could not decode generated WAV: {exc}"

    if sample_width == 1:
        audio = np.frombuffer(raw, dtype=np.uint8).astype(np.float32)
        audio = (audio - 128.0) / 128.0
    elif sample_width == 2:
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sample_width == 3:
        raw_array = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        signed = (
            raw_array[:, 0].astype(np.int32)
            | (raw_array[:, 1].astype(np.int32) << 8)
            | (raw_array[:, 2].astype(np.int32) << 16)
        )
        signed = np.where(signed & 0x800000, signed - 0x1000000, signed)
        audio = signed.astype(np.float32) / 8388608.0
    elif sample_width == 4:
        audio = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        return None, f"Unsupported WAV bit depth: {sample_width * 8}-bit."

    if channels > 1:
        audio = audio.reshape(-1, channels)
    else:
        audio = np.column_stack([audio, audio])

    return audio.astype(np.float32), "Decoded WAV for waveform display."


def render_waveform_svg(audio: np.ndarray, width: int = 1100, height: int = 220) -> str:
    """Create a lightweight SVG waveform from mono or stereo audio."""
    if audio is None or len(audio) == 0:
        return ""

    if audio.ndim > 1:
        mono = audio.mean(axis=1)
    else:
        mono = audio

    mono = np.nan_to_num(mono.astype(np.float32))
    peak = float(np.max(np.abs(mono))) if len(mono) else 0.0
    if peak > 0:
        mono = mono / peak

    bucket_count = min(width, max(80, len(mono) // 80))
    if bucket_count <= 0:
        return ""

    buckets = np.array_split(mono, bucket_count)
    amplitudes = [float(np.max(np.abs(bucket))) if len(bucket) else 0.0 for bucket in buckets]
    center = height / 2
    usable_height = height * 0.82
    bar_width = width / bucket_count

    bars = []
    for index, amp in enumerate(amplitudes):
        x = index * bar_width
        bar_height = max(1.0, amp * usable_height)
        y = center - bar_height / 2
        bars.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{max(1.0, bar_width * 0.72):.2f}" height="{bar_height:.2f}" rx="2" fill="url(#waveGradient)" opacity="0.92" />'
        )

    return f'''
    <svg viewBox="0 0 {width} {height}" width="100%" height="{height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Audio waveform">
        <defs>
            <linearGradient id="waveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#6ee7ff" />
                <stop offset="50%" stop-color="#ff66c4" />
                <stop offset="100%" stop-color="#b8ff6a" />
            </linearGradient>
        </defs>
        <rect x="0" y="0" width="{width}" height="{height}" rx="22" fill="rgba(5,8,18,0.76)" />
        <line x1="0" y1="{center:.2f}" x2="{width}" y2="{center:.2f}" stroke="rgba(255,255,255,0.20)" stroke-width="1" />
        {''.join(bars)}
    </svg>
    '''


def show_waveform(audio: Optional[np.ndarray], label: str) -> None:
    """Display a waveform panel if audio is available."""
    if audio is None:
        return
    svg = render_waveform_svg(audio)
    if svg:
        st.markdown(
            f"""
            <div class="panel">
                <h3>{label}</h3>
                {svg}
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_audio_player(wav_bytes: bytes, label: str, loop_audio: bool) -> None:
    """Show an HTML audio player with optional loop mode."""
    encoded = base64.b64encode(wav_bytes).decode("utf-8")
    loop_attr = "loop" if loop_audio else ""
    mode_label = "Looping" if loop_audio else "Play once"
    st.markdown(
        f"""
        <div class="loop-audio-card">
            <b>{label} — {mode_label}</b>
            <audio controls {loop_attr} preload="metadata">
                <source src="data:audio/wav;base64,{encoded}" type="audio/wav">
            </audio>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- Interactive waveform player ---

def show_interactive_waveform_player(wav_bytes: bytes, label: str, loop_audio: bool, height: int = 330) -> None:
    """Show a real waveform player with a moving playhead and click-to-seek."""
    encoded = base64.b64encode(wav_bytes).decode("utf-8")
    loop_js = "true" if loop_audio else "false"
    safe_id = f"waveplayer_{abs(hash((label, len(wav_bytes), loop_audio))) % 10_000_000}"
    mode_label = "Looping" if loop_audio else "Play once"

    components.html(
        f"""
        <div id="{safe_id}" style="
            box-sizing:border-box;
            width:100%;
            border:1px solid rgba(255,255,255,0.16);
            border-radius:22px;
            padding:16px;
            background:linear-gradient(135deg, rgba(12,18,35,0.98), rgba(28,16,38,0.94));
            color:#ffffff;
            font-family:Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif;
            box-shadow:0 18px 54px rgba(0,0,0,0.26);
        ">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:10px;">
                <div>
                    <div style="font-size:1.05rem; font-weight:800; letter-spacing:-0.02em;">{label}</div>
                    <div style="font-size:0.82rem; color:#aeb9d6; margin-top:3px;">{mode_label} · click the waveform to jump to a spot</div>
                </div>
                <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; justify-content:flex-end;">
                    <button class="playBtn" style="
                        border:1px solid rgba(255,255,255,0.22);
                        border-radius:999px;
                        background:linear-gradient(135deg, rgba(110,231,255,0.26), rgba(255,102,196,0.24));
                        color:#fff;
                        font-weight:900;
                        padding:11px 18px;
                        cursor:pointer;
                    ">▶ Play</button>
                    <button class="stopBtn" style="
                        border:1px solid rgba(255,255,255,0.22);
                        border-radius:999px;
                        background:rgba(255,255,255,0.08);
                        color:#fff;
                        font-weight:900;
                        padding:11px 18px;
                        cursor:pointer;
                    ">■ Stop</button>
                    <button class="loopBtn" style="
                        border:1px solid rgba(184,255,106,0.46);
                        border-radius:999px;
                        background:rgba(184,255,106,0.24);
                        color:#fff;
                        font-weight:900;
                        padding:11px 18px;
                        cursor:pointer;
                    ">↻ Loop On</button>
                    <button class="scrubBtn" style="
                        border:1px solid rgba(110,231,255,0.42);
                        border-radius:999px;
                        background:rgba(110,231,255,0.16);
                        color:#fff;
                        font-weight:900;
                        padding:11px 18px;
                        cursor:pointer;
                    ">⌁ Scrub On</button>
                    <button class="muteBtn" style="
                        border:1px solid rgba(255,255,255,0.22);
                        border-radius:999px;
                        background:rgba(255,255,255,0.08);
                        color:#fff;
                        font-weight:900;
                        padding:11px 14px;
                        cursor:pointer;
                    ">🔊</button>
                    <div style="display:flex; align-items:center; gap:7px; color:#cdd8ff; font-size:0.78rem; font-family:JetBrains Mono, monospace;">
                        <span>VOL</span>
                        <input class="volumeSlider" type="range" min="0" max="100" value="85" style="width:96px; accent-color:#6ee7ff; cursor:pointer;" />
                    </div>
                </div>
            </div>

            <canvas class="waveCanvas" height="170" style="
                width:100%;
                height:170px;
                border-radius:18px;
                background:rgba(5,8,18,0.82);
                display:block;
                cursor:crosshair;
            "></canvas>

            <div style="display:flex; align-items:center; justify-content:space-between; color:#cdd8ff; font-family:JetBrains Mono, monospace; font-size:0.78rem; margin-top:10px;">
                <span class="timeNow">00:00.00</span>
                <span class="spotReadout">spot: 0.0%</span>
                <span class="timeTotal">00:00.00</span>
            </div>

            <audio class="audio" preload="auto">
                <source src="data:audio/wav;base64,{encoded}" type="audio/wav">
            </audio>
        </div>

        <script>
        (async function() {{
            const root = document.getElementById("{safe_id}");
            const audio = root.querySelector(".audio");
            const canvas = root.querySelector(".waveCanvas");
            const ctx = canvas.getContext("2d");
            const playBtn = root.querySelector(".playBtn");
            const stopBtn = root.querySelector(".stopBtn");
            const loopBtn = root.querySelector(".loopBtn");
            const scrubBtn = root.querySelector(".scrubBtn");
            const muteBtn = root.querySelector(".muteBtn");
            const volumeSlider = root.querySelector(".volumeSlider");
            const timeNow = root.querySelector(".timeNow");
            const timeTotal = root.querySelector(".timeTotal");
            const spotReadout = root.querySelector(".spotReadout");
            let loopAudio = {loop_js};
            let scrubMode = true;
            let isScrubbing = false;
            let wasPlayingBeforeScrub = false;
            let scrubAuditionTimer = null;
            let scrubClickSuppressed = false;
            let playerVolume = 0.85;
            let previousVolume = 0.85;
            audio.volume = playerVolume;
            let peaks = [];
            let decodedDuration = 0;
            let audioCtx = null;
            let decodedBuffer = null;
            let scrubSource = null;
            let scrubGain = null;
            let lastScrubAuditionMs = 0;

            function resizeCanvas() {{
                const rect = canvas.getBoundingClientRect();
                const dpr = window.devicePixelRatio || 1;
                canvas.width = Math.max(300, Math.floor(rect.width * dpr));
                canvas.height = Math.floor(170 * dpr);
                ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
                drawWaveform();
            }}

            function fmt(seconds) {{
                if (!isFinite(seconds)) return "00:00.00";
                const m = Math.floor(seconds / 60);
                const s = seconds - m * 60;
                return String(m).padStart(2, "0") + ":" + s.toFixed(2).padStart(5, "0");
            }}

            function refreshLoopButton() {{
                // Use manual looping instead of the native audio.loop attribute.
                // This makes Loop Off immediate: it finishes the current pass and stops,
                // instead of allowing the browser to queue another loop cycle.
                audio.loop = false;
                if (loopAudio) {{
                    loopBtn.textContent = "↻ Loop On";
                    loopBtn.style.background = "rgba(184,255,106,0.24)";
                    loopBtn.style.borderColor = "rgba(184,255,106,0.46)";
                }} else {{
                    loopBtn.textContent = "↻ Loop Off";
                    loopBtn.style.background = "rgba(255,255,255,0.08)";
                    loopBtn.style.borderColor = "rgba(255,255,255,0.22)";
                }}
            }}

            function refreshScrubButton() {{
                if (scrubMode) {{
                    scrubBtn.textContent = "⌁ Scrub On";
                    scrubBtn.style.background = "rgba(110,231,255,0.18)";
                    scrubBtn.style.borderColor = "rgba(110,231,255,0.48)";
                }} else {{
                    scrubBtn.textContent = "⌁ Scrub Off";
                    scrubBtn.style.background = "rgba(255,255,255,0.08)";
                    scrubBtn.style.borderColor = "rgba(255,255,255,0.22)";
                }}
            }}

            function refreshVolumeButton() {{
                if (audio.volume <= 0.001 || audio.muted) {{
                    muteBtn.textContent = "🔇";
                    muteBtn.style.background = "rgba(255,255,255,0.08)";
                    muteBtn.style.borderColor = "rgba(255,255,255,0.22)";
                }} else {{
                    muteBtn.textContent = audio.volume < 0.45 ? "🔉" : "🔊";
                    muteBtn.style.background = "rgba(110,231,255,0.16)";
                    muteBtn.style.borderColor = "rgba(110,231,255,0.42)";
                }}
            }}

            async function ensureAudioContext() {{
                try {{
                    if (!audioCtx) {{
                        const AudioCtx = window.AudioContext || window.webkitAudioContext;
                        audioCtx = new AudioCtx();
                    }}
                    if (audioCtx.state === "suspended") {{
                        await audioCtx.resume();
                    }}
                    return true;
                }} catch (err) {{
                    console.warn("AudioContext could not start:", err);
                    return false;
                }}
            }}

            async function playScrubAuditionAt(seconds) {{
                if (!scrubMode || !decodedBuffer) return;

                const nowMs = performance.now();
                if (nowMs - lastScrubAuditionMs < 42) return;
                lastScrubAuditionMs = nowMs;

                const ready = await ensureAudioContext();
                if (!ready) return;

                try {{
                    if (scrubSource) {{
                        try {{ scrubSource.stop(); }} catch (err) {{}}
                        scrubSource.disconnect();
                        scrubSource = null;
                    }}
                    if (scrubGain) {{
                        try {{ scrubGain.disconnect(); }} catch (err) {{}}
                        scrubGain = null;
                    }}

                    const source = audioCtx.createBufferSource();
                    const gain = audioCtx.createGain();
                    source.buffer = decodedBuffer;
                    gain.gain.setValueAtTime(Math.max(0.001, playerVolume), audioCtx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.18);
                    source.connect(gain);
                    gain.connect(audioCtx.destination);

                    const offset = Math.max(0, Math.min(decodedBuffer.duration - 0.05, seconds));
                    source.start(0, offset, 0.18);
                    scrubSource = source;
                    scrubGain = gain;

                    source.onended = () => {{
                        if (scrubSource === source) scrubSource = null;
                        try {{ gain.disconnect(); }} catch (err) {{}}
                    }};
                }} catch (err) {{
                    console.warn("Scrub audition failed:", err);
                }}
            }}

            function seekFromPointer(event, shouldAudition) {{
                const rect = canvas.getBoundingClientRect();
                const clientX = event.touches && event.touches.length ? event.touches[0].clientX : event.clientX;
                const ratio = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
                const duration = audio.duration || decodedDuration || 0;
                if (duration > 0) {{
                    const targetTime = Math.max(0, Math.min(duration - 0.03, ratio * duration));
                    audio.currentTime = targetTime;
                    timeNow.textContent = fmt(targetTime);
                    spotReadout.textContent = "spot: " + (ratio * 100).toFixed(1) + "% · " + fmt(targetTime);
                    drawWaveform();
                    if (shouldAudition && scrubMode) {{
                        playScrubAuditionAt(targetTime);
                    }}
                }}
            }}

            function drawWaveform() {{
                const rect = canvas.getBoundingClientRect();
                const w = rect.width;
                const h = 170;
                const center = h / 2;

                ctx.clearRect(0, 0, w, h);
                const bg = ctx.createLinearGradient(0, 0, w, h);
                bg.addColorStop(0, "rgba(5,8,18,0.96)");
                bg.addColorStop(1, "rgba(18,10,28,0.96)");
                ctx.fillStyle = bg;
                ctx.fillRect(0, 0, w, h);

                ctx.strokeStyle = "rgba(255,255,255,0.16)";
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(0, center);
                ctx.lineTo(w, center);
                ctx.stroke();

                if (!peaks.length) {{
                    ctx.fillStyle = "rgba(174,185,214,0.72)";
                    ctx.font = "13px Inter, sans-serif";
                    ctx.fillText("Loading waveform...", 18, center - 10);
                    return;
                }}

                const grad = ctx.createLinearGradient(0, 0, w, 0);
                grad.addColorStop(0, "#6ee7ff");
                grad.addColorStop(0.52, "#ff66c4");
                grad.addColorStop(1, "#b8ff6a");
                ctx.fillStyle = grad;

                const step = w / peaks.length;
                for (let i = 0; i < peaks.length; i++) {{
                    const amp = peaks[i];
                    const barH = Math.max(1, amp * h * 0.82);
                    const x = i * step;
                    ctx.globalAlpha = 0.94;
                    ctx.fillRect(x, center - barH / 2, Math.max(1, step * 0.72), barH);
                }}
                ctx.globalAlpha = 1;

                const duration = audio.duration || decodedDuration || 1;
                const progress = Math.max(0, Math.min(1, audio.currentTime / duration));
                const x = progress * w;

                ctx.fillStyle = "rgba(255,255,255,0.12)";
                ctx.fillRect(0, 0, x, h);

                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, h);
                ctx.stroke();

                ctx.fillStyle = "#ffffff";
                ctx.beginPath();
                ctx.arc(x, center, 6, 0, Math.PI * 2);
                ctx.fill();
            }}

            async function buildPeaks() {{
                try {{
                    const response = await fetch("data:audio/wav;base64,{encoded}");
                    const arrayBuffer = await response.arrayBuffer();
                    const AudioCtx = window.AudioContext || window.webkitAudioContext;
                    if (!audioCtx) audioCtx = new AudioCtx();
                    decodedBuffer = await audioCtx.decodeAudioData(arrayBuffer.slice(0));
                    decodedDuration = decodedBuffer.duration;
                    const channelCount = decodedBuffer.numberOfChannels;
                    const length = decodedBuffer.length;
                    const targetPeaks = 900;
                    const blockSize = Math.max(1, Math.floor(length / targetPeaks));
                    peaks = [];
                    for (let i = 0; i < targetPeaks; i++) {{
                        let start = i * blockSize;
                        let end = Math.min(length, start + blockSize);
                        let max = 0;
                        for (let ch = 0; ch < channelCount; ch++) {{
                            const data = decodedBuffer.getChannelData(ch);
                            for (let j = start; j < end; j++) {{
                                const v = Math.abs(data[j]);
                                if (v > max) max = v;
                            }}
                        }}
                        peaks.push(Math.min(1, max));
                    }}
                    timeTotal.textContent = fmt(decodedDuration);
                    drawWaveform();
                }} catch (err) {{
                    console.error(err);
                    peaks = [0.2,0.5,0.3,0.7,0.4,0.2,0.6,0.3,0.5,0.2];
                    drawWaveform();
                }}
            }}

            playBtn.addEventListener("click", async () => {{
                if (audio.paused) {{
                    await audio.play();
                    playBtn.textContent = "⏸ Pause";
                }} else {{
                    audio.pause();
                    playBtn.textContent = "▶ Play";
                }}
            }});

            stopBtn.addEventListener("click", () => {{
                audio.pause();
                audio.currentTime = 0;
                playBtn.textContent = "▶ Play";
                timeNow.textContent = fmt(0);
                drawWaveform();
            }});

            loopBtn.addEventListener("click", () => {{
                loopAudio = !loopAudio;
                refreshLoopButton();
            }});

            scrubBtn.addEventListener("click", () => {{
                scrubMode = !scrubMode;
                refreshScrubButton();
            }});

            muteBtn.addEventListener("click", () => {{
                if (audio.volume > 0.001 && !audio.muted) {{
                    previousVolume = audio.volume;
                    audio.volume = 0;
                    audio.muted = true;
                    volumeSlider.value = 0;
                }} else {{
                    audio.muted = false;
                    audio.volume = previousVolume || 0.85;
                    playerVolume = audio.volume;
                    volumeSlider.value = Math.round(audio.volume * 100);
                }}
                refreshVolumeButton();
            }});

            volumeSlider.addEventListener("input", () => {{
                const value = Number(volumeSlider.value) / 100;
                playerVolume = value;
                audio.volume = value;
                audio.muted = value <= 0.001;
                if (value > 0.001) previousVolume = value;
                refreshVolumeButton();
            }});

            canvas.addEventListener("click", (event) => {{
                if (scrubClickSuppressed) return;
                seekFromPointer(event, false);
            }});

            canvas.addEventListener("mousedown", async (event) => {{
                if (!scrubMode) return;
                isScrubbing = true;
                wasPlayingBeforeScrub = !audio.paused;
                await ensureAudioContext();
                seekFromPointer(event, true);
            }});

            window.addEventListener("mousemove", (event) => {{
                if (!isScrubbing || !scrubMode) return;
                seekFromPointer(event, true);
            }});

            window.addEventListener("mouseup", () => {{
                if (!isScrubbing) return;
                isScrubbing = false;
                scrubClickSuppressed = true;
                if (scrubAuditionTimer) clearTimeout(scrubAuditionTimer);
                if (scrubSource) {{
                    try {{ scrubSource.stop(); }} catch (err) {{}}
                    scrubSource = null;
                }}
                if (!wasPlayingBeforeScrub) {{
                    audio.pause();
                    playBtn.textContent = "▶ Play";
                }}
                drawWaveform();
                setTimeout(() => {{ scrubClickSuppressed = false; }}, 80);
            }});

            canvas.addEventListener("touchstart", async (event) => {{
                if (!scrubMode) return;
                event.preventDefault();
                isScrubbing = true;
                wasPlayingBeforeScrub = !audio.paused;
                await ensureAudioContext();
                seekFromPointer(event, true);
            }}, {{ passive: false }});

            window.addEventListener("touchmove", (event) => {{
                if (!isScrubbing || !scrubMode) return;
                event.preventDefault();
                seekFromPointer(event, true);
            }}, {{ passive: false }});

            window.addEventListener("touchend", () => {{
                if (!isScrubbing) return;
                isScrubbing = false;
                scrubClickSuppressed = true;
                if (scrubAuditionTimer) clearTimeout(scrubAuditionTimer);
                if (scrubSource) {{
                    try {{ scrubSource.stop(); }} catch (err) {{}}
                    scrubSource = null;
                }}
                if (!wasPlayingBeforeScrub) {{
                    audio.pause();
                    playBtn.textContent = "▶ Play";
                }}
                drawWaveform();
                setTimeout(() => {{ scrubClickSuppressed = false; }}, 80);
            }});

            canvas.addEventListener("mousemove", (event) => {{
                const rect = canvas.getBoundingClientRect();
                const ratio = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
                const duration = audio.duration || decodedDuration || 0;
                spotReadout.textContent = "spot: " + (ratio * 100).toFixed(1) + "%" + (duration ? " · " + fmt(ratio * duration) : "");
            }});

            audio.addEventListener("timeupdate", () => {{
                timeNow.textContent = fmt(audio.currentTime);
                drawWaveform();
            }});

            audio.addEventListener("loadedmetadata", () => {{
                timeTotal.textContent = fmt(audio.duration);
                drawWaveform();
            }});

            audio.addEventListener("ended", async () => {{
                if (loopAudio) {{
                    audio.currentTime = 0;
                    try {{
                        await audio.play();
                        playBtn.textContent = "⏸ Pause";
                    }} catch (err) {{
                        playBtn.textContent = "▶ Play";
                    }}
                }} else {{
                    audio.pause();
                    audio.currentTime = 0;
                    playBtn.textContent = "▶ Play";
                    timeNow.textContent = fmt(0);
                    drawWaveform();
                }}
            }});

            window.addEventListener("resize", resizeCanvas);
            refreshLoopButton();
            refreshScrubButton();
            refreshVolumeButton();
            resizeCanvas();
            await buildPeaks();
            setInterval(drawWaveform, 80);
        }})();
        </script>
        """,
        height=height,
        scrolling=False,
    )



# --- Sample-based pad looper helpers ---


def read_wav_upload(uploaded_file) -> Tuple[Optional[np.ndarray], str]:
    """Read a user-uploaded WAV file into a mono float32 numpy array. Supports common WAV bit depths including 8/16/24/32-bit PCM and 32-bit float."""
    if uploaded_file is None:
        return None, "No sample uploaded."

    try:
        uploaded_file.seek(0)
        with wave.open(uploaded_file, "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            source_rate = wav_file.getframerate()
            frame_count = wav_file.getnframes()
            compression = wav_file.getcomptype()
            raw = wav_file.readframes(frame_count)
    except Exception as exc:
        return None, f"Could not read WAV file: {exc}"

    if compression != "NONE":
        return None, "Compressed WAV files are not supported yet. Please export as standard PCM WAV."

    if sample_width == 1:
        audio = np.frombuffer(raw, dtype=np.uint8).astype(np.float32)
        audio = (audio - 128.0) / 128.0
        bit_depth_label = "8-bit PCM"
    elif sample_width == 2:
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        bit_depth_label = "16-bit PCM"
    elif sample_width == 3:
        raw_array = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        signed = (
            raw_array[:, 0].astype(np.int32)
            | (raw_array[:, 1].astype(np.int32) << 8)
            | (raw_array[:, 2].astype(np.int32) << 16)
        )
        signed = np.where(signed & 0x800000, signed - 0x1000000, signed)
        audio = signed.astype(np.float32) / 8388608.0
        bit_depth_label = "24-bit PCM"
    elif sample_width == 4:
        # Most common web/app exports are 32-bit PCM. Some DAWs export 32-bit float WAV;
        # if values look invalid as int PCM, retry as float32.
        int_audio = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
        float_audio = np.frombuffer(raw, dtype=np.float32).astype(np.float32)
        if np.isfinite(float_audio).all() and float(np.nanmax(np.abs(float_audio))) <= 8.0 and float(np.nanmax(np.abs(int_audio))) < 0.0001:
            audio = np.clip(float_audio, -1.0, 1.0)
            bit_depth_label = "32-bit float"
        else:
            audio = int_audio
            bit_depth_label = "32-bit PCM"
    else:
        return None, f"Unsupported WAV bit depth: {sample_width * 8}-bit. Please use 8, 16, 24, or 32-bit WAV."

    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)

    if source_rate != SAMPLE_RATE and len(audio) > 2:
        old_positions = np.linspace(0.0, 1.0, len(audio), endpoint=False)
        new_length = max(2, int(len(audio) * SAMPLE_RATE / source_rate))
        new_positions = np.linspace(0.0, 1.0, new_length, endpoint=False)
        audio = np.interp(new_positions, old_positions, audio).astype(np.float32)

    audio = audio.astype(np.float32)
    audio = np.nan_to_num(audio)
    audio = audio - float(np.mean(audio))
    peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
    if peak > 0:
        audio = audio / peak

    return audio, f"Loaded sample: {channels} channel(s), {source_rate} Hz, {bit_depth_label}, {len(audio) / SAMPLE_RATE:.2f} sec."


# --- AIFF/AIF and multi-format upload support ---

def _read_aiff_extended_float80(raw: bytes) -> float:
    """Decode the 80-bit extended float used by AIFF sample-rate fields."""
    if len(raw) != 10:
        return float(SAMPLE_RATE)
    expon = ((raw[0] & 0x7F) << 8) | raw[1]
    sign = -1 if (raw[0] & 0x80) else 1
    hi_mant = int.from_bytes(raw[2:6], "big", signed=False)
    lo_mant = int.from_bytes(raw[6:10], "big", signed=False)
    if expon == 0 and hi_mant == 0 and lo_mant == 0:
        return 0.0
    mantissa = hi_mant * (2.0 ** -31) + lo_mant * (2.0 ** -63)
    return float(sign * mantissa * (2.0 ** (expon - 16383)))


def _decode_aiff_pcm(raw: bytes, sample_width_bytes: int) -> Tuple[Optional[np.ndarray], str]:
    """Decode big-endian AIFF PCM sample bytes to float32."""
    if sample_width_bytes == 1:
        audio = np.frombuffer(raw, dtype=np.int8).astype(np.float32) / 128.0
        return audio, "8-bit AIFF PCM"
    if sample_width_bytes == 2:
        audio = np.frombuffer(raw, dtype=">i2").astype(np.float32) / 32768.0
        return audio, "16-bit AIFF PCM"
    if sample_width_bytes == 3:
        raw_array = np.frombuffer(raw, dtype=np.uint8)
        usable = (len(raw_array) // 3) * 3
        raw_array = raw_array[:usable].reshape(-1, 3)
        signed = (
            (raw_array[:, 0].astype(np.int32) << 16)
            | (raw_array[:, 1].astype(np.int32) << 8)
            | raw_array[:, 2].astype(np.int32)
        )
        signed = np.where(signed & 0x800000, signed - 0x1000000, signed)
        audio = signed.astype(np.float32) / 8388608.0
        return audio, "24-bit AIFF PCM"
    if sample_width_bytes == 4:
        audio = np.frombuffer(raw, dtype=">i4").astype(np.float32) / 2147483648.0
        return audio, "32-bit AIFF PCM"
    return None, f"Unsupported AIFF bit depth: {sample_width_bytes * 8}-bit. Please use 8, 16, 24, or 32-bit AIFF/AIF."


def read_aiff_upload(uploaded_file) -> Tuple[Optional[np.ndarray], str]:
    """Read a user-uploaded AIFF/AIF file into a mono float32 numpy array."""
    if uploaded_file is None:
        return None, "No sample uploaded."

    try:
        uploaded_file.seek(0)
        data = uploaded_file.read()
    except Exception as exc:
        return None, f"Could not read AIFF file: {exc}"

    if len(data) < 12 or data[0:4] != b"FORM" or data[8:12] not in (b"AIFF", b"AIFC"):
        return None, "This does not look like a valid AIFF/AIF file."

    pos = 12
    channels = None
    frame_count = None
    sample_width_bytes = None
    source_rate = None
    compression = b"NONE"
    sound_data = None

    while pos + 8 <= len(data):
        chunk_id = data[pos:pos + 4]
        chunk_size = int.from_bytes(data[pos + 4:pos + 8], "big", signed=False)
        chunk_start = pos + 8
        chunk_end = min(len(data), chunk_start + chunk_size)
        chunk = data[chunk_start:chunk_end]

        if chunk_id == b"COMM" and len(chunk) >= 18:
            channels = int.from_bytes(chunk[0:2], "big", signed=False)
            frame_count = int.from_bytes(chunk[2:6], "big", signed=False)
            sample_size_bits = int.from_bytes(chunk[6:8], "big", signed=False)
            source_rate = int(round(_read_aiff_extended_float80(chunk[8:18])))
            sample_width_bytes = max(1, int(math.ceil(sample_size_bits / 8)))
            if len(chunk) >= 22:
                compression = chunk[18:22]
        elif chunk_id == b"SSND" and len(chunk) >= 8:
            offset = int.from_bytes(chunk[0:4], "big", signed=False)
            block_size = int.from_bytes(chunk[4:8], "big", signed=False)
            _ = block_size
            sound_data = chunk[8 + offset:]

        pos = chunk_end + (chunk_size % 2)

    if channels is None or frame_count is None or sample_width_bytes is None or source_rate is None or sound_data is None:
        return None, "Could not find required AIFF COMM/SSND chunks."

    if compression not in (b"NONE", b"sowt"):
        return None, "Compressed AIFF/AIFC files are not supported yet. Please export as standard PCM AIFF or WAV."

    decoded, bit_depth_label = _decode_aiff_pcm(sound_data, sample_width_bytes)
    if decoded is None:
        return None, bit_depth_label

    expected_values = frame_count * channels
    if expected_values > 0:
        decoded = decoded[:expected_values]

    if channels > 1 and len(decoded) >= channels:
        decoded = decoded.reshape(-1, channels).mean(axis=1)

    if source_rate != SAMPLE_RATE and len(decoded) > 2:
        old_positions = np.linspace(0.0, 1.0, len(decoded), endpoint=False)
        new_length = max(2, int(len(decoded) * SAMPLE_RATE / source_rate))
        new_positions = np.linspace(0.0, 1.0, new_length, endpoint=False)
        decoded = np.interp(new_positions, old_positions, decoded).astype(np.float32)

    audio = decoded.astype(np.float32)
    audio = np.nan_to_num(audio)
    audio = audio - float(np.mean(audio))
    peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
    if peak > 0:
        audio = audio / peak

    return audio, f"Loaded sample: {channels} channel(s), {source_rate} Hz, {bit_depth_label}, {len(audio) / SAMPLE_RATE:.2f} sec."


def read_audio_upload(uploaded_file) -> Tuple[Optional[np.ndarray], str]:
    """Read WAV, AIF, or AIFF uploads into mono float32 audio for the sampler."""
    if uploaded_file is None:
        return None, "No sample uploaded."
    name = getattr(uploaded_file, "name", "").lower()
    if name.endswith((".aif", ".aiff")):
        return read_aiff_upload(uploaded_file)
    return read_wav_upload(uploaded_file)


def extract_sampler_grain(sample: np.ndarray, freeze_position: float, grain_ms: int) -> np.ndarray:
    """Extract a short crossfaded grain from the uploaded sample."""
    if sample is None or len(sample) < 32:
        return np.zeros(1024, dtype=np.float32)

    grain_size = int(SAMPLE_RATE * grain_ms / 1000)
    grain_size = max(512, min(grain_size, len(sample)))
    start = int((len(sample) - grain_size) * freeze_position)
    start = max(0, min(start, len(sample) - grain_size))
    grain = sample[start:start + grain_size].copy().astype(np.float32)

    fade_size = min(len(grain) // 4, int(SAMPLE_RATE * 0.025))
    if fade_size > 4:
        fade_in = np.linspace(0.0, 1.0, fade_size, dtype=np.float32)
        fade_out = np.linspace(1.0, 0.0, fade_size, dtype=np.float32)
        grain[:fade_size] *= fade_in
        grain[-fade_size:] *= fade_out

    peak = np.max(np.abs(grain)) if len(grain) else 0
    if peak > 0:
        grain = grain / peak
    return grain


def pitch_resample_grain(grain: np.ndarray, semitones: float, target_length: int) -> np.ndarray:
    """Transpose a grain by resampling, then tile it to the requested length."""
    if len(grain) < 4 or target_length <= 0:
        return np.zeros(max(1, target_length), dtype=np.float32)

    ratio = 2 ** (semitones / 12.0)
    pitched_length = max(4, int(len(grain) / ratio))
    old_positions = np.linspace(0.0, 1.0, len(grain), endpoint=False)
    new_positions = np.linspace(0.0, 1.0, pitched_length, endpoint=False)
    pitched = np.interp(new_positions, old_positions, grain).astype(np.float32)

    repeats = int(np.ceil(target_length / len(pitched))) + 1
    tiled = np.tile(pitched, repeats)[:target_length].astype(np.float32)

    # Tiny loop smoothing so the repeated grain feels more pad-like.
    fade = min(256, max(8, len(pitched) // 12))
    if fade < len(tiled) // 2:
        for pos in range(len(pitched), len(tiled), len(pitched)):
            lo = max(0, pos - fade)
            hi = min(len(tiled), pos + fade)
            if hi > lo:
                window = np.linspace(0.92, 1.0, hi - lo, dtype=np.float32)
                tiled[lo:hi] *= window

    return tiled



def render_sample_pad_audio(
    sample: np.ndarray,
    notes: List[PadNote],
    bpm: int,
    bars: int,
    mode: str,
    movement: float,
    warmth: float,
    width: float,
    pump: float,
    freeze_position: float,
    grain_ms: int,
    root: str,
) -> bytes:
    """Render a real sample-based pad loop guided by generated MIDI notes."""
    seconds_per_bar = 60.0 / bpm * 4.0
    total_seconds = bars * seconds_per_bar
    total_samples = int(total_seconds * SAMPLE_RATE)
    t = np.linspace(0, total_seconds, total_samples, endpoint=False)

    base_grain = extract_sampler_grain(sample, freeze_position, grain_ms)
    root_midi = ROOT_TO_MIDI[root] - 12

    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    for note in notes:
        start_sec = note.start_bar * seconds_per_bar
        end_sec = min(total_seconds, start_sec + note.length_bars * seconds_per_bar)
        start_idx = int(start_sec * SAMPLE_RATE)
        end_idx = int(end_sec * SAMPLE_RATE)
        length = end_idx - start_idx
        if length <= 0:
            continue

        semitones = note.midi - root_midi
        layer = pitch_resample_grain(base_grain, semitones, length)
        nt = np.linspace(0, note.length_bars * seconds_per_bar, length, endpoint=False)

        attack = max(1, int(0.20 * SAMPLE_RATE))
        release = max(1, int(0.55 * SAMPLE_RATE))
        env = np.ones(length, dtype=np.float32)
        env[: min(attack, length)] *= np.linspace(0, 1, min(attack, length))
        env[-min(release, length):] *= np.linspace(1, 0, min(release, length))

        slow_amp = 0.82 + 0.18 * np.sin(2 * np.pi * (0.035 + movement * 0.08) * nt + note.midi)
        layer = layer * env * slow_amp * (note.velocity / 127.0)

        if mode == "IDM Fragment":
            gate_rate = 2.0 + movement * 14.0
            gate = (np.sin(2 * np.pi * gate_rate * nt + note.midi) > -0.10).astype(np.float32)
            layer *= gate
        elif mode == "Dub Chord Cloud":
            layer = one_pole_lowpass(layer, 900 + warmth * 1800)
        elif mode == "Ambient Freeze":
            layer = one_pole_lowpass(layer, 650 + warmth * 2400)
        elif mode == "Techno Pressure":
            sub = np.sin(2 * np.pi * note.frequency * 0.25 * nt).astype(np.float32) * 0.07
            layer = layer + sub * env
        elif mode == "Micronaut in Detroit":
            layer = soft_clip(layer, 1.2 + warmth)

        pan = random.Random(note.midi + 99).uniform(-width, width)
        l_gain = math.cos((pan + 1) * math.pi / 4)
        r_gain = math.sin((pan + 1) * math.pi / 4)
        left[start_idx:end_idx] += layer * l_gain
        right[start_idx:end_idx] += layer * r_gain

    beat_phase = (t * bpm / 60.0) % 1.0
    duck = 1.0 - pump * np.exp(-beat_phase * 8.5)
    left *= duck
    right *= duck

    cutoff = 700 + warmth * 3800 + movement * 700
    left = one_pole_lowpass(left, cutoff)
    right = one_pole_lowpass(right, cutoff * 1.05)

    left = soft_clip(left, 1.2 + warmth * 1.8)
    right = soft_clip(right, 1.2 + warmth * 1.8)

    stereo = np.column_stack([left, right])
    peak = float(np.max(np.abs(stereo))) if len(stereo) else 0.0
    if peak > 0:
        stereo = stereo / peak * 0.86

    pcm = (stereo * 32767).astype(np.int16)
    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm.tobytes())
    return output.getvalue()


# --- MIDI-triggered sample playback for sampler mode ---
def render_midi_triggered_sample_audio(
    sample: np.ndarray,
    notes: List[PadNote],
    bpm: int,
    bars: int,
    mode: str,
    movement: float,
    warmth: float,
    width: float,
    pump: float,
    root: str,
    hybrid_blur: bool = False,
) -> bytes:
    """Render the uploaded sample as if generated MIDI notes are triggering a sampler."""
    seconds_per_bar = 60.0 / bpm * 4.0
    total_seconds = bars * seconds_per_bar
    total_samples = int(total_seconds * SAMPLE_RATE)
    t = np.linspace(0, total_seconds, total_samples, endpoint=False)

    clean_sample = np.nan_to_num(sample.astype(np.float32))
    if len(clean_sample) < 32:
        clean_sample = np.zeros(1024, dtype=np.float32)

    root_midi = ROOT_TO_MIDI[root] - 12
    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    for note in notes:
        start_sec = note.start_bar * seconds_per_bar
        note_seconds = note.length_bars * seconds_per_bar
        if hybrid_blur:
            note_seconds += 1.25
        end_sec = min(total_seconds, start_sec + note_seconds)
        start_idx = int(start_sec * SAMPLE_RATE)
        end_idx = int(end_sec * SAMPLE_RATE)
        target_length = end_idx - start_idx
        if target_length <= 0:
            continue

        semitones = note.midi - root_midi
        layer = pitch_resample_grain(clean_sample, semitones, target_length)
        nt = np.linspace(0, note_seconds, target_length, endpoint=False)

        attack_time = 0.015 if not hybrid_blur else 0.16
        release_time = 0.18 if not hybrid_blur else 0.85
        attack = max(1, int(attack_time * SAMPLE_RATE))
        release = max(1, int(release_time * SAMPLE_RATE))
        env = np.ones(target_length, dtype=np.float32)
        env[: min(attack, target_length)] *= np.linspace(0, 1, min(attack, target_length))
        env[-min(release, target_length):] *= np.linspace(1, 0, min(release, target_length))

        if mode == "IDM Fragment":
            gate_rate = 3.0 + movement * 18.0
            gate = (np.sin(2 * np.pi * gate_rate * nt + note.midi) > -0.18).astype(np.float32)
            layer *= gate
        elif mode == "Dub Chord Cloud":
            layer = one_pole_lowpass(layer, 900 + warmth * 2200)
        elif mode == "Ambient Freeze":
            layer = one_pole_lowpass(layer, 600 + warmth * 2600)
        elif mode == "Techno Pressure":
            layer = one_pole_lowpass(layer, 500 + warmth * 2400)
        elif mode == "Micronaut in Detroit":
            layer = soft_clip(layer, 1.15 + warmth)

        layer = layer * env * (note.velocity / 127.0)

        if hybrid_blur:
            slow_amp = 0.86 + 0.14 * np.sin(2 * np.pi * (0.045 + movement * 0.07) * nt + note.midi)
            layer *= slow_amp

        pan = random.Random(note.midi + 177).uniform(-width, width)
        l_gain = math.cos((pan + 1) * math.pi / 4)
        r_gain = math.sin((pan + 1) * math.pi / 4)
        left[start_idx:end_idx] += layer * l_gain
        right[start_idx:end_idx] += layer * r_gain

    beat_phase = (t * bpm / 60.0) % 1.0
    duck = 1.0 - pump * np.exp(-beat_phase * 8.5)
    left *= duck
    right *= duck

    cutoff = 800 + warmth * 4200 + movement * 700
    left = one_pole_lowpass(left, cutoff)
    right = one_pole_lowpass(right, cutoff * 1.06)

    left = soft_clip(left, 1.15 + warmth * 1.7)
    right = soft_clip(right, 1.15 + warmth * 1.7)

    stereo = np.column_stack([left, right])
    peak = float(np.max(np.abs(stereo))) if len(stereo) else 0.0
    if peak > 0:
        stereo = stereo / peak * 0.86

    pcm = (stereo * 32767).astype(np.int16)
    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm.tobytes())
    return output.getvalue()


def render_pad_audio(
    notes: List[PadNote],
    bpm: int,
    bars: int,
    mode: str,
    movement: float,
    warmth: float,
    width: float,
    pump: float,
) -> bytes:
    seconds_per_bar = 60.0 / bpm * 4.0
    total_seconds = bars * seconds_per_bar
    total_samples = int(total_seconds * SAMPLE_RATE)
    t = np.linspace(0, total_seconds, total_samples, endpoint=False)

    left = np.zeros(total_samples, dtype=np.float32)
    right = np.zeros(total_samples, dtype=np.float32)

    mode_detune = {
        "Dub Chord Cloud": 0.004,
        "Ambient Freeze": 0.002,
        "IDM Fragment": 0.012,
        "Micronaut in Detroit": 0.003,
        "Techno Pressure": 0.006,
    }.get(mode, 0.004)

    for note in notes:
        start_sec = note.start_bar * seconds_per_bar
        end_sec = min(total_seconds, start_sec + note.length_bars * seconds_per_bar)
        start_idx = int(start_sec * SAMPLE_RATE)
        end_idx = int(end_sec * SAMPLE_RATE)
        if end_idx <= start_idx:
            continue

        nt = t[start_idx:end_idx] - start_sec
        length = len(nt)
        attack = max(1, int(0.18 * SAMPLE_RATE))
        release = max(1, int(0.42 * SAMPLE_RATE))
        env = np.ones(length, dtype=np.float32)
        env[: min(attack, length)] *= np.linspace(0, 1, min(attack, length))
        env[-min(release, length):] *= np.linspace(1, 0, min(release, length))

        f = note.frequency
        wobble = 1.0 + np.sin(2 * np.pi * (0.04 + movement * 0.08) * nt) * mode_detune
        osc1 = np.sin(2 * np.pi * f * wobble * nt)
        osc2 = np.sin(2 * np.pi * (f * 0.501) * nt + 0.8)
        osc3 = np.sin(2 * np.pi * (f * 1.005) * nt + 1.7)
        tone = (osc1 * 0.48 + osc2 * 0.32 + osc3 * 0.20) * env * (note.velocity / 127.0)

        if mode == "IDM Fragment":
            gate_rate = 2.0 + movement * 10.0
            gate = (np.sin(2 * np.pi * gate_rate * nt) > -0.25).astype(np.float32)
            random_mask = np.random.default_rng(note.midi).uniform(0.78, 1.0, length)
            tone *= gate * random_mask
        elif mode == "Techno Pressure":
            tone += 0.14 * np.sin(2 * np.pi * (f * 0.25) * nt) * env
        elif mode == "Dub Chord Cloud":
            tone += 0.10 * np.sin(2 * np.pi * (f * 0.999) * nt + np.sin(nt * 0.2)) * env
        elif mode == "Micronaut in Detroit":
            tone = np.sign(tone) * np.sqrt(np.abs(tone)) * env

        pan = random.Random(note.midi).uniform(-width, width)
        l_gain = math.cos((pan + 1) * math.pi / 4)
        r_gain = math.sin((pan + 1) * math.pi / 4)
        left[start_idx:end_idx] += tone * l_gain
        right[start_idx:end_idx] += tone * r_gain

    # Tempo pump / sidechain feel.
    beat_phase = (t * bpm / 60.0) % 1.0
    duck = 1.0 - pump * np.exp(-beat_phase * 8.5)
    left *= duck
    right *= duck

    cutoff = 850 + warmth * 3400 + movement * 600
    left = one_pole_lowpass(left, cutoff)
    right = one_pole_lowpass(right, cutoff * 1.08)

    left = soft_clip(left, 1.4 + warmth * 1.8)
    right = soft_clip(right, 1.4 + warmth * 1.8)

    stereo = np.column_stack([left, right])
    peak = np.max(np.abs(stereo))
    if peak > 0:
        stereo = stereo / peak * 0.86

    pcm = (stereo * 32767).astype(np.int16)
    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm.tobytes())
    return output.getvalue()



# --- Built-in oscillator samples ---
def generate_builtin_sample(
    waveform: str,
    root: str,
    octave: int,
    duration_seconds: float,
    tone: float,
) -> Tuple[np.ndarray, str]:
    """Generate a built-in mono sample source so users do not need to upload audio."""
    duration_seconds = max(0.25, min(12.0, float(duration_seconds)))
    total_samples = int(SAMPLE_RATE * duration_seconds)
    t = np.linspace(0, duration_seconds, total_samples, endpoint=False)

    midi_note = ROOT_TO_MIDI[root] + (int(octave) - 4) * 12
    frequency = midi_to_frequency(midi_note)
    phase = frequency * t

    if waveform == "Sine":
        audio = np.sin(2 * np.pi * phase)
    elif waveform == "Triangle":
        audio = (2.0 / np.pi) * np.arcsin(np.sin(2 * np.pi * phase))
    elif waveform == "Square":
        audio = np.sign(np.sin(2 * np.pi * phase))
    elif waveform == "Sawtooth":
        audio = 2.0 * (phase - np.floor(phase + 0.5))
    elif waveform == "Sub Sine":
        audio = (
            0.72 * np.sin(2 * np.pi * phase * 0.5)
            + 0.28 * np.sin(2 * np.pi * phase)
        )
    elif waveform == "Noise Texture":
        rng = np.random.default_rng(404)
        audio = rng.normal(0, 0.45, total_samples).astype(np.float32)
        audio = one_pole_lowpass(audio, 350 + tone * 3800)
        audio += 0.18 * np.sin(2 * np.pi * phase)
    else:
        audio = np.sin(2 * np.pi * phase)

    audio = np.nan_to_num(audio.astype(np.float32))

    # Simple tone shaping and anti-harshness.
    if waveform in ["Square", "Sawtooth", "Noise Texture"]:
        cutoff = 500 + tone * 5200
        audio = one_pole_lowpass(audio, cutoff)

    # Soft fade to avoid clicks.
    fade_size = min(len(audio) // 5, int(SAMPLE_RATE * 0.035))
    if fade_size > 8:
        fade_in = np.linspace(0.0, 1.0, fade_size, dtype=np.float32)
        fade_out = np.linspace(1.0, 0.0, fade_size, dtype=np.float32)
        audio[:fade_size] *= fade_in
        audio[-fade_size:] *= fade_out

    peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
    if peak > 0:
        audio = audio / peak

    label = f"Built-in {waveform}: {root}{octave}, {frequency:.2f} Hz, {duration_seconds:.2f} sec."
    return audio.astype(np.float32), label


# -----------------------------
# UI
# -----------------------------
st.markdown(
    f"""
    <div class="hero">
        <h1>◈ {APP_TITLE}</h1>
        <p>{APP_SUBTITLE}</p>
        <div class="badge-row">
            <div class="badge">MIDI NOTES → PAD BED</div>
            <div class="badge">SAMPLE LOOPER CONCEPT</div>
            <div class="badge">DUB / HOUSE / AMBIENT / IDM</div>
            <div class="badge">ABLETON-READY EXPORTS</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### ◈ Pad Engine")
    bpm = st.slider("Tempo", 70, 150, 122)
    bars = st.selectbox("Loop Length", [4, 8, 16], index=1)
    root = st.selectbox("Root Note", NOTE_NAMES, index=0)
    scale_name = st.selectbox("Scale / Color", list(SCALES.keys()), index=1)
    progression_name = st.selectbox("MIDI Generator Recipe", list(PROGRESSION_RECIPES.keys()), index=1)
    density = st.selectbox("Pad Density", ["Thin", "Medium", "Thick"], index=1)
    octave_shift = st.slider("Octave Shift", -2, 2, -1)

    st.markdown("### ◇ Audio Mood")
    mode = st.selectbox("Looper Mode", list(MODE_DESCRIPTIONS.keys()), index=3)
    movement = st.slider("Movement", 0.0, 1.0, 0.42)
    warmth = st.slider("Warmth / Saturation", 0.0, 1.0, 0.66)
    width = st.slider("Stereo Width", 0.0, 1.0, 0.72)
    pump = st.slider("Club Pump", 0.0, 0.85, 0.22)

    st.markdown("### ◎ Sampler Source")
    use_sampler = st.checkbox("Use sampler/audio source", value=True)
    sample_source_choice = st.radio(
        "Sample Source",
        ["Upload Your Own", "Sample Pool"],
        index=0,
        help="Upload your own audio, or choose a simple built-in wave from the small sample pool.",
    )
    built_in_waveform = st.selectbox(
        "Sample Pool Wave",
        ["None", "Sine", "Triangle", "Square", "Sawtooth", "Sub Sine", "Noise Texture"],
        index=0,
        help="Choose None if you do not want a built-in sample. Pick a wave only when you want to use the sample pool.",
    )
    built_in_octave = st.slider("Built-in Wave Octave", 1, 5, 2)
    built_in_duration = st.slider("Built-in Wave Length", 0.25, 8.0, 2.0, step=0.25)
    built_in_tone = st.slider("Built-in Wave Tone", 0.0, 1.0, 0.55)
    sample_playback_style = st.radio(
        "Sample Playback Style",
        ["Freeze Pad", "MIDI Clip Sampler", "Hybrid"],
        index=0,
        help="Freeze Pad turns one sample grain into a pad. MIDI Clip Sampler triggers the uploaded sample from the generated MIDI notes. Hybrid triggers the sample but blurs it into a pad.",
    )
    playback_mode = st.radio("Audio Player Mode", ["Loop", "Play once"], index=0, horizontal=True)
    loop_audio = playback_mode == "Loop"
    freeze_position = st.slider("Sample Freeze Position", 0.0, 1.0, 0.42)
    grain_ms = st.slider("Sampler Grain Size", 60, 2000, 420)

    randomize = st.button("Randomize beautiful pad settings")

if randomize:
    bpm = random.choice([92, 98, 105, 112, 118, 122, 126, 130, 136])
    root = random.choice(NOTE_NAMES)
    scale_name = random.choice(list(SCALES.keys()))
    progression_name = random.choice(list(PROGRESSION_RECIPES.keys()))
    density = random.choice(["Thin", "Medium", "Thick"])
    octave_shift = random.choice([-2, -1, -1, 0])
    mode = random.choice(list(MODE_DESCRIPTIONS.keys()))
    movement = random.uniform(0.15, 0.85)
    warmth = random.uniform(0.35, 0.92)
    width = random.uniform(0.45, 0.95)
    pump = random.uniform(0.04, 0.55)

notes = generate_pad_notes(root, scale_name, progression_name, bars, density, octave_shift)

metrics = st.columns(5)
metrics[0].metric("Tempo", f"{bpm} BPM")
metrics[1].metric("Length", f"{bars} bars")
metrics[2].metric("Root", root)
metrics[3].metric("Scale", scale_name.split(" /")[0])
metrics[4].metric("Notes", len(notes))

tab_build, tab_sample, tab_perform, tab_export = st.tabs([
    "Build Pad",
    "Sample Looper",
    "Performance View",
    "Export",
])

with tab_build:
    left_col, right_col = st.columns([1.1, 0.9])

    with left_col:
        st.markdown(
            f"""
            <div class="panel">
                <h3>Current engine: {mode}</h3>
                <p style="color:#aeb9d6;">{MODE_DESCRIPTIONS[mode]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        note_rows = []
        for note in notes:
            note_rows.append(
                {
                    "Note": note.name,
                    "MIDI": note.midi,
                    "Frequency": round(note.frequency, 2),
                    "Velocity": note.velocity,
                    "Start Bar": note.start_bar + 1,
                    "Length Bars": note.length_bars,
                }
            )
        st.dataframe(note_rows, use_container_width=True, hide_index=True)

    with right_col:
        st.markdown("""
        <div class="panel">
            <h3>Integration idea</h3>
            <div class="mini-card"><b>MIDI Generator Brain</b><span>Creates the harmonic notes, root, mode, density, voicing, and progression.</span></div><br>
            <div class="mini-card"><b>Audio Looper Body</b><span>Uses those notes to guide pitch, freeze points, chord beds, and exported pad loops.</span></div><br>
            <div class="mini-card"><b>Ableton Workflow</b><span>Export MIDI + WAV together, then drag both into Ableton for instant arrangement layers.</span></div>
        </div>
        """, unsafe_allow_html=True)

with tab_sample:
    st.markdown("""
    <div class="panel">
        <h3>Real Sampler Engine</h3>
        <p style="color:#aeb9d6;">Choose a built-in wave or upload/drag-and-drop your own sample. PadLoop Lab will use the MIDI chords above to re-pitch, layer, and loop that audio into a playable pad bed.</p>
    </div>
    <div class="drop-zone-panel">
        <h3>⇣ Drag & Drop Sample Zone</h3>
        <p>Choose from the small Sample Pool, or drop a <b>WAV, AIF, AIFF, MP3, MP4, or M4A</b> file onto the uploader below. Chord stabs, synth notes, vocal tones, Rhodes hits, field recordings, noise loops, and texture samples all work.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drag and drop a WAV, AIF, AIFF, MP3, MP4, or M4A sample here, or click Browse Files",
        type=["wav", "aif", "aiff", "mp3", "mp4", "m4a"],
        accept_multiple_files=False,
        help="Drag a WAV, AIF, AIFF, MP3, MP4, or M4A file from Finder directly onto this uploader. MP3/MP4/M4A decoding requires pydub and ffmpeg.",
    )
    sample_audio, sample_status = read_audio_upload(uploaded)

    if sample_source_choice == "Sample Pool":
        if built_in_waveform == "None":
            sample_audio = None
            sample_status = "No sample pool wave selected."
            st.info("Sample Pool is available, but nothing is selected yet. Choose Sine, Triangle, Square, Sawtooth, Sub Sine, or Noise Texture when you want to use a built-in source.")
        else:
            sample_audio, sample_status = generate_builtin_sample(
                built_in_waveform,
                root,
                built_in_octave,
                built_in_duration,
                built_in_tone,
            )
            browser_preview_bytes = audio_to_wav_bytes(sample_audio)
            show_interactive_waveform_player(browser_preview_bytes, f"Sample Pool source — {built_in_waveform}", loop_audio)
            st.success(sample_status)
            st.markdown(
                f"""
                <div class="panel">
                    <h3>Sample Pool source is active</h3>
                    <p style="color:#aeb9d6;">You selected <b>{built_in_waveform}</b> from the small sample pool. Current sampler style: <b>{sample_playback_style}</b>. This is only used because you chose it; otherwise the app waits for your uploaded sample.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    elif uploaded:
        if sample_audio is not None:
            browser_preview_bytes = audio_to_wav_bytes(sample_audio)
            show_interactive_waveform_player(browser_preview_bytes, "Original uploaded sample", loop_audio)
            st.success(sample_status)
            st.markdown(
                f"""
                <div class="panel">
                    <h3>Sampler routing is active</h3>
                    <p style="color:#aeb9d6;">The player above already shows the waveform and moving playhead. Current sampler style: <b>{sample_playback_style}</b>. Freeze Pad grabs a grain around <b>{freeze_position:.0%}</b> using a <b>{grain_ms} ms</b> window. MIDI Clip Sampler uses the generated MIDI notes to trigger and pitch the uploaded sample like an instrument.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.error(sample_status)
    else:
        st.info("Choose from the small Sample Pool, or upload a chord stab, synth note, vocal tone, Rhodes hit, field recording, noise loop, or any short audio file. Then go to Export to generate the sample-based pad loop.")

    st.markdown("""
    <div class="panel">
        <h3>How this works</h3>
        <p style="color:#aeb9d6;">MIDI generator = harmony brain. Uploaded WAV = oscillator/source. Sampler engine = re-pitches the sample to every chord note, crossfades the layers, adds warmth, movement, stereo width, and club pump.</p>
    </div>
    """, unsafe_allow_html=True)

with tab_perform:
    st.markdown("""
    <div class="panel">
        <h3>Performance View</h3>
        <p style="color:#aeb9d6;">These are the live-scene ideas for the finished looper. Later, these can become big buttons, keyboard shortcuts, or MIDI-mappable controls.</p>
    </div>
    """, unsafe_allow_html=True)

    pad_cols = st.columns(4)
    controls = [
        ("Freeze", "Hold a tiny slice and turn it into a drone."),
        ("Reverse Ghost", "Add reversed shadows behind the pad."),
        ("Dub Wash", "Push delay/reverb into a long tail."),
        ("Half Speed", "Drop the loop into darker time."),
        ("Glitch Dust", "IDM fragments and little unstable cuts."),
        ("Warm House", "Soft organ/Rhodes-style pad thickening."),
        ("Pressure", "Low-mid techno tension layer."),
        ("Make Less Obvious", "Blur sample identity into texture."),
    ]
    for index, (label, desc) in enumerate(controls):
        with pad_cols[index % 4]:
            st.markdown(f"<div class='mini-card'><b>{label}</b><span>{desc}</span></div>", unsafe_allow_html=True)

with tab_export:
    st.markdown("""
    <div class="panel">
        <h3>Export the current idea</h3>
        <p style="color:#aeb9d6;">Download a generated WAV pad preview and matching MIDI notes. Drag both into Ableton: WAV for instant texture, MIDI for controlling your own synth or sampler.</p>
    </div>
    """, unsafe_allow_html=True)

    if sample_source_choice == "Sample Pool" and built_in_waveform != "None":
        sample_audio, sample_status = generate_builtin_sample(
            built_in_waveform,
            root,
            built_in_octave,
            built_in_duration,
            built_in_tone,
        )
    else:
        sample_audio, sample_status = read_audio_upload(uploaded) if "uploaded" in locals() else (None, "No sample uploaded.")

    st.markdown("""
    <div class="panel">
        <h3>MIDI Notes Driving This Export</h3>
        <p style="color:#aeb9d6;">Edit these notes before rendering. Change MIDI for pitch, Start Bar for timing, Length Bars for duration, and Velocity for level.</p>
    </div>
    """, unsafe_allow_html=True)

    editable_rows = st.data_editor(
        notes_to_editor_rows(notes),
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Note Name": st.column_config.TextColumn("Note Name", disabled=True),
            "MIDI": st.column_config.NumberColumn("MIDI", min_value=12, max_value=120, step=1),
            "Start Bar": st.column_config.NumberColumn("Start Bar", min_value=1.0, max_value=float(bars), step=0.25),
            "Length Bars": st.column_config.NumberColumn("Length Bars", min_value=0.25, max_value=float(bars), step=0.25),
            "Velocity": st.column_config.NumberColumn("Velocity", min_value=1, max_value=127, step=1),
        },
        key="export_midi_note_editor",
    )

    edited_notes = editor_rows_to_notes(editable_rows, bars)
    if not edited_notes:
        edited_notes = notes

    show_midi_piano_roll(edited_notes, bars, "Visual MIDI Piano Roll")

    if use_sampler and sample_audio is not None:
        if sample_playback_style == "MIDI Clip Sampler":
            wav_bytes = render_midi_triggered_sample_audio(
                sample_audio,
                edited_notes,
                bpm,
                bars,
                mode,
                movement,
                warmth,
                width,
                pump,
                root,
                hybrid_blur=False,
            )
            st.success("Using the generated MIDI notes to trigger and pitch the uploaded sample like a sampler instrument.")
        elif sample_playback_style == "Hybrid":
            wav_bytes = render_midi_triggered_sample_audio(
                sample_audio,
                edited_notes,
                bpm,
                bars,
                mode,
                movement,
                warmth,
                width,
                pump,
                root,
                hybrid_blur=True,
            )
            st.success("Using the generated MIDI notes to trigger the sample, then blurring it into a pad-like layer.")
        else:
            wav_bytes = render_sample_pad_audio(
                sample_audio,
                edited_notes,
                bpm,
                bars,
                mode,
                movement,
                warmth,
                width,
                pump,
                freeze_position,
                grain_ms,
                root,
            )
            st.success("Using uploaded WAV as a freeze/grain source for this pad loop.")
    else:
        wav_bytes = render_pad_audio(edited_notes, bpm, bars, mode, movement, warmth, width, pump)
        if use_sampler:
            st.warning("No usable uploaded WAV found yet, so this export is using the internal synth preview. Upload a WAV in the Sample Looper tab to activate the sampler.")
        else:
            st.info("Using internal synth preview. Turn on sampler mode and upload a WAV to generate audio from your own sample.")

    midi_bytes = create_midi_file(edited_notes, bpm, bars)

    show_interactive_waveform_player(wav_bytes, "Generated pad loop preview", loop_audio)

    source_label = sample_playback_style.lower().replace(" ", "_") if use_sampler and sample_audio is not None else "synth"
    name_stub = f"padloop_{source_label}_{root}_{scale_name.split(' /')[0].lower()}_{mode.lower().replace(' ', '_')}_{bpm}bpm_{bars}bars"
    dl_cols = st.columns(2)
    with dl_cols[0]:
        st.download_button(
            "Download WAV Pad Loop",
            data=wav_bytes,
            file_name=f"{name_stub}.wav",
            mime="audio/wav",
            use_container_width=True,
        )
    with dl_cols[1]:
        if MIDO_AVAILABLE:
            st.download_button(
                "Download Matching MIDI Notes",
                data=midi_bytes,
                file_name=f"{name_stub}.mid",
                mime="audio/midi",
                use_container_width=True,
            )
        else:
            st.warning("Install mido to enable MIDI export: pip install mido")

st.caption("PadLoop Lab v1.7.2 — fixed unreadable Streamlit upload chip by hiding it and adding a readable loaded-file status panel.")