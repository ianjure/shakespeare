import re
import streamlit as st
from fpdf import FPDF
from PIL import Image
from utils import generate_script

# [STREAMLIT] PAGE CONFIGURATION
icon = Image.open("icon.png")
st.set_page_config(page_title="Shakespeare", page_icon=icon, initial_sidebar_state="collapsed")
st.logo("logo.svg")

# [STREAMLIT] ADJUST HEADER
header = """
    <style>
    [data-testid="stHeader"] {
        height: 5.3rem;
        width: auto;
        z-index: 1;
    }
    </style>
        """
st.markdown(header, unsafe_allow_html=True)

# [STREAMLIT] ADJUST TOP PADDING
top = """
    <style>
    .block-container {
        padding-top: 0rem;
        padding-bottom: 2rem;
        margin-top: -2rem;
    }
    </style>
        """
st.markdown(top, unsafe_allow_html=True)

# [STREAMLIT] HIDE TEXT ANCHOR
hide_anchor = """
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none;
    }
    </style>
    """
st.markdown(hide_anchor, unsafe_allow_html=True)

# [STREAMLIT] ADJUST LOGO SIZE
logo = """
    <style>
    [data-testid="stLogo"] {
        width: 12rem;
        height: auto;
    }
    </style>
        """
st.markdown(logo, unsafe_allow_html=True)

#  [STEAMLIT] CHANGE FONT STYLE
with open( "style.css" ) as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)
text_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

    [data-testid="stSliderThumbValue"] {
      font-family: 'Poppins', sans-serif !important;
      font-weight: 300; 
    }
    [data-testid="stSliderTickBarMin"] {
      font-family: 'Poppins', sans-serif !important;
      font-weight: 300; 
    }
    [data-testid="stSliderTickBarMax"] {
      font-family: 'Poppins', sans-serif !important;
      font-weight: 300; 
    }
    </style>
        """
st.markdown(text_style, unsafe_allow_html=True)

# [FPDF] GENERATE A PDF FILE FROM CONVERSATION
def generate_pdf(script):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.add_font("DejaVuBook", "", "dejavu-sans-book.ttf", uni=True)
    pdf.add_font("DejaVuBold", "", "dejavu-sans-bold.ttf", uni=True)
    
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    lines = script.splitlines()
    for line in lines:
        if line.startswith("##"):
            title = line[2:].strip()
            title = re.sub(r"\s*\(.*\)$", "", title)
            title = f"Title: {title}"
            pdf.set_font("DejaVuBold", size=12)
            pdf.cell(0, 5, txt=title, ln=True)
            pdf.ln(4)
        else:
            if line.lower().startswith("host:"):
                pdf.set_font("DejaVuBold", size=12)
                pdf.write(4, line)
                pdf.ln(10)
            else:
                chunks = re.split(r"(\*\*.*?\*\*)", line)
                for chunk in chunks:
                    if chunk.startswith("**") and chunk.endswith("**"):
                        bold_text = chunk[2:-2]
                        pdf.set_font("DejaVuBold", size=10)
                        pdf.write(4, bold_text)
                    else:
                        pdf.set_font("DejaVuBook", "", size=10)
                        pdf.write(4, chunk)
                pdf.ln(4)
    
    pdf_output = pdf.output(dest="S")
    return bytes(pdf_output)

# [STREAMLIT] APP TITLE AND HEADER
st.markdown("<h2 style='text-align: center;'>YouTube Scriptwriting Tool</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='font-size: 1.2rem; text-align: center;'>Generate a video script by specifying a topic, length, target audience, and creativity level.</h4>", unsafe_allow_html=True)

# [STREAMLIT] SIDEBAR TP CAPTURE API KEY
st.sidebar.title("API Configuration")
st.sidebar.text_input("Enter your Gemini API key:", type="password", key="api_key")

# [STREAMLIT] MAIN INPUT FIELDS
with st.container(border=True):
    prompt = st.text_input("Provide the topic of the video:")
    video_length_column, target_audience_column = st.columns(2)
    with video_length_column:
        video_length_options = ["5 Mins", "10 Mins", "15 Mins", "20 Mins"]
        video_length = st.segmented_control("Specify video length:", video_length_options, selection_mode="single")
    with target_audience_column:
        audience_options = ["Kids", "Teens", "Adults"]
        target_audience = st.segmented_control("Select target audience:", audience_options, selection_mode="single")
    creativity = st.slider("Set creativity level:", min_value=0.0, max_value=1.0, value=0.5)

    # [STREAMLIT] BUTTON TO GENERATE THE SCRIPT
    if prompt and video_length and target_audience:
        generate_script_button = st.button("**GENERATE SCRIPT**", type="primary", use_container_width=True)
    else:
        generate_script_button = st.button("**GENERATE SCRIPT**", type="primary", disabled=True, use_container_width=True)

# [STREAMLIT] WHEN THE BUTTON IS CLICKED, THE SCRIPT WILL BE GENERATED
if generate_script_button:
    api_key = st.session_state.api_key
    if not api_key:
        st.error("Please provide a valid Gemini API key.")
    else:
        title, script, search_data = generate_script(prompt, video_length, target_audience, creativity, api_key)
        title = title.replace('\n', '')
        st.success("Script generated successfully!")
        download_button = st.download_button(label="**DOWNLOAD SCRIPT**", type="secondary", key="download", data=generate_pdf(script),
                                             file_name=f"{title}.pdf", mime="application/pdf", use_container_width=True)
        if download_button:
            st.rerun()

        if search_data != "None":
            with st.expander("Show search data"):
                st.write(search_data)