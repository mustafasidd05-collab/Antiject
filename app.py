"""
PromptShield Interactive Demo App.
Side-by-side comparison: Unprotected Victim Agent vs Protected Agent with PromptShield.
"""

import json
import os
import streamlit as st
from dotenv import load_dotenv

from promptshield.firewall import PromptShield, Policy, escape_untrusted_delimiters, wrap_untrusted_data
from promptshield.judge import GemmaJudge, MockJudge
from promptshield.scanner import Scanner
from promptshield.victim_agent import VictimAgent
from promptshield.loaders import load_text, load_html, load_pdf

load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="PromptShield - Prompt-Injection Firewall",
    page_icon="🛡️",
    layout="wide",
)

# Custom CSS for clean layout and clear alerts (no glassmorphism)
st.markdown("""
<style>
    .metric-card {
        padding: 12px;
        border-radius: 6px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        margin-bottom: 8px;
    }
    .status-badge-red {
        background-color: #ffebe9;
        color: #cf222e;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        border: 1px solid #ff8182;
    }
    .status-badge-green {
        background-color: #dafbe1;
        color: #1a7f37;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        border: 1px solid #4ac26b;
    }
    .status-badge-orange {
        background-color: #fff8c5;
        color: #9a6700;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        border: 1px solid #d4a72c;
    }
</style>
""", unsafe_allow_html=True)

# Helper to load sample files
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "demo", "samples")

def get_sample_content(filename: str) -> str:
    path = os.path.join(SAMPLE_DIR, filename)
    if not os.path.exists(path):
        return ""
    if filename.endswith(".html"):
        return load_html(path)
    return load_text(path)

# ----------------- SIDEBAR CONFIGURATION -----------------
st.sidebar.title("🛡️ PromptShield Settings")

# API Key handling
env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
api_key_input = st.sidebar.text_input(
    "Google GenAI API Key (Optional)",
    value=st.session_state.get("api_key", env_key),
    type="password",
    help="Enter API key to unlock live Gemma evaluation. If omitted, PromptShield runs in MockJudge simulation mode.",
)
if api_key_input:
    st.session_state["api_key"] = api_key_input
else:
    st.session_state["api_key"] = None

# Model Configuration
active_key = st.session_state.get("api_key")
if active_key:
    judge = GemmaJudge(api_key=active_key)
else:
    judge = MockJudge()

policy_choice = st.sidebar.selectbox(
    "Firewall Policy",
    options=["BALANCED", "STRICT", "PERMISSIVE"],
    index=0,
    help="Balanced: Blocks risk >= 0.70, sanitizes >= 0.30. Strict: Blocks risk >= 0.50. Permissive: Blocks risk >= 0.85.",
)
active_policy = Policy[policy_choice]

agent_mode = st.sidebar.radio(
    "Victim Agent Execution Mode",
    options=["Deterministic Simulation (Default)", "Live Model Execution"],
    index=0,
    help="Simulation mode is deterministic, instantaneous, and logs mock email dispatch. Live mode uses GenAI model directly.",
)
use_live_agent = (agent_mode == "Live Model Execution" and active_key is not None)

# Preset Document Selection
preset_choice = st.sidebar.selectbox(
    "Choose Preset or Custom Document",
    options=[
        "Preset: Poisoned Résumé (Hidden Exfiltration)",
        "Preset: Poisoned Invoice (Hidden Comment)",
        "Preset: Clean Engineering Report (Benign)",
        "Preset: Security Research Blog (Hard Negative)",
        "Custom Text Input",
        "Upload File (.txt, .pdf, .html)",
    ],
    index=0,
)

# Text Retrieval based on Preset
doc_text = ""
if preset_choice == "Preset: Poisoned Résumé (Hidden Exfiltration)":
    doc_text = get_sample_content("poisoned_resume.txt")
elif preset_choice == "Preset: Poisoned Invoice (Hidden Comment)":
    doc_text = get_sample_content("poisoned_invoice.html")
elif preset_choice == "Preset: Clean Engineering Report (Benign)":
    doc_text = get_sample_content("clean_report.txt")
elif preset_choice == "Preset: Security Research Blog (Hard Negative)":
    doc_text = get_sample_content("security_blog_post.txt")
