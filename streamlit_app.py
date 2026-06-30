#CS230 Final Project
#Karina Wu

import plotly.express as px
import plotly.graph_objects as go
try:
    from streamlit_lottie import st_lottie
except ModuleNotFoundError:
    def st_lottie(*args, **kwargs):
        return None

import streamlit as st
import pandas as pd
import random
import math
import json
import os
import textwrap
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(
    page_title="LEGO Quest",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# DATA LOADING

DATA_FILE = "LegoUSACanada.xlsx"

FALLBACK_STORES = [
    {
        "Store Name": "LEGO Store — Rockefeller Center",
        "City": "New York",
        "State": "NY",
        "Country": "USA",
        "ZIP": "10020",
        "Full Address": "636 5th Ave, New York, NY 10020",
        "Latitude": 40.7590,
        "Longitude": -73.9777,
        "Explore Score": 98,
        "Theme": "Flagship City Quest",
        "Nearby Fun": "Rockefeller Center, Nintendo NY, Bryant Park, Times Square",
    },
    {
        "Store Name": "LEGO Store — Flatiron District",
        "City": "New York",
        "State": "NY",
        "Country": "USA",
        "ZIP": "10010",
        "Full Address": "200 5th Ave, New York, NY 10010",
        "Latitude": 40.7410,
        "Longitude": -73.9897,
        "Explore Score": 94,
        "Theme": "Urban Builder Quest",
        "Nearby Fun": "Eataly, Madison Square Park, Flatiron Building, cafés",
    },
    {
        "Store Name": "LEGO Store — Natick Mall",
        "City": "Natick",
        "State": "MA",
        "Country": "USA",
        "ZIP": "01760",
        "Full Address": "1245 Worcester St, Natick, MA 01760",
        "Latitude": 42.3009,
        "Longitude": -71.3846,
        "Explore Score": 89,
        "Theme": "Mall Adventure Quest",
        "Nearby Fun": "Natick Mall, dessert shops, coffee, family shopping",
    },
    {
        "Store Name": "LEGO Store — Burlington Mall",
        "City": "Burlington",
        "State": "MA",
        "Country": "USA",
        "ZIP": "01803",
        "Full Address": "75 Middlesex Turnpike, Burlington, MA 01803",
        "Latitude": 42.4850,
        "Longitude": -71.2148,
        "Explore Score": 86,
        "Theme": "Suburban Explorer Quest",
        "Nearby Fun": "Burlington Mall, cafés, family restaurants, toy browsing",
    },
    {
        "Store Name": "LEGO Store — Disney Springs",
        "City": "Orlando",
        "State": "FL",
        "Country": "USA",
        "ZIP": "32830",
        "Full Address": "1672 E Buena Vista Dr, Orlando, FL 32830",
        "Latitude": 28.3702,
        "Longitude": -81.5180,
        "Explore Score": 99,
        "Theme": "Legendary Vacation Quest",
        "Nearby Fun": "Disney Springs, World of Disney, dessert spots, lakeside walk",
    },
]


def load_store_data():
    try:
        if Path(DATA_FILE).exists():
            df = pd.read_excel(DATA_FILE)
            return df
    except Exception:
        pass
    return pd.DataFrame(FALLBACK_STORES)


df = load_store_data()

# Normalize common columns
for col in ["Store Name", "City", "State", "Country", "ZIP", "Full Address", "Explore Score", "Theme", "Nearby Fun"]:
    if col not in df.columns:
        df[col] = ""

if "Explore Score" not in df.columns or df["Explore Score"].astype(str).str.len().sum() == 0:
    df["Explore Score"] = [random.randint(72, 99) for _ in range(len(df))]

# SESSION STATE

def init_state():
    defaults = {
        "screen": "Quest Map",
        "xp": 0,
        "coins": 1250,
        "gems": 32,
        "visited": [],
        "collection": [],
        "last_drop": None,
        "show_reward": False,
        "zip_code": "",
        "active_store": None,
        "avatar_name": "LULU",
        "avatar_face": "Sparkle Smile",
        "avatar_hair": "Bubble Ponytail",
        "avatar_outfit": "Quest Hoodie",
        "avatar_accessory": "Star Glasses",
        "avatar_color": "Yellow Pop",
        "sound": True,
        "stress_mode": 3,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# GAME CONTENT

DROPS = [
    {
        "id": "city_builder",
        "name": "City Builder",
        "rarity": "Common",
        "series": "LEGO City",
        "icon": "🏙️",
        "xp": 10,
        "color": "#006DB7",
        "fact": "LEGO City sets are designed around everyday rescue, transport, and city-building stories.",
        "quote": "Build the block. Own the street.",
        "minifig": "👷",
        "power": "Street Planning",
    },
    {
        "id": "space_explorer",
        "name": "Space Explorer",
        "rarity": "Common",
        "series": "LEGO Space",
        "icon": "🚀",
        "xp": 10,
        "color": "#006DB7",
        "fact": "Classic LEGO Space is one of the most iconic adventure themes in LEGO history.",
        "quote": "Tiny rocket. Giant dream.",
        "minifig": "👨‍🚀",
        "power": "Orbit Jump",
    },
    {
        "id": "botanical_dreamer",
        "name": "Botanical Dreamer",
        "rarity": "Common",
        "series": "LEGO Botanicals",
        "icon": "🌸",
        "xp": 12,
        "color": "#25A9E0",
        "fact": "LEGO Botanicals turn flowers and plants into displayable building experiences.",
        "quote": "Grow beauty from bricks.",
        "minifig": "🧚",
        "power": "Flower Bloom",
    },
    {
        "id": "ninja_kai",
        "name": "Ninja Kai",
        "rarity": "Rare",
        "series": "LEGO NINJAGO",
        "icon": "🥷",
        "xp": 25,
        "color": "#8E44AD",
        "fact": "NINJAGO combines martial arts, dragons, elemental powers, and team adventure.",
        "quote": "Spin fast. Strike bright.",
        "minifig": "🥷",
        "power": "Spin Dash",
    },
    {
        "id": "pirate_captain",
        "name": "Brickbeard Captain",
        "rarity": "Rare",
        "series": "LEGO Pirates",
        "icon": "🏴‍☠️",
        "xp": 25,
        "color": "#8E44AD",
        "fact": "LEGO Pirates helped define treasure-hunting play with ships, islands, and secret maps.",
        "quote": "Treasure hides under every tile.",
        "minifig": "🧔",
        "power": "Treasure Radar",
    },
    {
        "id": "galaxy_pilot",
        "name": "Galaxy Pilot",
        "rarity": "Epic",
        "series": "LEGO Icons",
        "icon": "🛸",
        "xp": 50,
        "color": "#F5A623",
        "fact": "Advanced LEGO display sets often use complex building techniques for collectors.",
        "quote": "The map is only the launchpad.",
        "minifig": "🧑‍🚀",
        "power": "Hyperdrive",
    },
    {
        "id": "dragon_guardian",
        "name": "Golden Dragon",
        "rarity": "Legendary",
        "series": "LEGO Mythic Quest",
        "icon": "🐉",
        "xp": 100,
        "color": "#FF4FD8",
        "fact": "Dragon builds are often collector favorites because they combine fantasy, motion, and display value.",
        "quote": "A legendary pull chooses its builder.",
        "minifig": "🐲",
        "power": "Rainbow Flame",
    },
]

RARITY_WEIGHTS = {
    "Common": 62,
    "Rare": 25,
    "Epic": 10,
    "Legendary": 3,
}

RARITY_CLASS = {
    "Common": "common-card",
    "Rare": "rare-card",
    "Epic": "epic-card",
    "Legendary": "legendary-card",
}

RARITY_GLOW = {
    "Common": "#006DB7",
    "Rare": "#8E44AD",
    "Epic": "#FFD500",
    "Legendary": "#FF4FD8",
}

AVATAR_PARTS = {
    "face": ["Sparkle Smile", "Cool Wink", "Brave Hero", "Sleepy Builder", "Mischief Mode"],
    "hair": ["Bubble Ponytail", "Messy Star Hair", "Space Helmet", "Red Cap", "Ninja Hood"],
    "outfit": ["Quest Hoodie", "Blue Explorer Jacket", "Red Racing Suit", "Pastel Dream Fit", "Golden Armor"],
    "accessory": ["Star Glasses", "Tiny Backpack", "Headphones", "Magic Wand", "Camera"],
    "color": ["Yellow Pop", "LEGO Red", "Ocean Blue", "Candy Purple", "Gold Shine"],
}


def player_level():
    return st.session_state.xp // 100 + 1


def xp_progress():
    return st.session_state.xp % 100


def collection_names():
    return [item["name"] for item in st.session_state.collection]


def unique_collection_count():
    return len(set(collection_names()))


def get_drop():
    weighted_pool = []
    for item in DROPS:
        weighted_pool.extend([item] * RARITY_WEIGHTS[item["rarity"]])
    return random.choice(weighted_pool)


def store_to_dict(row):
    data = {}
    for col in df.columns:
        try:
            value = row[col]
            if pd.isna(value):
                value = ""
            data[col] = value
        except Exception:
            data[col] = ""
    return data


def choose_stores(zipcode=""):
    if df.empty:
        return FALLBACK_STORES[:3]
    sample_n = min(4, len(df))
    if zipcode:
        exact = df[df["ZIP"].astype(str).str.contains(str(zipcode)[:3], na=False)]
        if len(exact) > 0:
            return [store_to_dict(row) for _, row in exact.head(sample_n).iterrows()]
    ranked = df.copy()
    try:
        ranked["Explore Score"] = pd.to_numeric(ranked["Explore Score"], errors="coerce").fillna(80)
        ranked = ranked.sort_values("Explore Score", ascending=False)
    except Exception:
        pass
    return [store_to_dict(row) for _, row in ranked.head(sample_n).iterrows()]


# GLOBAL CSS

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@600;700;800;900&display=swap');

:root {
    --lego-red: #E3000B;
    --lego-yellow: #FFD500;
    --lego-blue: #006DB7;
    --cream: #FFF4D8;
    --ink: #1E1E1E;
    --green: #22A447;
    --purple: #8E44AD;
    --gold: #F5A623;
}

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(255,213,0,.35), transparent 18%),
        radial-gradient(circle at 86% 12%, rgba(0,109,183,.22), transparent 22%),
        radial-gradient(circle at 50% 90%, rgba(227,0,11,.16), transparent 24%),
        linear-gradient(180deg, #FFF7DE 0%, #DFF8FF 48%, #FFF0C4 100%);
    color: var(--ink);
    overflow-x: hidden;
}

[data-testid="stSidebar"], [data-testid="collapsedControl"] {
    display: none !important;
}

.block-container {
    padding-top: 0.7rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 1500px !important;
}

h1, h2, h3, h4 {
    font-family: 'Fredoka', sans-serif;
}

#MainMenu, footer, header {
    visibility: hidden;
}

button[kind="primary"], .stButton > button {
    background: linear-gradient(180deg, #FFF176 0%, #FFD500 55%, #FFB000 100%) !important;
    color: #1E1E1E !important;
    border: 5px solid white !important;
    border-radius: 999px !important;
    padding: 0.8rem 1.6rem !important;
    font-family: 'Fredoka', sans-serif !important;
    font-weight: 900 !important;
    font-size: 1.05rem !important;
    box-shadow: 0 8px 0 #B67800, 0 16px 28px rgba(0,0,0,.24) !important;
    transition: all .18s ease !important;
}

.stButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 11px 0 #B67800, 0 22px 34px rgba(0,0,0,.25) !important;
}

.stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stSlider {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
}

.stTextInput input {
    border-radius: 18px !important;
    border: 4px solid white !important;
    box-shadow: 0 8px 0 rgba(0,0,0,.10) !important;
    background: rgba(255,255,255,.92) !important;
    padding: 1rem !important;
}

