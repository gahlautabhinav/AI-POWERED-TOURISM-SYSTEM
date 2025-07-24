import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from backendLogic import recommend_places, create_itinerary
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="WanderWise - Smart Travel Companion", 
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'rec_submitted' not in st.session_state:
    st.session_state.rec_submitted = False

# Custom CSS for enhanced styling
def get_css_styles(dark_mode=False):
    if dark_mode:
        return """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* DARK MODE STYLES */
    .stApp {
        font-family: 'Poppins', sans-serif;
        background-color: #1a202c !important;
        color: #e2e8f0 !important;
    }
    
    /* Fix Streamlit default text colors for dark mode */
    .stMarkdown, .stText, p, div, span, h1, h2, h3, h4, h5, h6 {
        color: #e2e8f0 !important;
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        padding: 2.5rem 0;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: #e2e8f0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        border: 1px solid #4a5568;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        color: #e2e8f0 !important;
    }
    
    .main-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        color: #a0aec0 !important;
        opacity: 1;
    }
    
    /* Navigation Styles */
    .nav-container {
        background: #2d3748;
        padding: 1.2rem;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
        display: flex;
        justify-content: center;
        gap: 1rem;
        border: 1px solid #4a5568;
    }
    
    /* Fix button text colors */
    .stButton > button {
        background: linear-gradient(45deg, #38a169 0%, #2f855a 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 25px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(56, 161, 105, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(56, 161, 105, 0.4) !important;
        background: linear-gradient(45deg, #2f855a 0%, #276749 100%) !important;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, rgba(45, 55, 72, 0.9), rgba(26, 32, 44, 0.9)), url('https://images.unsplash.com/photo-1488646953014-85cb44e25828?ixlib=rb-4.0.3');
        background-size: cover;
        background-position: center;
        padding: 4rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: #e2e8f0;
        margin: 2rem 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        border: 1px solid #4a5568;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #e2e8f0 !important;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        margin-bottom: 2rem;
        color: #a0aec0 !important;
        opacity: 1;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        text-align: center;
        transition: transform 0.3s ease;
        margin: 1rem 0;
        border: 2px solid #4a5568;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.4);
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #e2e8f0 !important;
        margin-bottom: 1rem;
    }
    
    .feature-desc {
        color: #a0aec0 !important;
        line-height: 1.7;
        font-size: 1rem;
    }
    
    /* Form Styles */
    .form-container {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        margin: 2rem 0;
        border: 2px solid #4a5568;
    }
    
    .form-title {
        color: #e2e8f0 !important;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Streamlit input styling */
    .stTextInput > div > div > input {
        background-color: #1a202c !important;
        color: #e2e8f0 !important;
        border: 2px solid #4a5568 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }
    
    .stSelectbox > div > div > select {
        background-color: #1a202c !important;
        color: #e2e8f0 !important;
        border: 2px solid #4a5568 !important;
        border-radius: 10px !important;
    }
    
    .stMultiSelect > div > div > div {
        background-color: #1a202c !important;
        color: #e2e8f0 !important;
        border: 2px solid #4a5568 !important;
        border-radius: 10px !important;
    }
    
    /* Labels */
    .stTextInput > label, .stSelectbox > label, .stMultiSelect > label, .stSlider > label {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    /* Results Styles */
    .result-card {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border-left: 6px solid #4299e1;
        transition: all 0.3s ease;
        border: 2px solid #4a5568;
    }
    
    .result-card:hover {
        transform: translateX(8px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
    }
    
    .place-title {
        color: #e2e8f0 !important;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    
    .place-rating {
        color: #f6ad55 !important;
        font-weight: 600;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    .place-desc {
        color: #a0aec0 !important;
        line-height: 1.7;
        margin-bottom: 1rem;
        font-size: 1rem;
    }
    
    .place-address {
        color: #718096 !important;
        font-size: 0.95rem;
        margin-bottom: 1rem;
        font-style: italic;
    }
    
    /* Itinerary Styles */
    .itinerary-step {
        background: linear-gradient(145deg, #2d3748 0%, #1a202c 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 6px solid #4299e1;
        position: relative;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border: 2px solid #4a5568;
    }
    
    .step-number {
        position: absolute;
        top: -15px;
        left: 25px;
        background: linear-gradient(45deg, #4299e1 0%, #3182ce 100%);
        color: white;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(66, 153, 225, 0.4);
    }
    
    .step-time {
        color: #63b3ed !important;
        font-weight: 700;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    .itinerary-step h4 {
        color: #e2e8f0 !important;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0.5rem 0 !important;
    }
    
    .itinerary-step .place-rating {
        color: #f6ad55 !important;
    }
    
    .itinerary-step .place-desc {
        color: #a0aec0 !important;
    }
    
    .itinerary-step .place-address {
        color: #718096 !important;
    }
    
    /* Stats Section */
    .stats-container {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        border-radius: 20px;
        padding: 3rem;
        color: #e2e8f0;
        text-align: center;
        margin: 3rem 0;
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        border: 2px solid #4a5568;
    }
    
    .stat-item {
        margin: 1.5rem 0;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        display: block;
        color: #e2e8f0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .stat-label {
        font-size: 1.1rem;
        color: #a0aec0 !important;
        opacity: 1;
        font-weight: 500;
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #1a202c 0%, #0d1117 100%);
        color: #e2e8f0 !important;
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin-top: 4rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        border: 2px solid #4a5568;
    }
    
    .footer p {
        color: #e2e8f0 !important;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background-color: #1a365d !important;
        color: #68d391 !important;
        border: 2px solid #38a169 !important;
        border-radius: 10px !important;
    }
    
    .stError {
        background-color: #742a2a !important;
        color: #fc8181 !important;
        border: 2px solid #e53e3e !important;
        border-radius: 10px !important;
    }
    
    .stWarning {
        background-color: #744210 !important;
        color: #f6ad55 !important;
        border: 2px solid #ed8936 !important;
        border-radius: 10px !important;
    }
    
    .stInfo {
        background-color: #1a365d !important;
        color: #63b3ed !important;
        border: 2px solid #4299e1 !important;
        border-radius: 10px !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #2d3748 !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        .hero-title {
            font-size: 2rem;
        }
        .feature-card {
            padding: 1.5rem;
        }
    }
</style>
"""
    else:
        return """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* LIGHT MODE STYLES */
    .stApp {
        font-family: 'Poppins', sans-serif;
        background-color: #ffffff;
        color: #2d3748;
    }
    
    /* Fix Streamlit default text colors */
    .stMarkdown, .stText, p, div, span, h1, h2, h3, h4, h5, h6 {
        color: #2d3748 !important;
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        padding: 2.5rem 0;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 40px rgba(66, 153, 225, 0.3);
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        color: white !important;
    }
    
    .main-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        color: #bee3f8 !important;
        opacity: 1;
    }
    
    /* Navigation Styles */
    .nav-container {
        background: white;
        padding: 1.2rem;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        display: flex;
        justify-content: center;
        gap: 1rem;
    }
    
    /* Fix button text colors */
    .stButton > button {
        background: linear-gradient(45deg, #38a169 0%, #2f855a 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 25px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(56, 161, 105, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(56, 161, 105, 0.4) !important;
        background: linear-gradient(45deg, #2f855a 0%, #276749 100%) !important;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, rgba(66, 153, 225, 0.9), rgba(49, 130, 206, 0.9)), url('https://images.unsplash.com/photo-1488646953014-85cb44e25828?ixlib=rb-4.0.3');
        background-size: cover;
        background-position: center;
        padding: 4rem 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: white !important;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        margin-bottom: 2rem;
        color: #bee3f8 !important;
        opacity: 1;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(145deg, #ffffff 0%, #f7fafc 100%);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease;
        margin: 1rem 0;
        border: 2px solid #e2e8f0;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #2d3748 !important;
        margin-bottom: 1rem;
    }
    
    .feature-desc {
        color: #4a5568 !important;
        line-height: 1.7;
        font-size: 1rem;
    }
    
    /* Form Styles */
    .form-container {
        background: linear-gradient(145deg, #ffffff 0%, #f7fafc 100%);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border: 2px solid #e2e8f0;
    }
    
    .form-title {
        color: #2d3748 !important;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Streamlit input styling */
    .stTextInput > div > div > input {
        background-color: white !important;
        color: #2d3748 !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }
    
    .stSelectbox > div > div > select {
        background-color: white !important;
        color: #2d3748 !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
    }
    
    .stMultiSelect > div > div > div {
        background-color: white !important;
        color: #2d3748 !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
    }
    
    /* Labels */
    .stTextInput > label, .stSelectbox > label, .stMultiSelect > label, .stSlider > label {
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    /* Results Styles */
    .result-card {
        background: linear-gradient(145deg, #ffffff 0%, #f7fafc 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-left: 6px solid #4299e1;
        transition: all 0.3s ease;
        border: 2px solid #e2e8f0;
    }
    
    .result-card:hover {
        transform: translateX(8px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .place-title {
        color: #2d3748 !important;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }
    
    .place-rating {
        color: #ed8936 !important;
        font-weight: 600;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    .place-desc {
        color: #4a5568 !important;
        line-height: 1.7;
        margin-bottom: 1rem;
        font-size: 1rem;
    }
    
    .place-address {
        color: #718096 !important;
        font-size: 0.95rem;
        margin-bottom: 1rem;
        font-style: italic;
    }
    
    /* Itinerary Styles */
    .itinerary-step {
        background: linear-gradient(145deg, #ebf8ff 0%, #bee3f8 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 6px solid #4299e1;
        position: relative;
        box-shadow: 0 8px 25px rgba(66, 153, 225, 0.2);
    }
    
    .step-number {
        position: absolute;
        top: -15px;
        left: 25px;
        background: linear-gradient(45deg, #4299e1 0%, #3182ce 100%);
        color: white;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(66, 153, 225, 0.4);
    }
    
    .step-time {
        color: #2b6cb0 !important;
        font-weight: 700;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    .itinerary-step h4 {
        color: #2d3748 !important;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0.5rem 0 !important;
    }
    
    .itinerary-step .place-rating {
        color: #ed8936 !important;
    }
    
    .itinerary-step .place-desc {
        color: #4a5568 !important;
    }
    
    .itinerary-step .place-address {
        color: #718096 !important;
    }
    
    /* Stats Section */
    .stats-container {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        border-radius: 20px;
        padding: 3rem;
        color: white;
        text-align: center;
        margin: 3rem 0;
        box-shadow: 0 15px 40px rgba(66, 153, 225, 0.3);
    }
    
    .stat-item {
        margin: 1.5rem 0;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        display: block;
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .stat-label {
        font-size: 1.1rem;
        color: #bee3f8 !important;
        opacity: 1;
        font-weight: 500;
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        color: #e2e8f0 !important;
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin-top: 4rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .footer p {
        color: #e2e8f0 !important;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background-color: #f0fff4 !important;
        color: #2f855a !important;
        border: 2px solid #9ae6b4 !important;
        border-radius: 10px !important;
    }
    
    .stError {
        background-color: #fed7d7 !important;
        color: #c53030 !important;
        border: 2px solid #feb2b2 !important;
        border-radius: 10px !important;
    }
    
    .stWarning {
        background-color: #fffbeb !important;
        color: #d69e2e !important;
        border: 2px solid #fbd38d !important;
        border-radius: 10px !important;
    }
    
    .stInfo {
        background-color: #ebf8ff !important;
        color: #2b6cb0 !important;
        border: 2px solid #90cdf4 !important;
        border-radius: 10px !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f7fafc !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        .hero-title {
            font-size: 2rem;
        }
        .feature-card {
            padding: 1.5rem;
        }
    }
</style>
"""

