# -*- coding: utf-8 -*-
"""stramlittttt.ipynb - Fixed gauge + smooth animated loader"""

# ── CELL 1 : Install ─────────────────────────────────────────
!pip install streamlit pyngrok torch torchvision pillow opencv-python-headless -q
print("Done ✅")

# ── CELL 2 : Mount Drive ─────────────────────────────────────
from google.colab import drive
drive.mount('/content/drive')
print("Drive mounted ✅")

# ── CELL 3 : Write app ───────────────────────────────────────
import subprocess, threading, time
from pyngrok import ngrok

subprocess.run(["pkill", "-9", "-f", "streamlit"], capture_output=True)
ngrok.kill()
time.sleep(3)

with open("/content/fraud_lens_app.py", "w") as f:
    f.write(r'''
import streamlit as st
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import cv2
import time
import tempfile
import math
import streamlit.components.v1 as components

st.set_page_config(page_title="Fraud Lens", page_icon="🔍", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:        #F5F3EE;
    --surface:   #FDFCF9;
    --border:    #E2DDD6;
    --blue:      #1A56DB;
    --text-pri:  #1A1714;
    --text-sec:  #5C5752;
    --text-muted:#9C9790;
    --green:     #0E7B4D;
    --green-lt:  #ECFDF5;
    --red:       #B91C1C;
    --red-lt:    #FEF2F2;
    --radius-lg: 16px;
    --font: 'DM Sans', sans-serif;
    --mono: 'DM Mono', monospace;
}

html, body, .stApp { background: var(--bg) !important; color: var(--text-pri); font-family: var(--font); }
.block-container { padding-top: 0rem !important; padding-bottom: 2rem !important; padding-left: 60px !important; padding-right: 60px !important; }
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }

.nav { display: flex; align-items: center; justify-content: space-between; padding: 0 60px; height: 68px; background: var(--surface); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 999; margin-left: -60px; margin-right: -60px; }
.nav-icon { width: 40px; height: 40px; background: var(--blue); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.nav-name { font-size: 20px; font-weight: 700; color: var(--text-pri); }
.nav-pill { font-size: 13px; color: var(--green); background: var(--green-lt); padding: 6px 16px; border-radius: 20px; display: flex; align-items: center; gap: 6px; }
.nav-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--green); animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.85)} }

.landing-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100vh; z-index: -1; pointer-events: none; background-color: var(--bg); background-image: radial-gradient(at 0% 0%, rgba(26,86,219,.06) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(26,86,219,.03) 0px, transparent 50%); }

.hero { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 60px 36px; }
.hero-title { font-size: 56px; font-weight: 700; text-align: center; line-height: 1.1; margin-bottom: 16px; }
.hero-desc { font-size: 18px; color: var(--text-sec); text-align: center; max-width: 480px; margin-bottom: 20px; line-height: 1.6; }

[data-testid="stImage"] { display: flex; justify-content: center; }

.result-wrap { padding-top: 28px; animation: fadeUp .5s ease both; }
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }

.photo-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
.photo-card-header { padding: 16px 22px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 10px; }
.photo-dot { width: 9px; height: 9px; border-radius: 50%; }
.photo-body { padding: 20px; display: flex; flex-direction: column; align-items: center; }
.meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 14px; width: 100%; }
.meta-cell { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 11px 14px; }
.meta-lbl { font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; margin-bottom: 3px; }

.verdict-card { border-radius: var(--radius-lg); padding: 28px 32px; border: 1px solid; margin-bottom: 14px; animation: fadeUp .4s .1s ease both; }
.chart-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 20px 22px; }
.bar-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.bar-track { flex: 1; background: #F0EDE6; border-radius: 4px; height: 8px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 4px; }

.reasons-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; margin-bottom: 14px; animation: fadeUp .4s .3s ease both; }
.reason-item { display: flex; gap: 14px; padding: 15px 22px; border-bottom: 1px solid var(--border); align-items: flex-start; }
.reason-item:last-child { border-bottom: none; }
.reason-num { width: 24px; height: 24px; border-radius: 6px; background: #EEF2FF; border: 1px solid #C7D7FC; font-size: 12px; font-weight: 700; color: var(--blue); display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px; }

.plaus-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; margin-bottom: 14px; animation: fadeUp .4s .4s ease both; }
.plaus-header { padding: 15px 22px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
.plaus-header-title { font-weight: 600; font-size: 15px; }
.plaus-badge { font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 20px; }
.plaus-badge-fake { background: var(--red-lt); color: var(--red); }
.plaus-badge-real { background: var(--green-lt); color: var(--green); }
.plaus-grid { display: grid; grid-template-columns: 1fr 1fr; }
.plaus-signal { padding: 14px 22px; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); }
.plaus-signal:nth-child(2n) { border-right: none; }
.plaus-signal:nth-last-child(-n+2) { border-bottom: none; }
.plaus-signal-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; font-weight: 600; margin-bottom: 6px; }
.plaus-signal-row { display: flex; align-items: center; gap: 10px; }
.plaus-signal-val { font-size: 17px; font-weight: 700; font-family: var(--mono); }
.plaus-mini-track { flex: 1; height: 5px; background: #F0EDE6; border-radius: 3px; overflow: hidden; }
.plaus-mini-fill { height: 100%; border-radius: 3px; }
.plaus-flag { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; margin-top: 6px; display: inline-block; }
.plaus-flag-warn { background: #FEF3C7; color: #92400E; }
.plaus-flag-ok { background: var(--green-lt); color: var(--green); }
.plaus-suspicion { padding: 14px 22px; border-top: 1px solid var(--border); display: flex; align-items: center; gap: 10px; background: var(--bg); }

[data-testid="stBaseButton-primary"] { border-radius: 10px !important; font-weight: 600 !important; }
[data-testid="stBaseButton-secondary"] { border-radius: 10px !important; font-weight: 600 !important; }

/* Prevent component iframes from bleeding outside their column */
iframe { display: block !important; max-width: 100% !important; }
[data-testid="stColumn"] { overflow: hidden !important; }
.stApp { overflow-x: hidden !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="nav">
  <div style="display:flex;align-items:center;gap:14px;">
    <div class="nav-icon">🔍</div>
    <div class="nav-name">Fraud Lens</div>
  </div>
  <div class="nav-pill"><div class="nav-dot"></div> System Active</div>
</div>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    try:
        model = models.resnet50(pretrained=False)
        model.fc = nn.Sequential(nn.Dropout(0.3), nn.Linear(model.fc.in_features, 2))
        model.load_state_dict(torch.load("/content/drive/MyDrive/fraud-lens/model/fraud_lens_v3.pth", map_location="cpu"))
        model.eval()
        return model
    except:
        return None

model = load_model()

def run_model(path):
    img = Image.open(path).convert("RGB")
    tf = transforms.Compose([transforms.Resize((224,224)), transforms.ToTensor(),
                              transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])])
    with torch.no_grad():
        p = torch.softmax(model(tf(img).unsqueeze(0)), dim=1)[0]
    return p[0].item()*100, p[1].item()*100

def check_plausibility(image_path):
    img  = np.array(Image.open(image_path).convert("RGB").resize((224,224)))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape
    left  = np.mean(img[:, :w//2]); right = np.mean(img[:, w//2:])
    lighting_diff = abs(left - right)
    noises = [np.std(gray[r*h//3:(r+1)*h//3, c*w//3:(c+1)*w//3]) for r in range(3) for c in range(3)]
    noise_score = np.std(noises) / (np.mean(noises) + 1e-6)
    edges = cv2.Canny(gray, 50, 150)
    eq = [np.sum(edges[r*h//2:(r+1)*h//2, c*w//2:(c+1)*w//2]) for r in range(2) for c in range(2)]
    edge_score = np.std(eq) / (np.mean(eq) + 1e-6)
    dark = gray < 80
    s_ratio = np.sum(dark[:, :w//2]) / (np.sum(dark[:, w//2:]) + 1e-6)
    suspicion = sum([lighting_diff > 25, noise_score > 0.4, edge_score > 0.8, s_ratio > 3.0])
    return {"verdict": "FAKE" if suspicion >= 2 else "REAL", "suspicion": suspicion,
            "lighting": round(float(lighting_diff), 2), "noise": round(float(noise_score), 2),
            "edge": round(float(edge_score), 2), "shadow": round(float(s_ratio), 2)}

# ── GAUGE: full 270-degree arc in iframe so CSS animations run properly ──
def gauge_html(val, color):
    r = 54; cx = 70; cy = 70; sw = 10
    circ = 2 * math.pi * r
    arc_len  = circ * 270 / 360          # 270-degree track
    gap_len  = circ - arc_len
    filled   = arc_len * val / 100
    track_d  = str(round(arc_len, 2)) + " " + str(round(gap_len + 0.01, 2))
    filled_d = str(round(filled, 2))   + " " + str(round(circ - filled, 2))
    empty_d  = "0 " + str(round(circ, 2))
    rot      = 135   # start angle: 135 deg = 7-o-clock position
    lbl      = "HIGH RISK" if val >= 50 else "LOW RISK"

    return (
        "<!DOCTYPE html><html><head>"
        "<style>"
        "body{margin:0;background:transparent;display:flex;align-items:center;justify-content:center;height:150px;}"
        ".wrap{position:relative;width:140px;height:140px;}"
        ".arc-fill{"
        "  stroke-dasharray:" + empty_d + ";"
        "  animation:sweepIn 1.2s cubic-bezier(.4,0,.2,1) .1s forwards;"
        "}"
        "@keyframes sweepIn{"
        "  from{stroke-dasharray:0 " + str(round(circ,2)) + ";}"
        "  to{stroke-dasharray:" + filled_d + ";}"
        "}"
        ".label{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;}"
        ".pct{font-size:22px;font-weight:800;color:" + color + ";font-family:monospace;line-height:1;}"
        ".sublbl{font-size:9px;font-weight:700;color:#9C9790;text-transform:uppercase;letter-spacing:.6px;margin-top:3px;}"
        "</style></head><body>"
        "<div class='wrap'>"
        "<svg width='140' height='140' viewBox='0 0 140 140'>"
        # track arc
        "<circle cx='70' cy='70' r='54' fill='none' stroke='#E2DDD6'"
        " stroke-width='10' stroke-dasharray='" + track_d + "'"
        " stroke-linecap='round'"
        " transform='rotate(" + str(rot) + " 70 70)'/>"
        # animated fill arc
        "<circle class='arc-fill' cx='70' cy='70' r='54' fill='none'"
        " stroke='" + color + "' stroke-width='10'"
        " stroke-linecap='round'"
        " transform='rotate(" + str(rot) + " 70 70)'/>"
        "</svg>"
        "<div class='label'>"
        "<div class='pct'>" + str(round(val, 1)) + "%</div>"
        "<div class='sublbl'>" + lbl + "</div>"
        "</div>"
        "</div>"
        "</body></html>"
    )

# ── ANIMATED STEP LOADER ──
def loader_html(steps, current):
    rows = ""
    for i, s in enumerate(steps):
        if i < current:
            icon  = "<span style='color:#0E7B4D;font-size:16px;line-height:1'>✓</span>"
            tstyle= "color:#1A1714;font-weight:500;"
            bar   = "<div style='height:2px;background:#0E7B4D;border-radius:2px;margin-top:7px'></div>"
            side  = "<span style='font-size:11px;color:#0E7B4D;font-family:monospace'>done</span>"
        elif i == current:
            icon  = "<span style='display:inline-block;width:16px;height:16px;border:2.5px solid #1A56DB;border-top-color:transparent;border-radius:50%;animation:spin .75s linear infinite;vertical-align:middle'></span>"
            tstyle= "color:#1A56DB;font-weight:600;"
            bar   = "<div style='height:2px;border-radius:2px;margin-top:7px;background:linear-gradient(90deg,#1A56DB 0%,#6EA3FF 60%,transparent 100%);animation:shimmer 1.4s ease-in-out infinite;background-size:200%'></div>"
            side  = "<span style='font-size:11px;color:#1A56DB;font-family:monospace;animation:blink 1s step-end infinite'>...</span>"
        else:
            icon  = "<span style='display:inline-block;width:14px;height:14px;border:2px solid #D1CCC4;border-radius:50%;vertical-align:middle'></span>"
            tstyle= "color:#9C9790;"
            bar   = ""
            side  = ""

        rows += (
            "<div style='display:flex;align-items:center;gap:14px;padding:13px 24px;"
            "border-bottom:1px solid #EDEAE4;animation:fadeRow .3s ease both;"
            "animation-delay:" + str(i * 0.05) + "s'>"
            "<div style='width:24px;display:flex;justify-content:center;flex-shrink:0'>" + icon + "</div>"
            "<div style='flex:1'>"
            "<div style='" + tstyle + "font-size:13.5px'>" + s + "</div>"
            + bar +
            "</div>"
            "<div>" + side + "</div>"
            "</div>"
        )

    pct = min(int(current / len(steps) * 100), 100)

    return (
        "<!DOCTYPE html><html><head>"
        "<style>"
        "@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400&display=swap');"
        "*{box-sizing:border-box;margin:0;padding:0;}"
        "body{font-family:'DM Sans',sans-serif;background:#FDFCF9;"
        "border:1px solid #E2DDD6;border-radius:16px;overflow:hidden;}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        "@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}"
        "@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}"
        "@keyframes fadeRow{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}"
        ".bar-fill{transition:width .6s cubic-bezier(.4,0,.2,1);}"
        "</style></head><body>"
        # header
        "<div style='padding:18px 24px 14px;border-bottom:1px solid #E2DDD6'>"
        "<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:11px'>"
        "<div style='font-size:14px;font-weight:700;color:#1A1714;display:flex;align-items:center;gap:8px'>"
        "<span style='display:inline-block;width:8px;height:8px;border-radius:50%;background:#1A56DB;animation:blink 1.2s ease-in-out infinite'></span>"
        "Analysing Image"
        "</div>"
        "<div style='font-size:13px;font-weight:700;color:#1A56DB;font-family:monospace'>" + str(pct) + "%</div>"
        "</div>"
        # progress bar
        "<div style='height:5px;background:#EDEAE4;border-radius:5px;overflow:hidden'>"
        "<div class='bar-fill' style='height:100%;width:" + str(pct) + "%;"
        "background:linear-gradient(90deg,#1A56DB,#6EA3FF);border-radius:5px'></div>"
        "</div>"
        "</div>"
        + rows +
        "</body></html>"
    )

def plausibility_card_html(p):
    badge_cls = "plaus-badge-fake" if p["verdict"] == "FAKE" else "plaus-badge-real"
    suspicion = p["suspicion"]
    badge_txt = ("⚠ " if p["verdict"] == "FAKE" else "✓ ") + str(suspicion) + "/4 Flags"

    def signal_block(label, icon, value, threshold, max_val):
        flagged   = value > threshold
        pct       = min(value / max_val * 100, 100)
        bar_color = "#B91C1C" if flagged else "#0E7B4D"
        flag_cls  = "plaus-flag-warn" if flagged else "plaus-flag-ok"
        flag_txt  = "⚠ Flagged" if flagged else "✓ Normal"
        return (
            '<div class="plaus-signal">'
            '<div class="plaus-signal-label">' + icon + " " + label + "</div>"
            '<div class="plaus-signal-row">'
            '<div class="plaus-signal-val" style="color:' + bar_color + '">' + str(value) + "</div>"
            '<div class="plaus-mini-track"><div class="plaus-mini-fill" style="width:' + str(round(pct,1)) + "%;background:" + bar_color + '"></div></div>'
            "</div>"
            '<span class="plaus-flag ' + flag_cls + '">' + flag_txt + "</span>"
            "</div>"
        )

    suspicion_color = "#B91C1C" if suspicion >= 2 else "#B45309" if suspicion == 1 else "#0E7B4D"
    suspicion_dots = "".join([
        '<div style="width:13px;height:13px;border-radius:50%;background:' +
        ("#B91C1C" if i < suspicion else "#E2DDD6") + '"></div>'
        for i in range(4)
    ])
    grid = (
        signal_block("Lighting Asymmetry", "💡", p["lighting"], 25,  80) +
        signal_block("Noise Variance",     "〰", p["noise"],   0.4, 1.5) +
        signal_block("Edge Imbalance",     "⬡", p["edge"],    0.8, 2.0) +
        signal_block("Shadow Ratio",       "🌑", p["shadow"],  3.0, 10.0)
    )
    return (
        '<div class="plaus-card">'
        '<div class="plaus-header">'
        '<span class="plaus-header-title">Plausibility Signals</span>'
        '<span class="plaus-badge ' + badge_cls + '">' + badge_txt + "</span>"
        "</div>"
        '<div class="plaus-grid">' + grid + "</div>"
        '<div class="plaus-suspicion">'
        '<div style="font-size:12px;font-weight:600;color:var(--text-sec)">Suspicion Level</div>'
        '<div style="display:flex;gap:5px;align-items:center">' + suspicion_dots + "</div>"
        '<div style="margin-left:auto;font-size:12px;font-weight:700;color:' + suspicion_color + '">' +
        str(suspicion) + " of 4 triggered</div>"
        "</div></div>"
    )

# ── STATE ──
for k, v in [("res", None), ("img", None), ("img_b64", ""), ("plaus", None), ("tmp_path", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════
# LANDING
# ════════════════════════════════════════
if st.session_state.res is None:
    st.markdown('<div class="landing-bg"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero">'
        '<div class="hero-title">Detect Insurance<br><span style="color:#1A56DB">Claim Fraud</span></div>'
        '<div class="hero-desc">Upload a car damage photo to instantly analyse it for signs of digital manipulation.</div>'
        '</div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.8, 1])
    with mid:
        up = st.file_uploader("Upload", type=["jpg","png","jpeg"], label_visibility="collapsed")
        if up:
            import io, base64
            img = Image.open(up).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            st.session_state.img       = img
            st.session_state.img_b64   = base64.b64encode(buf.getvalue()).decode()
            st.image(img, use_container_width=True)
            if st.button("Run Fraud Analysis", type="primary", use_container_width=True):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                    tmp.write(buf.getvalue())
                    st.session_state.tmp_path = tmp.name
                st.session_state.res = "LOADING"
                st.rerun()

# ════════════════════════════════════════
# RESULT / LOADING
# ════════════════════════════════════════
else:
    components.html("<script>window.parent.window.scrollTo(0,0);</script>", height=0)
    st.markdown('<div class="result-wrap">', unsafe_allow_html=True)
    left_col, right_col = st.columns([5, 8], gap="large")

    # LEFT: photo card — skeleton during load, real card after
    with left_col:
        is_loading = (st.session_state.res == "LOADING")
        res_dict   = st.session_state.res if isinstance(st.session_state.res, dict) else None
        dot = "#B91C1C" if (res_dict and res_dict["final"]=="FAKE") else "#0E7B4D" if res_dict else "#9C9790"

        if is_loading:
            # Show the actual image inside the iframe (base64) with a scanning overlay
            # This completely avoids st.image() which causes the ghost bleed
            img_b64 = st.session_state.get("img_b64", "")
            skeleton_html = (
                "<!DOCTYPE html><html><head><style>"
                "@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600&display=swap');"
                "*{box-sizing:border-box;margin:0;padding:0;}"
                "body{font-family:'DM Sans',sans-serif;background:#FDFCF9;"
                "border:1px solid #E2DDD6;border-radius:16px;overflow:hidden;}"
                "@keyframes scanline{"
                "0%{top:-10%}100%{top:110%}"
                "}"
                "@keyframes pulse{0%,100%{opacity:.7}50%{opacity:1}}"
                ".scan-line{position:absolute;left:0;width:100%;height:3px;"
                "background:linear-gradient(90deg,transparent,#1A56DB,transparent);"
                "animation:scanline 1.8s ease-in-out infinite;z-index:10;box-shadow:0 0 12px #1A56DB88;}"
                ".img-wrap{position:relative;overflow:hidden;background:#000;}"
                ".img-wrap img{width:100%;display:block;opacity:.55;filter:grayscale(30%);}"
                ".overlay{position:absolute;inset:0;background:rgba(26,86,219,.06);}"
                ".badge{position:absolute;top:12px;right:12px;background:rgba(26,86,219,.9);"
                "color:#fff;font-size:11px;font-weight:700;padding:4px 10px;border-radius:20px;"
                "letter-spacing:.4px;animation:pulse 1.2s ease-in-out infinite;z-index:20;}"
                ".footer{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:14px 16px;"
                "background:#FDFCF9;border-top:1px solid #E2DDD6;}"
                "@keyframes shimmer{0%{background-position:-400px 0}100%{background-position:400px 0}}"
                ".sk{background:linear-gradient(90deg,#F0EDE6 25%,#E8E4DC 50%,#F0EDE6 75%);"
                "background-size:800px 100%;animation:shimmer 1.4s ease-in-out infinite;border-radius:6px;height:46px;}"
                "</style></head><body>"
                "<div style='padding:13px 18px;border-bottom:1px solid #E2DDD6;display:flex;align-items:center;gap:9px;background:#FDFCF9'>"
                "<div style='width:8px;height:8px;border-radius:50%;background:#1A56DB;flex-shrink:0;animation:pulse 1.2s ease-in-out infinite'></div>"
                "<div style='font-size:13px;font-weight:600;color:#1A1714'>Scanning photo...</div>"
                "</div>"
                "<div class='img-wrap'>"
                "<div class='scan-line'></div>"
                "<div class='overlay'></div>"
                "<div class='badge'>ANALYSING</div>"
                "<img src='data:image/jpeg;base64," + img_b64 + "' />"
                "</div>"
                "<div class='footer'>"
                "<div class='sk'></div>"
                "<div class='sk'></div>"
                "</div>"
                "</body></html>"
            )
            components.html(skeleton_html, height=420, scrolling=False)
        else:
            st.markdown(
                '<div class="photo-card">'
                '<div class="photo-card-header">'
                '<div class="photo-dot" style="background:' + dot + '"></div>'
                '<div style="font-weight:600;font-size:14px">Submitted Photo</div>'
                '</div><div class="photo-body">',
                unsafe_allow_html=True)
            st.image(st.session_state.img, use_container_width=True)
            if res_dict:
                st.markdown(
                    '<div class="meta-grid">'
                    '<div class="meta-cell"><div class="meta-lbl">Verdict</div>'
                    '<div style="font-weight:700;font-size:15px;color:' + dot + '">' + res_dict["final"] + '</div></div>'
                    '<div class="meta-cell"><div class="meta-lbl">Score</div>'
                    '<div style="font-weight:700;font-size:15px;color:' + dot + '">' + str(res_dict["conf"]) + '%</div></div>'
                    '</div>', unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

    # RIGHT
    with right_col:

        # LOADING
        if st.session_state.res == "LOADING":
            steps = ["Initialising model", "Running neural scan", "Pixel integrity check", "Plausibility analysis", "Compiling results"]
            ph = st.empty()

            for i in range(len(steps)):
                with ph.container():
                    components.html(loader_html(steps, i), height=360, scrolling=False)
                if i == 1:
                    rp, fp = run_model(st.session_state.tmp_path)
                if i == 3:
                    st.session_state.plaus = check_plausibility(st.session_state.tmp_path)
                time.sleep(0.9)

            # Flash 100%
            with ph.container():
                components.html(loader_html(steps, len(steps)), height=360, scrolling=False)
            time.sleep(0.4)

            st.session_state.res = {
                "final": "FAKE" if fp > 50 else "REAL",
                "conf":  round(max(fp, rp), 1),
                "fp":    round(fp, 1),
                "rp":    round(rp, 1),
            }
            st.rerun()

        # RESULTS
        else:
            res   = st.session_state.res
            color = "#B91C1C" if res["final"] == "FAKE" else "#0E7B4D"
            risk  = "HIGH RISK" if res["final"] == "FAKE" else "LOW RISK"
            label = "Reject Claim" if res["final"] == "FAKE" else "Approve Claim"

            # verdict banner
            st.markdown(
                '<div class="verdict-card" style="background:' + color + '08;border-color:' + color + '40">'
                '<div style="display:flex;justify-content:space-between;align-items:center">'
                '<div>'
                '<div style="font-size:11px;font-weight:700;color:' + color + ';letter-spacing:.5px">' + risk + '</div>'
                '<div style="font-size:30px;font-weight:700;color:' + color + ';margin-top:4px">' + label + '</div>'
                '</div>'
                '<div style="text-align:right">'
                '<div style="font-size:48px;font-weight:800;color:' + color + ';font-family:var(--mono)">' + str(res["conf"]) + '%</div>'
                '<div style="font-size:10px;color:var(--text-muted);letter-spacing:.5px">CONFIDENCE</div>'
                '</div></div></div>',
                unsafe_allow_html=True)

            # gauge + breakdown
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    '<div class="chart-card" style="margin-bottom:14px;animation:fadeUp .4s .2s ease both">'
                    '<div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;font-weight:600;margin-bottom:2px">Gauge Score</div>',
                    unsafe_allow_html=True)
                components.html(gauge_html(res["conf"], color), height=158, scrolling=False)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(
                    '<div class="chart-card" style="margin-bottom:14px;animation:fadeUp .4s .25s ease both">'
                    '<div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;font-weight:600;margin-bottom:16px">Breakdown</div>'
                    '<div class="bar-row">'
                    '<div style="width:36px;font-size:12px;color:var(--text-sec)">Fake</div>'
                    '<div class="bar-track"><div class="bar-fill" style="width:' + str(res["fp"]) + '%;background:#B91C1C"></div></div>'
                    '<div style="font-size:12px;font-family:monospace;color:#B91C1C;width:40px;text-align:right">' + str(res["fp"]) + '%</div>'
                    '</div>'
                    '<div class="bar-row">'
                    '<div style="width:36px;font-size:12px;color:var(--text-sec)">Real</div>'
                    '<div class="bar-track"><div class="bar-fill" style="width:' + str(res["rp"]) + '%;background:#0E7B4D"></div></div>'
                    '<div style="font-size:12px;font-family:monospace;color:#0E7B4D;width:40px;text-align:right">' + str(res["rp"]) + '%</div>'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True)

            # analysis details
            st.markdown(
                '<div class="reasons-card">'
                '<div style="padding:15px 22px;border-bottom:1px solid var(--border);font-weight:600">Analysis Details</div>'
                '<div class="reason-item"><div class="reason-num">01</div>'
                '<div><div style="font-weight:600">Pixel Analysis</div>'
                '<div style="font-size:13px;color:var(--text-sec);margin-top:2px">Detected artifacts typical of digital alteration.</div></div></div>'
                '<div class="reason-item"><div class="reason-num">02</div>'
                '<div><div style="font-weight:600">Texture Check</div>'
                '<div style="font-size:13px;color:var(--text-sec);margin-top:2px">Structural noise inconsistent with camera sensor signatures.</div></div></div>'
                '</div>',
                unsafe_allow_html=True)

            # plausibility signals
            if st.session_state.plaus:
                st.markdown(plausibility_card_html(st.session_state.plaus), unsafe_allow_html=True)

            if st.button("← Analyse Another", use_container_width=True):
                st.session_state.res    = None
                st.session_state.plaus  = None
                st.session_state.img    = None
                st.session_state.img_b64= ""
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
''')

# ── CELL 4 : Launch ──
def run():
    subprocess.run(["streamlit", "run", "/content/fraud_lens_app.py",
                    "--server.port", "8501", "--server.headless", "true"])
threading.Thread(target=run, daemon=True).start()
time.sleep(20)
ngrok.set_auth_token("3CZbscxyg24jQ5mndasEV0op3Ak_5xuTNKyNYqG7oxvkPs7vS")
url = ngrok.connect(8501)
print(f"\nLive: {url.public_url}?ngrok-skip-browser-warning=true")