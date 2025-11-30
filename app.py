"""
Streamlit Web Interface for GitGuard AI.
Run this using: streamlit run app.py
"""

import streamlit as st
import uuid
import os
import re
from dotenv import load_dotenv

load_dotenv()

# IMPORT FROM SRC PACKAGE
from src.graph import graph

# --- Helper: Extract Code Snippet from Diff ---
def extract_code_snippet(diff_text: str, file_path: str, target_line: int, context_lines: int = 4) -> str:
    """
    Parses a raw git diff to find the specific line of code at target_line,
    including surrounding context lines for better readability.
    """
    try:
        # Split diff into file chunks
        file_chunks = diff_text.split("diff --git")

        target_chunk = None
        for chunk in file_chunks:
            # Check if this chunk belongs to the file we want
            if f"b/{file_path}" in chunk or f" {file_path}" in chunk:
                target_chunk = chunk
                break

        if not target_chunk:
            return "[Code snippet not found in diff context]"

        lines = target_chunk.split('\n')
        current_line_num = 0
        snippet_lines = []

        # Track if we are inside a hunk
        in_hunk = False

        for line in lines:
            # Look for hunk header: @@ -old_start,old_len +new_start,new_len @@
            hunk_match = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
            if hunk_match:
                current_line_num = int(hunk_match.group(1)) - 1
                in_hunk = True
                continue

            if not in_hunk:
                continue

            # Identify diff lines: '+' (added), ' ' (context)
            # We ignore '-' (deleted) lines for the purpose of counting new file lines
            if line.startswith('+') or line.startswith(' '):
                current_line_num += 1

                # Check if current line is within the context window
                if target_line - context_lines <= current_line_num <= target_line + context_lines:
                    # Marker for the specific target line
                    marker = ">>" if current_line_num == target_line else "  "

                    # Preserve indentation but remove the first char (+ or space)
                    code_content = line[1:].rstrip()

                    snippet_lines.append(f"{marker} {current_line_num:4d} | {code_content}")

    except Exception as e:
        return f"[Error parsing diff: {str(e)}]"

    if not snippet_lines:
        return "[Target line outside of provided diff context]"

    return "\n".join(snippet_lines)

# --- Custom CSS for Mercedes F1 / Teenage Engineering Aesthetic ---
st.set_page_config(page_title="GitGuard AI // DATAPAD", page_icon="💾", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

    /* Global Font */
    html, body, [class*="css"]  {
        font-family: 'Space Mono', monospace;
        color: #F0F0F0; /* Silver/White */
        background-color: #15151E; /* Dark Asphalt/Black */
    }

    /* Streamlit Main Container */
    .stApp {
        background-color: #15151E;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 2px solid #00D2BE; /* Petronas Green Border */
    }

    /* Headings */
    h1, h2, h3 {
        font-family: 'Space Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #00D2BE; /* Petronas Green */
    }
    
    /* HIDE ANCHOR LINKS */
    [data-testid="stMarkdownContainer"] h1 a,
    [data-testid="stMarkdownContainer"] h2 a,
    [data-testid="stMarkdownContainer"] h3 a {
        display: none !important;
    }

    /* Buttons (Primary) - TE/F1 Style */
    .stButton > button {
        border-radius: 4px;
        background-color: #00D2BE; /* Petronas Green */
        color: #000000;
        border: none;
        font-weight: 700;
        text-transform: uppercase;
        box-shadow: 0px 4px 0px #005F56; /* Darker Green Shadow */
        transition: all 0.1s ease;
    }
    .stButton > button:hover {
        background-color: #00F5DE; /* Brighter Green */
        box-shadow: 0px 2px 0px #005F56;
        transform: translateY(2px);
    }
    .stButton > button:active {
        box-shadow: 0px 0px 0px #005F56;
        transform: translateY(4px);
    }

    /* Inputs */
    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background-color: #1A1A24; /* Darker input background */
        color: #00D2BE; /* Petronas Green Text */
        border: 1px solid #00D2BE; /* Petronas Green Border */
        border-radius: 4px;
        font-family: 'Space Mono', monospace;
    }
    
    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background-color: #1A1A24;
        color: #00D2BE;
        border: 1px solid #00D2BE;
        border-radius: 4px;
    }

    /* Status Container */
    [data-testid="stStatusWidget"] {
        background-color: #1A1A24;
        border: 1px solid #00D2BE;
        border-radius: 4px;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #1A1A24;
        border: 1px solid #00D2BE; /* Petronas Green Border */
        border-radius: 4px;
        color: #F0F0F0;
    }
    
    /* Divider */
    hr {
        border-color: #00D2BE;
        opacity: 0.6; /* Increased opacity */
    }
    
    /* Metrics/Text Highlight */
    code {
        color: #00D2BE;
        background-color: #222222;
        border: 1px solid #333333;
    }

</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("GitGuard AI // SYSTEM CORE")
st.caption("A U T O N O M O U S   C O D E   R E V I E W   D R O I D   [ v 2 . 1 ]")

st.markdown("---")