elif preset_choice == "Upload File (.txt, .pdf, .html)":
    uploaded_file = st.sidebar.file_uploader("Upload Document", type=["txt", "md", "pdf", "html", "htm"])
    if uploaded_file:
        file_bytes = uploaded_file.read()
        if uploaded_file.name.endswith(".pdf"):
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
            doc_text = load_pdf(tmp_path)
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        elif uploaded_file.name.endswith((".html", ".htm")):
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
            doc_text = load_html(tmp_path)
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        else:
            doc_text = file_bytes.decode("utf-8", errors="replace")
else:
    doc_text = st.sidebar.text_area("Paste document text here", height=200)

# Instantiate Firewall and Victim Agent
scanner = Scanner()
firewall = PromptShield(policy=active_policy, judge=judge, scanner=scanner)

if use_live_agent:
    victim = VictimAgent(
        firewall=firewall,
        live_model=True,
        client=getattr(judge, "client", None),
        model_name=getattr(judge, "model_name", "gemma-2-9b-it"),
    )
else:
    victim = VictimAgent(firewall=firewall, live_model=False)

# ----------------- MAIN UI BANNER -----------------
st.title("PromptShield: Prompt-Injection Firewall for AI Agents")
st.markdown("Defending autonomous AI agents against indirect prompt injection via a **3-Layer Defense-in-Depth** pipeline.")

# Active Model Status Banner
col_status1, col_status2 = st.columns([3, 1])
with col_status1:
    model_name_label = firewall.model_label
    if "MockJudge" in model_name_label:
        st.warning(f"**Active Classifier:** `{model_name_label}` — Provide an API key in the sidebar to activate live Gemma models.")
    else:
        st.success(f"**Active Classifier:** `{model_name_label}` (Live Cloud Inference)")
with col_status2:
    st.info(f"**Policy:** `{active_policy.value}`")

# Document Viewer Expander
with st.expander("📄 View Input Document Content", expanded=True):
    st.text_area("Raw Untrusted Input", value=doc_text, height=180, disabled=True)

# Run Button
trigger_scan = st.button("🚀 Analyze & Execute Side-by-Side Comparison", type="primary", use_container_width=True)

