import streamlit as st
from google import generativeai as genai
import pdfplumber
import docx

# --- Load API Key ---
try:
    GOOGLE_API_KEY = st.secrets["google"]["api_key"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except KeyError:
    st.error("""
    ❌ API key not found. Please configure:
    1. Create .streamlit/secrets.toml with:
       [google]
       api_key = "your_api_key_here"
    2. For deployment, add secrets in Streamlit Cloud settings
    """)
    st.stop()
except Exception as e:
    st.error(f"❌ Failed to configure Gemini: {str(e)}")
    st.stop()

# --- Tone Options ---
TONES = {
    "Professional": "formal business language",
    "Friendly": "approachable but professional tone",
    "Enthusiastic": "energetic and passionate wording",
    "Concise": "bullet points with maximum impact"
}

# --- Language Options ---
LANGUAGE_OPTIONS = {
    "English": {"code": "en", "icon": "🇬🇧"},
    "Spanish": {"code": "es", "icon": "🇪🇸"},
    "French": {"code": "fr", "icon": "🇫🇷"},
    "German": {"code": "de", "icon": "🇩🇪"},
    "Portuguese": {"code": "pt", "icon": "🇵🇹"},
    "Chinese": {"code": "zh", "icon": "🇨🇳"},
    "Japanese": {"code": "ja", "icon": "🇯🇵"}
}

# --- Page Setup ---
st.set_page_config(page_title="Job Application Booster", page_icon="💼")

# --- Sidebar Settings ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    temperature = st.slider(
        "🔥 Model Creativity (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values = more creative/random, lower = more deterministic"
    )

    selected_lang = st.selectbox(
        "🌐 Language",
        options=list(LANGUAGE_OPTIONS.keys()),
        format_func=lambda x: f"{LANGUAGE_OPTIONS[x]['icon']} {x}"
    )

    tone = st.radio(
        "🎯 Select Tone",
        options=list(TONES.keys()),
        index=0,
        help="Choose the tone you'd like the content written in"
    )

    st.markdown("---")
    st.header("📄 What to Generate")
    generate_cl = st.checkbox("✉️ Cover Letter", value=True)
    generate_ri = st.checkbox("📝 Resume Improvements", value=True)
    generate_it = st.checkbox("💡 Interview Tips", value=True)
    generate_cv = st.checkbox("🔄 Rewrite My CV to Match This Job", help="Optimized resume based on the job post")

# --- Translation Dictionary ---
TRANSLATIONS = {
    "title": {
        "en": "💼 Job Application Booster",
        "es": "💼 Mejorador de Solicitudes",
        "fr": "💼 Optimisateur de Candidatures"
    },
    "subheader": {
        "en": "Step 2: Design Your Application Assistant Interface",
        "es": "Paso 2: Diseñe su Asistente de Aplicación",
        "fr": "Étape 2 : Concevez votre assistant de candidature"
    },
    "generate_button": {
        "en": "🚀 Boost My Application",
        "es": "🚀 Mejorar Mi Solicitud",
        "fr": "🚀 Booster ma candidature"
    },
    "warning_fill_fields": {
        "en": "⚠️ Please fill out both Resume and Job Description.",
        "es": "⚠️ Por favor complete tanto el currículum como la descripción del trabajo.",
        "fr": "⚠️ Veuillez remplir à la fois le CV et la description de poste."
    },
    "warning_select_option": {
        "en": "⚠️ Please select at least one generation option.",
        "es": "⚠️ Seleccione al menos una opción de generación.",
        "fr": "⚠️ Veuillez sélectionner au moins une option de génération."
    },
    "generating_message": {
        "en": "✨ Gemini is generating...",
        "es": "✨ Gemini está generando...",
        "fr": "✨ Gemini génère..."
    },
    "error_prefix": {
        "en": "⚠️ Generation failed",
        "es": "⚠️ Error en la generación",
        "fr": "⚠️ Échec de la génération"
    },
    "footer_tip": {
        "en": "Built with ❤️ by Okoli Chidozie (GoldenBlaze)",
        "es": "Creado con ❤️ por Okoli Chidozie (GoldenBlaze)",
        "fr": "Conçu avec ❤️ par Okoli Chidozie (GoldenBlaze)"
    }
}

# --- Translator Function ---
def t(key):
    lang_code = LANGUAGE_OPTIONS[selected_lang]["code"]
    return TRANSLATIONS.get(key, {}).get(lang_code, key)

# --- Main UI Content ---
st.title(t("title"))
st.subheader(t("subheader"))

# --- File Upload Section in Main Body ---
st.header("📂 Upload Documents")

col1, col2 = st.columns(2)
with col1:
    uploaded_resume = st.file_uploader(
        "Upload Resume (.pdf or .docx)",
        type=["pdf", "docx"],
        key="resume_uploader",
        help="Upload your resume file"
    )
with col2:
    uploaded_jd = st.file_uploader(
        "Upload Job Description (.pdf or .docx)",
        type=["pdf", "docx"],
        key="jd_uploader",
        help="Upload the job description file"
    )

