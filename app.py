import streamlit as st
import os
import json
from dotenv import load_dotenv

load_dotenv()

from utils.api_handler import QuizAPIHandler
from utils.parser import parse_llm_json
from utils.scoring import calculate_score, export_csv, export_pdf

# --- UI STATE INITIALIZATION ---
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "current_text" not in st.session_state:
    st.session_state.current_text = ""

# Set page configuration
st.set_page_config(
    page_title="EduPulse // AI Study Quiz Suite", 
    layout="wide", 
    page_icon=None,
    initial_sidebar_state="expanded"
)

# --- ADVANCED CUSTOM CSS INJECTION ---
st.markdown("""
    <style>
    /* Global Canvas Styling & Clean Pastel Orange Background Base */
    .stApp {
        background-color: #FFEDD5 !important;
    }
    
    /* Force Left Sidebar Panel to a Rich Dark Orange Scheme */
    [data-testid="stSidebar"] {
        background-color: #EA580C !important;
        border-right: 1px solid #C2410C;
    }
    
    /* Make sidebar text highly readable (White text against dark orange background) */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    
    /* Force Right Side Parameter Containers and Metrics Panel to match the Rich Dark Orange Scheme */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #EA580C !important;
        border: 1px solid #C2410C !important;
        border-radius: 16px !important;
    }
    
    /* Ensure right side text elements inside containers are white for high contrast */
    div[data-testid="stVerticalBlockBorderWrapper"] h3, 
    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] span,
    div[data-testid="stVerticalBlockBorderWrapper"] label {
        color: #FFFFFF !important;
    }
    
    /* Fix specific widget metrics layout configurations inside the right panel */
    [data-testid="stMetricWidget"] {
        background-color: #EA580C !important;
        padding: 10px;
        border-radius: 8px;
    }
    
    /* Style metric values to display clearly in white */
    [data-testid="stMetricValue"] div {
        color: #FFFFFF !important;
    }
    [data-testid="stMetricLabel"] div {
        color: #FFEDD5 !important;
    }
    
    .main .block-container { 
        padding-top: 3rem; 
        padding-bottom: 3rem; 
        max-width: 1100px; 
    }
    
    h1, h2, h3 { 
        font-family: 'Inter', system-ui, sans-serif; 
        font-weight: 700; 
        color: #2C3E50; 
    }
    
    /* Clear, unboxed space formatting structure for text elements */
    .stQuestionBlock {
        background: transparent !important;
        padding: 0px 0px 10px 0px;
        margin-bottom: 35px;
    }
    
    /* Darker Background Modification for the Input Text Area Box */
    .stTextArea textarea {
        background-color: #E2E8F0 !important;
        color: #1A252C !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    /* Clean container tweaks */
    [data-testid="stForm"] {
        background: #FFFFFF;
        border-radius: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR & CONTENT MANAGEMENT PANEL ---
with st.sidebar:
    st.markdown("### Control Workspace")
    st.caption("Load data matrices or extract performance logs effortlessly.")
    st.markdown("---")
    
    use_benchmark = st.checkbox("Activate Quality Benchmarks", value=False)
    if use_benchmark:
        benchmark_file = st.selectbox("Choose Core Dataset Domain", ["dbms", "python", "sql", "os"])
        try:
            with open(os.path.join("benchmark", f"{benchmark_file}.txt"), "r") as src:
                st.session_state.current_text = src.read()
            st.success(f"Successfully mounted data matrix: {benchmark_file.upper()}")
        except FileNotFoundError:
            st.error("Target benchmark file vector not discovered.")
    
    st.markdown("---")

try:
    with open(os.path.join("data", "quiz_rules.json"), "r") as f:
        config_rules = json.load(f)
except FileNotFoundError:
    st.error("Missing critical backend system config rules asset layout.")
    st.stop()


# --- HEADER WORKSPACE ---
st.markdown("<h1 style='text-align: center; margin-bottom: 5px; color: #7C2D12;'>EduPulse Study Suite</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9A3412; font-size: 1.1rem; margin-bottom: 40px;'>Instantly convert complex study documents into crisp, structured knowledge assessments.</p>", unsafe_allow_html=True)


# --- VIEW CONTAINER 1: CONFIGURATION & TEXT INPUT ---
if st.session_state.quiz_data is None:
    # Split primary layout sections dynamically using columns
    layout_col1, layout_col2 = st.columns([5, 3], gap="large")
    
    with layout_col1:
        st.markdown("### Source Material Payload")
        input_text = st.text_area(
            "Paste text contents (notes, articles, slides):",
            value=st.session_state.current_text,
            height=340,
            placeholder="Input text here to build the assessment context boundary structure...",
            label_visibility="collapsed"
        )
        
    with layout_col2:
        st.markdown("### Generation Tuning")
        
        with st.container(border=True):
            num_questions = st.slider(
                "Total Question Volume", 
                min_value=min(config_rules["application_constraints"]["supported_counts"]),
                max_value=max(config_rules["application_constraints"]["supported_counts"]),
                step=5,
                value=5
            )
            
            difficulty = st.segmented_control(
                "Target Cognitive Difficulty",
                options=config_rules["application_constraints"]["difficulty_levels"],
                default="Easy"
            ) or "Easy"
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            generate_btn = st.button("Compile & Synthesize Quiz", type="primary", use_container_width=True)
            
    if generate_btn:
        word_count = len(input_text.strip().split())
        if word_count < config_rules["application_constraints"]["min_word_count"]:
            st.error(f"Input validation failed: requires at least {config_rules['application_constraints']['min_word_count']} words (Current: {word_count}).")
        else:
            with st.spinner("Locking contextual parameters and compiling quiz modules..."):
                try:
                    handler = QuizAPIHandler()
                    raw_response = handler.generate_quiz(input_text, num_questions, difficulty)
                    st.session_state.quiz_data = parse_llm_json(raw_response)
                    st.session_state.user_answers = {}
                    st.session_state.submitted = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Generation Exception: {str(e)}")


# --- VIEW CONTAINER 2 & 3: QUIZ DISPATCH & ASSESSMENT RESULTS ---
else:
    quiz = st.session_state.quiz_data
    
    # Left column holds questions, Right side panels scorecard metrics
    quiz_col, metrics_col = st.columns([5, 3], gap="large")
    
    with quiz_col:
        for idx, q in enumerate(quiz):
            # Formatted clean structural padding block container layout
            st.markdown(f'<div class="stQuestionBlock">', unsafe_allow_html=True)
            st.markdown(f"<span style='color: #EA580C; font-weight:bold; text-transform: uppercase; font-size: 0.8rem;'>Question {idx+1}</span>", unsafe_allow_html=True)
            st.markdown(f"### {q['question']}")
            
            options = q["options"]
            current_selection = st.session_state.user_answers.get(idx, None)
            
            if not st.session_state.submitted:
                chosen = st.radio(
                    f"q_radio_{idx}",
                    options,
                    index=options.index(current_selection) if current_selection in options else None,
                    key=f"ui_node_{idx}",
                    label_visibility="collapsed"
                )
                st.session_state.user_answers[idx] = chosen
            else:
                user_ans = st.session_state.user_answers.get(idx, None)
                correct_ans = q["correct_answer"]
                
                for opt in options:
                    if opt == correct_ans:
                        st.markdown(f"<div style='background-color: rgba(16, 185, 129, 0.12); color: #0E6245; padding: 10px; border-radius: 8px; margin: 4px 0; border-left: 5px solid #10B981; font-weight: 500;'>Correct Option: {opt}</div>", unsafe_allow_html=True)
                    elif opt == user_ans and user_ans != correct_ans:
                        st.markdown(f"<div style='background-color: rgba(239, 68, 68, 0.12); color: #7A1C1C; padding: 10px; border-radius: 8px; margin: 4px 0; border-left: 5px solid #EF4444;'>Your Selection: {opt}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='padding: 10px; opacity: 0.75; color: #2C3E50;'>{opt}</div>", unsafe_allow_html=True)
                        
                st.markdown(f"<div style='margin-top: 12px; font-style: italic; font-size:0.9rem; color:#64748B;'>Explanation Trace: {q.get('explanation', 'Verified from text.')}</div>", unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True) # End of question container element

    with metrics_col:
        if not st.session_state.submitted:
            st.markdown("### Submission Panel")
            with st.container(border=True):
                st.info("Ensure all options selections are populated. Once finalized, responses are evaluated instantly.")
                submit_btn = st.button("Submit Final Answers", type="primary", use_container_width=True)
                
                if submit_btn:
                    if len(st.session_state.user_answers) < len(quiz) or None in st.session_state.user_answers.values():
                        st.warning("Please address all assessment modules before submission.")
                    else:
                        st.session_state.submitted = True
                        st.rerun()
        else:
            score, detailed_results = calculate_score(quiz, st.session_state.user_answers)
            pct = int((score / len(quiz)) * 100)
            
            st.markdown("### Metrics Scorecard")
            with st.container(border=True):
                st.metric("Assessment Score Performance", f"{score} / {len(quiz)}", f"{pct}% Accuracy")
                st.progress(score / len(quiz))
                
                st.markdown("---")
                st.markdown("#### Export Analytics")
                
                csv_file = export_csv(detailed_results)
                pdf_file = export_pdf(detailed_results, f"{score}/{len(quiz)} ({pct}%)")
                
                with open(csv_file, "rb") as f:
                    st.download_button("Download Raw CSV Logs", data=f, file_name="perf_logs.csv", mime="text/csv", use_container_width=True)
                with open(pdf_file, "rb") as f:
                    st.download_button("Print Official PDF Report", data=f, file_name="final_report.pdf", mime="application/pdf", use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Restart & Load New Material", type="secondary", use_container_width=True):
                st.session_state.quiz_data = None
                st.session_state.user_answers = {}
                st.session_state.submitted = False
                st.rerun()