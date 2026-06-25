import streamlit as st


def setup_config():
    st.set_page_config(
        page_title="ORI — Ton conseiller orientation · L'Étudiant",
        page_icon=None,
        layout="centered",
        initial_sidebar_state="expanded",
    )


def load_css():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&family=Atkinson+Hyperlegible:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  /* ── Brand (DS Tomato) ── */
  --le-red: #e71336;
  --le-red-dark: #c1102d;
  --le-red-soft: #fdebef;

  /* ── Night scale ── */
  --le-ink: #1b232b;        /* Night 600 */
  --le-night-500: #272e36;
  --le-night-400: #333a41;
  --le-text: #1b232b;       /* Titres = Night 600 */
  --le-muted: #6b7176;

  /* ── Stone / Neutral ── */
  --le-border: #d8dadb;     /* Stone 100 */
  --le-grey: #f3f2ee;       /* Fond de page L'Étudiant prod (beige chaud) */
  --le-grey-2: #eef0f1;
  --le-stone-50: #f9fafb;
  --le-stone-300: #c8cacc;

  /* ── Couleurs de rubriques ── */
  --le-ori: #0597f2;        /* Orientation Blue */
  --le-apple: #c0df16;      /* Collège */
  --le-citrus: #ffb600;     /* Bac */
  --le-raspberry: #ef4b81;  /* Alternance */
  --le-spritz: #ff6a14;     /* Vie étudiante */
  --le-pool: #0085bf;       /* UI fonctionnel */
  --le-mint: #00a82d;       /* Succès / validation */

  /* ── Ombres (subtiles, style prod) ── */
  --shadow-xs: 0 1px 2px rgba(27,35,43,.04);
  --shadow-sm: 0 2px 6px rgba(27,35,43,.05);
  --shadow-md: 0 4px 12px rgba(27,35,43,.08);
  --shadow-lg: 0 10px 30px rgba(27,35,43,.12);

  /* ── Rayons (DS tw-rounded-*) ── */
  --r-sm: 2px;   /* tw-rounded-sm — boutons, inputs */
  --r-md: 8px;   /* tw-rounded-lg — cartes */
  --r-lg: 8px;   /* cartes plus grandes */
  --r-xl: 8px;   /* swipe cards (aligné DS) */
}

/* ══════════ Base ══════════ */
html, body, [class*="css"], .stMarkdown, p, span, div, li, label, input, textarea {
  font-family: 'Outfit', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--le-text);
}
h1, h2, h3, h4, .display, .eyebrow {
  font-family: 'Barlow Condensed', sans-serif !important;
  letter-spacing: -.01em;
}
.stApp { background: var(--le-grey); }

/* Hide Streamlit chrome */
#MainMenu, footer, header, .stDeployButton, div[data-testid="stDecoration"], div[data-testid="stToolbar"] { display: none !important; }

/* Main container width — narrow, conversational */
.block-container {
  padding: 84px 1rem 6rem !important;
  max-width: 760px !important;
}
@media (max-width: 640px){ .block-container { padding: 76px .6rem 6rem !important; } }

/* ══════════ Top nav (Header Tomato — DS §1.7) ══════════ */
.ori-nav {
  position: fixed; top: 0; left: 0; right: 0; height: 56px; z-index: 99990;
  background: var(--le-red);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 1rem;
  box-shadow: 0 1px 6px rgba(231,19,54,.18);
}
.ori-nav-l { display: flex; align-items: center; gap: 10px; }
.ori-mark {
  font-family: 'Barlow Condensed', sans-serif; font-weight: 800; font-size: 1.5rem;
  color: #fff; line-height: 1; letter-spacing: .02em;
}
.ori-nav img { height: 20px; display: block; opacity: .95; }
.ori-pill {
  font-family: 'Outfit', sans-serif; font-size: .58rem; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase; color: var(--le-ink); background: #fff;
  padding: 2px 7px; border-radius: var(--r-sm);
}
.ori-nav-r { color: rgba(255,255,255,.92); font-size: .8rem; font-weight: 600; font-family: 'Outfit', sans-serif; }
@media (max-width: 640px){ .ori-nav-r { display: none; } }

