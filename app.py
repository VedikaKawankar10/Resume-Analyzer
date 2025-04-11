import streamlit as st
from analyzer import analyze_resume
from utils import extract_text_from_pdf, extract_text_from_txt, save_to_pdf
import matplotlib.pyplot as plt

# ----------------------------
# 🌟 Streamlit Page Config
# ----------------------------
st.set_page_config(page_title="Resume vs JD Analyzer", layout="wide", page_icon="📄")

# ----------------------------
# 🎨 Custom CSS Styling
# ----------------------------
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 0.5em 1em;
        border-radius: 10px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stFileUploader {
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# 📌 Header Section
# ----------------------------
st.title("📄 Resume vs Job Description Analyzer")
st.markdown("Upload a **resume** and a **job description** to analyze matching skills, missing keywords, and get improvement suggestions!")

# ----------------------------
# 📂 Sidebar - File Uploads
# ----------------------------
st.sidebar.header("📁 Upload Files")

resume_file = st.sidebar.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
upload_option = st.sidebar.radio("Upload JD as", ("Upload File", "Paste Text"))

jd_file = None
jd_text_input = ""
jd_text = ""

if upload_option == "Upload File":
    jd_file = st.sidebar.file_uploader("Upload JD File (PDF or TXT)", type=["pdf", "txt"])
else:
    jd_text_input = st.sidebar.text_area("Paste JD Text")

# ----------------------------
# 🔘 Button State Management
# ----------------------------
if "analyze_clicked" not in st.session_state:
    st.session_state["analyze_clicked"] = False

if st.button("🚀 Analyze"):
    st.session_state["analyze_clicked"] = True

# ----------------------------
# 🔍 Perform Analysis
# ----------------------------
if st.session_state["analyze_clicked"]:
    if not resume_file:
        st.warning("Please upload a resume file.")
    elif (not jd_file and upload_option == "Upload File") or (upload_option == "Paste Text" and not jd_text_input.strip()):
        st.warning("Please provide a job description.")
    else:
        try:
            jd_text = extract_text_from_pdf(jd_file) if jd_file and jd_file.name.endswith(".pdf") else (
                extract_text_from_txt(jd_file) if jd_file else jd_text_input.strip()
            )
            resume_text = extract_text_from_pdf(resume_file) if resume_file.name.endswith(".pdf") else extract_text_from_txt(resume_file)

            result = analyze_resume(jd_text, resume_text)

            st.session_state["result"] = result
            st.session_state["resume_text"] = resume_text
            st.session_state["jd_text"] = jd_text
        except Exception as e:
            st.error(f"Error during analysis: {e}")

# ----------------------------
# 📊 Display Results
# ----------------------------
if "result" in st.session_state:
    result = st.session_state["result"]
    resume_text = st.session_state["resume_text"]
    jd_text = st.session_state["jd_text"]

    st.markdown("## 📊 Match Summary")
    st.success(f"**Match Score:** `{result['match_score']}%`")
    st.markdown(f"**Total JD Keywords:** {len(result['jd_keywords'])}")
    st.markdown(f"**Matched Skills:** {len(result['matched_keywords'])}")
    st.markdown(f"**Missing Skills:** {len(result['missing_keywords'])}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Matched Keywords")
        st.write(result["matched_keywords"] if result["matched_keywords"] else "None")

    with col2:
        st.markdown("### ❌ Missing Keywords")
        st.write(result["missing_keywords"] if result["missing_keywords"] else "None")

    st.markdown("### 📈 Match Distribution")
    counts = [len(result["matched_keywords"]), len(result["missing_keywords"])]
    labels = ["Matched", "Missing"]
    colors = ["#00cc96", "#ff6361"]

    fig, ax = plt.subplots()
    ax.pie(counts, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    st.markdown("### 💡 Resume Improvement Suggestions")
    if result["missing_keywords"]:
        st.markdown("Try adding these skills/keywords to improve your match:")
        st.write(result["missing_keywords"])
    else:
        st.success("Your resume already includes all important keywords from the JD!")

    st.markdown("---")
    st.markdown("### 🧾 Resume & JD Preview")
    preview_col1, preview_col2 = st.columns(2)
    with preview_col1:
        st.markdown("#### 📝 Resume Text")
        st.write(resume_text)
    with preview_col2:
        st.markdown("#### 📌 Job Description")
        st.write(jd_text)

    # ----------------------------
    # 📄 Save as PDF
    # ----------------------------
    with st.expander("📥 Save or Share Report"):
        if st.button("💾 Save Analysis as PDF"):
            file_path = save_to_pdf(result, jd_text, resume_text)
            with open(file_path, "rb") as f:
                st.download_button("⬇️ Download PDF", f, file_name="resume_vs_jd_analysis.pdf", mime="application/pdf")
