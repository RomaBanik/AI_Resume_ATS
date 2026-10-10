import streamlit as st
import fitz
import os
import re
import time
import hashlib
from dotenv import load_dotenv
from google import genai


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ResumeAI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# GEMINI SETUP
# =========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY was not found. Please check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f5f7fb;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 30px;
        padding-bottom: 50px;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #111827 !important;
    }

    p {
        color: #374151;
    }

    /* SIDEBAR */

    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: white !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: #374151;
    }

    section[data-testid="stSidebar"] textarea {
        background-color: #0d1117 !important;
        color: white !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
    }

    section[data-testid="stSidebar"] textarea::placeholder {
        color: #9ca3af !important;
    }

    section[data-testid="stSidebar"] section[data-testid="stFileUploaderDropzone"] {
        background-color: #0d1117;
        border: 1px solid #374151;
        border-radius: 12px;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        min-height: 45px;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e1e5eb;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.03);
    }

    .stProgress > div > div > div > div {
        border-radius: 10px;
    }

    details {
        border-radius: 12px !important;
    }

    hr {
        border-color: #e5e7eb;
    }

    .skill-badge {
        display: inline-block;
        padding: 7px 12px;
        margin: 4px 4px 4px 0;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        background: #eef5ff;
        border: 1px solid #c9ddf5;
        color: #1f4f85;
    }

    .takeaway-card {
        background: #cfe3fa;
        border: 1px solid #b8d2ee;
        border-radius: 15px;
        padding: 20px;
        margin-top: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# PDF EXTRACTION
# =========================================================

def extract_text_from_pdf(pdf_file):

    document = fitz.open(
        stream=pdf_file.read(),
        filetype="pdf"
    )

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(text):

    text = text.lower()
    text = " ".join(text.split())

    return text


# =========================================================
# SKILLS DATABASE
# =========================================================

skills = [
    "python",
    "java",
    "javascript",
    "sql",
    "html",
    "css",
    "bootstrap",
    "react",
    "angular",
    "node.js",
    "node",
    "express.js",
    "express",
    "git",
    "github",
    "django",
    "flask",
    "rest api",
    "rest",
    "mongodb",
    "mysql",
    "postgresql",
    "c",
    "c++",
    "data structures",
    "machine learning",
    "artificial intelligence",
    "streamlit",
    "pandas",
    "numpy",
    "power bi",
    "excel"
]


# =========================================================
# FIND SKILLS
# =========================================================

def find_matching_skills(text):

    matched_skills = []

    for skill in skills:

        pattern = (
            r"(?<![a-zA-Z0-9])"
            + re.escape(skill)
            + r"(?![a-zA-Z0-9])"
        )

        if re.search(pattern, text):
            matched_skills.append(skill)

    return matched_skills


# =========================================================
# COMPARE SKILLS
# =========================================================

def compare_skills(jd_skills, resume_text):

    matched = []
    missing = []

    for skill in jd_skills:

        pattern = (
            r"(?<![a-zA-Z0-9])"
            + re.escape(skill)
            + r"(?![a-zA-Z0-9])"
        )

        if re.search(pattern, resume_text):
            matched.append(skill)
        else:
            missing.append(skill)

    return matched, missing


# =========================================================
# KEYWORD EXTRACTION
# =========================================================

def extract_keywords(text):

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b",
        text.lower()
    )

    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "this",
        "that",
        "are",
        "you",
        "your",
        "from",
        "will",
        "have",
        "has",
        "our",
        "they",
        "their",
        "into",
        "about",
        "using",
        "should",
        "would",
        "could",
        "can",
        "job",
        "role",
        "work",
        "working"
    }

    keywords = []

    for word in words:

        if word not in stop_words and word not in keywords:
            keywords.append(word)

    return keywords


# =========================================================
# KEYWORD SCORE
# =========================================================

def calculate_keyword_score(resume_text, job_description):

    jd_keywords = extract_keywords(job_description)

    if not jd_keywords:
        return 0

    matched = 0

    for keyword in jd_keywords:

        if keyword in resume_text:
            matched += 1

    return round(
        (matched / len(jd_keywords)) * 100,
        2
    )