if trigger_scan or doc_text:
    st.markdown("---")
    left_col, right_col = st.columns(2)

    # ----------------- LEFT COLUMN: UNPROTECTED -----------------
    with left_col:
        st.subheader("❌ Unprotected Victim Agent")
        st.caption("Agent ingests raw untrusted data directly without defensive inspection.")

        unprotected_result = victim.run_unprotected(doc_text)

        if unprotected_result["compromised"]:
            st.markdown('<div class="status-badge-red">⚠️ STATUS: COMPROMISED (Data Exfiltration)</div>', unsafe_allow_html=True)
            st.error(unprotected_result["alert"])
            st.markdown("#### Triggered Unauthorized Tool Actions:")
            for t in unprotected_result["tool_calls"]:
                st.code(
                    f"Tool: {t['tool']}\nRecipient: {t['arguments'].get('to')}\nPayload: {t['arguments'].get('body')}",
                    language="python"
                )
            st.markdown("#### Agent Output:")
            st.write(unprotected_result["summary"])
        else:
            st.markdown('<div class="status-badge-green">✔️ STATUS: CLEAN (Normal Operation)</div>', unsafe_allow_html=True)
            st.info("No indirect directives triggered. Document summarized normally.")
            st.write(unprotected_result["summary"])

    # ----------------- RIGHT COLUMN: PROTECTED -----------------
    with right_col:
        st.subheader("🛡️ Protected with PromptShield")
        st.caption("PromptShield intercepts and sanitizes payload before the agent processes it.")

        protected_result = victim.run_protected(doc_text)
        verdict = protected_result.get("verdict")

        if verdict:
            # Verdict Badge
            if verdict.verdict == "BLOCK":
                st.markdown('<div class="status-badge-red">🛑 VERDICT: BLOCK (Payload Refused)</div>', unsafe_allow_html=True)
            elif verdict.verdict == "SANITIZE":
                st.markdown('<div class="status-badge-orange">⚠️ VERDICT: SANITIZE (Quote Excised)</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-badge-green">🛡️ VERDICT: ALLOW (Clean & Tag-Wrapped)</div>', unsafe_allow_html=True)

            # Metric Cards
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Composite Risk", f"{verdict.risk_score:.2f}")
            with m2:
                total_lat = verdict.latency_breakdown.get("total_ms", 0.0)
                st.metric("Total Latency", f"{total_lat:.1f} ms")
            with m3:
                l1_count = len(verdict.layer1_matches)
                st.metric("L1 Triggers", f"{l1_count} matches")

            # Layer Breakdown
            with st.expander("🔍 Layer-by-Layer Forensic Analysis", expanded=True):
                st.markdown("**Layer 1 (Fast Scanner):**")
                if verdict.layer1_triggered:
                    for m in verdict.layer1_matches:
                        st.write(f"- `{m.rule_id}` ({m.name}) -> Snippet: `{m.matched_text}` (Severity: {m.severity})")
                else:
                    st.write("- Clean (No invisible Unicode or known pattern signatures)")

                st.markdown("**Layer 2 (Gemma Judge):**")
                if verdict.layer2_skipped:
                    st.info("⚡ Layer 2 skipped because Layer 1 produced a confident BLOCK.")
                elif not verdict.judge_available:
                    st.warning(f"⚠️ Layer 2 unavailable ({verdict.judge_error}). Fell back to Layer 1 rule scan.")
                elif verdict.judge_result:
                    j = verdict.judge_result
                    st.write(f"- Classification: `{'Attack' if j.is_attack else 'Clean'}` (Confidence: {j.confidence:.2f})")
                    if j.quote:
                        st.markdown(f"- **Extracted Malicious Quote:**")
                        st.code(j.quote, language="text")
                        st.caption(f"Quote Verified in Source: `{j.quote_verified}`")
                    st.write(f"- Reason: {j.reason}")

            # Delimiter Wrapping Inspection
            if verdict.wrapped_text:
                with st.expander("📦 Safe <untrusted_data> Tag Wrapping", expanded=False):
                    st.code(verdict.wrapped_text, language="xml")

            # Protected Agent Outcome
            st.markdown("#### Protected Agent Execution:")
            if verdict.verdict == "BLOCK":
                st.success("🔒 **Refusal Gate:** Payload was never provided to the agent. Zero data exfiltrated!")
            else:
                st.success("🔒 **Contained Execution:** Agent processed sanitized content. Tool call avoided!")
                st.write(protected_result["summary"])

# ----------------- BENCHMARK RESULTS SECTION -----------------
st.markdown("---")
st.subheader("📊 Empirical Benchmark Results (40 Curated Samples)")
st.caption("Evaluated across 20 attacks and 20 benign documents in English, Hindi, and Hinglish across HR, Invoices, and Customer Support.")

benchmark_file = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
if os.path.exists(benchmark_file):
    with open(benchmark_file, "r", encoding="utf-8") as f:
        bench_data = json.load(f)

    res = bench_data.get("results", {})
    cols = st.columns(3)
    
    config_keys = [
        ("Layer 1 Only (Rules)", "layer1_only", cols[0]),
        ("Gemma Judge Only", "judge_only", cols[1]),
        ("Combined (PromptShield)", "combined", cols[2]),
    ]

    for title, key, col in config_keys:
        cfg = res.get(key, {})
        with col:
            st.markdown(f"#### {title}")
            st.write(f"- **Caught:** `{cfg.get('tp', 0)} / {cfg.get('total_attacks', 20)}`")
            st.write(f"- **Missed:** `{cfg.get('fn', 0)}`")
            st.write(f"- **False Alarms:** `{cfg.get('fp', 0)} / {cfg.get('total_benign', 20)}`")
            st.write(f"- **F1 Score:** `{cfg.get('f1', 0.0):.3f}`")
            st.write(f"- **Avg Latency:** `{cfg.get('avg_latency_ms', 0.0)} ms`")

    if not bench_data.get("is_live_gemma", False):
        st.info("ℹ️ Note: These benchmark figures were produced in Simulation Mode (MockJudge) without a live API key. Run `python evaluate.py` with `GEMINI_API_KEY` to update live Gemma figures.")
else:
    st.info("Run `python evaluate.py` to generate the latest benchmark metrics table.")