# Apply CSS styles
st.markdown(get_css_styles(st.session_state.dark_mode), unsafe_allow_html=True)

# Navigation function
def set_page(page_name):
    st.session_state.page = page_name
    st.session_state.submitted = False

# Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🌍 WanderWise</h1>
    <p class="main-subtitle">Your AI-Powered Smart Travel Companion</p>
</div>
""", unsafe_allow_html=True)

# Dark mode toggle
col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
with col6:
    if st.button("🌙" if not st.session_state.dark_mode else "☀️", key="dark_mode_toggle", help="Toggle dark/light mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Navigation
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🏠 Home", key="nav_home"):
        set_page('home')

with col2:
    if st.button("🗺️ Plan Trip", key="nav_plan"):
        set_page('planner')

with col3:
    if st.button("📍 Recommendations", key="nav_recommendations"):
        set_page('recommendations')

with col4:
    if st.button("💡 About", key="nav_about"):
        set_page('about')

with col5:
    if st.button("📞 Contact", key="nav_contact"):
        set_page('contact')

# Page Content
if st.session_state.page == 'home':
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h2 class="hero-title">Discover Your Perfect Journey</h2>
        <p class="hero-subtitle">Plan personalized trips based on your mood, budget, and time preferences</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🎯</span>
            <h3 class="feature-title">Smart Recommendations</h3>
            <p class="feature-desc">Get personalized suggestions based on your mood, budget, and available time using advanced AI algorithms.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🗺️</span>
            <h3 class="feature-title">Interactive Maps</h3>
            <p class="feature-desc">Visualize your journey with interactive maps, complete routes, and detailed location information.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">⏰</span>
            <h3 class="feature-title">Time-Optimized Itineraries</h3>
            <p class="feature-desc">Create efficient travel schedules that maximize your experience within your available time.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Stats Section
    st.markdown("""
    <div class="stats-container">
        <div class="row">
            <div class="col">
                <div class="stat-item">
                    <span class="stat-number">10K+</span>
                    <span class="stat-label">Happy Travelers</span>
                </div>
            </div>
            <div class="col">
                <div class="stat-item">
                    <span class="stat-number">500+</span>
                    <span class="stat-label">Cities Covered</span>
                </div>
            </div>
            <div class="col">
                <div class="stat-item">
                    <span class="stat-number">50K+</span>
                    <span class="stat-label">Places Recommended</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Call to Action
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
        if st.button("🚀 Start Planning Your Trip", key="cta_button", help="Click to begin your journey"):
            set_page('planner')
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == 'planner':
    st.markdown("""
    <div class="form-container">
        <h2 class="form-title">🎯 Plan Your Perfect Trip</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Create form layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📍 Destination Details")
        user_text = st.text_input("🏙️ Enter City or Place Name", value="Ahmedabad", help="Enter the city you want to explore")
        
        st.markdown("### 🎭 Your Mood")
        moods = st.multiselect(
            "What kind of experience are you looking for?",
            ["Family", "Relaxing", "Casual", "Romantic", "Cultural", "Spiritual",
             "Nature", "Relaxation", "Adventure", "Shopping", "Educational", "History", "Industrial"],
            default=["Relaxing"],
            help="Select all moods that match your travel preferences"
        )
        
        st.markdown("### 💰 Budget Range")
        budget = st.selectbox(
            "What's your spending preference?",
            options=["Free", "Regular", "Moderate", "Premium"],
            index=1,
            help="Choose your budget range for activities and dining"
        )
        
        st.markdown("### ⏰ Time Available")
        hours = st.slider("How many hours do you have?", 1, 12, 4, help="Total time available for your trip")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🎯 Get My Recommendations", key="get_recommendations", help="Generate personalized recommendations"):
            st.session_state.submitted = True
    
    with col2:
        if st.session_state.submitted:
            with st.spinner("🔮 Creating your perfect itinerary..."):
                # Simulate loading time for better UX
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.003)  # 0.003 for faster UI
                    progress_bar.progress(i + 1)
                
                try:
                    geolocator = Nominatim(user_agent="wanderwise_app")
                    location = geolocator.geocode(user_text)
                    
                    if location is None:
                        st.error("❌ Could not find location. Please enter a valid city name.")
                    else:
                        coords = (location.latitude, location.longitude)
                        tourist_df, food_df = recommend_places(
                            user_text=user_text,
                            location_coords=coords,
                            moods=moods,
                            budget={"Free": 0, "Regular": 300, "Moderate": 500, "Premium": 800}[budget],
                            time_hr=hours
                        )
                        
                        st.success("✅ Your personalized itinerary is ready!")
                        
                        if tourist_df.empty and food_df.empty:
                            st.warning("😲 No recommendations found. Try adjusting your preferences.")
                        else:
                            # Display itinerary
                            itinerary = create_itinerary(coords, tourist_df, food_df, total_time_hr=hours)
                            
                            st.markdown("### 🗓️ Your Personalized Itinerary")
                            
                            for i, step in enumerate(itinerary):
                                icon = "🌟" if step["type"] == "place" else "🍽️"
                                
                                st.markdown(f"""
                                <div class="itinerary-step">
                                    <div class="step-number">{i+1}</div>
                                    <h4>{icon} {step['name']}</h4>
                                    <div class="step-time">📅 Arrival: {step['arrival'].strftime('%I:%M %p')} | ⏱️ Duration: {step['stay_duration_hr']} hour(s)</div>
                                    <div class="place-rating">⭐ {step['rating']} ({step['reviews']} reviews)</div>
                                    <div class="place-desc">{step.get('desc', step.get('description', 'No description available'))}</div>
                                    <div class="place-address">📍 {step.get('address', 'Address not available')}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                maps_url = f"https://www.google.com/maps/dir/?api=1&origin={coords[0]},{coords[1]}&destination={step['lat']},{step['lng']}&travelmode=driving"
                                st.markdown(
                                    f"""
                                    <a href="{maps_url}" target="_blank">
                                    <button style="padding:6px 12px; background-color:#0254b3; color:white; border:none; border-radius:6px;">
                                        🧭 Get Directions to {step['name']}
                                    </button>
                                    </a>
                                    """,
                                    unsafe_allow_html=True
                                )


                            # Add complete route with all stops
                            if itinerary:
                                # Build Google Maps route with multiple stops
                                origin = f"{coords[0]},{coords[1]}"
                                destination = f"{itinerary[-1]['lat']},{itinerary[-1]['lng']}"

                                # Add all intermediate stops except the last one
                                waypoints = [
                                    f"{step['lat']},{step['lng']}"
                                    for step in itinerary[:-1]
                                ]
                                # Construct route link
                                maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode=driving"
                                if waypoints:
                                    maps_url += "&waypoints=" + "|".join(waypoints)

                                st.markdown("### 🗺️ Complete Route with All Stops")
                                st.markdown(f"[🚗 View Complete Route on Google Maps]({maps_url})", unsafe_allow_html=True)
                                st.markdown("---")
                
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.info("Please check if your backend functions are working correctly.")
        
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #666;">
                <h3>👈 Fill in your preferences</h3>
                <p>Complete the form on the left to get your personalized travel recommendations</p>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == 'recommendations':
    st.markdown("""
    <div class="form-container">
        <h2 class="form-title">🗺️ Smart Travel Recommendations</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Create form layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📍 Destination Details")
        user_text = st.text_input("🏙️ Enter City or Place Name", value="Ahmedabad", help="Enter the city you want to explore", key="rec_city")
        
        st.markdown("### 🎭 Your Mood")
        moods = st.multiselect(
            "What kind of experience are you looking for?",
            ["Family", "Relaxing", "Casual", "Romantic", "Cultural", "Spiritual",
             "Nature", "Relaxation", "Adventure", "Shopping", "Educational", "History", "Industrial"],
            default=["Relaxing"],
            help="Select all moods that match your travel preferences",
            key="rec_moods"
        )
        
        st.markdown("### 💰 Budget Range")
        budget = st.selectbox(
            "What's your spending preference?",
            options=["Free", "Regular", "Moderate", "Premium"],
            index=1,
            help="Choose your budget range for activities and dining",
            key="rec_budget"
        )
        
        st.markdown("### ⏰ Time Available")
        hours = st.slider("How many hours do you have?", 1, 12, 4, help="Total time available for your trip", key="rec_hours")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🎯 Get Recommendations", key="get_rec_recommendations", help="Generate personalized recommendations"):
            st.session_state.rec_submitted = True
    
    with col2:
        if st.session_state.rec_submitted:
            with st.spinner("🔮 Finding amazing places for you..."):
                # Simulate loading time for better UX
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.003)
                    progress_bar.progress(i + 1)
                
                try:
                    geolocator = Nominatim(user_agent="wanderwise_app")
                    location = geolocator.geocode(user_text)
                    
                    if location is None:
                        st.error("❌ Could not find location. Please enter a valid city name.")
                    else:
                        coords = (location.latitude, location.longitude)
                        tourist_df, food_df = recommend_places(
                            user_text=user_text,
                            location_coords=coords,
                            moods=moods,
                            budget={"Free": 0, "Regular": 300, "Moderate": 500, "Premium": 800}[budget],
                            time_hr=hours
                        )
                        
                        st.success("✅ Found amazing places for you!")
                        
                        if tourist_df.empty and food_df.empty:
                            st.warning("😲 No recommendations found. Try adjusting your preferences.")
                        else:
                            st.markdown(f"### 📍 Recommended Places in **{user_text}**")
                            
                            # Display tourist attractions
                            if not tourist_df.empty:
                                st.markdown("### 🌟 Tourist Attractions")
                                for _, row in tourist_df.iterrows():
                                    st.markdown(f"""
                                    <div class="result-card">
                                        <h4 class="place-title">📌 {row['name']}</h4>
                                        <div class="place-rating">⭐ {row['rating']} ({row['reviews']} reviews)</div>
                                        <div class="place-desc">{row.get('description', 'No description available')}</div>
                                        <div class="place-address">📍 {row.get('address', 'Address not available')}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    maps_url = f"https://www.google.com/maps/dir/?api=1&origin={coords[0]},{coords[1]}&destination={row['lat']},{row['lng']}&travelmode=driving"
                                    st.markdown(f"<a href='{maps_url}' target='_blank'><button style='padding:6px 12px; background-color:#0254b3; color:white; border:none; border-radius:6px;'>🧭 Get Directions to {row['name']}</button></a>", unsafe_allow_html=True)

                            
                            # Display food places
                            if not food_df.empty:
                                st.markdown("### 🍽️ Food & Cafes")
                                for _, row in food_df.iterrows():
                                    st.markdown(f"""
                                    <div class="result-card">
                                        <h4 class="place-title">🍽️ {row['name']}</h4>
                                        <div class="place-rating">⭐ {row['rating']} ({row['reviews']} reviews)</div>
                                        <div class="place-desc">{row.get('description', 'No description available')}</div>
                                        <div class="place-address">📍 {row.get('address', 'Address not available')}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    maps_url = f"https://www.google.com/maps/dir/?api=1&origin={coords[0]},{coords[1]}&destination={row['lat']},{row['lng']}&travelmode=driving"
                                    st.markdown(f"<a href='{maps_url}' target='_blank'><button style='padding:6px 12px; background-color:#0254b3; color:white; border:none; border-radius:6px;'>🧭 Get Directions to {row['name']}</button></a>", unsafe_allow_html=True)


                            # Display interactive map
                            st.markdown("### 🗺️ Interactive Map")
                            m = folium.Map(location=coords, zoom_start=12)
                            cluster = MarkerCluster().add_to(m)
                            
                            # Add tourist attractions to map
                            if not tourist_df.empty:
                                for _, row in tourist_df.iterrows():
                                    popup = f"""
                                    <b>{row['name']}</b><br>
                                    <b>Type:</b> {row.get('type', 'Tourist Attraction')}<br>
                                    <b>Rating:</b> ⭐ {row['rating']} ({row['reviews']} reviews)<br>
                                    <b>Description:</b> {row.get('description', 'No description available')}<br>
                                    <b>Address:</b> {row.get('address', 'Address not available')}<br>
                                    <a href='https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lng']}' target='_blank'>View on Google Maps</a>
                                    """
                                    folium.Marker(location=(row['lat'], row['lng']),
                                                  popup=folium.Popup(popup, max_width=300),
                                                  icon=folium.Icon(color='green')).add_to(cluster)
                            
                            # Add food places to map
                            if not food_df.empty:
                                for _, row in food_df.iterrows():
                                    popup = f"""
                                    <b>{row['name']}</b><br>
                                    <b>Type:</b> {row.get('type', 'Food & Dining')}<br>
                                    <b>Rating:</b> ⭐ {row['rating']} ({row['reviews']} reviews)<br>
                                    <b>Description:</b> {row.get('description', 'No description available')}<br>
                                    <b>Address:</b> {row.get('address', 'Address not available')}<br>
                                    <a href='https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lng']}' target='_blank'>View on Google Maps</a>
                                    """
                                    folium.Marker(location=(row['lat'], row['lng']),
                                                  popup=folium.Popup(popup, max_width=300),
                                                  icon=folium.Icon(color='orange')).add_to(cluster)
                            
                            st_folium(m, width=1100, height=600)
                
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    st.info("Please check if your backend functions are working correctly.")
        
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #6b7280;">
                <h3>👈 Set your preferences</h3>
                <p>Complete the form on the left to discover amazing places based on your mood and preferences</p>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == 'about':
    st.markdown("""
    <div class="form-container">
        <h2 class="form-title">💡 About WanderWise</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🌟 Our Mission
        WanderWise is designed to revolutionize how you plan and experience travel. We believe that every journey should be perfectly tailored to your preferences, mood, and constraints.
        
        ### 🚀 What Makes Us Different
        - **AI-Powered Recommendations**: Our advanced algorithms analyze your preferences to suggest the perfect places
        - **Mood-Based Planning**: Travel experiences that match your current mood and desires
        - **Time-Optimized Routes**: Make the most of your available time with efficient itineraries
        - **Budget-Conscious**: Recommendations that fit your budget without compromising on experience
        """)
    
    with col2:
        st.markdown("""
        ### 🔧 How It Works
        1. **Tell Us About You**: Share your destination, mood, budget, and available time
        2. **AI Analysis**: Our system processes thousands of data points to find perfect matches
        3. **Get Recommendations**: Receive a personalized itinerary with detailed information
        4. **Explore & Navigate**: Use interactive maps and direct links to plan your route
        
        ### 📊 Our Impact
        - Helped 10,000+ travelers discover new experiences
        - Covers 500+ cities worldwide
        - 50,000+ curated recommendations
        """)

elif st.session_state.page == 'contact':
    st.markdown("""
    <div class="form-container">
        <h2 class="form-title">📞 Get In Touch</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💌 Send Us a Message")
        
        with st.form("contact_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Email Address")
            subject = st.selectbox("Subject", ["General Inquiry", "Technical Support", "Feature Request", "Bug Report", "Partnership"])
            message = st.text_area("Your Message", height=150)
            
            submitted = st.form_submit_button("Send Message")
            
            if submitted:
                st.success("✅ Thank you for your message! We'll get back to you soon.")
    
    with col2:
        st.markdown("""
        ### 🌐 Connect With Us
        
        **📧 Email:** support@wanderwise.com
        
        **📱 Phone:** +1 (555) 123-4567
        
        **🏢 Address:**
        123 Travel Street
        Adventure City, AC 12345
        
        **🕒 Support Hours:**
        Monday - Friday: 9 AM - 6 PM
        Saturday - Sunday: 10 AM - 4 PM
        
        ### 🔗 Follow Us
        - 🐦 Twitter: @WanderWiseAI
        - 📘 Facebook: WanderWise Travel
        - 📸 Instagram: @wanderwise_travel
        - 💼 LinkedIn: WanderWise
        """)

# Footer
st.markdown("""
<div class="footer">
    <p>© 2025 WanderWise - Your AI-Powered Smart Travel Companion</p>
    <p>Made with ❤️ for travelers around the world</p>
</div>
""", unsafe_allow_html=True)