# =========================================================
# SKILL SCORE
# =========================================================

def calculate_skill_score(matched_skills, jd_skills):

    if not jd_skills:
        return 0

    return round(
        (len(matched_skills) / len(jd_skills)) * 100,
        2
    )


# =========================================================
# JOB RELEVANCE
# =========================================================

def calculate_job_relevance(resume_text, job_description):

    important_terms = [
        "developer",
        "software",
        "programming",
        "web",
        "database",
        "api",
        "application",
        "development",
        "project",
        "intern",
        "engineering",
        "technology"
    ]

    jd_terms = []

    for term in important_terms:

        if term in job_description:
            jd_terms.append(term)

    if not jd_terms:
        return 0

    matched = 0

    for term in jd_terms:

        if term in resume_text:
            matched += 1

    return round(
        (matched / len(jd_terms)) * 100,
        2
    )


# =========================================================
# RESUME COMPLETENESS
# =========================================================

def calculate_completeness(resume_text):

    sections = [
        "education",
        "experience",
        "skills",
        "project",
        "projects",
        "certification",
        "certificate",
        "contact",
        "objective",
        "summary"
    ]

    found = 0

    for section in sections:

        if section in resume_text:
            found += 1

    return round(
        (found / len(sections)) * 100,
        2
    )


# =========================================================
# EXPERIENCE / EDUCATION ALIGNMENT
# =========================================================

def calculate_alignment(resume_text, job_description):

    alignment_terms = [
        "bachelor",
        "degree",
        "bca",
        "btech",
        "computer",
        "experience",
        "internship",
        "intern",
        "graduate",
        "student"
    ]

    jd_terms = []

    for term in alignment_terms:

        if term in job_description:
            jd_terms.append(term)

    if not jd_terms:
        return 70

    matched = 0

    for term in jd_terms:

        if term in resume_text:
            matched += 1

    return round(
        (matched / len(jd_terms)) * 100,
        2
    )


# =========================================================
# ATS SCORE
# =========================================================

def calculate_ats_score(
    keyword_score,
    skill_score,
    relevance_score,
    completeness_score,
    alignment_score
):

    score = (
        keyword_score * 0.30
        + skill_score * 0.30
        + relevance_score * 0.20
        + completeness_score * 0.10
        + alignment_score * 0.10
    )

    return round(score, 2)


# =========================================================
# BASIC SUGGESTIONS
# =========================================================

def generate_basic_suggestions(
    missing_skills,
    completeness_score,
    keyword_score
):

    suggestions = []

    if missing_skills:

        suggestions.append(
            "Add relevant missing skills only if you genuinely have experience with them."
        )

    if completeness_score < 70:

        suggestions.append(
            "Improve the structure with clear Skills, Projects, Education and Experience sections."
        )

    if keyword_score < 60:

        suggestions.append(
            "Use relevant job-description keywords where they accurately match your experience."
        )

    suggestions.append(
        "Keep section headings standard and bullet points concise."
    )

    suggestions.append(
        "Quantify project achievements with measurable results when possible."
    )

    return suggestions[:3]


# =========================================================
# GEMINI ANALYSIS
# =========================================================

