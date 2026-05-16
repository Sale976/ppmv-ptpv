import streamlit as st
import re
import os
import base64

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Pretraga Pravilnika PPMV / PTPV",
    page_icon="📋",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main header */
    .main-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: #1a3a5c;
        text-align: center;
        line-height: 1.35;
        margin-bottom: 3rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 0.5rem;
    }
    /* Info box */
    .info-box {
        background: #eaf3fb;
        border-left: 4px solid #2196F3;
        border-radius: 6px;
        padding: 0.65rem 1rem;
        font-size: 1rem;
        color: #1a3a5c;
        margin-bottom: 1rem;
    }
    /* Result card */
    .result-card {
        background: #fff;
        /* Fiksna širina je uklonjena kako bi kolone bile responzivne */
        border: 1px solid #d0dbe8;
        border-radius: 8px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.65rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .result-card:hover {
        border-color: #2196F3;
        box-shadow: 0 2px 8px rgba(33,150,243,0.12);
    }
    .result-topic {
        font-size: 1rem;
        font-weight: 600;
        color: #1a3a5c;
    }
    .result-meta {
        font-size: 0.82rem;
        color: #666;
        margin-top: -0.1rem;
    }
    .badge-ppmv {
        display: inline-block;
        background: #1565C0;
        color: #fff;
        border-radius: 4px;
        padding: 1px 7px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-ptpv {
        display: inline-block;
        background: #2e7d32;
        color: #fff;
        border-radius: 4px;
        padding: 1px 7px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .highlight {
        background: #fff176;
        border-radius: 3px;
        padding: 0 2px;
    }
    .no-results {
        text-align: center;
        color: #888;
        padding: 2rem 0;
        font-size: 1rem;
    }
    .result-count {
        font-size: 0.85rem;
        color: #555;
        margin-bottom: 0.75rem;
        font-style: italic;
    }

    /* Hide Streamlit default branding */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Load & parse pravilnik.txt ────────────────────────────────────────────────
PRAVILNIK_PATH = os.path.join(os.path.dirname(__file__), "pravilnik.txt")

@st.cache_data
def load_entries(path):
    entries = []
    pattern = re.compile(
        r"^(?P<topic>.+?)\s+--\s+(?:član|tačka)\s+(?P<article>[^\(]+)\((?P<law>PPMV|PTPV)\)\s+str\.\s+(?P<page>\d+)",
        re.IGNORECASE
    )
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("---"):
                    continue
                m = pattern.search(line)
                if m:
                    entries.append({
                        "topic": m.group("topic").strip(),
                        "article": m.group("article").strip(),
                        "law": m.group("law").upper(),
                        "page": int(m.group("page")),
                        "raw": line,
                    })
    except FileNotFoundError:
        st.error(f"Fajl 'pravilnik.txt' nije pronađen na putanji: {path}")
    return entries

entries = load_entries(PRAVILNIK_PATH)

# ── PDF helpers ───────────────────────────────────────────────────────────────
PDF_FILES = {
    "PPMV": os.path.join(os.path.dirname(__file__), "ppmv.pdf"),
    "PTPV": os.path.join(os.path.dirname(__file__), "ptpv.pdf"),
}

@st.cache_data
def get_pdf_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# ── Highlight helper ──────────────────────────────────────────────────────────
def highlight(text, query):
    if not query:
        return text
    escaped = re.escape(query)
    return re.sub(f"({escaped})", r'<span class="highlight">\1</span>', text, flags=re.IGNORECASE)

# ── Session state inicijalizacija ─────────────────────────────────────────────
if "about_open" not in st.session_state:
    st.session_state.about_open = False
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "active_pdf_idx" not in st.session_state:
    st.session_state.active_pdf_idx = None
if "last_search_state" not in st.session_state:
    st.session_state.last_search_state = ("", "Svi")

# ── Header ────────────────────────────────────────────────────────────────────
hcol_title, hcol_about = st.columns([9, 1])
with hcol_title:
    st.markdown(
        '<div class="main-title">📋 Web aplikacija za pretragu Pravilnika o Podeli Motornih Vozila (PPMV)'
        ' i Pravilnika o Tehničkom Pregledu Vozila (PTPV)</div>',
        unsafe_allow_html=True
    )
    
    st.markdown(
        '<div class="subtitle">🛈 Pravilnik o Podeli Motornih i Priključnih Vozila, br. 53 од 20. јуна 2025.   |   Pravilnik o Tehničkom Pregledu Vozila, br. 62 od 26. маја 2022.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Pretražite članove i tačke pravilnika po ključnim rečima</div>',
        unsafe_allow_html=True
    )
with hcol_about:
    st.markdown("<div style='padding-top:0.4rem; text-align:right;'>", unsafe_allow_html=True)
    if st.button("ℹ️ O aplikaciji", use_container_width=True):
        st.session_state.about_open = not st.session_state.about_open
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── Tip box ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="info-box">'
    '🛈 <strong>Primer načina pretrage:</strong> Unosom reči npr. <span style="font-style: italic; color: #FF4500;">"svetlo"</span> aplikacija vraća više mogućih '
    'rezultata, međutim ako se unese <span style="font-style: italic; color: #FF4500;">"kratko svetlo"</span> dobija se jedan rezultat.'
    '</div>',
    unsafe_allow_html=True
)

# ── Search row ────────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1])

with col_input:
    query = st.text_input(
        label="Pretraga",
        placeholder="Unesite ključnu reč (npr. kočnice, tahograf, svetlo...)",
        label_visibility="collapsed",
        key=f"search_input_{st.session_state.input_key}",
    )

with col_btn:
    if st.button("\U0001f5d1\ufe0f Obriši", use_container_width=True):
        st.session_state.input_key += 1
        st.session_state.active_pdf_idx = None  # Resetuje otvoren PDF
        st.rerun()

# ── Filter radio ──────────────────────────────────────────────────────────────
filter_law = st.radio(
    "Filtriraj po pravilniku:",
    options=["Svi", "PPMV", "PTPV"],
    horizontal=True,
    index=0,
)

st.divider()

# ── Search logic ──────────────────────────────────────────────────────────────
query = query.strip()

# Ako korisnik promeni tekst pretrage ili filter, automatski zatvori otvoren PDF
if st.session_state.last_search_state != (query, filter_law):
    st.session_state.active_pdf_idx = None
    st.session_state.last_search_state = (query, filter_law)

if query:
    results = [
        e for e in entries
        if query.lower() in e["topic"].lower()
        and (filter_law == "Svi" or e["law"] == filter_law)
    ]

    count = len(results)
    if count == 0:
        st.markdown(
            f'<div class="no-results">🔍 Nema rezultata za „<strong>{query}</strong>".<br>'
            'Pokušajte sa drugom ključnom rečju.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="result-count">Pronađeno rezultata: <strong>{count}</strong> za upit „{query}"</div>',
            unsafe_allow_html=True
        )

        for idx, entry in enumerate(results):
            badge_cls = "badge-ppmv" if entry["law"] == "PPMV" else "badge-ptpv"
            topic_hl = highlight(entry["topic"], query)

            # Koristimo standardne Streamlit kolone (5 i 1.5 proporcija)
            col_card, col_pdf_link = st.columns([5, 1.5])
            
            with col_card:
                st.markdown(
                    f'<div class="result-card">'
                    f'<div class="result-topic">{topic_hl}</div>'
                    f'<div class="result-meta">'
                    f'<span class="{badge_cls}">{entry["law"]}</span>'
                    f'Član <strong>{entry["article"]}</strong>. &nbsp;|&nbsp; '
                    f'Strana: <strong>{entry["page"]}</strong>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )

            with col_pdf_link:
                # Prazan prostor da se dugme vertikalno centrira u odnosu na karticu
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                
                # Menjamo tekst dugmeta u zavisnosti od toga da li je PDF već otvoren
                is_active = (st.session_state.active_pdf_idx == idx)
                btn_label = "Zatvori PDF" if is_active else f"📄 Otvori str. {entry['page']}"
                
                if st.button(btn_label, use_container_width=True, key=f"btn_{idx}"):
                    if is_active:
                        st.session_state.active_pdf_idx = None # Zatvori ako je kliknuto ponovo
                    else:
                        st.session_state.active_pdf_idx = idx  # Postavi aktivni dokument
                    st.rerun()

            # Ako je dugme za ovaj specifični rezultat kliknuto, prikazujemo PDF ispod reda
            if st.session_state.active_pdf_idx == idx:
                pdf_path = PDF_FILES.get(entry["law"])
                b64_data = get_pdf_b64(pdf_path)
                
                if b64_data:
                    # Iframe se koristi jer pregledači NE blokiraju data URIs kada su ugrađeni unutar stranice
                    data_uri = f"data:application/pdf;base64,{b64_data}#page={entry['page']}"
                    st.markdown(
                        f"""
                        <div style="margin-bottom: 25px;">
                            <iframe src="{data_uri}" width="100%" height="750px" 
                            style="border: 2px solid #2196F3; border-radius: 8px;">
                            </iframe>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.error("⚠️ PDF fajl nedostaje na disku/serveru.")

else:
    st.markdown(
        '<div class="no-results">👆 Unesite ključnu reč u polje za pretragu da biste pronašli članove pravilnika.</div>',
        unsafe_allow_html=True
    )

# ── About dialog ─────────────────────────────────────────────────────────────
if st.session_state.about_open:
    st.markdown(
        """
        <div class="about-card" style="border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: #fff; margin-bottom: 20px;">
            <h2>📋 O aplikaciji</h2>
            <span class="about-version">Verzija 1.0</span>
            <hr class="about-divider">
            <div class="about-row">
                <span class="about-icon">📌</span>
                <span class="about-label">Namena:</span>
                <span class="about-value">Pretraga Pravilnika o Podeli Motornih Vozila (PPMV) i Pravilnika o Tehničkom Pregledu Vozila (PTPV)</span>
            </div>
            <div class="about-row">
                <span class="about-icon">👨‍💻</span>
                <span class="about-label">Autori:</span>
                <span class="about-value">Aleksandar &amp; Claude (Anthropic AI)</span>
            </div>
            <div class="about-row about-email">
                <span class="about-icon">✉️</span>
                <span class="about-label">Kontakt:</span>
                <span class="about-value"><a href="mailto:aca1976@mts.rs">aca1976@mts.rs</a></span>
            </div>
            <div class="about-row">
                <span class="about-icon">📄</span>
                <span class="about-label">Podaci:</span>
                <span class="about-value">pravilnik.txt, ppmv.pdf, ptpv.pdf</span>
            </div>
            <p class="about-footer-note" style="margin-top:10px; font-size:0.8rem; color:#888;">© 2025 Aleksandar · Sva prava zadržana</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("✖️ Zatvori O aplikaciji"):
        st.session_state.about_open = False
        st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size:0.78rem; color:#aaa;'>"
    "📋 Pretraga Pravilnika PPMV / PTPV &nbsp;·&nbsp; Verzija 1.0 &nbsp;·&nbsp; "
    "<a href='mailto:aca1976@mts.rs' style='color:#aaa;'>aca1976@mts.rs</a>"
    "</div>",
    unsafe_allow_html=True
)