# --- Sidebar ---
with st.sidebar:
    st.markdown("## /// CONFIGURATION ///")
    st.markdown("`TARGET_SYSTEM:`")
    repo_name = st.text_input("Repository", value="aeon-toolkit/aeon", label_visibility="collapsed")

    st.markdown("`SIGNAL_FREQUENCY:`")
    pr_number = st.number_input("PR Number", min_value=1, value=3133, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("## /// AI CORE ///")
    model_choice = st.selectbox(
        "Select Processing Unit",
        options=["gpt-4o-mini", "gpt-4o", "gpt-4.1-nano", "gpt-4.1-mini"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    if not os.getenv("GITHUB_TOKEN"):
        st.error("⚠️ SECURE CONNECTION REQUIRED")
        st.markdown("`ACCESS_TOKEN:`")
        os.environ["GITHUB_TOKEN"] = st.text_input("Enter Token", type="password", label_visibility="collapsed")
    else:
        st.success("✅ SECURE CONNECTION ESTABLISHED")

    st.markdown(f"`SYSTEM_STATUS:` **ONLINE**")
    st.markdown(f"`ACTIVE_MODEL:` **{model_choice.upper()}**")

# --- State ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "comments" not in st.session_state:
    st.session_state.comments = None
if "pr_diff" not in st.session_state:
    st.session_state.pr_diff = ""

# --- Logic ---
def run_scan():
    """Phase 1: Analysis"""
    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id,
            "model": model_choice  # Pass selected model to backend
        }
    }
    initial_state = {"repo_name": repo_name, "pr_number": pr_number}

    # Custom status container
    placeholder = st.empty()
    with placeholder.container():
        st.info(f"Initiating Scanning Sequence ({model_choice})...")

        # Simulate terminal output
        log_container = st.container()

        for event in graph.stream(initial_state, config):
            for node, val in event.items():
                with log_container:
                    st.markdown(f"`> NODE EXECUTED: {node.upper()}`")

    placeholder.empty()

    # Check HITL state
    snapshot = graph.get_state(config)
    if snapshot.next:
        # Retrieve comments and the raw DIFF
        st.session_state.comments = snapshot.values.get("proposed_comments", [])
        st.session_state.pr_diff = snapshot.values.get("pr_diff", "")
    else:
        st.session_state.comments = []
        st.session_state.pr_diff = ""

def approve_post():
    """Phase 2: Posting"""
    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id,
            "model": model_choice
        }
    }

    with st.status("TRANSMITTING DATA TO GITHUB...", expanded=True):
        graph.update_state(config, {"review_approved": True})
        result_msg = ""
        for event in graph.stream(None, config):
            for val in event.values():
                if "messages" in val:
                    # Fix: Handle both tuple and Message object formats
                    last_msg = val["messages"][-1]
                    if hasattr(last_msg, "content"):
                        result_msg = last_msg.content
                    elif isinstance(last_msg, tuple) and len(last_msg) > 1:
                        result_msg = last_msg[1]
                    else:
                        result_msg = str(last_msg)

                    st.markdown(f"`> {result_msg}`")

        st.session_state.comments = None # Reset
        st.session_state.pr_diff = ""

# --- UI Render ---

# Main Action Area
col_a, col_b = st.columns([1, 2])

with col_a:
    st.markdown("### `COMMAND`")
    if st.button("INITIALIZE SCAN"):
        run_scan()

with col_b:
    st.markdown("### `TELEMETRY`")

    # CASE 1: Waiting for input
    if st.session_state.comments is None:
        st.markdown("""
        ```text
        WAITING FOR INPUT...
        --------------------
        NO ANOMALIES DETECTED
        IN LOCAL BUFFER.
        ```
        """)

    # CASE 2: Scan ran, but NO comments found (Empty List)
    elif len(st.session_state.comments) == 0:
        st.success("✅ SCAN COMPLETE. NO ANOMALIES DETECTED.")
        st.markdown("""
        ```text
        SYSTEM REPORT:
        --------------
        CODE INTEGRITY: 100%
        THREAT LEVEL: 0
        STATUS: CLEAN
        ```
        """)
        if st.button("RESET SYSTEM"):
            st.session_state.comments = None
            st.rerun()

# CASE 3: Scan ran, Comments found (List has items)
if st.session_state.comments and len(st.session_state.comments) > 0:
    st.markdown("---")
    st.markdown(f"## /// ANOMALY REPORT [{len(st.session_state.comments)}] ///")

    for i, c in enumerate(st.session_state.comments, 1):
        # Extract code snippet using helper
        code_chunk = extract_code_snippet(
            st.session_state.pr_diff,
            c.file_path,
            c.line_number
        )

        with st.expander(f"REPORT #{i:02d} // {c.file_path} // L{c.line_number}"):
            st.markdown(f"`SEVERITY_LEVEL:` **{c.severity.upper()}**")
            # Display the code line in a visually distinct way
            st.markdown(f"**CODE SNIPPET:**")
            st.code(code_chunk, language="python")
            st.markdown(f"**COMMENT:**")
            st.info(c.body)

    st.markdown("---")
    st.markdown("### `AUTHORIZATION`")

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("TRANSMIT"):
            approve_post()
    with c2:
        if st.button("ABORT"):
            st.session_state.comments = None
            st.warning("TRANSMISSION ABORTED.")
            st.rerun()