def generate_gemini_analysis(
    resume_text,
    job_description
):

    prompt = f"""
You are an expert ATS resume analyzer.

Analyze the resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

The user wants a VERY SHORT and EASY-TO-SCAN result.

Do NOT write long paragraphs.
Do NOT repeat the same information.
Do NOT give an exact ATS score.

Return ONLY these sections:

SUMMARY:
One sentence maximum.

STRENGTHS:
Exactly 3 short bullet points.
Maximum 8 words per bullet.

SKILL_GAPS:
Maximum 3 short items.
Use skill names or short phrases.

TOP_IMPROVEMENTS:
Exactly 3 short actionable points.
Maximum 12 words per point.

FINAL_TAKEAWAY:
One short sentence.
Maximum 20 words.

IMPORTANT RULES:

- Never invent skills.
- Never invent experience.
- Never invent projects.
- Never invent education.
- Never invent certifications.
- Never invent achievements.
- Only use facts from the resume.
- If a skill is missing, identify it.
- Do NOT tell the user to falsely add a skill.
- For missing skills, say they should be added ONLY if the user genuinely has that skill.
- Do not tell the user to learn a skill unless explicitly asked.
- Keep every answer concise.
- No long explanations.
"""

    # Create a unique key for this exact resume + JD
    analysis_key = hashlib.sha256(
        (
            resume_text.strip()
            + "||JOB||"
            + job_description.strip()
        ).encode("utf-8")
    ).hexdigest()

    # Create cache
    if "gemini_cache" not in st.session_state:
        st.session_state.gemini_cache = {}

    # If same resume + same JD was already analyzed,
    # do NOT call Gemini again.
    if analysis_key in st.session_state.gemini_cache:

        return st.session_state.gemini_cache[analysis_key]

    # Models to try
    models_to_try = [
    "gemini-3.5-flash-lite"
]

    last_error = None

    for model_name in models_to_try:

        for attempt in range(2):

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response and response.text:

                    result = response.text

                    # Save result in session cache
                    st.session_state.gemini_cache[
                        analysis_key
                    ] = result

                    return result

                last_error = Exception(
                    "Gemini returned an empty response."
                )

            except Exception as error:

                last_error = error

                error_text = str(error).lower()

                temporary_error = (
                    "429" in error_text
                    or "resource_exhausted" in error_text
                    or "503" in error_text
                    or "service_unavailable" in error_text
                    or "500" in error_text
                    or "504" in error_text
                )

                # Retry only temporary errors
                if temporary_error and attempt == 0:

                    time.sleep(2)

                    continue

                # Move to fallback model
                break

    # If both models fail, show actual error
    raise Exception(
        f"Gemini API request failed.\n\n"
        f"Actual error:\n{str(last_error)}"
    )


# =========================================================
# PARSE GEMINI RESPONSE
# =========================================================

def parse_gemini_response(text):

    sections = {
        "SUMMARY": [],
        "STRENGTHS": [],
        "SKILL_GAPS": [],
        "TOP_IMPROVEMENTS": [],
        "FINAL_TAKEAWAY": []
    }

    current_section = None

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        clean_line = re.sub(
            r"^[#*\-\d.)\s]+",
            "",
            line
        ).strip()

        upper_line = clean_line.upper()

        if upper_line.startswith("SUMMARY"):

            current_section = "SUMMARY"
            continue

        if upper_line.startswith("STRENGTHS"):

            current_section = "STRENGTHS"
            continue

        if upper_line.startswith("SKILL_GAPS"):

            current_section = "SKILL_GAPS"
            continue

        if upper_line.startswith("TOP_IMPROVEMENTS"):

            current_section = "TOP_IMPROVEMENTS"
            continue

        if upper_line.startswith("FINAL_TAKEAWAY"):

            current_section = "FINAL_TAKEAWAY"
            continue

        if current_section:

            clean_line = re.sub(
                r"^[•\-*]+\s*",
                "",
                clean_line
            ).strip()

            if clean_line:

                sections[current_section].append(
                    clean_line
                )

    sections["SUMMARY"] = sections["SUMMARY"][:1]
    sections["STRENGTHS"] = sections["STRENGTHS"][:3]
    sections["SKILL_GAPS"] = sections["SKILL_GAPS"][:3]
    sections["TOP_IMPROVEMENTS"] = sections["TOP_IMPROVEMENTS"][:3]
    sections["FINAL_TAKEAWAY"] = sections["FINAL_TAKEAWAY"][:1]

    return sections


# =========================================================
# GEMINI DISPLAY
# =========================================================

