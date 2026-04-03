import streamlit as st
import os
import shutil
import tempfile
import re
from extractor import extract_text_from_pdf, extract_images_from_pdf
from ai_processor import AIProcessor
from report_generator import generate_pdf_report

# -----------------------------------------------------------------------------
# ⚪ MINIMALIST LIGHT PROFESSIONAL REDESIGN
# -----------------------------------------------------------------------------
st.set_page_config(page_title="DDR Generator | Professional", layout="wide", initial_sidebar_state="expanded")

# Clean Canvas CSS: High-Contrast "Black on White", Apple-esque Minimalism
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #EF7F6D; /* Palette Top Coral */
        --primary-dark: #D36C59;
        --secondary: #FDC7A5; /* Palette Mid Peach */
        --bg: #FFF8E7; /* Palette Bottom Cream (Softened) */
        --sidebar-bg: #FFFFFF;
        --text: #2D3436; /* Warm Charcoal */
        --text-muted: #636E72;
        --border: #FDC7A5; /* Peach Border */
        --card-bg: #FFFFFF;
    }

    /* 1. Global Baseline */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
        background-color: var(--bg) !important;
        color: var(--text);
    }
    
    header[data-testid="stHeader"] { background-color: transparent !important; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }

    /* 2. Sidebar Refinement (Mint Dashboard Style) */
    [data-testid="stSidebar"] {
        background-color: var(--bg) !important; /* Matches original Page Background */
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h2 {
        color: var(--text) !important; 
        font-weight: 500;
    }
    
    /* Verified Models List Specific High-Contrast Rule */
    .diag-results-box {
        background: #2D3436 !important;
        padding: 15px;
        border-radius: 10px;
        color: #FFFFFF !important;
        margin-top: 10px;
    }
    .diag-results-box * {
        color: #FFFFFF !important;
    }
    /* Style checkboxes/radio to match mint */
    .stCheckbox > label > div[row-gap="0"] > div:first-child {
        background-color: var(--primary) !important;
    }
    
    /* Sidebar Verification Text Visibility */
    [data-testid="stSidebar"] .stAlert, [data-testid="stSidebar"] code, [data-testid="stSidebar"] span {
        color: white !important;
    }
    [data-testid="stSidebar"] .stAlert p {
        color: white !important;
    }

    /* 3. Hero Branding (Clean Serif Look) */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #D35400; /* Darker Coral/Orange */
        margin-bottom: 0px;
        letter-spacing: -0.02em;
    }

    /* 4. Dashboard-Style Upload Pads */
    .stFileUploader {
        background: var(--card-bg) !important;
        border: 2px dashed #D1D5DB !important;
        border-radius: 16px !important;
        padding: 24px !important;
        transition: all 0.3s ease;
    }
    .stFileUploader:hover {
        border-color: var(--primary) !important;
        background: #F9FFF2 !important;
    }

    /* 5. Palette Primary Action Button */
    .stButton > button {
        background-color: var(--primary) !important;
        border-radius: 12px !important;
        border: none !important;
        color: white !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.2s ease;
        box-shadow: 0 4px 15px -3px rgba(239, 127, 109, 0.4);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        background-color: var(--primary-dark) !important;
        box-shadow: 0 6px 20px -5px rgba(239, 127, 109, 0.6);
    }

    /* 5b. UNIVERSAL SIDEBAR WHITE FORCE */
    /* Targets every possible text container in the sidebar buttons, code, and alerts */
    [data-testid="stSidebar"] button[kind="secondary"] *,
    [data-testid="stSidebar"] button[kind="primary"] *,
    [data-testid="stSidebar"] .stButton button *,
    [data-testid="stSidebar"] .stCodeContainer *,
    [data-testid="stSidebar"] pre,
    [data-testid="stSidebar"] code,
    [data-testid="stSidebar"] code * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* 6. Clean Dashboard Cards */
    .obs-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
    }
    /* Specific override for sidebar diagnostic box to be dark/warm */
    .diag-card {
        background: #2D3436 !important;
        border: 1px solid #636E72 !important;
        color: #FFFFFF !important;
    }
    .diag-card h4, .diag-card p, .diag-card div, .diag-card span {
        color: #FFFFFF !important;
    }
    .diag-card .badge {
        color: #15803D !important; /* Keep badge text readable */
    }
    
    .badge {
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }

    /* 7. Step Labels (Palette Accents) */
    .step-label {
        font-size: 0.85rem;
        color: #FFFFFF;
        font-weight: 600;
        background: var(--primary);
        padding: 4px 12px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 12px;
    }
    
    /* 8. Code Block Visibility Force */
    [data-testid="stSidebar"] .stCodeContainer {
        background-color: #0F172A !important; /* Deep Navy */
        border: 1px solid #334155 !important;
        margin-bottom: 10px !important;
    }
    [data-testid="stSidebar"] code {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. CLEAN SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color: #1E293B; margin-bottom:0;'>🧠 AI Diagnostic Console</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size:0.8rem;'>System Configuration</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    api_key_field = st.text_input("🔑 Google AI Key", type="password", placeholder="Enter key...")
    
    with st.expander("🤖 MODEL SOURCE", expanded=True):
        m_sel = st.selectbox("Intelligence Level", ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash", "Custom..."])
        t_m = st.text_input("Manual ID", placeholder="gemini-...") if m_sel == "Custom..." else m_sel
        creativity = st.slider("Temperature", 0.0, 1.0, 0.1)

    st.markdown("---")
    # Use Session State to keep diagnostic results visible between re-renders
    if st.button("🔍 Model Diagnostic", key="sidebar_diag_btn"):
        if api_key_field:
            import google.generativeai as genai
            try:
                genai.configure(api_key=api_key_field)
                st.session_state.diag_models = [m.name.replace("models/", "") for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
                if not st.session_state.diag_models: st.sidebar.warning("⚠️ No compatible models found.")
            except Exception as e: st.sidebar.error(f"Diagnostic Error: {e}")
        else: st.sidebar.warning("Please enter your API Key first.")

    # Persistent Display of Diagnostic Results using a premium "Engine Hub" look
    if "diag_models" in st.session_state and st.session_state.diag_models:
        # Generate Grid Badges for Models (Visual only - Palette Style)
        badges_html = "".join([f'<span style="background:#EF7F6D; color:#FFFFFF; border:1px solid #D36C59; padding:3px 8px; border-radius:4px; font-size:0.7rem; font-weight:700; margin:3px; display:inline-block;">{m}</span>' for m in st.session_state.diag_models])
        
        st.sidebar.markdown(f"""
        <div style="background:#FFF8E7; border:1px solid #FDC7A5; padding:12px; border-radius:10px; margin-top:10px;">
            <div style="display:flex; align-items:center; margin-bottom:8px;">
                <div style="width:8px; height:8px; background:#EF7F6D; border-radius:50%; margin-right:8px; animation: pulse 1.5s infinite;"></div>
                <h4 style="margin:0; font-size:0.8rem; color:#2D3436;">VERIFIED MODELS</h4>
            </div>
            <div style="display:flex; flex-wrap:wrap; margin-bottom:10px;">
                {badges_html}
            </div>
            <p style='font-size:0.65rem; font-weight:700; color:#64748B; border-top:1px solid #F1F5F9; padding-top:8px; margin-bottom:5px;'>📋 CLICK TO COPY INDIVIDUAL ID:</p>
        </div>
        <style>
        @keyframes pulse {{
            0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 127, 109, 0.7); }}
            70% {{ transform: scale(1); box-shadow: 0 0 0 4px rgba(239, 127, 109, 0); }}
            100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 127, 109, 0); }}
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Individual compact copy blocks for every model
        for m in st.session_state.diag_models:
            st.sidebar.code(m, language="text")

# -----------------------------------------------------------------------------
# 2. HERO SECTION (MINIMALIST)
# -----------------------------------------------------------------------------
st.markdown("""
    <div style="text-align: center; padding: 40px 0 20px 0;">
        <h1 class="hero-title">✨AI-Powered DDR Generator</h1>
        <p class="hero-subtitle" style="margin-top:10px;">Transform inspection and thermal data into actionable diagnostic reports</p>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. CLEAN UPLOADERS
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
col_a, col_b = st.columns(2)

with col_a:
    file_insp = st.file_uploader("📄 Structural Inspection Report", type=["pdf"])

with col_b:
    file_therm = st.file_uploader("🌡️ Thermal Imaging Report", type=["pdf"])

st.markdown("<br>", unsafe_allow_html=True)
btn_start = st.button("🚀 Generate Diagnostic Report", type="primary", use_container_width=True)

# -----------------------------------------------------------------------------
# 4. EXECUTION FLOW
# -----------------------------------------------------------------------------
if btn_start:
    if not api_key_field: st.error("Auth Failed: API key required.")
    elif not file_insp or not file_therm: st.warning("Input Missing: Both PDF briefs are required.")
    else:
        tmp_p = tempfile.mkdtemp()
        try:
            path_i = os.path.join(tmp_p, "i.pdf")
            path_t = os.path.join(tmp_p, "t.pdf")
            path_imgs = os.path.join(tmp_p, "imgs"); os.makedirs(path_imgs, exist_ok=True)

            with open(path_i, "wb") as f: f.write(file_insp.getbuffer())
            with open(path_t, "wb") as f: f.write(file_therm.getbuffer())

            with st.status("📋 Synthesis in Progress...", expanded=True) as status:
                st.markdown('<p class="step-label">Phase 1: PDF Extraction...</p>', unsafe_allow_html=True)
                txt_insp = extract_text_from_pdf(path_i)
                txt_therm = extract_text_from_pdf(path_t)
                
                st.markdown('<p class="step-label">Phase 2: Isolating Imagery...</p>', unsafe_allow_html=True)
                map_imgs = extract_images_from_pdf(path_t, path_imgs)
                
                st.markdown('<p class="step-label">Phase 3: AI Observation Merging...</p>', unsafe_allow_html=True)
                processor = AIProcessor(api_key=api_key_field, model=t_m, temperature=creativity, strict_mode=True)
                bonus_ans = processor.analyze_observations(txt_insp, txt_therm)
                
                st.markdown('<p class="step-label">Phase 4: Drafting Final Protocol...</p>', unsafe_allow_html=True)
                final_rpt = processor.generate_final_ddr(txt_insp, txt_therm, bonus_ans)
                status.update(label="✅ Analysis Succeeded", state="complete", expanded=False)

            # Technical Expander
            with st.expander("🛠️ Engineering Synthesis Log", expanded=False):
                st.markdown(bonus_ans)

            st.markdown("---")
            st.markdown("### 📋 Final Technical Output")
            
            # Metadata Brief
            meta_match = re.search(r"\[\[METADATA_START\]\](.*?)\[\[METADATA_END\]\]", final_rpt, re.S)
            if meta_match:
                st.markdown(f"<div style='border:1px solid #E2E8F0; padding:15px; border-radius:8px; margin-bottom:20px; background:#F8FAFB;'><b>Property Context:</b><br>{meta_match.group(1).strip()}</div>", unsafe_allow_html=True)
                clean_report = final_rpt.replace(meta_match.group(0), "")
            else: clean_report = final_rpt

            # Minimalist Card Rendering
            headers = ["1. PROPERTY ISSUE SUMMARY", "2. AREA-WISE OBSERVATIONS", "3. PROBABLE ROOT CAUSE", "4. SEVERITY ASSESSMENT", "5. RECOMMENDED ACTIONS", "6. ADDITIONAL NOTES", "7. MISSING OR UNCLEAR INFORMATION"]
            parts = re.split(f"(?:#+\s+)?({'|'.join([re.escape(s) for s in headers])})", clean_report, flags=re.IGNORECASE)
            
            if len(parts) > 1:
                for i in range(1, len(parts), 2):
                    h_txt, c_txt = parts[i].strip(), parts[i+1].strip().split("---")[0].strip()
                    
                    # Minimal Badges
                    b_ui = ""
                    if "SEVERITY" in h_txt.upper():
                        if "HIGH" in c_txt.upper(): b_ui = '<span class="badge" style="background:#FEE2E2; color:#B91C1C;">Critical</span>'
                        elif "MEDIUM" in h_txt.upper(): b_ui = '<span class="badge" style="background:#FEF3C7; color:#B45309;">Review</span>'
                        else: b_ui = '<span class="badge" style="background:#DCFCE7; color:#15803D;">Stable</span>'

                    # Logic to find and display thermal images in the UI
                    img_html = ""
                    try:
                        pg_match = re.search(r"(?:PAGE|PHOTO|IMAGE)\s*(\d+)", c_txt.upper())
                        if pg_match:
                            pg_num = int(pg_match.group(1))
                            if pg_num in map_imgs:
                                import base64
                                for img_path in map_imgs[pg_num]:
                                    with open(img_path, "rb") as im_f:
                                        enc_img = base64.b64encode(im_f.read()).decode()
                                        img_html += f'<img src="data:image/png;base64,{enc_img}" style="max-width:100%; border-radius:10px; margin-top:12px; border:1px solid #E2E8F0;">'
                    except: pass

                    st.markdown(f"""
<div class="obs-card" style="width:100%;">
<div style="display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid #F1F5F9; padding-bottom:8px;">
<h4 style="margin:0; font-size:1.1rem; color:#1E293B;">{h_txt}</h4>
{b_ui}
</div>
<div style="color:#475569; font-size:0.95rem; line-height:1.7;">
{c_txt.replace("[[AREA_START]]", "<div style='border-top:1px dashed #E2E8F0; padding-top:10px; margin-top:10px;'>").replace("[[AREA_END]]", "</div>").replace("[[NAME]]:", "<b>Zone:</b>").replace("[[FINDING]]:", "<br><b>Finding:</b>").replace("[[DETAILS]]:", "<br><b>Context:</b>").replace("[[IMAGE_REF]]:", "<br><b>Evidence:</b>")}
{img_html}
</div>
</div>
""", unsafe_allow_html=True)
            else: st.markdown(final_rpt)

            st.markdown("### 📥 Final Export")
            path_pdf = os.path.join(tmp_p, "Final_DDR.pdf")
            generate_pdf_report(final_rpt, map_imgs, path_pdf, include_images=True)
            
            col_z1, col_z2 = st.columns(2)
            with col_z1:
                with open(path_pdf, "rb") as f: st.download_button("🏆 DOWNLOAD PDF BRIEF", f, "DDR_Protocol.pdf", "application/pdf", use_container_width=True)
            with col_z2:
                st.download_button("📄 EXPORT MARKDOWN", final_rpt, "Raw_DDR.md", "text/markdown", use_container_width=True)

        except Exception as e: st.error(f"Processing Error: {e}")
        finally: pass