/* ══════════ Sidebar (DS §1.8 light mode) ══════════ */
section[data-testid="stSidebar"] { background: var(--le-stone-50); border-right: 1px solid #e5e7eb; }
section[data-testid="stSidebar"] > div { padding-top: 68px; }
.side-h {
  font-family: 'Barlow Condensed', sans-serif; text-transform: uppercase; letter-spacing: .06em;
  font-size: .72rem; font-weight: 700; color: var(--le-muted); margin: .25rem 0 .6rem;
}

/* ══════════ Buttons (DS §1.3 — rectangular, tw-rounded-sm) ══════════ */
.stButton > button {
  width: 100%;
  background: #fff; color: var(--le-ink);
  border: 1.5px solid var(--le-ink); border-radius: var(--r-sm);
  font-family: 'Outfit', sans-serif; font-weight: 700; font-size: .88rem;
  padding: .45rem 1rem; transition: all .2s ease; line-height: 1.25;
  height: 36px;
}
.stButton > button:hover {
  background: var(--le-stone-50); border-color: var(--le-night-500); color: var(--le-ink);
}
.stButton > button:active { transform: translateY(1px); }
.stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
  background: var(--le-red); color: #fff; border-color: var(--le-red);
}
.stButton > button[kind="primary"]:hover { background: var(--le-red-dark); border-color: var(--le-red-dark); color: #fff; }

/* Form submit = solid Tomato */
.stFormSubmitButton > button { background: var(--le-red) !important; color:#fff !important; border:none !important; border-radius: var(--r-sm) !important; font-weight:700 !important; }
.stFormSubmitButton > button:hover { background: var(--le-red-dark) !important; }

/* ══════════ Chat messages ══════════ */
div[data-testid="stChatMessage"] {
  background: transparent; padding: .15rem 0; gap: .75rem;
}
div[data-testid="stChatMessage"]:has(img[alt="assistant avatar"]) .stMarkdown,
div[data-testid="stChatMessageContent"] { font-size: .95rem; line-height: 1.6; font-family: 'Atkinson Hyperlegible', 'Outfit', sans-serif; }
div[data-testid="stChatMessageAvatarAssistant"] { background: var(--le-red) !important; border-radius: var(--r-sm) !important; }
div[data-testid="stChatMessageAvatarUser"] { background: var(--le-ink) !important; border-radius: var(--r-sm) !important; }

/* ══════════ Quick-reply chips ══════════ */
.chips-label { font-size: .72rem; color: var(--le-muted); margin: .2rem 0 .35rem; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; }

/* ══════════ Métier card (DS §1.6 — rounded-lg, stone border) ══════════ */
.metier-card {
  background: #fff; border: 1px solid var(--le-border); border-radius: var(--r-md);
  padding: 1rem 1.1rem; margin: .5rem 0; box-shadow: var(--shadow-xs);
  transition: box-shadow .2s ease, transform .2s ease, border-color .2s ease;
}
.metier-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); border-color: var(--le-stone-300); }
.metier-top { display:flex; align-items:center; gap:.6rem; margin-bottom:.35rem; }
.metier-ico {
  width: 36px; height: 36px; flex:0 0 36px; border-radius: var(--r-sm); background: var(--le-red-soft);
  display:flex; align-items:center; justify-content:center; font-size: 1.1rem;
}
.metier-title { font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:1.15rem; color:var(--le-ink); line-height:1.1; }
.metier-tag { display:inline-block; font-size:.65rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase;
  color: #fff; background: var(--le-red); padding:2px 8px; border-radius:0; }
.metier-desc { font-size:.88rem; color:var(--le-night-400); line-height:1.5; margin:.3rem 0 .6rem; font-family: 'Atkinson Hyperlegible', sans-serif; }
.metier-link { font-family:'Outfit',sans-serif; font-weight:700; font-size:.82rem; color:var(--le-red); text-decoration:none; }
.metier-link:hover { text-decoration: underline; }

/* ══════════ Swipe card (DS-aligned) ══════════ */
.swipe-shell { display:flex; justify-content:center; margin:.4rem 0 .2rem; }
.swipe-card {
  width: 100%; max-width: 400px; background:#fff; border:1px solid var(--le-border);
  border-radius: var(--r-md); box-shadow: var(--shadow-lg); padding: 2rem 1.4rem; text-align:center;
}
.swipe-emoji { font-size: 3.2rem; line-height:1; margin-bottom: .7rem; }
.swipe-title { font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:1.6rem; color:var(--le-ink); margin-bottom:.8rem; }
.swipe-kw { display:flex; flex-wrap:wrap; gap:.35rem; justify-content:center; }
.kw {
  background: var(--le-grey-2); color: var(--le-ink); font-size:.75rem; font-weight:600;
  padding: 4px 10px; border-radius: 0; font-family: 'Outfit', sans-serif; text-transform: uppercase; letter-spacing: .02em;
}

/* ══════════ Tags (DS §1.5 — squared badges) ══════════ */
.ori-tag {
  display:inline-block; background: var(--le-grey-2); border:none;
  color: var(--le-ink); font-size:.68rem; font-weight:700; padding:3px 8px; border-radius:0;
  margin:2px 3px 2px 0; text-transform:uppercase; letter-spacing:.03em;
  font-family: 'Outfit', sans-serif;
}
.ori-tag.red { background: var(--le-red); color:#fff; border:none; }

/* ══════════ Hero (landing) ══════════ */
.hero { text-align:center; padding: 1.5rem 0 .5rem; }
.eyebrow {
  display:inline-block; font-size:.68rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
  color: #fff; background: var(--le-red); padding:5px 12px; border-radius:0; margin-bottom:1rem;
  font-family: 'Outfit', sans-serif;
}
.hero-title { font-size: 3.3rem; font-weight: 800; line-height: 1.02; color: var(--le-ink); margin: 0 0 1rem; }
.hero-title .em { color: var(--le-red); }
@media (max-width: 640px){ .hero-title { font-size: 2.3rem; } }
.hero-sub { font-size: 1.05rem; color: var(--le-muted); max-width: 540px; margin: 0 auto 1.6rem; line-height:1.55; font-family: 'Atkinson Hyperlegible', sans-serif; }

/* feature row */
.feat { background:#fff; border:1px solid var(--le-border); border-radius:var(--r-md); padding:1.1rem 1rem; height:100%; transition: box-shadow .2s ease, transform .2s ease; }
.feat:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.feat-ico { font-size:1.5rem; margin-bottom:.4rem; }
.feat-h { font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:1.12rem; color:var(--le-ink); margin-bottom:.25rem; }
.feat-p { font-size:.85rem; color:var(--le-muted); line-height:1.45; font-family: 'Atkinson Hyperlegible', sans-serif; }

/* trust strip */
.trust { display:flex; gap:1.4rem; justify-content:center; flex-wrap:wrap; color:var(--le-muted); font-size:.78rem; font-weight:600; margin:.4rem 0 1.4rem; font-family: 'Outfit', sans-serif; }
.trust b { color: var(--le-ink); }

/* ══════════ Inputs (DS §1.4 — rounded-sm, focus night-600) ══════════ */
.stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {
  border-radius: var(--r-sm) !important; border:1px solid var(--le-stone-300) !important; background:#fff !important;
  font-family: 'Outfit', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--le-ink) !important; box-shadow: none !important;
}
div[data-testid="stChatInput"] textarea { font-size: .95rem !important; font-family: 'Outfit', sans-serif !important; }
div[data-testid="stChatInput"] { border-radius: var(--r-sm) !important; border-color: var(--le-stone-300) !important; }

/* misc */
hr { border:none; border-top:1px solid var(--le-border); margin:1rem 0; }
a { color: var(--le-red); text-decoration:none; font-weight:700; }
a:hover { text-decoration: underline; }
.ori-foot { text-align:center; color:var(--le-muted); font-size:.75rem; padding:2rem 0 .5rem; font-family: 'Outfit', sans-serif; }
.note { background: #fff; border:1px solid var(--le-border); border-radius:var(--r-md); padding:.7rem .9rem; font-size:.84rem; color:var(--le-muted); font-family: 'Atkinson Hyperlegible', sans-serif; }
.section-h { font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:1.5rem; color:var(--le-ink); margin:.2rem 0 .1rem; border-bottom: 2px solid var(--le-red); width: fit-content; padding-bottom: 2px; }
.section-rule { width:0; height:0; margin:.3rem 0 1rem; }

/* ══════════ Top tabs (navigation) ══════════ */
.tabs-wrap { margin: -.2rem 0 .2rem; }

@media (max-width: 640px) {
  /* Rendre les boutons d'onglets horizontaux scrollables de gauche à droite sur mobile au lieu de les écraser */
  div[data-testid="stHorizontalBlock"]:has(button[data-testid*="baseButton-"]) {
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    gap: 8px !important;
    padding-bottom: 8px !important;
    -ms-overflow-style: none; /* IE et Edge */
    scrollbar-width: none; /* Firefox */
  }
  div[data-testid="stHorizontalBlock"]:has(button[data-testid*="baseButton-"])::-webkit-scrollbar {
    display: none; /* Chrome, Safari, Opera */
  }
  div[data-testid="stHorizontalBlock"]:has(button[data-testid*="baseButton-"]) > div {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 90px !important;
  }
}

/* ══════════ Page header ══════════ */
.page-head { margin:.2rem 0 1.1rem; }
.page-eyebrow { font-size:.68rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color: #fff; background: var(--le-red); padding: 3px 8px; border-radius: 0; display: inline-block; font-family: 'Outfit', sans-serif; }
.greet { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:2.3rem; color:var(--le-ink); line-height:1.04; margin:.4rem 0 .2rem; }
.greet .em { color:var(--le-red); }
.page-sub { color:var(--le-muted); font-size:.95rem; font-family: 'Atkinson Hyperlegible', sans-serif; }

/* ══════════ Generic card (DS §1.6 — rounded-lg) ══════════ */
.card { background:#fff; border:1px solid var(--le-border); border-radius:var(--r-md); padding:1.1rem 1.2rem; box-shadow:var(--shadow-xs); margin:.2rem 0; transition: box-shadow .2s ease; }
.card:hover { box-shadow: var(--shadow-sm); }
.card-h { font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:1.2rem; color:var(--le-ink); margin:0 0 .5rem; display:flex; align-items:center; gap:.45rem; }
.card-hint { font-size:.78rem; color:var(--le-muted); margin:.2rem 0 .6rem; font-family: 'Outfit', sans-serif; }

/* ══════════ Completion ring ══════════ */
.ring-wrap { display:flex; align-items:center; gap:1.1rem; }
.ring-num { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:1.4rem; fill:var(--le-ink); }
.ring-txt b { color:var(--le-ink); }
.ring-txt { font-size:.88rem; color:var(--le-muted); line-height:1.4; font-family: 'Outfit', sans-serif; }

/* ══════════ Milestone stepper (colors from DS) ══════════ */
.stepper { display:flex; margin:.5rem 0 .2rem; }
.step { flex:1; text-align:center; position:relative; padding-top:32px; }
.step::before { content:''; position:absolute; top:11px; left:0; right:0; height:3px; background:var(--le-grey-2); z-index:0; }
.step:first-child::before { left:50%; }
.step:last-child::before { right:50%; }
.step .dot { position:absolute; top:0; left:50%; transform:translateX(-50%); width:24px; height:24px; border-radius:50%; background:#fff; border:3px solid var(--le-grey-2); z-index:1; display:flex; align-items:center; justify-content:center; font-size:.72rem; font-weight:800; color:#fff; }
.step.done .dot { background:var(--le-mint); border-color:var(--le-mint); }
.step.done::before { background:var(--le-mint); }
.step.current .dot { background:var(--le-red); border-color:var(--le-red); box-shadow:0 0 0 4px var(--le-red-soft); }
.step .lbl { font-size:.72rem; font-weight:700; color:var(--le-ink); line-height:1.15; display:block; padding:0 2px; font-family: 'Outfit', sans-serif; }
.step.todo .lbl { color:var(--le-muted); }
.step .ds { font-size:.64rem; color:var(--le-muted); display:block; margin-top:2px; padding:0 2px; }
@media (max-width:640px){ .step .ds { display:none; } .step .lbl { font-size:.64rem; } }

/* ══════════ Event card (DS-aligned) ══════════ */
.ev-card { display:flex; gap:1rem; background:#fff; border:1px solid var(--le-border); border-radius:var(--r-md); padding:1rem 1.1rem; box-shadow:var(--shadow-xs); margin:.5rem 0; transition:box-shadow .2s ease, transform .2s ease, border-color .2s ease; }
.ev-card:hover { box-shadow:var(--shadow-md); transform:translateY(-2px); border-color:var(--le-stone-300); }
.ev-date { flex:0 0 56px; text-align:center; background:var(--le-red-soft); border-radius:var(--r-sm); padding:.5rem .2rem; align-self:flex-start; }
.ev-day { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:1.5rem; color:var(--le-red); line-height:1; }
.ev-mon { font-size:.62rem; font-weight:700; text-transform:uppercase; color:var(--le-red); letter-spacing:.04em; font-family: 'Outfit', sans-serif; }
.ev-body { flex:1; min-width:0; }
.ev-tags { display:flex; gap:.35rem; align-items:center; flex-wrap:wrap; margin-bottom:.1rem; }
.ev-type { display:inline-block; font-size:.6rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase; color:var(--le-muted); background:var(--le-grey-2); padding:2px 7px; border-radius:0; font-family: 'Outfit', sans-serif; }
.ev-badge { display:inline-block; font-size:.6rem; font-weight:700; letter-spacing:.04em; text-transform:uppercase; color:#fff; background:var(--le-red); padding:2px 7px; border-radius:0; font-family: 'Outfit', sans-serif; }
.ev-title { font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:1.15rem; color:var(--le-ink); margin:.25rem 0 .1rem; line-height:1.1; }
.ev-meta { font-size:.78rem; color:var(--le-muted); margin-bottom:.35rem; font-family: 'Outfit', sans-serif; }
.ev-blurb { font-size:.85rem; color:var(--le-night-400); line-height:1.45; margin-bottom:.2rem; font-family: 'Atkinson Hyperlegible', sans-serif; }

/* ══════════ CTA cards ══════════ */
.cta-card { background:#fff; border:1px solid var(--le-border); border-radius:var(--r-md); padding:1rem; height:100%; transition: box-shadow .2s ease, transform .2s ease; }
.cta-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.cta-ico { font-size:1.5rem; }
.cta-h { font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:1.05rem; color:var(--le-ink); margin:.3rem 0 .15rem; }
.cta-p { font-size:.8rem; color:var(--le-muted); line-height:1.4; font-family: 'Atkinson Hyperlegible', sans-serif; }

/* ══════════ Swipe extras ══════════ */
.swipe-progress { text-align:center; color:var(--le-muted); font-size:.78rem; margin:.2rem 0 .5rem; font-family: 'Outfit', sans-serif; }
.swipe-sub { font-size:.88rem; color:var(--le-muted); margin-top:.5rem; line-height:1.5; font-family: 'Atkinson Hyperlegible', sans-serif; }

/* ══════════ Profile insights ══════════ */
.insight { background:#fff; border:1px solid var(--le-border); border-radius:var(--r-md); padding:.7rem .9rem; margin:.4rem 0; }
.insight-h { font-size:.65rem; font-weight:700; text-transform:uppercase; letter-spacing:.05em; color:var(--le-muted); margin-bottom:.35rem; font-family: 'Outfit', sans-serif; }

/* ══════════ Stat pills ══════════ */
.stat { text-align:center; background:#fff; border:1px solid var(--le-border); border-radius:var(--r-md); padding:.7rem .4rem; }
.stat-n { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:1.7rem; color:var(--le-red); line-height:1; }
.stat-l { font-size:.68rem; color:var(--le-muted); font-weight:600; margin-top:.2rem; font-family: 'Outfit', sans-serif; }

/* ══════════ Scrollbar (DS-inspired) ══════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--le-grey); }
::-webkit-scrollbar-thumb { background: var(--le-border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--le-muted); }
</style>
""",
        unsafe_allow_html=True,
    )