def display_gemini_analysis(analysis):

    st.divider()

    st.header(
        "🤖 Gemini Quick Insights"
    )

    st.caption(
        "Short AI insights based on your resume and job description."
    )

    sections = parse_gemini_response(
        analysis
    )

    # QUICK SUMMARY

    if sections["SUMMARY"]:

        with st.container(border=True):

            st.subheader(
                "📌 Quick Summary"
            )

            st.write(
                sections["SUMMARY"][0]
            )

    # STRENGTHS + GAPS

    strength_col, gap_col = st.columns(
        2,
        gap="medium"
    )

    with strength_col:

        with st.container(border=True):

            st.subheader(
                "💪 Top Strengths"
            )

            if sections["STRENGTHS"]:

                for item in sections["STRENGTHS"]:

                    st.success(
                        "✓ " + item
                    )

            else:

                st.info(
                    "No specific strengths identified."
                )

    with gap_col:

        with st.container(border=True):

            st.subheader(
                "⚠️ Main Skill Gaps"
            )

            if sections["SKILL_GAPS"]:

                for item in sections["SKILL_GAPS"]:

                    st.warning(
                        "• " + item
                    )

            else:

                st.success(
                    "No major skill gaps identified."
                )

    # IMPROVEMENTS

    with st.container(border=True):

        st.subheader(
            "🚀 Top 3 Improvements"
        )

        if sections["TOP_IMPROVEMENTS"]:

            for index, item in enumerate(
                sections["TOP_IMPROVEMENTS"],
                start=1
            ):

                st.write(
                    f"**{index}.** {item}"
                )

        else:

            st.info(
                "No specific improvements identified."
            )

    # FINAL TAKEAWAY

    if sections["FINAL_TAKEAWAY"]:

        takeaway = f"""
        <div class="takeaway-card">

        <div style="
        font-size:17px;
        font-weight:750;
        color:#111827;
        margin-bottom:7px;
        ">
        🎯 Final Takeaway
        </div>

        <div style="
        font-size:15px;
        color:#374151;
        line-height:1.5;
        ">
        {sections["FINAL_TAKEAWAY"][0]}
        </div>

        </div>
        """

        st.markdown(
            takeaway,
            unsafe_allow_html=True
        )

    # FULL RESPONSE

    with st.expander(
        "🔎 View Full Gemini Response"
    ):

        st.write(
            analysis
        )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title(
        "📄 ResumeAI"
    )

    st.write(
        "ATS Resume Builder & Analyzer"
    )

    st.divider()

    st.subheader(
        "📤 Upload Resume"
    )

    resume = st.file_uploader(
        "Upload your resume",
        type=["pdf"]
    )

    st.divider()

    st.subheader(
        "📝 Job Description"
    )

    job_description = st.text_area(
        "Paste the job description",
        height=270,
        placeholder="Paste the complete job description here..."
    )

    st.divider()

    analyze_button = st.button(
        "🚀 Analyze Resume",
        use_container_width=True
    )


# =========================================================
# HERO SECTION
# =========================================================

hero = """
<div style="
background:#ffffff;
border:1px solid #dfe5ed;
border-radius:20px;
padding:38px 42px;
margin-bottom:28px;
box-shadow:0 4px 18px rgba(0,0,0,0.04);
">

<div style="
font-size:14px;
font-weight:700;
color:#4f8fd8;
letter-spacing:1px;
margin-bottom:12px;
">
✨ AI-POWERED RESUME ANALYSIS
</div>

<div style="
font-size:38px;
font-weight:800;
color:#111827;
line-height:1.2;
margin-bottom:14px;
">
Build a Resume That Matches the Job 🎯
</div>

<div style="
font-size:17px;
color:#4b5563;
line-height:1.7;
max-width:900px;
">
Upload your resume and provide a job description.
ResumeAI analyzes your resume, identifies matching skills,
calculates an ATS-style score and provides AI-powered
improvement suggestions.
</div>

</div>
"""

st.markdown(
    hero,
    unsafe_allow_html=True
)


# =========================================================
# FEATURE SECTION
# =========================================================

st.header(
    "✨ What ResumeAI Does"
)

feature1, feature2, feature3 = st.columns(
    3,
    gap="medium"
)