# --- Text Input Section in Main Body ---
st.header("✍️ Provide Your Information")

# Initialize extracted text variables
extracted_resume = ""
extracted_jd = ""

# Process uploaded resume
if uploaded_resume:
    file_type = uploaded_resume.name.split('.')[-1]
    try:
        if file_type == "pdf":
            with pdfplumber.open(uploaded_resume) as pdf:
                extracted_resume = "\n".join([page.extract_text() or "" for page in pdf.pages])
        elif file_type == "docx":
            doc = docx.Document(uploaded_resume)
            extracted_resume = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error extracting resume text: {e}")

# Process uploaded job description
if uploaded_jd:
    file_type = uploaded_jd.name.split('.')[-1]
    try:
        if file_type == "pdf":
            with pdfplumber.open(uploaded_jd) as pdf:
                extracted_jd = "\n".join([page.extract_text() or "" for page in pdf.pages])
        elif file_type == "docx":
            doc = docx.Document(uploaded_jd)
            extracted_jd = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error extracting job description text: {e}")

# Text areas in main body
resume = st.text_area(
    "📄 Resume Content", 
    height=250, 
    value=extracted_resume,
    help="Your resume content (will auto-fill when you upload a file)"
)

job_desc = st.text_area(
    "📌 Job Description Content", 
    height=250, 
    value=extracted_jd,
    help="The job description content (will auto-fill when you upload a file)"
)

# --- Boost Button ---
st.header("2. Boost!")

if st.button(t("generate_button")):
    if not resume or not job_desc:
        st.warning(t("warning_fill_fields"))
    elif not (generate_cl or generate_ri or generate_it or generate_cv):
        st.warning(t("warning_select_option"))
    else:
        with st.spinner(t("generating_message")):
            items = []
            if generate_cl:
                items.append("### Cover Letter\nWrite a tailored cover letter to 'Hiring Manager'.")
            if generate_ri:
                items.append("### Resume Improvements\nList 3-5 actionable resume improvements.")
            if generate_it:
                items.append("### Interview Tips\nList 3-5 concise interview preparation tips.")
            if generate_cv:
                items.append("""
                ### Rewritten CV
                Generate a FULL rewritten version of my resume that:
                1. Matches the job description keywords
                2. Maintains all original factual information
                3. Uses professional formatting
                4. Prioritizes relevant skills/experience
                """)

            # The changed prompt starts here
            full_prompt = f"""
            You are a professional career coach and an expert in job applications.
            Given the following resume and job description, please generate the requested items in clearly separated sections using headings (###).
            Ensure the outputs are professional, concise, and highly relevant

            Resume:
            {resume}

            Job Description:
            {job_desc}

            Requested Outputs:
            {" ".join(items)}

            Additional Instructions:
            - Language: {LANGUAGE_OPTIONS[selected_lang]['code']}
            - Tone: {TONES[tone]}
            - Temperature: {temperature} (for creative variation)
            - Never invent information
            - Maintain factual accuracy
            - Use professional formatting
            - Highlight transferable skills
            """
            # The changed prompt ends here

            try:
                # Initialize empty containers for each section
                if generate_cl:
                    st.subheader("✉️ Cover Letter")
                    cl_container = st.empty()
                if generate_ri:
                    st.subheader("📝 Resume Improvements")
                    ri_container = st.empty()
                if generate_it:
                    st.subheader("💡 Interview Tips")
                    it_container = st.empty()
                if generate_cv:
                    st.subheader("🔄 Optimized CV")
                    cv_container = st.empty()

                # Process streaming response
                response = model.generate_content(
                    full_prompt,
                    stream=True,
                    generation_config={"temperature": temperature}
                )

                full_response = ""
                current_section = None
                
                for chunk in response:
                    chunk_text = chunk.text
                    full_response += chunk_text
                    
                    # Parse sections in real-time
                    lines = chunk_text.split('\n')
                    for line in lines:
                        if line.startswith("###"):
                            current_section = line.replace("###", "").strip()
                        else:
                            if current_section == "Cover Letter" and generate_cl:
                                cl_container.markdown(line + "▌")
                            elif current_section == "Resume Improvements" and generate_ri:
                                ri_container.markdown(line + "▌")
                            elif current_section == "Interview Tips" and generate_it:
                                it_container.markdown(line + "▌")
                            elif current_section == "Rewritten CV" and generate_cv:
                                cv_container.markdown(line + "▌")

                # Final update to remove the streaming cursor (▌)
                if generate_cl:
                    cl_container.markdown(full_response.split("### Cover Letter")[-1].split("###")[0].strip())
                if generate_ri:
                    ri_container.markdown(full_response.split("### Resume Improvements")[-1].split("###")[0].strip())
                if generate_it:
                    it_container.markdown(full_response.split("### Interview Tips")[-1].split("###")[0].strip())
                if generate_cv:
                    cv_container.markdown(full_response.split("### Rewritten CV")[-1].split("###")[0].strip())

            except Exception as e:
                st.error(f"{t('error_prefix')}: {str(e)}")

# --- Footer ---
st.markdown("---")
st.caption(t("footer_tip"))