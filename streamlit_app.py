import streamlit as st
import os
import sys
import datetime
import pandas as pd
from PIL import Image

# Fix path to include current directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from report_agent.crew import ReportAgentCrew

# --- Page Config ---
st.set_page_config(
    page_title="Autonomous Report Agent",
    page_icon="📊",
    layout="wide"
)

# --- Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .report-container {
        padding: 20px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Configuration")
    tone = st.selectbox("Tone of Voice", ["Professional", "Casual", "Executive Summary", "Detailed Technical"])
    language = st.selectbox("Language", ["English", "Vietnamese"])
    
    st.divider()
    st.info("This agent uses CrewAI and Google Gemini to analyze Olist E-commerce data.")
    
    # Handle API Key from secrets or manual input
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
        st.success("✅ API Key loaded from Secrets")
    else:
        api_key = st.text_input("Enter Gemini API Key", type="password")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            st.success("✅ API Key set for this session")
        else:
            st.warning("⚠️ Please provide an API Key")

# --- Main UI ---
st.title("📊 Autonomous Report Agent")
st.subheader("Turn natural language into professional data reports")

user_prompt = st.text_area("What would you like to analyze today?", 
                           placeholder="e.g., Phân tích doanh thu của seller 53243585a1d6dc2643021fd1853d8905 trong năm 2017...",
                           height=100)

if st.button("🚀 Run Analysis"):
    if not os.environ.get("GEMINI_API_KEY"):
        st.error("Please provide a Gemini API Key in the sidebar.")
    elif not user_prompt:
        st.error("Please enter an analysis request.")
    else:
        # Prepare output folder
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_folder_name = f"report_{timestamp}"
        # In Streamlit Cloud, we can use the local dir or /tmp
        report_folder = os.path.join(os.getcwd(), 'report_agent', 'results', report_folder_name)
        os.makedirs(report_folder, exist_ok=True)
        
        # Use forward slashes for safer prompt interpolation
        report_folder = report_folder.replace('\\', '/')

        inputs = {
            'user_prompt': user_prompt,
            'tone_of_voice': tone,
            'language': language,
            'report_folder': report_folder
        }

        with st.status("🤖 Agents are working...", expanded=True) as status:
            st.write("Initializing Crew...")
            try:
                # Run the crew
                result = ReportAgentCrew().crew().kickoff(inputs=inputs)
                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                
                st.balloons()
                
                # --- Display Results ---
                st.divider()
                st.header("📋 Final Report")
                
                # Try to read the generated markdown file
                report_path = os.path.join(report_folder, 'final_report.md')
                if os.path.exists(report_path):
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    
                    # Layout: 2 columns if there are images
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(report_content)
                    
                    with col2:
                        st.subheader("🖼️ Visualizations")
                        images = [f for f in os.listdir(report_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
                        if images:
                            for img_name in images:
                                img_path = os.path.join(report_folder, img_name)
                                st.image(img_path, caption=img_name, use_container_width=True)
                        else:
                            st.info("No charts were generated for this report.")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Report (Markdown)",
                        data=report_content,
                        file_name=f"report_{timestamp}.md",
                        mime="text/markdown"
                    )
                else:
                    st.write(result)
                    st.warning("Could not find the final_report.md file, displaying raw output above.")

            except Exception as e:
                status.update(label="❌ Error occurred", state="error")
                st.error(f"An error occurred: {str(e)}")

# --- Footer ---
st.divider()
st.caption("Powered by CrewAI, DuckDB, and Google Gemini Flash.")