with feature1:

    st.markdown(
        """
        <div style="
        background:#cfe3fa;
        border:1px solid #b8d2ee;
        border-radius:15px;
        padding:24px;
        min-height:205px;
        box-shadow:0 3px 10px rgba(0,0,0,0.03);
        ">

        <div style="font-size:30px;">
        🎯
        </div>

        <div style="
        font-size:22px;
        font-weight:750;
        color:#111827;
        margin-bottom:12px;
        ">
        ATS-Style Scoring
        </div>

        <div style="
        font-size:16px;
        color:#374151;
        line-height:1.6;
        ">
        Get a transparent score based on keywords,
        skills, job relevance, completeness and alignment.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with feature2:

    st.markdown(
        """
        <div style="
        background:#cfe3fa;
        border:1px solid #b8d2ee;
        border-radius:15px;
        padding:24px;
        min-height:205px;
        box-shadow:0 3px 10px rgba(0,0,0,0.03);
        ">

        <div style="font-size:30px;">
        🔍
        </div>

        <div style="
        font-size:22px;
        font-weight:750;
        color:#111827;
        margin-bottom:12px;
        ">
        Job Matching
        </div>

        <div style="
        font-size:16px;
        color:#374151;
        line-height:1.6;
        ">
        Compare your resume with the job description
        and identify matched and missing skills.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with feature3:

    st.markdown(
        """
        <div style="
        background:#cfe3fa;
        border:1px solid #b8d2ee;
        border-radius:15px;
        padding:24px;
        min-height:205px;
        box-shadow:0 3px 10px rgba(0,0,0,0.03);
        ">

        <div style="font-size:30px;">
        🤖
        </div>

        <div style="
        font-size:22px;
        font-weight:750;
        color:#111827;
        margin-bottom:12px;
        ">
        Gemini AI Insights
        </div>

        <div style="
        font-size:16px;
        color:#374151;
        line-height:1.6;
        ">
        Get personalized AI-powered suggestions
        for improving your resume.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HOW IT WORKS
# =========================================================

st.header(
    "⚡ How ResumeAI Works"
)

step1, step2, step3, step4 = st.columns(
    4,
    gap="medium"
)


steps = [
    ("1️⃣", "Upload", "Upload your resume PDF."),
    ("2️⃣", "Add Job", "Paste the job description."),
    ("3️⃣", "Analyze", "Compare your resume with the job."),
    ("4️⃣", "Improve", "Get AI-powered suggestions.")
]


for column, step in zip(
    [step1, step2, step3, step4],
    steps
):

    with column:

        st.markdown(
            f"""
            <div style="
            background:#cfe3fa;
            border:1px solid #b8d2ee;
            border-radius:15px;
            padding:22px;
            min-height:145px;
            box-shadow:0 3px 10px rgba(0,0,0,0.03);
            ">

            <div style="font-size:25px;">
            {step[0]}
            </div>

            <div style="
            font-size:20px;
            font-weight:750;
            color:#111827;
            margin:8px 0;
            ">
            {step[1]}
            </div>

            <div style="
            font-size:15px;
            color:#374151;
            line-height:1.5;
            ">
            {step[2]}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# ANALYSIS
# =========================================================

if analyze_button:

    # VALIDATION

    if resume is None:

        st.warning(
            "⚠️ Please upload your resume first."
        )

        st.stop()

    if not job_description.strip():

        st.warning(
            "⚠️ Please enter the Job Description."
        )

        st.stop()

    # PDF EXTRACTION

    with st.spinner(
        "📄 Reading your resume..."
    ):

        resume_text = extract_text_from_pdf(
            resume
        )

    if not resume_text.strip():

        st.error(
            "❌ No readable text was found in this PDF. "
            "Please upload a text-based PDF."
        )

        st.stop()

    # NORMALIZE

    normalized_resume = normalize_text(
        resume_text
    )

    normalized_jd = normalize_text(
        job_description
    )

    # SKILLS

    jd_skills = find_matching_skills(
        normalized_jd
    )

    matched_skills, missing_skills = compare_skills(
        jd_skills,
        normalized_resume
    )

    # SCORES

    keyword_score = calculate_keyword_score(
        normalized_resume,
        normalized_jd
    )

    skill_score = calculate_skill_score(
        matched_skills,
        jd_skills
    )

    relevance_score = calculate_job_relevance(
        normalized_resume,
        normalized_jd
    )

    completeness_score = calculate_completeness(
        normalized_resume
    )

    alignment_score = calculate_alignment(
        normalized_resume,
        normalized_jd
    )

    ats_score = calculate_ats_score(
        keyword_score,
        skill_score,
        relevance_score,
        completeness_score,
        alignment_score
    )

    # =====================================================
    # ATS DASHBOARD
    # =====================================================

    st.divider()

    st.header(
        "📊 ATS Analysis Dashboard"
    )

    st.caption(
        "This is an ATS-style score based on our defined methodology. "
        "It is not an exact score used by a specific company's ATS."
    )

    # SCORE

    score_left, score_right = st.columns(
        [1, 2],
        gap="medium"
    )

    with score_left:

        with st.container(border=True):

            st.metric(
                "ATS-Style Score",
                f"{ats_score} / 100"
            )

            st.progress(
                min(
                    ats_score / 100,
                    1.0
                )
            )

    with score_right:

        with st.container(border=True):

            st.subheader(
                "📌 Score Overview"
            )

            if ats_score >= 75:

                st.success(
                    "Strong alignment with this job description."
                )

            elif ats_score >= 50:

                st.warning(
                    "Moderate alignment. A few areas can be improved."
                )

            else:

                st.error(
                    "Several areas need improvement for this role."
                )

    # MATCH OVERVIEW

    st.header(
        "🎯 Match Overview"
    )

    overview1, overview2, overview3, overview4 = st.columns(
        4,
        gap="medium"
    )

    with overview1:

        st.metric(
            "Keyword Match",
            f"{keyword_score}%"
        )

    with overview2:

        st.metric(
            "Skills Match",
            f"{skill_score}%"
        )

    with overview3:

        st.metric(
            "Job Relevance",
            f"{relevance_score}%"
        )

    with overview4:

        st.metric(
            "Completeness",
            f"{completeness_score}%"
        )

    # =====================================================
    # SKILLS ANALYSIS
    # =====================================================

    st.header(
        "🧠 Skills Analysis"
    )

    matched_col, missing_col = st.columns(
        2,
        gap="medium"
    )

    with matched_col:

        with st.container(border=True):

            st.subheader(
                "✅ Matched Skills"
            )

            if matched_skills:

                st.caption(
                    f"{len(matched_skills)} matching skills detected"
                )

                badges = ""

                for skill in matched_skills:

                    badges += (
                        f'<span class="skill-badge">'
                        f'{skill}'
                        f'</span>'
                    )

                st.markdown(
                    badges,
                    unsafe_allow_html=True
                )

            else:

                st.info(
                    "No matching skills detected."
                )

    with missing_col:

        with st.container(border=True):

            st.subheader(
                "⚠️ Missing Skills"
            )

            if missing_skills:

                st.caption(
                    f"{len(missing_skills)} skills not detected"
                )

                badges = ""

                for skill in missing_skills:

                    badges += (
                        f'<span class="skill-badge">'
                        f'{skill}'
                        f'</span>'
                    )

                st.markdown(
                    badges,
                    unsafe_allow_html=True
                )

                st.caption(
                    "Add these only if you genuinely have the skill."
                )

            else:

                st.success(
                    "No missing skills detected."
                )

    # =====================================================
    # TOP IMPROVEMENTS
    # =====================================================

    st.header(
        "💡 Top 3 Resume Improvements"
    )

    suggestions = generate_basic_suggestions(
        missing_skills,
        completeness_score,
        keyword_score
    )

    for index, suggestion in enumerate(
        suggestions,
        start=1
    ):

        st.info(
            f"**{index}.** {suggestion}"
        )

    # =====================================================
    # GEMINI
    # =====================================================

    with st.spinner(
        "🤖 Gemini is analyzing your resume..."
    ):

        try:

            gemini_analysis = generate_gemini_analysis(
                resume_text,
                job_description
            )

            display_gemini_analysis(
                gemini_analysis
            )

        except Exception as error:

            error_message = str(error)

            st.warning(
                "⚠️ Gemini analysis could not be completed."
            )

            st.caption(
                "Your ATS score and resume analysis are still available."
            )

            with st.expander(
                "🔎 View Gemini API Error"
            ):

                st.code(
                    error_message
                )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "📄 ResumeAI • Python • Streamlit • PyMuPDF • Gemini AI"
)