.game-frame {
    position: relative;
    min-height: 890px;
    border-radius: 38px;
    border: 8px solid rgba(255,255,255,.94);
    overflow: hidden;
    background:
        radial-gradient(circle at 22% 16%, rgba(255,255,255,.95), transparent 10%),
        radial-gradient(circle at 88% 18%, rgba(255,255,255,.75), transparent 9%),
        linear-gradient(180deg,#7ED6FF 0%, #A9EAFF 33%, #CFF6FF 47%, #FFF2C2 100%);
    box-shadow:
        0 32px 90px rgba(0,0,0,.28),
        inset 0 0 0 2px rgba(255,255,255,.45);
}

.game-frame:before {
    content:"";
    position:absolute;
    inset:0;
    background:
        radial-gradient(circle at 12% 72%, rgba(255,213,0,.28), transparent 20%),
        radial-gradient(circle at 80% 70%, rgba(227,0,11,.18), transparent 19%),
        radial-gradient(circle at 52% 42%, rgba(255,255,255,.26), transparent 18%);
    pointer-events:none;
    z-index:1;
}

.cloud {
    position: absolute;
    background: rgba(255,255,255,.92);
    border-radius: 999px;
    filter: drop-shadow(0 12px 16px rgba(0,0,0,.08));
    animation: cloudDrift 18s ease-in-out infinite alternate;
    z-index: 2;
}
.cloud:before, .cloud:after {
    content:"";
    position:absolute;
    background: rgba(255,255,255,.95);
    border-radius:50%;
}
.cloud-one { width: 180px; height: 54px; left: 7%; top: 13%; animation-duration: 21s; }
.cloud-one:before { width:72px; height:72px; left:28px; top:-32px; }
.cloud-one:after { width:92px; height:92px; right:28px; top:-46px; }
.cloud-two { width: 230px; height: 62px; right: 9%; top: 21%; animation-duration: 25s; }
.cloud-two:before { width:88px; height:88px; left:42px; top:-42px; }
.cloud-two:after { width:110px; height:110px; right:38px; top:-58px; }
.cloud-three { width: 145px; height: 46px; left: 42%; top: 8%; opacity:.74; animation-duration: 19s; }
.cloud-three:before { width:60px; height:60px; left:26px; top:-28px; }
.cloud-three:after { width:78px; height:78px; right:16px; top:-38px; }

@keyframes cloudDrift {
    from { transform: translateX(-15px) translateY(0); }
    to { transform: translateX(22px) translateY(6px); }
}

.particle-field span {
    position:absolute;
    width:8px;
    height:8px;
    border-radius:50%;
    background:rgba(255,255,255,.85);
    z-index:3;
    animation: sparkle 3.5s infinite ease-in-out;
}

@keyframes sparkle {
    0%,100% { transform: scale(.4); opacity:.2; }
    50% { transform: scale(1.3); opacity:1; }
}

.brick-rain span {
    position: absolute;
    top: -70px;
    width: 30px;
    height: 24px;
    border-radius: 7px;
    box-shadow: inset 0 5px rgba(255,255,255,.35), 0 7px 0 rgba(0,0,0,.20);
    z-index: 18;
    animation: brickRain 7s linear infinite;
}
.brick-rain span:before,
.brick-rain span:after {
    content:"";
    position:absolute;
    top:5px;
    width:8px;
    height:8px;
    border-radius:50%;
    background:rgba(255,255,255,.36);
}
.brick-rain span:before { left:7px; }
.brick-rain span:after { right:7px; }

@keyframes brickRain {
    0% { transform: translateY(-90px) rotate(0deg); opacity:0; }
    10% { opacity:1; }
    100% { transform: translateY(980px) rotate(760deg); opacity:0; }
}

.top-hud {
    position: relative;
    z-index: 30;
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding: 22px 26px 0 26px;
}

.logo-badge {
    display:flex;
    align-items:center;
    gap:14px;
    background: linear-gradient(180deg,#FF2730 0%, #E3000B 52%, #9A0006 100%);
    border: 6px solid #FFD500;
    color:white;
    border-radius: 26px;
    padding: 14px 24px;
    font-family:'Fredoka', sans-serif;
    font-size: 26px;
    font-weight:900;
    letter-spacing:.5px;
    box-shadow: 0 11px 0 #6B0004, 0 20px 34px rgba(0,0,0,.28);
    transform: rotate(-1deg);
}
.logo-cube {
    width: 38px;
    height: 30px;
    background:#FFD500;
    border-radius: 8px;
    position:relative;
    box-shadow: inset 0 5px rgba(255,255,255,.36), 0 5px 0 rgba(0,0,0,.18);
}
.logo-cube:before,
.logo-cube:after {
    content:"";
    position:absolute;
    top:6px;
    width:8px;
    height:8px;
    background:rgba(255,255,255,.5);
    border-radius:50%;
}
.logo-cube:before { left:8px; }
.logo-cube:after { right:8px; }

.hud-right {
    display:flex;
    gap:12px;
    align-items:center;
}
.hud-pill {
    display:flex;
    align-items:center;
    gap:8px;
    background: rgba(255,255,255,.88);
    backdrop-filter: blur(10px);
    border: 4px solid white;
    border-radius:999px;
    padding: 11px 17px;
    font-family:'Fredoka', sans-serif;
    font-weight:900;
    font-size:17px;
    box-shadow: 0 9px 0 rgba(0,0,0,.12), 0 18px 30px rgba(0,0,0,.12);
}
.avatar-hud {
    width:56px;
    height:56px;
    display:grid;
    place-items:center;
    border-radius:50%;
    background: linear-gradient(180deg,#FFD500,#FF9F00);
    border:4px solid white;
    font-size:30px;
    box-shadow: 0 8px 0 rgba(0,0,0,.14);
}

.quest-world {
    position: relative;
    z-index: 12;
    margin: 22px 26px 0 26px;
    height: 610px;
    border: 8px solid rgba(255,255,255,.94);
    border-radius: 42px;
    overflow: hidden;
    background:
        linear-gradient(180deg, rgba(255,255,255,.28), rgba(255,255,255,0) 20%),
        linear-gradient(150deg, #00A6FF 0%, #00A6FF 34%, #6ED36E 35%, #42B849 68%, #2E9A3A 100%);
    box-shadow: 0 30px 70px rgba(0,0,0,.30), inset 0 0 0 2px rgba(255,255,255,.45);
}
.quest-world:before {
    content:"";
    position:absolute;
    inset:0;
    background-image:
        linear-gradient(30deg, rgba(255,255,255,.22) 12%, transparent 12.5%, transparent 87%, rgba(255,255,255,.22) 87.5%),
        linear-gradient(150deg, rgba(0,0,0,.08) 12%, transparent 12.5%, transparent 87%, rgba(0,0,0,.08) 87.5%);
    background-size: 76px 76px;
    opacity:.38;
    z-index:1;
}

.world-copy {
    position:absolute;
    left:48px;
    top:42px;
    z-index:12;
    color:white;
    max-width:430px;
}
.world-copy h1 {
    font-size: 82px;
    line-height:.82;
    margin: 0;
    color:white;
    text-shadow: 0 9px 0 rgba(0,0,0,.18), 0 16px 28px rgba(0,0,0,.22);
}
.world-copy p {
    margin-top:18px;
    font-size: 20px;
    line-height:1.25;
    font-weight:900;
    text-shadow:0 4px 10px rgba(0,0,0,.22);
}
.world-chip-row {
    display:flex;
    flex-wrap:wrap;
    gap:10px;
    margin-top:22px;
}
.world-chip {
    background:rgba(255,255,255,.92);
    color:#1E1E1E;
    border:3px solid white;
    border-radius:18px;
    padding:12px 15px;
    font-family:'Fredoka', sans-serif;
    font-weight:900;
    box-shadow:0 8px 0 rgba(0,0,0,.14), 0 14px 24px rgba(0,0,0,.12);
}

.river {
    position:absolute;
    right:-40px;
    bottom:56px;
    width:720px;
    height:126px;
    background: linear-gradient(180deg,#58D7FF,#0077C8);
    border: 6px solid rgba(255,255,255,.7);
    border-radius: 999px;
    transform: rotate(-16deg);
    box-shadow: inset 0 12px rgba(255,255,255,.28), 0 18px 30px rgba(0,0,0,.18);
    z-index:3;
}
.road {
    position:absolute;
    right:90px;
    top:130px;
    width:690px;
    height:72px;
    background: linear-gradient(180deg,#FFECC6,#D7A25A);
    border-radius:999px;
    border:6px solid rgba(255,255,255,.75);
    transform: rotate(18deg);
    z-index:3;
    box-shadow: inset 0 8px rgba(255,255,255,.3), 0 15px 24px rgba(0,0,0,.16);
}
.road:after {
    content:"";
    position:absolute;
    left:35px;
    right:35px;
    top:30px;
    height:8px;
    border-radius:999px;
    background: repeating-linear-gradient(90deg, rgba(255,255,255,.88) 0 36px, transparent 36px 72px);
}

.lego-tree {
    position:absolute;
    z-index:5;
    width:50px;
    height:72px;
}
.lego-tree .top {
    position:absolute;
    top:0;
    left:4px;
    width:48px;
    height:48px;
    border-radius:14px;
    background:linear-gradient(180deg,#6DF26D,#159B39);
    border:4px solid rgba(255,255,255,.8);
    box-shadow:0 12px 0 #0B6E25, 0 18px 18px rgba(0,0,0,.18);
}
.lego-tree .trunk {
    position:absolute;
    bottom:0;
    left:20px;
    width:18px;
    height:34px;
    background:#9B5A24;
    border-radius:7px;
    box-shadow:0 8px 0 #63360F;
}
.tree-a { right: 640px; top: 350px; }
.tree-b { right: 520px; top: 275px; transform:scale(.8); }
.tree-c { right: 110px; top: 365px; transform:scale(1.1); }
.tree-d { right: 370px; top: 90px; transform:scale(.9); }

.lego-building {
    position:absolute;
    z-index:7;
    width:190px;
    height:158px;
    right:240px;
    top:145px;
    border-radius:22px;
    border:8px solid white;
    background:linear-gradient(180deg,#FFF176,#FFD500 54%,#D99A00);
    box-shadow:0 24px 0 #996800, 0 38px 48px rgba(0,0,0,.36);
    text-align:center;
    padding-top:38px;
    font-family:'Fredoka', sans-serif;
    font-size:22px;
    font-weight:900;
}
.lego-building:before {
    content:"";
    position:absolute;
    top:-26px;
    left:28px;
    right:28px;
    height:30px;
    background:#FFD500;
    border:6px solid white;
    border-radius:16px 16px 0 0;
    box-shadow: inset 0 6px rgba(255,255,255,.32);
}
.lego-building span {
    background:#E3000B;
    color:white;
    border:4px solid white;
    border-radius:14px;
    padding:10px 24px;
    box-shadow:0 7px 0 rgba(0,0,0,.18);
}

.quest-pin {
    position:absolute;
    z-index:12;
    width:74px;
    height:74px;
    border-radius:50% 50% 50% 0;
    transform:rotate(-45deg);
    border:7px solid white;
    box-shadow: 0 0 24px rgba(255,213,0,.75), 0 14px 28px rgba(0,0,0,.32);
    animation: pinPulse 1.4s infinite ease-in-out;
}
.quest-pin:after {
    content:"";
    position:absolute;
    width:22px;
    height:22px;
    border-radius:50%;
    background:white;
    top:18px;
    left:18px;
}
.pin-red { background:#E3000B; right: 345px; top: 75px; animation-delay:.2s; }
.pin-blue { background:#006DB7; right: 585px; top: 235px; animation-delay:.5s; }
.pin-yellow { background:#FFD500; right: 90px; top: 205px; animation-delay:.8s; }
.pin-purple { background:#8E44AD; right: 430px; bottom: 92px; animation-delay:1.1s; }

@keyframes pinPulse {
    0%,100% { transform: rotate(-45deg) translateY(0) scale(1); }
    50% { transform: rotate(-45deg) translateY(-12px) scale(1.07); }
}

.drop-beacon {
    position:absolute;
    z-index:15;
    right: 540px;
    bottom: 75px;
    width: 112px;
    height: 142px;
    border-radius: 28px;
    border: 8px solid white;
    background:
        radial-gradient(circle at 50% 22%, rgba(255,255,255,.65), transparent 20%),
        linear-gradient(180deg,#D56BFF,#6B00C9 54%,#25005A);
    display:grid;
    place-items:center;
    color:white;
    font-size:78px;
    font-weight:900;
    box-shadow:0 0 45px rgba(255,213,0,.95), 0 24px 42px rgba(0,0,0,.35);
    animation: beaconFloat 1.35s ease-in-out infinite;
}
.drop-beacon:before {
    content:"";
    position:absolute;
    inset:-26px;
    border-radius:36px;
    background:radial-gradient(circle, rgba(255,213,0,.45), transparent 58%);
    z-index:-1;
    animation: auraPulse 1.35s ease-in-out infinite;
}
@keyframes beaconFloat {
    0%,100% { transform:translateY(0) rotate(-2deg); }
    50% { transform:translateY(-12px) rotate(2deg); }
}
@keyframes auraPulse {
    0%,100% { transform:scale(.9); opacity:.55; }
    50% { transform:scale(1.12); opacity:1; }
}

.checkin-floating {
    position:absolute;
    z-index:25;
    right:34px;
    bottom:34px;
    background:linear-gradient(180deg,#FFF176,#FFD500 55%,#F39B00);
    border:6px solid white;
    border-radius:999px;
    padding:20px 34px;
    font-family:'Fredoka', sans-serif;
    font-weight:900;
    font-size:25px;
    color:#1E1E1E;
    box-shadow:0 13px 0 #A56A00, 0 24px 42px rgba(0,0,0,.28);
    animation: checkBounce 1.3s infinite ease-in-out;
}
@keyframes checkBounce {
    0%,100% { transform:translateY(0); }
    50% { transform:translateY(-8px); }
}

.zip-panel {
    position:absolute;
    z-index:24;
    left:40px;
    bottom:34px;
    width:380px;
    padding:18px;
    border-radius:26px;
    border:5px solid white;
    background:rgba(255,255,255,.90);
    backdrop-filter: blur(12px);
    box-shadow:0 14px 0 rgba(0,0,0,.10), 0 26px 45px rgba(0,0,0,.20);
}
.zip-panel-title {
    font-family:'Fredoka', sans-serif;
    font-weight:900;
    font-size:20px;
    color:#006DB7;
    margin-bottom:8px;
}

.bottom-nav-game {
    position: relative;
    z-index: 35;
    display:grid;
    grid-template-columns: repeat(5, 1fr);
    gap:14px;
    margin:18px 26px 0 26px;
    padding:14px;
    border-radius:30px;
    border:6px solid white;
    background:rgba(255,255,255,.88);
    backdrop-filter: blur(14px);
    box-shadow:0 16px 0 rgba(0,0,0,.10), 0 30px 55px rgba(0,0,0,.20);
}
.nav-item {
    text-align:center;
    border-radius:20px;
    padding:13px 8px;
    background:linear-gradient(180deg,#FFFFFF,#F1F1F1);
    border:3px solid white;
    font-family:'Fredoka', sans-serif;
    font-weight:900;
    box-shadow:0 8px 0 rgba(0,0,0,.12);
}
.nav-active {
    background:linear-gradient(180deg,#FFF176,#FFD500);
    box-shadow:0 8px 0 #C88900, 0 0 24px rgba(255,213,0,.58);
}
.nav-icon { font-size:25px; display:block; }

.floating-panel {
    position: relative;
    z-index: 20;
    border-radius:30px;
    border:6px solid white;
    background:rgba(255,255,255,.90);
    backdrop-filter: blur(10px);
    box-shadow:0 15px 0 rgba(0,0,0,.10), 0 28px 48px rgba(0,0,0,.18);
    overflow:hidden;
}
.panel-head {
    padding:14px 18px;
    color:white;
    font-family:'Fredoka', sans-serif;
    font-weight:900;
    font-size:20px;
}
.panel-body { padding:18px; }
.blue-head { background:#006DB7; }
.red-head { background:#E3000B; }
.yellow-head { background:#FFD500; color:#1E1E1E; }
.green-head { background:#22A447; }
.purple-head { background:#8E44AD; }

.quest-list-row {
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:12px 0;
    border-bottom:1px solid rgba(0,0,0,.08);
    font-weight:900;
}
.reward-pill {
    background:#FFF3C4;
    border:3px solid white;
    border-radius:999px;
    padding:6px 10px;
    box-shadow:0 5px 0 rgba(0,0,0,.09);
    font-family:'Fredoka', sans-serif;
}

.reward-overlay {
    position: relative;
    z-index: 100;
    margin: 20px 26px;
    min-height: 650px;
    border-radius: 42px;
    border: 8px solid white;
    overflow: hidden;
    background:
        radial-gradient(circle at center, rgba(255,213,0,.95), transparent 18%),
        radial-gradient(circle at 50% 50%, rgba(255,255,255,.55), transparent 28%),
        linear-gradient(135deg,#12001F,#25005A 45%,#000 100%);
    box-shadow:0 35px 90px rgba(0,0,0,.42);
    animation: rewardScene .8s ease-out;
}
@keyframes rewardScene {
    from { transform:scale(.96); opacity:0; filter:blur(8px); }
    to { transform:scale(1); opacity:1; filter:blur(0); }
}

.burst-brick {
    position:absolute;
    left:50%;
    top:50%;
    width:34px;
    height:26px;
    border-radius:7px;
    box-shadow:inset 0 5px rgba(255,255,255,.36), 0 7px 0 rgba(0,0,0,.22);
    animation: burstOut 1.4s ease-out forwards;
}
.burst-brick:before,
.burst-brick:after {
    content:"";
    position:absolute;
    top:5px;
    width:8px;
    height:8px;
    border-radius:50%;
    background:rgba(255,255,255,.38);
}
.burst-brick:before { left:7px; }
.burst-brick:after { right:7px; }
@keyframes burstOut {
    0% { transform:translate(0,0) scale(.3) rotate(0deg); opacity:1; }
    72% { opacity:1; }
    100% { transform:translate(var(--x), var(--y)) scale(1.05) rotate(820deg); opacity:0; }
}

.collectible-card {
    position:absolute;
    left:50%;
    top:50%;
    width:340px;
    min-height:480px;
    transform:translate(-50%,-50%);
    border-radius:34px;
    border:7px solid rgba(255,255,255,.9);
    padding:22px;
    color:white;
    text-align:center;
    box-shadow:0 0 70px rgba(255,213,0,.75), 0 35px 85px rgba(0,0,0,.55);
    animation: cardReveal 1s cubic-bezier(.2,1.1,.2,1) both;
    overflow:hidden;
}
.collectible-card:before {
    content:"";
    position:absolute;
    inset:-60%;
    background:linear-gradient(115deg, transparent 35%, rgba(255,255,255,.52) 48%, transparent 60%);
    animation: shine 2.8s infinite;
    z-index:1;
}
.collectible-card > * { position:relative; z-index:2; }
@keyframes cardReveal {
    0% { transform:translate(-50%,-35%) scale(.35) rotateY(120deg) rotate(-12deg); opacity:0; }
    60% { transform:translate(-50%,-52%) scale(1.07) rotateY(-10deg) rotate(3deg); opacity:1; }
    100% { transform:translate(-50%,-50%) scale(1) rotateY(0deg) rotate(0); opacity:1; }
}
@keyframes shine {
    0% { transform:translateX(-30%) rotate(0deg); }
    100% { transform:translateX(30%) rotate(0deg); }
}
.common-card { background:linear-gradient(135deg,#006DB7,#00A6FF); }
.rare-card { background:linear-gradient(135deg,#4A148C,#9B4DFF); }
.epic-card { background:linear-gradient(135deg,#3A2400,#FFD500,#FF8C00); }
.legendary-card {
    background:linear-gradient(45deg,#ff004c,#ff9900,#ffee00,#33ff00,#00ffee,#0066ff,#cc00ff);
    background-size:400% 400%;
    animation: cardReveal 1s cubic-bezier(.2,1.1,.2,1) both, holoShift 4.5s linear infinite;
}
@keyframes holoShift {
    0% { background-position:0% 50%; }
    50% { background-position:100% 50%; }
    100% { background-position:0% 50%; }
}
.card-rarity {
    display:inline-block;
    padding:8px 14px;
    border-radius:999px;
    background:rgba(255,255,255,.24);
    border:2px solid rgba(255,255,255,.75);
    font-family:'Fredoka', sans-serif;
    font-weight:900;
    letter-spacing:.8px;
}
.card-figure {
    margin:18px auto 8px auto;
    width:170px;
    height:170px;
    display:grid;
    place-items:center;
    border-radius:32px;
    background:rgba(255,255,255,.22);
    border:5px solid rgba(255,255,255,.7);
    font-size:92px;
    box-shadow:inset 0 8px rgba(255,255,255,.22), 0 18px 32px rgba(0,0,0,.25);
}
.card-name {
    font-family:'Fredoka', sans-serif;
    font-size:34px;
    font-weight:900;
    line-height:1;
    margin-top:12px;
    text-shadow:0 5px 0 rgba(0,0,0,.16);
}
.card-series {
    margin-top:8px;
    font-weight:900;
    opacity:.95;
}
.card-fact {
    margin-top:16px;
    background:rgba(255,255,255,.22);
    border:2px solid rgba(255,255,255,.45);
    border-radius:18px;
    padding:12px;
    font-weight:800;
    line-height:1.25;
}
.card-xp {
    margin-top:15px;
    display:inline-block;
    background:#FFD500;
    color:#1E1E1E;
    border:4px solid white;
    border-radius:999px;
    padding:9px 18px;
    font-family:'Fredoka', sans-serif;
    font-weight:900;
    box-shadow:0 7px 0 rgba(0,0,0,.18);
}

.collection-grid {
    display:grid;
    grid-template-columns:repeat(4, minmax(160px, 1fr));
    gap:18px;
}
.dex-card {
    border-radius:28px;
    border:6px solid white;
    padding:20px;
    min-height:260px;
    text-align:center;
    box-shadow:0 14px 0 rgba(0,0,0,.10), 0 26px 40px rgba(0,0,0,.18);
    position:relative;
    overflow:hidden;
}
.dex-card:before {
    content:"";
    position:absolute;
    inset:-70%;
    background:linear-gradient(110deg, transparent, rgba(255,255,255,.42), transparent);
    transform:rotate(10deg);
    animation: shine 4s infinite;
}
.dex-icon { font-size:72px; margin:12px 0; position:relative; z-index:2; }
.dex-title { font-family:'Fredoka', sans-serif; font-size:24px; font-weight:900; position:relative; z-index:2; }
.dex-meta { font-weight:900; position:relative; z-index:2; }
.locked-card {
    background:linear-gradient(180deg,#EDEDED,#FFFFFF);
    filter:grayscale(100%);
    opacity:.62;
}

.avatar-stage {
    min-height:560px;
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:22px;
    align-items:stretch;
}
.big-minifig {
    height:520px;
    border-radius:34px;
    border:7px solid white;
    background:
        radial-gradient(circle at 50% 28%, rgba(255,213,0,.75), transparent 28%),
        linear-gradient(180deg,#B9F2FF,#FFF0C4);
    box-shadow:0 18px 0 rgba(0,0,0,.12), 0 32px 60px rgba(0,0,0,.20);
    display:flex;
    align-items:center;
    justify-content:center;
    flex-direction:column;
    overflow:hidden;
    position:relative;
}
.minifig-body {
    width:220px;
    height:330px;
    position:relative;
    animation:minifigFloat 2.8s ease-in-out infinite;
}
@keyframes minifigFloat {
    0%,100% { transform:translateY(0) rotate(-1deg); }
    50% { transform:translateY(-10px) rotate(1deg); }
}
.fig-head {
    position:absolute;
    top:10px;
    left:56px;
    width:108px;
    height:108px;
    border-radius:32px;
    background:linear-gradient(180deg,#FFE66D,#FFD500);
    border:6px solid white;
    box-shadow:0 12px 0 #C88D00;
    display:grid;
    place-items:center;
    font-size:42px;
    z-index:3;
}
.fig-hair {
    position:absolute;
    top:-4px;
    left:48px;
    width:124px;
    height:48px;
    border-radius:30px 30px 18px 18px;
    background:linear-gradient(180deg,#6B3A14,#2B1408);
    border:5px solid white;
    z-index:4;
}
.fig-torso {
    position:absolute;
    top:126px;
    left:37px;
    width:146px;
    height:132px;
    border-radius:22px;
    background:linear-gradient(180deg,#E3000B,#9B0007);
    border:6px solid white;
    box-shadow:0 13px 0 #650005;
    display:grid;
    place-items:center;
    color:white;
    font-family:'Fredoka', sans-serif;
    font-weight:900;
    font-size:28px;
}
.fig-arm-left, .fig-arm-right {
    position:absolute;
    top:142px;
    width:48px;
    height:124px;
    border-radius:22px;
    background:linear-gradient(180deg,#006DB7,#004B80);
    border:5px solid white;
    box-shadow:0 10px 0 rgba(0,0,0,.18);
}
.fig-arm-left { left:-10px; transform:rotate(14deg); }
.fig-arm-right { right:-10px; transform:rotate(-14deg); }
.fig-leg-left, .fig-leg-right {
    position:absolute;
    top:264px;
    width:64px;
    height:94px;
    border-radius:18px;
    background:linear-gradient(180deg,#006DB7,#003E70);
    border:5px solid white;
    box-shadow:0 11px 0 #002A4C;
}
.fig-leg-left { left:42px; }
.fig-leg-right { right:42px; }
.builder-controls {
    display:grid;
    gap:14px;
}
.selector-card {
    border-radius:24px;
    border:5px solid white;
    background:rgba(255,255,255,.88);
    padding:16px;
    box-shadow:0 10px 0 rgba(0,0,0,.09), 0 20px 35px rgba(0,0,0,.12);
}
.selector-card label {
    font-family:'Fredoka', sans-serif;
    font-weight:900;
    color:#006DB7;
    font-size:17px;
}

.store-card-game {
    border-radius:26px;
    border:5px solid white;
    background:linear-gradient(180deg,#FFFFFF,#FFF7DD);
    padding:18px;
    box-shadow:0 12px 0 rgba(0,0,0,.10), 0 22px 36px rgba(0,0,0,.14);
    margin-bottom:14px;
}
.store-card-game h3 {
    margin:0 0 6px 0;
    color:#E3000B;
}
.score-bubble {
    display:inline-block;
    background:#FFD500;
    border:3px solid white;
    border-radius:999px;
    padding:7px 12px;
    font-family:'Fredoka', sans-serif;
    font-weight:900;
    box-shadow:0 5px 0 rgba(0,0,0,.12);
}

.progress-orb {
    width:220px;
    height:220px;
    border-radius:50%;
    margin: 20px auto;
    background:
        radial-gradient(circle at 36% 28%, rgba(255,255,255,.8), transparent 18%),
        conic-gradient(#FFD500 calc(var(--pct) * 1%), rgba(255,255,255,.45) 0);
    border:8px solid white;
    display:grid;
    place-items:center;
    box-shadow:0 18px 0 rgba(0,0,0,.12), 0 30px 55px rgba(0,0,0,.20);
}
.progress-inner {
    width:150px;
    height:150px;
    border-radius:50%;
    background:#FFFFFF;
    display:grid;
    place-items:center;
    font-family:'Fredoka', sans-serif;
    font-size:34px;
    font-weight:900;
    color:#006DB7;
    border:5px solid rgba(255,255,255,.8);
}

@media (max-width: 900px) {
    .top-hud { flex-direction:column; align-items:flex-start; gap:18px; }
    .hud-right { flex-wrap:wrap; }
    .world-copy h1 { font-size:58px; }
    .quest-world { height:640px; }
    .zip-panel { position:absolute; left:20px; right:20px; bottom:110px; width:auto; }
    .checkin-floating { right:22px; bottom:26px; font-size:20px; }
    .bottom-nav-game { grid-template-columns:repeat(3, 1fr); }
    .avatar-stage { grid-template-columns:1fr; }
    .collection-grid { grid-template-columns:repeat(2, minmax(130px, 1fr)); }
}
</style>
""", unsafe_allow_html=True)


# SMALL HTML HELPERS

def particles_html():
    random.seed(4)
    spans = []
    for i in range(42):
        left = random.randint(3, 97)
        top = random.randint(5, 90)
        delay = round(random.random() * 4, 2)
        size = random.randint(4, 10)
        spans.append(f'<span style="left:{left}%; top:{top}%; width:{size}px; height:{size}px; animation-delay:{delay}s;"></span>')
    return '<div class="particle-field">' + ''.join(spans) + '</div>'


def brick_rain_html():
    colors = ["#E3000B", "#FFD500", "#006DB7", "#22A447"]
    spans = []
    for i in range(18):
        left = 3 + i * 5.4
        color = colors[i % len(colors)]
        delay = round((i * .37) % 5, 2)
        duration = round(5.7 + (i % 5) * .42, 2)
        spans.append(f'<span style="left:{left}%; background:{color}; animation-delay:{delay}s; animation-duration:{duration}s;"></span>')
    return '<div class="brick-rain">' + ''.join(spans) + '</div>'


def burst_bricks_html():
    colors = ["#E3000B", "#FFD500", "#006DB7", "#22A447", "#8E44AD", "#FF9F00"]
    bricks = []
    random.seed(11)
    for i in range(48):
        angle = (math.pi * 2) * i / 48
        distance = random.randint(180, 390)
        x = int(math.cos(angle) * distance)
        y = int(math.sin(angle) * distance)
        color = colors[i % len(colors)]
        delay = round(random.random() * .25, 2)
        bricks.append(
            f'<div class="burst-brick" style="background:{color}; --x:{x}px; --y:{y}px; animation-delay:{delay}s;"></div>'
        )
    return ''.join(bricks)


def top_hud():
    lvl = player_level()
    xp = st.session_state.xp
    coins = st.session_state.coins
    gems = st.session_state.gems
    return f"""
    <div class="top-hud">
        <div class="logo-badge"><div class="logo-cube"></div> LEGO Quest</div>
        <div class="hud-right">
            <div class="hud-pill"><span>⭐</span> LVL {lvl}</div>
            <div class="hud-pill"><span>⚡</span> XP {xp}</div>
            <div class="hud-pill"><span>🧱</span> {coins}</div>
            <div class="hud-pill"><span>💎</span> {gems}</div>
            <div class="avatar-hud">🙂</div>
        </div>
    </div>
    """


def nav_html(active):
    items = [
        ("Quest Map", "🗺️", "Map"),
        ("Avatar", "🙂", "Avatar"),
        ("Collection", "🎴", "Cards"),
        ("Progress", "🏆", "Rank"),
        ("Stores", "📍", "Stores"),
    ]
    html = '<div class="bottom-nav-game">'
    for key, icon, label in items:
        cls = "nav-item nav-active" if active == key else "nav-item"
        html += f'<div class="{cls}"><span class="nav-icon">{icon}</span>{label}</div>'
    html += '</div>'
    return html


def game_frame_open():
    st.markdown('<div class="game-frame">' + particles_html() + brick_rain_html() + '<div class="cloud cloud-one"></div><div class="cloud cloud-two"></div><div class="cloud cloud-three"></div>' + top_hud(), unsafe_allow_html=True)


def game_frame_close(active):
    st.markdown(nav_html(active) + '</div>', unsafe_allow_html=True)

# NAVIGATION BUTTONS OUTSIDE CUSTOM HTML

nav_cols = st.columns(5)
navs = ["Quest Map", "Avatar", "Collection", "Progress", "Stores"]
for i, nav in enumerate(navs):
    with nav_cols[i]:
        if st.button(nav, key=f"nav_{nav}", use_container_width=True):
            st.session_state.screen = nav
            st.session_state.show_reward = False
            st.rerun()


# SCREENS
import streamlit.components.v1 as components

def level():
    return st.session_state.xp // 100 + 1

def collected_names():
    return [item["name"] for item in st.session_state.collection]


if st.session_state.screen == "Quest Map":

    owned = len(set(collected_names()))

    quest_html = f"""
    <html>
    <head>
    <style>

    body {{
        margin:0;
        overflow:hidden;
        font-family:Arial,sans-serif;
    }}

    .screen {{

        position:relative;

        height:920px;

        border-radius:42px;

        overflow:hidden;

        background:
        radial-gradient(circle at 20% 10%, rgba(255,255,255,.7), transparent 12%),
        linear-gradient(
            180deg,
            #7ED6FF 0%,
            #B8ECFF 30%,
            #FFF1C7 100%
        );

        border:8px solid white;

        box-shadow:
        0 35px 90px rgba(0,0,0,.25);
    }}

    .brick-rain span {{

        position:absolute;

        top:-100px;

        width:28px;
        height:22px;

        border-radius:6px;

        animation:brickFall linear infinite;

        z-index:2;

        box-shadow:
        inset 0 5px rgba(255,255,255,.35),
        0 7px 0 rgba(0,0,0,.15);
    }}

    .brick-rain span:before,
    .brick-rain span:after {{

        content:"";

        position:absolute;

        top:4px;

        width:7px;
        height:7px;

        border-radius:50%;

        background:rgba(255,255,255,.35);
    }}

    .brick-rain span:before {{
        left:6px;
    }}

    .brick-rain span:after {{
        right:6px;
    }}

    @keyframes brickFall {{

        0% {{
            transform:
            translateY(-120px)
            rotate(0deg);

            opacity:0;
        }}

        10% {{
            opacity:1;
        }}

        100% {{
            transform:
            translateY(1200px)
            rotate(720deg);

            opacity:0;
        }}
    }}

    .top-hud {{

        position:absolute;

        top:22px;
        left:22px;
        right:22px;

        display:flex;

        justify-content:space-between;

        align-items:center;

        z-index:100;
    }}

    .logo {{

        background:
        linear-gradient(
            180deg,
            #FF2A34,
            #E3000B,
            #980005
        );

        color:white;

        border:6px solid #FFD500;

        border-radius:22px;

        padding:16px 28px;

        font-size:28px;

        font-weight:900;

        box-shadow:
        0 10px 0 #620004,
        0 18px 35px rgba(0,0,0,.25);
    }}

    .hud-right {{
        display:flex;
        gap:12px;
    }}

    .hud-pill {{

        background:rgba(255,255,255,.9);

        backdrop-filter:blur(10px);

        border-radius:999px;

        padding:12px 18px;

        font-weight:900;

        border:4px solid white;

        box-shadow:
        0 8px 0 rgba(0,0,0,.12);
    }}

    .game-ui {{

        position:absolute;

        top:110px;
        bottom:120px;
        left:20px;
        right:20px;

        display:flex;

        gap:20px;

        z-index:10;
    }}

    .panel {{

        background:
        linear-gradient(
            180deg,
            rgba(255,255,255,.95),
            rgba(255,255,255,.85)
        );

        backdrop-filter:blur(12px);

        border-radius:28px;

        border:5px solid white;

        box-shadow:
        0 14px 30px rgba(0,0,0,.16);

        overflow:hidden;
    }}

    .panel-title {{

        padding:14px 18px;

        font-weight:900;

        color:white;

        font-size:18px;
    }}

    .blue {{
        background:#006DB7;
    }}

    .red {{
        background:#E3000B;
    }}

    .green {{
        background:#22A447;
    }}

    .yellow {{
        background:#FFD500;
        color:#1E1E1E;
    }}

    .panel-body {{
        padding:18px;
    }}

    .left-panel {{

        width:270px;

        display:flex;

        flex-direction:column;

        gap:18px;
    }}

    .player-card {{
        padding:18px;
    }}

    .player-top {{
        display:flex;
        gap:14px;
        align-items:center;
    }}

    .avatar {{

        width:74px;
        height:74px;

        border-radius:22px;

        background:
        linear-gradient(
            180deg,
            #FFD500,
            #FFB300
        );

        display:flex;

        align-items:center;
        justify-content:center;

        font-size:40px;

        border:5px solid white;

        box-shadow:
        0 8px 0 rgba(0,0,0,.12);
    }}

    .xp-bar {{

        margin-top:10px;

        height:16px;

        border-radius:999px;

        background:#EAEAEA;

        overflow:hidden;
    }}

    .xp-fill {{

        width:72%;

        height:100%;

        background:
        linear-gradient(
            90deg,
            #FFD500,
            #FF8F00
        );
    }}

    .quest-row {{

        display:flex;

        justify-content:space-between;

        padding:12px 0;

        border-bottom:1px solid #eee;

        font-weight:800;
    }}

    .claim-btn {{

        margin-top:18px;

        background:
        linear-gradient(
            180deg,
            #FFE66D,
            #FFD500,
            #E59B00
        );

        border-radius:18px;

        padding:15px;

        text-align:center;

        font-weight:900;

        box-shadow:
        inset 0 5px rgba(255,255,255,.4),
        0 8px 0 rgba(0,0,0,.15);
    }}

    .event-card {{

        background:
        linear-gradient(
            135deg,
            #12001F,
            #41007D
        );

        color:white;

        padding:20px;
    }}

    .map-container {{
        flex:1;
    }}

    .lego-map {{

        position:relative;

        height:100%;

        border-radius:38px;

        overflow:hidden;

        border:6px solid white;

        background:
        linear-gradient(
            135deg,
            #00A6FF 0%,
            #00A6FF 35%,
            #6ED36E 36%,
            #35A842 100%
        );

        box-shadow:
        0 22px 55px rgba(0,0,0,.25);
    }}

    .road {{

        position:absolute;

        width:900px;
        height:90px;

        background:#E6BE7D;

        border-radius:999px;

        transform:rotate(25deg);

        top:180px;
        left:140px;

        border:6px solid rgba(255,255,255,.7);
    }}

    .river {{

        position:absolute;

        width:800px;
        height:120px;

        background:
        linear-gradient(
            180deg,
            #5AE3FF,
            #0089D0
        );

        border-radius:999px;

        transform:rotate(-18deg);

        bottom:90px;
        right:-50px;

        border:6px solid rgba(255,255,255,.7);
    }}

.store-main {{

    position:absolute;

    width:180px;
    height:150px;

    background:
    linear-gradient(
        180deg,
        #FFF176,
        #FFD500,
        #D99700
    );

    border-radius:24px;

    border:8px solid white;

    top:180px;
    left:50%;

    transform:translateX(-50%);

    box-shadow:
    0 24px 0 #9B6700,
    0 35px 45px rgba(0,0,0,.28);

    z-index:20;
}}

.store-click-zone {{

    position:absolute;

    width:210px;
    height:180px;

    top:170px;
    left:50%;

    transform:translateX(-50%);

    z-index:80;

    cursor:pointer;

    background:transparent;
}}

.store-click-zone:hover {{

    filter: drop-shadow(
        0 0 25px rgba(255,213,0,.9)
    );
}}

.lego-logo {{

    position:absolute;

    top:46px;
    left:50%;

    transform:translateX(-50%);

    background:#E3000B;

    color:white;

    border:4px solid white;

    border-radius:12px;

    padding:10px 20px;

    font-weight:900;
}}

        .quest-pin {{

            position:absolute;

            width:72px;
            height:72px;

            border-radius:
            50% 50% 50% 0;

            transform:rotate(-45deg);

            border:7px solid white;

            box-shadow:
            0 0 24px rgba(255,213,0,.7),
            0 14px 24px rgba(0,0,0,.28);

            animation:bounce 1.4s infinite;

            z-index:30;
        }}

        .quest-pin:after {{

            content:"";

            position:absolute;

            width:20px;
            height:20px;

            border-radius:50%;

            background:white;

            top:18px;
            left:18px;
        }}

    .red-pin {{
        background:#E3000B;
        top:100px;
        left:55%;
    }}

    .blue-pin {{
        background:#006DB7;
        top:360px;
        left:25%;
    }}

    .yellow-pin {{
        background:#FFD500;
        top:220px;
        right:120px;
    }}

    @keyframes bounce {{

        0%,100% {{
            transform:
            rotate(-45deg)
            translateY(0);
        }}

        50% {{
            transform:
            rotate(-45deg)
            translateY(-12px);
        }}
    }}

    .player-character {{

        position:absolute;

        width:90px;
        height:130px;

        bottom:120px;
        left:50%;

        transform:translateX(-50%);

        z-index:40;

        font-size:90px;
    }}

    .player-ring {{

        position:absolute;

        width:140px;
        height:140px;

        border-radius:50%;

        border:6px solid #6BE8FF;

        bottom:95px;
        left:50%;

        transform:translateX(-50%);

        z-index:30;

        box-shadow:
        0 0 30px #6BE8FF;

        animation:pulse 2s infinite;
    }}

    @keyframes pulse {{

        0%,100% {{
            transform:
            translateX(-50%)
            scale(1);
        }}

        50% {{
            transform:
            translateX(-50%)
            scale(1.08);
        }}
    }}

    .mystery-drop {{

        position:absolute;

        width:110px;
        height:140px;

        border-radius:28px;

        border:8px solid white;

        background:
        linear-gradient(
            180deg,
            #C56CFF,
            #5D00B5
        );

        box-shadow:
        0 0 40px rgba(255,213,0,.9);

        bottom:150px;
        left:38%;

        z-index:40;

        animation:floaty 1.5s infinite;
    }}

    .mystery-drop:after {{

        content:"?";

        position:absolute;

        left:50%;
        top:50%;

        transform:translate(-50%,-50%);

        color:white;

        font-size:70px;

        font-weight:900;
    }}

    @keyframes floaty {{

        0%,100% {{
            transform:translateY(0);
        }}

        50% {{
            transform:translateY(-12px);
        }}
    }}

    .right-panel {{

        width:270px;

        display:flex;

        flex-direction:column;

        gap:18px;
    }}

    .drop-pack {{

        height:180px;

        border-radius:24px;

        background:
        linear-gradient(
            180deg,
            #FFD500,
            #FF9F00
        );

        box-shadow:
        0 0 35px rgba(255,213,0,.9);

        position:relative;
    }}

    .drop-pack:after {{

        content:"?";

        position:absolute;

        left:50%;
        top:50%;

        transform:translate(-50%,-50%);

        font-size:90px;

        font-weight:900;

        color:white;
    }}

    .card-stack {{
        display:flex;
        gap:10px;
    }}

    .mini-card {{

        width:70px;
        height:100px;

        border-radius:18px;

        background:
        linear-gradient(
            180deg,
            #006DB7,
            #002F66
        );

        border:4px solid white;

        box-shadow:
        0 10px 20px rgba(0,0,0,.2);
    }}

    .store-preview {{

        padding:16px;

        border-radius:18px;

        background:#FFF5CC;

        font-weight:900;
    }}

    .bottom-nav {{

        position:absolute;

        left:20px;
        right:20px;
        bottom:20px;

        display:grid;

        grid-template-columns:repeat(5,1fr);

        gap:16px;

        z-index:100;
    }}

    .nav-item {{

        background:
        linear-gradient(
            180deg,
            #FFFFFF,
            #ECECEC
        );

        border-radius:22px;

        padding:16px;

        text-align:center;

        font-weight:900;

        border:5px solid white;

        box-shadow:
        0 10px 0 rgba(0,0,0,.12);
    }}

    .active-nav {{

        background:
        linear-gradient(
            180deg,
            #FFE66D,
            #FFD500
        );
    }}

    </style>
    </head>

    <body>

    <div class="screen">

        <div class="brick-rain">

            <span style="left:5%;background:#E3000B;animation-duration:6s;"></span>
            <span style="left:14%;background:#FFD500;animation-duration:7s;"></span>
            <span style="left:24%;background:#006DB7;animation-duration:5s;"></span>
            <span style="left:36%;background:#E3000B;animation-duration:8s;"></span>
            <span style="left:48%;background:#FFD500;animation-duration:6s;"></span>
            <span style="left:60%;background:#006DB7;animation-duration:7s;"></span>
            <span style="left:72%;background:#E3000B;animation-duration:5s;"></span>
            <span style="left:84%;background:#FFD500;animation-duration:8s;"></span>

        </div>

        <div class="top-hud">

            <div class="logo">
                LEGO Quest
            </div>

            <div class="hud-right">

                <div class="hud-pill">
                    ⭐ LVL {level()}
                </div>

                <div class="hud-pill">
                    🧱 {st.session_state.xp}
                </div>

                <div class="hud-pill">
                    🎴 {owned}
                </div>

            </div>

        </div>

        <div class="game-ui">

            <div class="left-panel">

                <div class="panel player-card">

                    <div class="player-top">

                        <div class="avatar">
                            🙂
                        </div>

                        <div>

                            <h2 style="margin:0;">
                                LULU
                            </h2>

                            <p style="margin:0;font-weight:900;">
                                LEVEL {level()}
                            </p>

                            <div class="xp-bar">
                                <div class="xp-fill"></div>
                            </div>

                        </div>

                    </div>

                </div>

                <div class="panel">

                    <div class="panel-title blue">
                        DAILY QUESTS
                    </div>

                    <div class="panel-body">

                        <div class="quest-row">
                            📍 Check in at 2 stores
                        </div>

                        <div class="quest-row">
                            🎴 Collect 3 cards
                        </div>

                        <div class="quest-row">
                            👟 Walk 2000 steps
                        </div>

                        <div class="claim-btn">
                            CLAIM REWARD
                        </div>

                    </div>

                </div>

                <div class="panel event-card">

                    <h2 style="margin-top:0;">
                        DRAGON INVASION
                    </h2>

                    <p>
                        Collect dragon cards this week and unlock legendary rewards.
                    </p>

                </div>

            </div>

            <div class="map-container">

                <div class="lego-map">

                    <div class="road"></div>

                    <div class="river"></div>

                    <div class="store-main">

    <div class="lego-logo">
        LEGO
    </div>

</div>

<div class="store-click-zone" onclick="window.parent.location.search='?quest=zip'"></div>。

</div>

                        <div class="lego-logo">
                            LEGO
                        </div>

                    </div>

                    <div class="quest-pin red-pin"></div>

                    <div class="quest-pin blue-pin"></div>

                    <div class="quest-pin yellow-pin"></div>

                    <div class="mystery-drop"></div>

                    <div class="player-ring"></div>

                    

                </div>

            </div>

            <div class="right-panel">

                <div class="panel">

                    <div class="panel-title red">
                        TODAY'S DROP
                    </div>

                    <div class="panel-body">

                        <div class="drop-pack"></div>

                    </div>

                </div>

                <div class="panel">

                    <div class="panel-title green">
                        COLLECTION
                    </div>

                    <div class="panel-body">

                        <div class="card-stack">

                            <div class="mini-card"></div>

                            <div class="mini-card"></div>

                            <div class="mini-card"></div>

                        </div>

                    </div>

                </div>

                <div class="panel">

                    <div class="panel-title yellow">
                        NEARBY STORE
                    </div>

                    <div class="panel-body">

                        <div class="store-preview">

                            LEGO Store<br>
                            Explore Score: 98

                        </div>

                    </div>

                </div>

            </div>

        </div>

        

    </div>

    </body>
    </html>
    """

    components.html(
        quest_html,
        height=920,
        scrolling=False
    )
    # ==============================
    # STABLE LEGO CHECK-IN PANEL
    # ==============================
    # ==============================
    # STABLE LEGO CHECK-IN + CARD REVEAL
    # ==============================

    if "quest_step" not in st.session_state:
        st.session_state.quest_step = "idle"

    if "last_card" not in st.session_state:
        st.session_state.last_card = None

    st.markdown("""
    <div style="
        margin-top:24px;
        padding:28px;
        border-radius:34px;
        border:7px solid white;
        background:
            radial-gradient(circle at 20% 20%, rgba(255,213,0,.55), transparent 30%),
            linear-gradient(180deg,#FFFFFF,#FFF1C7);
        box-shadow:0 18px 0 rgba(0,0,0,.10),0 30px 60px rgba(0,0,0,.22);
        text-align:center;
    ">
        <h1 style="color:#E3000B;margin:0;">📍 LEGO Store Check-In Quest</h1>
        <p style="font-weight:900;font-size:18px;">
            Press START QUEST, enter your ZIP code, and unlock a mystery collectible card.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.quest_step == "idle":
        if st.button("✨ START QUEST", use_container_width=True):
            st.session_state.quest_step = "zip"
            st.rerun()

    if st.session_state.quest_step == "zip":
        zip_code = st.text_input(
            "Enter your ZIP code",
            placeholder="Example: 10001",
            key="zip_checkin_input"
        )

        if st.button("✅ CHECK IN & OPEN CARD DROP", use_container_width=True):
            if not zip_code.strip():
                st.warning("Please enter a ZIP code first.")
            else:
                card = get_drop()

                st.session_state.zip_code = zip_code
                st.session_state.collection.append(card)
                st.session_state.xp += card["xp"]
                st.session_state.last_card = card
                st.session_state.quest_step = "reward"

                if "Nearby LEGO Store" not in st.session_state.visited:
                    st.session_state.visited.append("Nearby LEGO Store")

                st.balloons()
                st.rerun()

    elif st.session_state.quest_step == "reward" and st.session_state.last_card:
        card = st.session_state.last_card

        rarity_color = {
            "Common": "#2D9CDB",
            "Rare": "#6C5CE7",
            "Epic": "#9B51E0",
            "Legendary": "#F2C94C",
            "Mythic": "#FF4FD8"
        }.get(card["rarity"], "#FFD500")

        card_number = random.randint(1, 99)
        atk = random.randint(40, 95)
        defense = random.randint(40, 95)

        card_html = """
        <style>
        .collect-card-wrap {
            margin-top: 28px;
            display:flex;
            justify-content:center;
        }

        .collect-card {
            width: 330px;
            min-height: 520px;
            border-radius: 28px;
            padding: 14px;
            background:
                linear-gradient(145deg, RARITY_COLOR, #111827);
            border: 7px solid white;
            box-shadow:
                0 0 45px RARITY_COLOR,
                0 28px 70px rgba(0,0,0,.45);
            position:relative;
            overflow:hidden;
            animation: cardPop .7s ease-out;
        }

        .collect-card:before {
            content:"";
            position:absolute;
            inset:-40%;
            background:linear-gradient(115deg, transparent 35%, rgba(255,255,255,.5), transparent 65%);
            animation: shineCard 3s infinite;
        }

        .card-number {
            position:absolute;
            top:12px;
            right:14px;
            background:white;
            color:#111;
            border-radius:12px;
            padding:6px 10px;
            font-weight:900;
            z-index:3;
        }

        .card-logo {
            position:absolute;
            top:12px;
            left:12px;
            background:#E3000B;
            color:white;
            border:3px solid white;
            border-radius:8px;
            padding:6px 8px;
            font-size:11px;
            font-weight:900;
            z-index:3;
        }

        .card-art {
            height:250px;
            border-radius:22px;
            background:
                radial-gradient(circle at 50% 35%, rgba(255,255,255,.95), transparent 18%),
                radial-gradient(circle at center, RARITY_COLOR, transparent 55%),
                linear-gradient(180deg,#7ED6FF,#1E3A8A);
            border:5px solid rgba(255,255,255,.9);
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:115px;
            margin-bottom:12px;
            position:relative;
            z-index:2;
        }

        .card-info {
            background:rgba(255,255,255,.92);
            border-radius:20px;
            padding:14px;
            position:relative;
            z-index:2;
            color:#111;
        }

        .card-name {
            font-size:25px;
            font-weight:900;
            color:#111;
            margin-bottom:6px;
        }

        .card-rarity {
            display:inline-block;
            background:RARITY_COLOR;
            color:white;
            border-radius:999px;
            padding:5px 12px;
            font-size:12px;
            font-weight:900;
            margin-bottom:10px;
        }

        .card-fact {
            font-size:14px;
            line-height:1.35;
            font-weight:800;
            color:#333;
        }

        .card-stats {
            margin-top:12px;
            display:flex;
            justify-content:space-between;
            gap:8px;
        }

        .stat {
            background:#FFF1C7;
            border-radius:12px;
            padding:7px 9px;
            font-size:12px;
            font-weight:900;
        }

        @keyframes cardPop {
            0% { transform:scale(.65) rotate(-6deg); opacity:0; }
            70% { transform:scale(1.06) rotate(2deg); opacity:1; }
            100% { transform:scale(1) rotate(0); }
        }

        @keyframes shineCard {
            0% { transform:translateX(-60%) rotate(10deg); }
            100% { transform:translateX(60%) rotate(10deg); }
        }
        </style>

        <div class="collect-card-wrap">
            <div class="collect-card">
                <div class="card-logo">LEGO<br>QUEST</div>
                <div class="card-number">#CARD_NUMBER</div>

                <div class="card-art">
                    CARD_ICON
                </div>

                <div class="card-info">
                    <div class="card-name">CARD_NAME</div>
                    <div class="card-rarity">CARD_RARITY</div>
                    <div class="card-fact">CARD_FACT</div>

                    <div class="card-stats">
                        <div class="stat">ATK CARD_ATK</div>
                        <div class="stat">DEF CARD_DEF</div>
                        <div class="stat">XP +CARD_XP</div>
                    </div>
                </div>
            </div>
        </div>
        """

        card_html = textwrap.dedent(card_html).strip()

        card_html = (
            card_html
            .replace("RARITY_COLOR", rarity_color)
            .replace("CARD_NUMBER", f"{card_number:02d}")
            .replace("CARD_ICON", card.get("icon", "🧱"))
            .replace("CARD_NAME", card["name"])
            .replace("CARD_RARITY", card["rarity"].upper())
            .replace("CARD_FACT", card.get("fact", "A mysterious LEGO Quest collectible."))
            .replace("CARD_ATK", str(atk))
            .replace("CARD_DEF", str(defense))
            .replace("CARD_XP", str(card["xp"]))
        )

        st.success(
            f"🎉 You unlocked {card['name']} ({card['rarity']}) +{card['xp']} XP! Added to Collection."
        )

        components.html(card_html, height=660, scrolling=False)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🎴 VIEW COLLECTION", use_container_width=True):
                st.session_state.screen = "Collection"
                st.session_state.quest_step = "idle"
                st.rerun()

        with col2:
            if st.button("🔁 CHECK IN AGAIN", use_container_width=True):
                st.session_state.quest_step = "idle"
                st.rerun()
# ------------------------- AVATAR -------------------------
elif st.session_state.screen == "Avatar":

    import streamlit.components.v1 as components

    if "avatar_name" not in st.session_state:
        st.session_state.avatar_name = "LULU"

    st.markdown("## 🙂 LEGO Avatar Builder")

    col1, col2 = st.columns([1.15, 0.85])

    with col2:
        name = st.text_input("Avatar Name", st.session_state.avatar_name)

        hair = st.selectbox(
            "Hair",
            ["Brown Hair", "Black Hair", "Blonde Hair", "Red Cap", "Space Helmet"]
        )

        face = st.selectbox(
            "Face",
            ["Smile", "Cool Glasses", "Wink", "Brave Face"]
        )

        outfit = st.selectbox(
            "Outfit",
            ["Red Quest Hoodie", "Blue Explorer Jacket", "Yellow Builder Suit", "Purple Dream Fit"]
        )

        accessory = st.selectbox(
            "Accessory",
            ["Star Glasses", "Headphones", "Backpack", "Magic Wand", "None"]
        )

        if st.button("✨ Generate My LEGO Avatar", use_container_width=True):
            st.session_state.avatar_name = name
            st.session_state.avatar_hair = hair
            st.session_state.avatar_face = face
            st.session_state.avatar_outfit = outfit
            st.session_state.avatar_accessory = accessory
            st.success("Avatar generated!")

    hair_color = {
        "Brown Hair": "linear-gradient(180deg,#6B3A14,#2A1407)",
        "Black Hair": "linear-gradient(180deg,#222,#000)",
        "Blonde Hair": "linear-gradient(180deg,#FFE66D,#D99A00)",
        "Red Cap": "linear-gradient(180deg,#E3000B,#980005)",
        "Space Helmet": "linear-gradient(180deg,#DFF8FF,#8FDFFF)",
    }[hair]

    body_color = {
        "Red Quest Hoodie": "linear-gradient(180deg,#E3000B,#980005)",
        "Blue Explorer Jacket": "linear-gradient(180deg,#006DB7,#003A66)",
        "Yellow Builder Suit": "linear-gradient(180deg,#FFD500,#D99A00)",
        "Purple Dream Fit": "linear-gradient(180deg,#8E44AD,#3C096C)",
    }[outfit]

    mouth_html = {
        "Smile": '<div class="av2-mouth smile"></div>',
        "Cool Glasses": '<div class="av2-mouth smile"></div>',
        "Wink": '<div class="av2-mouth smile"></div><div class="av2-wink"></div>',
        "Brave Face": '<div class="av2-mouth brave"></div>',
    }[face]

    glasses_html = ""
    if face == "Cool Glasses" or accessory == "Star Glasses":
        glasses_html = '<div class="av2-glasses"></div>'

    accessory_html = ""
    if accessory == "Headphones":
        accessory_html = '<div class="av2-headphones"></div>'
    elif accessory == "Backpack":
        accessory_html = '<div class="av2-backpack"></div>'
    elif accessory == "Magic Wand":
        accessory_html = '<div class="av2-wand">✨</div>'

    avatar_html = f"""
    <html>
    <head>
    <style>
    body {{
        margin: 0;
        font-family: Arial, sans-serif;
        background: transparent;
    }}

    .av2-page {{
        height: 720px;
        border-radius: 42px;
        border: 8px solid white;
        background:
            radial-gradient(circle at 50% 35%, rgba(255,213,0,.8), transparent 28%),
            radial-gradient(circle at 20% 15%, rgba(255,255,255,.8), transparent 16%),
            linear-gradient(180deg,#7ED6FF 0%, #FFF1C7 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        box-shadow: 0 35px 90px rgba(0,0,0,.25);
        position: relative;
    }}

    .av2-title {{
        position: absolute;
        top: 24px;
        left: 28px;
        background: linear-gradient(180deg,#E3000B,#980005);
        color: white;
        border: 6px solid #FFD500;
        border-radius: 26px;
        padding: 16px 28px;
        font-size: 30px;
        font-weight: 900;
        box-shadow: 0 10px 0 #620004;
    }}

    .av2-ring {{
        position: absolute;
        width: 430px;
        height: 430px;
        border-radius: 50%;
        border: 8px solid rgba(255,255,255,.8);
        box-shadow: 0 0 55px rgba(255,213,0,.9);
        animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
        0%,100% {{ transform: scale(1); opacity: .75; }}
        50% {{ transform: scale(1.12); opacity: 1; }}
    }}

    .av2-figure {{
        position: relative;
        width: 280px;
        height: 470px;
        z-index: 5;
        animation: floaty 2.5s ease-in-out infinite;
    }}

    @keyframes floaty {{
        0%,100% {{ transform: translateY(0) rotate(-1deg); }}
        50% {{ transform: translateY(-14px) rotate(1deg); }}
    }}

    .av2-hair {{
        position: absolute;
        top: 18px;
        left: 58px;
        width: 164px;
        height: 64px;
        border-radius: 44px 44px 18px 18px;
        background: {hair_color};
        border: 7px solid white;
        z-index: 9;
        box-shadow: 0 10px 0 rgba(0,0,0,.16);
    }}

    .av2-head {{
        position: absolute;
        top: 60px;
        left: 70px;
        width: 140px;
        height: 140px;
        border-radius: 36px;
        background: linear-gradient(180deg,#FFE66D,#FFD500);
        border: 7px solid white;
        z-index: 8;
        box-shadow: 0 14px 0 #C88D00;
    }}

    .av2-eye {{
        position: absolute;
        top: 52px;
        width: 15px;
        height: 15px;
        border-radius: 50%;
        background: #1E1E1E;
    }}

    .left-eye {{ left: 38px; }}
    .right-eye {{ right: 38px; }}

    .av2-mouth.smile {{
        position: absolute;
        left: 52px;
        bottom: 32px;
        width: 36px;
        height: 16px;
        border-bottom: 6px solid #1E1E1E;
        border-radius: 0 0 30px 30px;
    }}

    .av2-mouth.brave {{
        position: absolute;
        left: 52px;
        bottom: 38px;
        width: 38px;
        height: 6px;
        border-radius: 999px;
        background: #1E1E1E;
    }}

    .av2-wink {{
        position: absolute;
        top: 54px;
        right: 34px;
        width: 22px;
        height: 6px;
        background: #1E1E1E;
        border-radius: 999px;
        z-index: 20;
    }}

    .av2-glasses {{
        position: absolute;
        top: 42px;
        left: 22px;
        width: 92px;
        height: 32px;
        border: 5px solid #1E1E1E;
        border-radius: 20px;
        z-index: 20;
    }}

    .av2-glasses:after {{
        content: "";
        position: absolute;
        top: 10px;
        left: 40px;
        width: 12px;
        height: 5px;
        background: #1E1E1E;
    }}

    .av2-body {{
        position: absolute;
        top: 222px;
        left: 45px;
        width: 190px;
        height: 150px;
        border-radius: 30px;
        background: {body_color};
        border: 7px solid white;
        color: white;
        font-size: 42px;
        font-weight: 900;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 16px 0 rgba(0,0,0,.28);
        z-index: 5;
    }}

    .av2-arm {{
        position: absolute;
        top: 238px;
        width: 58px;
        height: 138px;
        border-radius: 28px;
        background: linear-gradient(180deg,#006DB7,#003A66);
        border: 7px solid white;
        box-shadow: 0 12px 0 rgba(0,0,0,.16);
        z-index: 4;
    }}

    .av2-arm-left {{
        left: 0;
        transform: rotate(12deg);
    }}

    .av2-arm-right {{
        right: 0;
        transform: rotate(-12deg);
    }}

    .av2-leg {{
        position: absolute;
        top: 382px;
        width: 82px;
        height: 98px;
        border-radius: 22px;
        background: linear-gradient(180deg,#006DB7,#003A66);
        border: 7px solid white;
        box-shadow: 0 13px 0 #002A4C;
        z-index: 4;
    }}

    .av2-leg-left {{ left: 52px; }}
    .av2-leg-right {{ right: 52px; }}

    .av2-name {{
        position: absolute;
        bottom: 24px;
        background: rgba(255,255,255,.92);
        border: 5px solid white;
        border-radius: 999px;
        padding: 12px 24px;
        font-size: 22px;
        font-weight: 900;
        box-shadow: 0 10px 0 rgba(0,0,0,.14);
    }}

    .av2-headphones {{
        position: absolute;
        top: 72px;
        left: 56px;
        width: 168px;
        height: 95px;
        border: 10px solid #1E1E1E;
        border-bottom: none;
        border-radius: 70px 70px 0 0;
        z-index: 30;
    }}

    .av2-backpack {{
        position: absolute;
        top: 235px;
        right: -12px;
        width: 60px;
        height: 110px;
        border-radius: 20px;
        background: linear-gradient(180deg,#FFD500,#D99A00);
        border: 6px solid white;
        z-index: 3;
    }}

    .av2-wand {{
        position: absolute;
        right: -22px;
        top: 210px;
        font-size: 52px;
        z-index: 40;
        transform: rotate(18deg);
    }}
    </style>
    </head>

    <body>
        <div class="av2-page">
            <div class="av2-title">🙂 LEGO Avatar Builder</div>
            <div class="av2-ring"></div>

            <div class="av2-figure">
                {accessory_html}

                <div class="av2-hair"></div>

                <div class="av2-head">
                    <div class="av2-eye left-eye"></div>
                    <div class="av2-eye right-eye"></div>
                    {mouth_html}
                    {glasses_html}
                </div>

                <div class="av2-arm av2-arm-left"></div>
                <div class="av2-arm av2-arm-right"></div>

                <div class="av2-body">LQ</div>

                <div class="av2-leg av2-leg-left"></div>
                <div class="av2-leg av2-leg-right"></div>
            </div>

            <div class="av2-name">{name}</div>
        </div>
    </body>
    </html>
    """

    with col1:
        components.html(avatar_html, height=740, scrolling=False)
# ------------------------- COLLECTION ---------------------
elif st.session_state.screen == "Collection":

    import streamlit.components.v1 as components

    owned_names = set(collected_names())
    owned = len(owned_names)
    total = len(DROPS)

    shelf_items_html = ""

    for item in DROPS:
        unlocked = item["name"] in owned_names

        if unlocked:
            shelf_items_html += f"""
            <div class="toy-slot unlocked">
                <div class="rarity-badge {item['rarity'].lower()}">{item['rarity']}</div>
                <div class="toy-glow"></div>
                <div class="toy-figure">
                    <div class="toy-head">{item.get("minifig", item.get("icon", "🙂"))}</div>
                    <div class="toy-body">{item["series"][:2]}</div>
                    <div class="toy-legs"></div>
                </div>
                <div class="toy-name">{item["name"]}</div>
            </div>
            """
        else:
            shelf_items_html += """
            <div class="toy-slot locked">
                <div class="lock-icon">🔒</div>
                <div class="toy-figure grey">
                    <div class="toy-head">?</div>
                    <div class="toy-body">??</div>
                    <div class="toy-legs"></div>
                </div>
                <div class="toy-name">Unknown</div>
            </div>
            """

    collection_html = f"""
    <html>
    <head>
    <style>
    body {{
        margin:0;
        font-family:Arial,sans-serif;
        background:transparent;
    }}

    .collection-page {{
        min-height:900px;
        border-radius:42px;
        border:8px solid white;
        padding:28px;
        background:
            radial-gradient(circle at 20% 8%, rgba(255,213,0,.42), transparent 18%),
            radial-gradient(circle at 90% 15%, rgba(0,109,183,.24), transparent 22%),
            linear-gradient(180deg,#7ED6FF 0%, #FFF1C7 100%);
        box-shadow:0 35px 90px rgba(0,0,0,.25);
        overflow:hidden;
        position:relative;
    }}

    .collection-title {{
        display:flex;
        justify-content:space-between;
        align-items:center;
        margin-bottom:24px;
        position:relative;
        z-index:5;
    }}

    .logo-title {{
        background:linear-gradient(180deg,#E3000B,#980005);
        color:white;
        border:6px solid #FFD500;
        border-radius:26px;
        padding:16px 28px;
        font-size:34px;
        font-weight:900;
        box-shadow:0 10px 0 #620004;
    }}

    .progress-pill {{
        background:rgba(255,255,255,.92);
        border:5px solid white;
        border-radius:999px;
        padding:14px 22px;
        font-size:22px;
        font-weight:900;
        box-shadow:0 9px 0 rgba(0,0,0,.12);
    }}

    .cabinet {{
        background:
            linear-gradient(180deg,#B87535,#7A3E16);
        border:10px solid white;
        border-radius:36px;
        padding:34px 28px 42px;
        box-shadow:
            inset 0 10px rgba(255,255,255,.22),
            0 30px 70px rgba(0,0,0,.35);
        position:relative;
        z-index:4;
    }}

    .cabinet:before {{
        content:"LEGO QUEST DISPLAY CABINET";
        position:absolute;
        top:-28px;
        left:50%;
        transform:translateX(-50%);
        background:linear-gradient(180deg,#FFD500,#FF9F00);
        border:6px solid white;
        border-radius:999px;
        padding:10px 28px;
        font-size:20px;
        font-weight:900;
        box-shadow:0 8px 0 #9B6700;
    }}

    .shelf-row {{
        display:grid;
        grid-template-columns:repeat(4, 1fr);
        gap:24px;
        margin-top:28px;
        padding-bottom:28px;
        border-bottom:14px solid #4A220C;
        box-shadow:0 12px 0 rgba(255,255,255,.18);
    }}

    .toy-slot {{
        min-height:280px;
        border-radius:28px;
        background:
            linear-gradient(180deg,rgba(255,255,255,.88),rgba(255,255,255,.62));
        border:6px solid white;
        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:flex-end;
        padding:18px;
        position:relative;
        box-shadow:
            inset 0 8px rgba(255,255,255,.35),
            0 18px 35px rgba(0,0,0,.22);
        overflow:hidden;
    }}

    .toy-slot.unlocked {{
        animation: toyPop .6s ease-out;
    }}

    @keyframes toyPop {{
        0% {{ transform:scale(.8); opacity:0; }}
        70% {{ transform:scale(1.06); opacity:1; }}
        100% {{ transform:scale(1); }}
    }}

    .toy-slot.locked {{
        filter:grayscale(100%);
        opacity:.62;
    }}

    .toy-glow {{
        position:absolute;
        width:170px;
        height:170px;
        border-radius:50%;
        background:radial-gradient(circle,rgba(255,213,0,.75),transparent 65%);
        top:28px;
        animation: glowPulse 2s infinite;
    }}

    @keyframes glowPulse {{
        0%,100% {{ transform:scale(1); opacity:.7; }}
        50% {{ transform:scale(1.2); opacity:1; }}
    }}

    .rarity-badge {{
        position:absolute;
        top:14px;
        right:14px;
        color:white;
        border:3px solid white;
        border-radius:999px;
        padding:6px 10px;
        font-size:12px;
        font-weight:900;
        z-index:5;
    }}

    .common {{ background:#006DB7; }}
    .rare {{ background:#8E44AD; }}
    .epic {{ background:#FFD500; color:#1E1E1E; }}
    .legendary {{
        background:linear-gradient(45deg,#ff004c,#ff9900,#ffee00,#33ff00,#00ffee,#0066ff,#cc00ff);
    }}

    .toy-figure {{
        position:relative;
        width:130px;
        height:180px;
        z-index:4;
        animation: floatToy 2.4s ease-in-out infinite;
    }}

    @keyframes floatToy {{
        0%,100% {{ transform:translateY(0); }}
        50% {{ transform:translateY(-8px); }}
    }}

    .toy-head {{
        position:absolute;
        top:0;
        left:25px;
        width:80px;
        height:80px;
        border-radius:22px;
        background:linear-gradient(180deg,#FFE66D,#FFD500);
        border:6px solid white;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:38px;
        box-shadow:0 10px 0 #C88D00;
    }}

    .toy-body {{
        position:absolute;
        top:92px;
        left:12px;
        width:106px;
        height:72px;
        border-radius:20px;
        background:linear-gradient(180deg,#E3000B,#980005);
        border:6px solid white;
        display:flex;
        align-items:center;
        justify-content:center;
        color:white;
        font-size:22px;
        font-weight:900;
        box-shadow:0 10px 0 #620004;
    }}

    .toy-legs {{
        position:absolute;
        bottom:0;
        left:28px;
        width:74px;
        height:38px;
        border-radius:12px;
        background:linear-gradient(180deg,#006DB7,#003A66);
        border:6px solid white;
        box-shadow:0 8px 0 #002A4C;
    }}

    .grey .toy-head,
    .grey .toy-body,
    .grey .toy-legs {{
        background:linear-gradient(180deg,#BEBEBE,#777);
        box-shadow:0 8px 0 #555;
    }}

    .toy-name {{
        margin-top:14px;
        background:rgba(255,255,255,.92);
        border:4px solid white;
        border-radius:999px;
        padding:8px 14px;
        font-weight:900;
        text-align:center;
        z-index:5;
        box-shadow:0 6px 0 rgba(0,0,0,.12);
    }}

    .lock-icon {{
        position:absolute;
        top:16px;
        left:16px;
        font-size:28px;
        z-index:6;
    }}

    .sparkle {{
        position:absolute;
        width:10px;
        height:10px;
        border-radius:50%;
        background:white;
        animation:sparkle 3s infinite;
    }}

    @keyframes sparkle {{
        0%,100% {{ transform:scale(.4); opacity:.2; }}
        50% {{ transform:scale(1.3); opacity:1; }}
    }}

    @media(max-width:900px){{
        .shelf-row {{
            grid-template-columns:repeat(2,1fr);
        }}
    }}
    </style>
    </head>

    <body>
        <div class="collection-page">

            <div class="sparkle" style="left:8%;top:20%;animation-delay:.2s;"></div>
            <div class="sparkle" style="left:88%;top:18%;animation-delay:1s;"></div>
            <div class="sparkle" style="left:70%;top:78%;animation-delay:1.6s;"></div>
            <div class="sparkle" style="left:20%;top:84%;animation-delay:2.1s;"></div>

            <div class="collection-title">
                <div class="logo-title">🎴 Collection Cabinet</div>
                <div class="progress-pill">Collected {owned} / {total}</div>
            </div>

            <div class="cabinet">
                <div class="shelf-row">
                    {shelf_items_html}
                </div>
            </div>

        </div>
    </body>
    </html>
    """

    components.html(
        collection_html,
        height=960,
        scrolling=True
    )


    # ------------------------------
    # CHART2: collection rarity pie chart
    # ------------------------------
    st.markdown("""
    <div style="
        margin-top:22px;
        padding:22px;
        border-radius:30px;
        border:6px solid white;
        background:rgba(255,255,255,.92);
        box-shadow:0 14px 0 rgba(0,0,0,.10), 0 24px 45px rgba(0,0,0,.18);
    ">
        <h2 style="margin:0 0 10px 0;color:#E3000B;">📊 Collection Rarity Pie Chart</h2>
        <p style="font-weight:900;margin:0;">This chart shows the rarity mix of your collected LEGO Quest cards.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.collection:
        collection_df = pd.DataFrame(st.session_state.collection)
        if "rarity" in collection_df.columns:
            rarity_counts = collection_df["rarity"].value_counts().reset_index()
            rarity_counts.columns = ["Rarity", "Count"]

            fig_rarity = px.pie(
                rarity_counts,
                names="Rarity",
                values="Count",
                title="Your Collection by Rarity"
            )
            fig_rarity.update_layout(title_x=0.5, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_rarity, use_container_width=True)
    else:
        rarity_counts = pd.DataFrame([
            {"Rarity": "Common", "Count": len([x for x in DROPS if x["rarity"] == "Common"])},
            {"Rarity": "Rare", "Count": len([x for x in DROPS if x["rarity"] == "Rare"])},
            {"Rarity": "Epic", "Count": len([x for x in DROPS if x["rarity"] == "Epic"])},
            {"Rarity": "Legendary", "Count": len([x for x in DROPS if x["rarity"] == "Legendary"])},
        ])
        fig_rarity = px.pie(
            rarity_counts,
            names="Rarity",
            values="Count",
            title="Available Card Rarities Before You Collect"
        )
        fig_rarity.update_layout(title_x=0.5, margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(fig_rarity, use_container_width=True)
    # ==============================
    # STABLE LEGO CHECK-IN PANEL
    # ==============================

    if "quest_step" not in st.session_state:
        st.session_state.quest_step = "idle"

    if "last_card" not in st.session_state:
        st.session_state.last_card = None

    st.markdown("""
    <div style="
        margin-top:24px;
        padding:28px;
        border-radius:34px;
        border:7px solid white;
        background:
            radial-gradient(circle at 20% 20%, rgba(255,213,0,.55), transparent 30%),
            linear-gradient(180deg,#FFFFFF,#FFF1C7);
        box-shadow:0 18px 0 rgba(0,0,0,.10),0 30px 60px rgba(0,0,0,.22);
        text-align:center;
    ">
        <h1 style="color:#E3000B;margin:0;">📍 LEGO Store Check-In Quest</h1>
        <p style="font-weight:900;font-size:18px;">
            Start a quest, enter your ZIP code, and unlock a mystery collectible card.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.quest_step == "idle":
        if st.button("✨ START QUEST", use_container_width=True):
            st.session_state.quest_step = "zip"
            st.rerun()

    elif st.session_state.quest_step == "zip":
        zip_code = st.text_input(
            "Enter your ZIP code",
            placeholder="Example: 10001",
            key="zip_checkin_input"
        )

        if st.button("✅ CHECK IN & OPEN CARD DROP", use_container_width=True):
            if not zip_code.strip():
                st.warning("Please enter a ZIP code first.")
            else:
                card = get_drop()
                st.session_state.zip_code = zip_code
                st.session_state.collection.append(card)
                st.session_state.xp += card["xp"]
                st.session_state.last_card = card
                st.session_state.quest_step = "reward"
                st.balloons()
                st.rerun()

    elif st.session_state.quest_step == "reward" and st.session_state.last_card:
        card = st.session_state.last_card
        rarity_color = {
            "Common": "#2D9CDB",
            "Rare": "#6C5CE7",
            "Epic": "#9B51E0",
            "Legendary": "#F2C94C",
            "Mythic": "#FF4FD8"
        }.get(card["rarity"], "#FFD500")

        card_name = str(card.get("name", "Mystery Card"))
        card_rarity = str(card.get("rarity", "Common"))
        card_fact = str(card.get("fact", "A mysterious LEGO Quest collectible."))
        card_icon = str(card.get("icon", "🧱"))
        card_xp = int(card.get("xp", 0))
        card_number = random.randint(1, 99)
        atk = random.randint(40, 95)
        defense = random.randint(40, 95)

        reward_html = f"""
<style>
.collect-card-wrap {{ margin-top:28px; display:flex; justify-content:center; }}
.collect-card {{ width:330px; min-height:520px; border-radius:28px; padding:14px; background:linear-gradient(145deg, {rarity_color}, #111827); border:7px solid white; box-shadow:0 0 45px {rarity_color}, 0 28px 70px rgba(0,0,0,.45); position:relative; overflow:hidden; animation:cardPop .7s ease-out; }}
.collect-card:before {{ content:""; position:absolute; inset:-40%; background:linear-gradient(115deg, transparent 35%, rgba(255,255,255,.5), transparent 65%); animation:shineCard 3s infinite; }}
.card-number {{ position:absolute; top:12px; right:14px; background:white; color:#111; border-radius:12px; padding:6px 10px; font-weight:900; z-index:4; }}
.card-logo {{ position:absolute; top:12px; left:12px; background:#E3000B; color:white; border:3px solid white; border-radius:8px; padding:6px 8px; font-size:11px; font-weight:900; z-index:4; line-height:1.05; }}
.card-art {{ height:250px; border-radius:22px; background:radial-gradient(circle at 50% 35%, rgba(255,255,255,.95), transparent 18%), radial-gradient(circle at center, {rarity_color}, transparent 55%), linear-gradient(180deg,#7ED6FF,#1E3A8A); border:5px solid rgba(255,255,255,.9); display:flex; align-items:center; justify-content:center; font-size:115px; margin-bottom:12px; position:relative; z-index:2; }}
.card-info {{ background:rgba(255,255,255,.92); border-radius:20px; padding:14px; position:relative; z-index:2; color:#111; }}
.card-name {{ font-size:25px; font-weight:900; color:#111; margin-bottom:6px; }}
.card-rarity {{ display:inline-block; background:{rarity_color}; color:white; border-radius:999px; padding:5px 12px; font-size:12px; font-weight:900; margin-bottom:10px; }}
.card-fact {{ font-size:14px; line-height:1.35; font-weight:800; color:#333; }}
.card-stats {{ margin-top:12px; display:flex; justify-content:space-between; gap:8px; }}
.stat {{ background:#FFF1C7; border-radius:12px; padding:7px 9px; font-size:12px; font-weight:900; }}
@keyframes cardPop {{ 0% {{ transform:scale(.65) rotate(-6deg); opacity:0; }} 70% {{ transform:scale(1.06) rotate(2deg); opacity:1; }} 100% {{ transform:scale(1) rotate(0); }} }}
@keyframes shineCard {{ 0% {{ transform:translateX(-60%) rotate(10deg); }} 100% {{ transform:translateX(60%) rotate(10deg); }} }}
</style>
<div class="collect-card-wrap">
  <div class="collect-card">
    <div class="card-logo">LEGO<br>QUEST</div>
    <div class="card-number">#{card_number:02d}</div>
    <div class="card-art">{card_icon}</div>
    <div class="card-info">
      <div class="card-name">{card_name}</div>
      <div class="card-rarity">{card_rarity.upper()}</div>
      <div class="card-fact">{card_fact}</div>
      <div class="card-stats">
        <div class="stat">ATK {atk}</div>
        <div class="stat">DEF {defense}</div>
        <div class="stat">XP +{card_xp}</div>
      </div>
    </div>
  </div>
</div>
"""
        components.html(textwrap.dedent(reward_html).strip(), height=660, scrolling=False)
# ------------------------- PROGRESS -----------------------
if st.session_state.screen == "Progress":

    import streamlit.components.v1 as components
    import random

    player_names = [
        "BrickNova", "LegoLulu", "QuestKai", "MiniMax", "StarBuilder",
        "PixelNinja", "GoldenDuck", "CityHero", "BrickQueen", "ToyPilot",
        "NinjaPop", "DragonMia", "BlockHunter", "SunnyKai", "GalaxyJay",
        "BuildBunny", "RedBrick", "BlueRocket", "CloudMason", "MagicStud",
        "TinyTitan", "BrickStorm", "HappyBuilder", "QuestMochi", "EpicLena",
        "MiniDragon", "StudMaster", "BrickRider", "LuckyLego", "ToyRunner",
        "BuildStar", "CaptainStud", "NeonBlock", "QuestBee", "LegoDream",
        "BlockyZoe", "SkyBuilder", "BrickFlash", "UltraMini", "QuestFox",
        "RainbowStud", "BrickAngel", "MiniWizard", "StoreHunter", "ToyLegend",
        "BrickChamp", "YellowHero", "BlockPrincess", "NinjaLulu", "GalinQuest"
    ]

    states = ["NY", "CA", "MA", "FL", "TX", "IL", "WA", "NJ", "PA", "GA"]

    random.seed(8)

    ranking = []

    for i in range(50):
        ranking.append({
            "rank": i + 1,
            "name": player_names[i],
            "state": random.choice(states),
            "level": random.randint(3, 38),
            "xp": random.randint(800, 9800),
            "cards": random.randint(5, 80),
            "stores": random.randint(1, 28),
            "avatar": random.choice(["🙂", "😎", "🥷", "🚀", "🐉", "👑", "🧱"])
        })

    ranking = sorted(ranking, key=lambda x: x["xp"], reverse=True)

    for idx, player in enumerate(ranking):
        player["rank"] = idx + 1

    current_player = {
        "rank": 12,
        "name": st.session_state.get("avatar_name", "LULU"),
        "state": "MA",
        "level": level(),
        "xp": st.session_state.xp,
        "cards": len(st.session_state.collection),
        "stores": len(st.session_state.visited),
        "avatar": "🙂"
    }

    ranking.insert(11, current_player)

    rows_html = ""

    for p in ranking[:50]:

        if p["rank"] == 1:
            badge = "🥇"
            row_class = "top-one"
        elif p["rank"] == 2:
            badge = "🥈"
            row_class = "top-two"
        elif p["rank"] == 3:
            badge = "🥉"
            row_class = "top-three"
        else:
            badge = f"#{p['rank']}"
            row_class = ""

        if p["name"] == current_player["name"]:
            row_class += " current-player"

        rows_html += f"""
        <div class="rank-row {row_class}">
            <div class="rank-num">{badge}</div>
            <div class="rank-avatar">{p['avatar']}</div>
            <div class="rank-player">
                <div class="rank-name">{p['name']}</div>
                <div class="rank-meta">{p['state']} | Level {p['level']}</div>
            </div>
            <div class="rank-stat">⭐ {p['xp']}</div>
            <div class="rank-stat">🎴 {p['cards']}</div>
            <div class="rank-stat">📍 {p['stores']}</div>
        </div>
        """

    ranking_html = f"""
    <html>
    <head>
    <style>
    body {{
        margin:0;
        font-family:Arial,sans-serif;
        background:transparent;
    }}

    .ranking-page {{
        min-height:920px;
        border-radius:42px;
        border:8px solid white;
        padding:30px;
        background:
            radial-gradient(circle at 20% 10%, rgba(255,213,0,.45), transparent 18%),
            radial-gradient(circle at 90% 18%, rgba(0,109,183,.25), transparent 22%),
            linear-gradient(180deg,#7ED6FF 0%, #FFF1C7 100%);
        box-shadow:0 35px 90px rgba(0,0,0,.25);
        overflow:hidden;
        position:relative;
    }}

    .ranking-title {{
        display:flex;
        justify-content:space-between;
        align-items:center;
        margin-bottom:26px;
    }}

    .ranking-logo {{
        background:linear-gradient(180deg,#E3000B,#980005);
        color:white;
        border:6px solid #FFD500;
        border-radius:26px;
        padding:16px 30px;
        font-size:34px;
        font-weight:900;
        box-shadow:0 10px 0 #620004;
    }}

    .season-pill {{
        background:rgba(255,255,255,.92);
        border:5px solid white;
        border-radius:999px;
        padding:14px 22px;
        font-size:20px;
        font-weight:900;
        box-shadow:0 9px 0 rgba(0,0,0,.12);
    }}

    .podium {{
        display:grid;
        grid-template-columns:1fr 1.2fr 1fr;
        gap:22px;
        margin-bottom:28px;
        align-items:end;
    }}

    .podium-card {{
        border:7px solid white;
        border-radius:32px;
        text-align:center;
        padding:22px;
        background:rgba(255,255,255,.9);
        box-shadow:0 20px 45px rgba(0,0,0,.2);
        font-weight:900;
    }}

    .podium-card.first {{
        min-height:260px;
        background:linear-gradient(180deg,#FFF176,#FFD500);
        box-shadow:0 0 45px rgba(255,213,0,.8);
    }}

    .podium-card.second {{
        min-height:220px;
    }}

    .podium-card.third {{
        min-height:200px;
    }}

    .podium-avatar {{
        font-size:72px;
        margin:10px 0;
    }}

    .podium-rank {{
        font-size:42px;
    }}

    .leaderboard {{
        background:rgba(255,255,255,.9);
        border:8px solid white;
        border-radius:36px;
        padding:18px;
        box-shadow:0 25px 60px rgba(0,0,0,.22);
    }}

    .rank-header,
    .rank-row {{
        display:grid;
        grid-template-columns:90px 70px 1fr 120px 110px 110px;
        gap:14px;
        align-items:center;
    }}

    .rank-header {{
        padding:12px 18px;
        font-weight:900;
        color:#555;
        font-size:14px;
        letter-spacing:1px;
    }}

    .rank-row {{
        margin-bottom:12px;
        padding:14px 18px;
        border-radius:24px;
        background:linear-gradient(180deg,#FFFFFF,#F5F5F5);
        border:4px solid white;
        box-shadow:0 8px 0 rgba(0,0,0,.08);
        font-weight:900;
    }}

    .rank-num {{
        font-size:24px;
        color:#E3000B;
    }}

    .rank-avatar {{
        width:54px;
        height:54px;
        border-radius:18px;
        background:linear-gradient(180deg,#FFD500,#FF9F00);
        border:4px solid white;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:30px;
        box-shadow:0 6px 0 rgba(0,0,0,.12);
    }}

    .rank-name {{
        font-size:20px;
        color:#1E1E1E;
    }}

    .rank-meta {{
        font-size:13px;
        color:#666;
    }}

    .rank-stat {{
        background:#FFF5CC;
        border:3px solid white;
        border-radius:999px;
        padding:8px 12px;
        text-align:center;
        box-shadow:0 5px 0 rgba(0,0,0,.08);
    }}

    .top-one {{
        background:linear-gradient(180deg,#FFF176,#FFD500);
        box-shadow:0 0 35px rgba(255,213,0,.75);
    }}

    .top-two {{
        background:linear-gradient(180deg,#FFFFFF,#DDE7FF);
    }}

    .top-three {{
        background:linear-gradient(180deg,#FFE4C2,#FFB86B);
    }}

    .current-player {{
        outline:6px solid #006DB7;
        box-shadow:
            0 0 30px rgba(0,109,183,.7),
            0 8px 0 rgba(0,0,0,.08);
    }}

    .sparkle {{
        position:absolute;
        width:10px;
        height:10px;
        border-radius:50%;
        background:white;
        animation:sparkle 3s infinite;
    }}

    @keyframes sparkle {{
        0%,100% {{ transform:scale(.4); opacity:.2; }}
        50% {{ transform:scale(1.3); opacity:1; }}
    }}
    </style>
    </head>

    <body>
        <div class="ranking-page">

            <div class="sparkle" style="left:8%;top:18%;animation-delay:.2s;"></div>
            <div class="sparkle" style="left:88%;top:15%;animation-delay:1s;"></div>
            <div class="sparkle" style="left:70%;top:86%;animation-delay:1.6s;"></div>

            <div class="ranking-title">
                <div class="ranking-logo">🏆 US LEGO Quest Ranking</div>
                <div class="season-pill">Season 01 | United States</div>
            </div>

            <div class="podium">
                <div class="podium-card second">
                    <div class="podium-rank">🥈</div>
                    <div class="podium-avatar">{ranking[1]['avatar']}</div>
                    <h2>{ranking[1]['name']}</h2>
                    <p>{ranking[1]['xp']} XP</p>
                </div>

                <div class="podium-card first">
                    <div class="podium-rank">🥇</div>
                    <div class="podium-avatar">{ranking[0]['avatar']}</div>
                    <h1>{ranking[0]['name']}</h1>
                    <p>{ranking[0]['xp']} XP</p>
                </div>

                <div class="podium-card third">
                    <div class="podium-rank">🥉</div>
                    <div class="podium-avatar">{ranking[2]['avatar']}</div>
                    <h2>{ranking[2]['name']}</h2>
                    <p>{ranking[2]['xp']} XP</p>
                </div>
            </div>

            <div class="leaderboard">
                <div class="rank-header">
                    <div>RANK</div>
                    <div></div>
                    <div>PLAYER</div>
                    <div>XP</div>
                    <div>CARDS</div>
                    <div>STORES</div>
                </div>

                {rows_html}
            </div>

        </div>
    </body>
    </html>
    """

    components.html(
        ranking_html,
        height=980,
        scrolling=True
    )
# ------------------------- STORES -------------------------
if st.session_state.screen == "Stores":

    import pydeck as pdk

    st.markdown("""
    <style>
    .store-map-page {
        border-radius: 42px;
        border: 8px solid white;
        padding: 28px;
        background:
            radial-gradient(circle at 20% 10%, rgba(255,213,0,.45), transparent 18%),
            radial-gradient(circle at 90% 20%, rgba(0,109,183,.25), transparent 22%),
            linear-gradient(180deg,#7ED6FF 0%, #FFF1C7 100%);
        box-shadow: 0 35px 90px rgba(0,0,0,.25);
    }

    .store-title {
        background:linear-gradient(180deg,#E3000B,#980005);
        color:white;
        border:6px solid #FFD500;
        border-radius:26px;
        padding:16px 30px;
        font-size:34px;
        font-weight:900;
        display:inline-block;
        box-shadow:0 10px 0 #620004;
        margin-bottom:22px;
    }

    .map-card {
        border:8px solid white;
        border-radius:34px;
        overflow:hidden;
        box-shadow:0 25px 60px rgba(0,0,0,.25);
        background:white;
    }

    .store-card {
        background:rgba(255,255,255,.92);
        border:6px solid white;
        border-radius:28px;
        padding:18px;
        margin-bottom:14px;
        box-shadow:0 12px 0 rgba(0,0,0,.10), 0 22px 36px rgba(0,0,0,.16);
    }

    .store-card h3 {
        margin:0 0 6px 0;
        color:#E3000B;
    }

    .rarity-pill {
        display:inline-block;
        border:3px solid white;
        border-radius:999px;
        padding:7px 12px;
        font-weight:900;
        box-shadow:0 5px 0 rgba(0,0,0,.12);
        color:white;
    }

    .common-pill { background:#006DB7; }
    .rare-pill { background:#8E44AD; }
    .epic-pill { background:#F5A623; color:#1E1E1E; }
    .legendary-pill { background:linear-gradient(45deg,#ff004c,#ff9900,#ffee00,#00ffee,#0066ff,#cc00ff); }

    .chart-card {
        background:rgba(255,255,255,.92);
        border:6px solid white;
        border-radius:28px;
        padding:18px;
        margin:18px 0;
        box-shadow:0 12px 0 rgba(0,0,0,.10), 0 22px 36px rgba(0,0,0,.16);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="store-map-page">
        <div class="store-title">📍 LEGO Store Quest Map</div>
    """, unsafe_allow_html=True)

    map_df = df.copy()

    if "Latitude" in map_df.columns and "Longitude" in map_df.columns:
        map_df["Latitude"] = pd.to_numeric(map_df["Latitude"], errors="coerce")
        map_df["Longitude"] = pd.to_numeric(map_df["Longitude"], errors="coerce")
        map_df = map_df.dropna(subset=["Latitude", "Longitude"])
    else:
        map_df = pd.DataFrame(FALLBACK_STORES)

    # ------------------------------
    # ST1 / ST2: rarity selector for store recommendations
    # ------------------------------
    rarity_choice = st.select_slider(
        "Choose the rarity level you want to hunt for:",
        options=["Common", "Rare", "Epic", "Legendary"],
        value="Rare"
    )

    rarity_descriptions = {
        "Common": "Easy, low-pressure stores for casual browsing and a simple family-friendly quest.",
        "Rare": "Popular stores with stronger surrounding activities and a better outing experience.",
        "Epic": "Destination stores in high-energy areas where the trip feels more like an adventure.",
        "Legendary": "Flagship or vacation-style stores that feel like a special LEGO Quest event."
    }

    rarity_class = rarity_choice.lower() + "-pill"

    st.markdown(f"""
    <div class="store-card">
        <h3>🎯 Rarity Hunt Mode: {rarity_choice}</h3>
        <p style="font-weight:900;">{rarity_descriptions[rarity_choice]}</p>
        <span class="rarity-pill {rarity_class}">{rarity_choice} Store Hunt</span>
    </div>
    """, unsafe_allow_html=True)

    # ------------------------------
    # CHART1: dataset-level bar chart by state
    # ------------------------------
    if not map_df.empty and "State" in map_df.columns:
        state_counts = (
            map_df["State"]
            .astype(str)
            .replace("", "Unknown")
            .value_counts()
            .reset_index()
        )
        state_counts.columns = ["State", "Number of LEGO Stores"]

        fig_state = px.bar(
            state_counts.head(25),
            x="State",
            y="Number of LEGO Stores",
            text="Number of LEGO Stores",
            title="Number of LEGO Stores by State"
        )
        fig_state.update_traces(textposition="outside")
        fig_state.update_layout(
            title_x=0.5,
            xaxis_title="State",
            yaxis_title="Number of Stores",
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(fig_state, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------
    # Store recommendation logic, no Explore Score
    # ------------------------------
    recommended_stores = map_df.copy()

    if rarity_choice == "Common":
        # Simple nearby/suburban style picks: smaller list, stable and easy.
        recommended_stores = recommended_stores.head(8)
    elif rarity_choice == "Rare":
        # Good city/suburban mix.
        preferred_states = ["MA", "NY", "NJ", "PA", "CT", "CA", "FL"]
        filtered = recommended_stores[recommended_stores["State"].astype(str).isin(preferred_states)]
        recommended_stores = filtered.head(8) if not filtered.empty else recommended_stores.head(8)
    elif rarity_choice == "Epic":
        # Bigger destination-market states.
        preferred_states = ["NY", "CA", "FL", "IL", "MA", "TX", "NV"]
        filtered = recommended_stores[recommended_stores["State"].astype(str).isin(preferred_states)]
        recommended_stores = filtered.head(8) if not filtered.empty else recommended_stores.head(8)
    elif rarity_choice == "Legendary":
        # Flagship / vacation / destination language when available.
        name_addr = (
            recommended_stores.get("Store Name", "").astype(str) + " " +
            recommended_stores.get("Full Address", "").astype(str) + " " +
            recommended_stores.get("City", "").astype(str)
        )
        filtered = recommended_stores[
            name_addr.str.contains("Disney|Rockefeller|New York|Flagship|Las Vegas|Orlando|Anaheim|Mall of America", case=False, na=False)
        ]
        recommended_stores = filtered.head(8) if not filtered.empty else recommended_stores.head(8)

    recommended_stores = recommended_stores.head(8)

    if not map_df.empty:
        map_df["tooltip"] = (
            "<b>" + map_df["Store Name"].astype(str) + "</b><br/>"
            + map_df["City"].astype(str) + ", "
            + map_df["State"].astype(str) + "<br/>"
            + map_df["Full Address"].astype(str)
        )

    col1, col2 = st.columns([2.2, 0.9])

    with col1:
        st.markdown('<div class="map-card">', unsafe_allow_html=True)

        if not map_df.empty:
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position="[Longitude, Latitude]",
                get_radius=28000,
                get_fill_color="[227, 0, 11, 190]",
                get_line_color="[255, 213, 0, 255]",
                line_width_min_pixels=4,
                pickable=True,
            )

            text_layer = pdk.Layer(
                "TextLayer",
                data=map_df.head(20),
                get_position="[Longitude, Latitude]",
                get_text="Store Name",
                get_size=12,
                get_color="[30, 30, 30, 220]",
                get_alignment_baseline="bottom",
                get_pixel_offset="[0, -18]",
            )

            # Clear, readable national view; pitch removed so it is easier to see.
            view_state = pdk.ViewState(
                latitude=39.3,
                longitude=-96.5,
                zoom=3.0,
                pitch=0,
            )

            deck = pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state=view_state,
                layers=[layer, text_layer],
                tooltip={
                    "html": """
                    <b>{Store Name}</b><br/>
                    📍 {City}, {State}<br/>
                    {Full Address}
                    """,
                    "style": {
                        "backgroundColor": "#E3000B",
                        "color": "white",
                        "borderRadius": "14px",
                        "padding": "12px",
                        "fontWeight": "bold",
                    },
                },
            )

            st.pydeck_chart(deck, use_container_width=True)
        else:
            st.warning("No latitude/longitude data found for the map.")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f"### 🎯 Recommended Stores for {rarity_choice} Hunt")

        for _, row in recommended_stores.iterrows():
            st.markdown(f"""
            <div class="store-card">
                <h3>{row.get("Store Name", "LEGO Store")}</h3>
                <b>{row.get("City", "")}, {row.get("State", "")}</b><br>
                <small>{row.get("Full Address", "")}</small><br><br>
                <span class="rarity-pill {rarity_class}">{rarity_choice} Quest Pick</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
# =========================================================
# DEBUG / RESET
# =========================================================
with st.expander("Developer Controls"):
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Reset Game"):
            for key in ["xp", "coins", "gems", "visited", "collection", "last_drop", "show_reward"]:
                if key in st.session_state:
                    del st.session_state[key]
            init_state()
            st.rerun()
    with c2:
        if st.button("Add Test Legendary"):
            legendary = [x for x in DROPS if x["rarity"] == "Legendary"][0]
            st.session_state.collection.append(legendary)
            st.session_state.last_drop = legendary
            st.session_state.xp += legendary["xp"]
            st.session_state.show_reward = True
            st.rerun()
    with c3:
        st.write("Data rows:", len(df))
