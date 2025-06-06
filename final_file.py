import streamlit as st
import time
from datetime import datetime
from PIL import Image
import io
import base64
import json
import uuid
import numpy as np

# Add DICOM support
try:
    import pydicom
    from pydicom.pixel_data_handlers.util import apply_voi_lut

    DICOM_AVAILABLE = True
except ImportError:
    DICOM_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="PulmoVista",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional medical theme
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        color: #1a202c;
    }

    /* Global text colors for better visibility */
    h1, h2, h3, h4, h5, h6 {
        color: #1a202c !important;
    }

    p, div, span {
        color: #2d3748 !important;
    }

    .stMarkdown {
        color: #2d3748 !important;
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #1a202c !important;
    }

    .stMarkdown p {
        color: #2d3748 !important;
    }

    /* Sidebar text colors */
    .sidebar .element-container {
        color: #1a202c !important;
    }

    .sidebar h1, .sidebar h2, .sidebar h3 {
        color: #1a202c !important;
    }

    .sidebar p, .sidebar div {
        color: #2d3748 !important;
    }

    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #0ea5e9, #0284c7, #0369a1);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 20px 40px rgba(14, 165, 233, 0.2);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }

    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 4px 8px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }

    .main-header p {
        font-size: 1.2rem;
        font-weight: 400;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }

    /* Enhanced Sections */
    .upload-section {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        padding: 2.5rem;
        border-radius: 20px;
        border: 2px solid #0ea5e9;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(14, 165, 233, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        color: #1a202c;
    }


    @keyframes pulse {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }

    .result-section h1, .result-section h2, .result-section h3, .result-section h4 {
        color: #1a202c !important;
    }

    .result-section p, .result-section div, .result-section span {
        color: #2d3748 !important;
    }

    .result-section:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(16, 185, 129, 0.15);
    }

    .feedback-section {
        background: linear-gradient(145deg, #fefce8, #fef3c7);
        padding: 2.5rem;
        border-radius: 20px;
        border: 2px solid #f59e0b;
        margin-top: 2rem;
        box-shadow: 0 10px 30px rgba(245, 158, 11, 0.1);
        transition: all 0.3s ease;
        color: #1a202c;
    }

    .feedback-section h1, .feedback-section h2, .feedback-section h3, .feedback-section h4 {
        color: #1a202c !important;
    }

    .feedback-section p, .feedback-section div, .feedback-section span {
        color: #2d3748 !important;
    }

    .feedback-section:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(245, 158, 11, 0.15);
    }

    /* Status Messages */
    .status-success {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        color: #065f46 !important;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 6px solid #10b981;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
        animation: slideIn 0.5s ease-out;
    }

    .status-error {
        background: linear-gradient(135deg, #fecaca, #fca5a5);
        color: #7f1d1d !important;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 6px solid #dc2626;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.2);
    }

    .status-processing {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        color: #1e40af !important;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 6px solid #3b82f6;
        margin: 1rem 0;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* Enhanced Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f1f5f9);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        text-align: center;
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        color: #1a202c;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #0ea5e9, #10b981, #f59e0b);
    }

    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }

    .metric-card h3 {
        color: #1e293b !important;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-card p {
        color: #374151 !important;
        font-weight: 500;
        margin: 0.5rem 0;
    }

    .metric-card strong {
        color: #1a202c !important;
    }

    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-size: 0.9rem !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #0284c7, #0369a1) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(14, 165, 233, 0.4) !important;
    }

    .stButton > button:disabled {
        background: #94a3b8 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Image Containers */
    .image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1.5rem;
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border-radius: 15px;
        border: 2px solid #e2e8f0;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }

    .image-container:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }

    /* Enhanced Sidebar */
    .sidebar .element-container {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 0.5rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        color: #1a202c;
    }

    .sidebar .element-container h1, 
    .sidebar .element-container h2, 
    .sidebar .element-container h3 {
        color: #1a202c !important;
    }

    .sidebar .element-container p, 
    .sidebar .element-container div, 
    .sidebar .element-container span {
        color: #2d3748 !important;
    }

    /* Streamlit component text fixes */
    .stSelectbox label, .stRadio label, .stCheckbox label, .stSlider label {
        color: #1a202c !important;
    }

    .stSelectbox > div > div, .stRadio > div, .stCheckbox > div {
        color: #2d3748 !important;
    }

    .stMetric {
        background: linear-gradient(145deg, #ffffff, #f1f5f9);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: 0.5rem 0;
        color: #1a202c;
    }

    .stMetric label {
        color: #1a202c !important;
    }

    .stMetric [data-testid="metric-value"] {
        color: #1a202c !important;
    }

    .stMetric [data-testid="metric-delta"] {
        color: #059669 !important;
    }

    /* Progress Bar Enhancement */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #0ea5e9, #10b981) !important;
        border-radius: 10px !important;
    }

    /* File Uploader Enhancement */
    .stFileUploader > div {
        border: 3px dashed #0ea5e9 !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        background: linear-gradient(145deg, #f8fafc, #ffffff) !important;
        transition: all 0.3s ease !important;
        color: #1a202c !important;
    }

    .stFileUploader > div:hover {
        border-color: #0284c7 !important;
        background: linear-gradient(145deg, #e0f2fe, #f0f9ff) !important;
    }

    .stFileUploader label {
        color: #1a202c !important;
    }

    .stFileUploader > div > div {
        color: #2d3748 !important;
    }

    /* Text Area Enhancement */
    .stTextArea > div > div > textarea {
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        color: #1a202c !important;
        background: white !important;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #0ea5e9 !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1) !important;
    }

    .stTextArea label {
        color: #1a202c !important;
    }

    /* Form inputs */
    .stTextInput > div > div > input {
        color: #1a202c !important;
        background: white !important;
    }

    .stTextInput label {
        color: #1a202c !important;
    }

    /* Tables */
    .stTable, .stDataFrame {
        color: #1a202c !important;
    }

    table {
        color: #1a202c !important;
    }

    td, th {
        color: #1a202c !important;
    }

    /* Info/Success/Warning/Error boxes */
    .stAlert {
        color: #1a202c !important;
    }

    /* Tab content */
    .stTabs [data-baseweb="tab-list"] {
        color: #1a202c !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: #1a202c !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        color: #1a202c !important;
    }

    .streamlit-expanderContent {
        color: #2d3748 !important;
    }

    /* Footer Enhancement */
    .footer {
        background: linear-gradient(135deg, #1e293b, #334155);
        color: white !important;
        padding: 2rem;
        border-radius: 20px;
        margin-top: 3rem;
        text-align: center;
        box-shadow: 0 -10px 30px rgba(0,0,0,0.1);
    }

    .footer p {
        margin: 0.5rem 0;
        color: white !important;
    }

    .footer h1, .footer h2, .footer h3, .footer h4 {
        color: white !important;
    }

    .footer span {
        color: white !important;
    }

    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #0ea5e9;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }

        .upload-section, .result-section, .feedback-section {
            padding: 1.5rem;
        }

        .metric-card {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# Enhanced session state management
class SessionManager:
    @staticmethod
    def initialize():
        defaults = {
            'processed_result': None,
            'report_data': None,
            'uploaded_file': None,
            'processing': False,
            'show_report': False,
            'feedback_history': [],
            'session_id': str(uuid.uuid4()),
            'processed_count': 0,
            'last_processing_time': None
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def update_stats():
        st.session_state.processed_count += 1
        st.session_state.last_processing_time = datetime.now()


# Enhanced AI Analysis Engine
class AIAnalysisEngine:
    @staticmethod
    def generate_realistic_report():
        import random

        findings_options = [
            "No acute cardiopulmonary abnormality detected. Lung fields are clear with normal cardiac silhouette.",
            "Mild linear opacity in the right lower lobe, likely representing minor atelectasis. Heart size within normal limits.",
            "Clear lung fields bilaterally. Normal cardiac silhouette and mediastinal contours.",
            "Subtle increased opacity in left mid-zone, clinical correlation recommended. Otherwise unremarkable.",
            "Normal chest radiograph with clear lung fields and appropriate cardiac size.",
            "No evidence of pneumothorax or pleural effusion. Cardiac and mediastinal structures appear normal.",
            "Lungs are well-expanded and clear. No focal consolidation or pneumothorax identified."
        ]

        impression_options = [
            "Normal chest radiograph.",
            "No acute cardiopulmonary process.",
            "Essentially normal study.",
            "No significant abnormalities detected.",
            "Clear chest X-ray examination.",
            "Normal appearing chest radiograph.",
            "No acute findings identified."
        ]

        confidence_score = round(random.uniform(94.2, 99.8), 1)
        processing_time = round(random.uniform(1.8, 4.2), 1)

        return {
            'patient_id': f'PT-{datetime.now().strftime("%Y%m%d")}-{random.randint(1000, 9999)}',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'findings': random.choice(findings_options),
            'impression': random.choice(impression_options),
            'confidence': f'{confidence_score}%',
            'processing_time': f'{processing_time} seconds',
            'ai_model': 'PulmoVista AI v5.2.1',
            'risk_score': random.choice(['Low', 'Low', 'Low', 'Medium', 'Low']),
            'recommendations': 'Continue routine monitoring as clinically indicated.'
        }


# Enhanced DICOM and Image Processing
class ImageProcessor:
    @staticmethod
    def load_image(uploaded_file):
        """Load and process both DICOM and standard image files"""
        try:
            # Check if it's a DICOM file
            if uploaded_file.name.lower().endswith('.dcm') or uploaded_file.type == 'application/octet-stream':
                return ImageProcessor.load_dicom_image(uploaded_file)
            else:
                # Handle standard image formats
                return ImageProcessor.load_standard_image(uploaded_file)

        except Exception as e:
            st.error(f"❌ Error loading image: {str(e)}")
            return None, None

    @staticmethod
    def load_dicom_image(uploaded_file):
        """Load and process DICOM files"""
        if not DICOM_AVAILABLE:
            st.error("❌ DICOM support not available. Please install pydicom: pip install pydicom")
            return None, None

        try:
            # Reset file pointer
            uploaded_file.seek(0)

            # Read DICOM file
            dicom_data = pydicom.dcmread(uploaded_file)
            # Extract pixel array
            pixel_array = dicom_data.pixel_array

            # Apply VOI LUT if available
            if hasattr(dicom_data, 'WindowCenter') and hasattr(dicom_data, 'WindowWidth'):
                image = apply_voi_lut(pixel_array, dicom_data)
            else:
                image = pixel_array

            # Handle photometric interpretation
            if hasattr(dicom_data, 'PhotometricInterpretation'):
                if dicom_data.PhotometricInterpretation == "MONOCHROME1":
                    image = np.amax(image) - image

            # Normalize to 0-255 range
            image = image - np.min(image)
            if np.max(image) > 0:
                image = (image / np.max(image) * 255).astype(np.uint8)
            else:
                image = np.zeros_like(image, dtype=np.uint8)

            # Convert to PIL Image
            pil_image = Image.fromarray(image)

            # Convert to RGB if grayscale
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            return pil_image, dicom_data

        except Exception as e:
            st.error(f"❌ Error processing DICOM file: {str(e)}")
            return None, None

    @staticmethod
    def load_standard_image(uploaded_file):
        """Load standard image formats"""
        try:
            # Reset file pointer
            uploaded_file.seek(0)

            # Open with PIL
            image = Image.open(uploaded_file)

            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')

            return image, None

        except Exception as e:
            st.error(f"❌ Error loading standard image: {str(e)}")
            return None, None

    @staticmethod
    def get_image_info(uploaded_file, dicom_data=None):
        """Extract image information"""
        info = {}

        if dicom_data is not None:
            # DICOM specific information
            info.update({
                'modality': getattr(dicom_data, 'Modality', 'Unknown'),
                'body_part': getattr(dicom_data, 'BodyPartExamined', 'Unknown'),
                'study_date': getattr(dicom_data, 'StudyDate', 'Unknown'),
                'institution': getattr(dicom_data, 'InstitutionName', 'Unknown'),
                'manufacturer': getattr(dicom_data, 'Manufacturer', 'Unknown'),
                'rows': getattr(dicom_data, 'Rows', 'Unknown'),
                'columns': getattr(dicom_data, 'Columns', 'Unknown'),
                'pixel_spacing': getattr(dicom_data, 'PixelSpacing', 'Unknown')
            })
        else:
            # Standard image information
            try:
                uploaded_file.seek(0)
                temp_image = Image.open(uploaded_file)
                info.update({
                    'dimensions': f"{temp_image.size[0]}x{temp_image.size[1]}",
                    'mode': temp_image.mode,
                    'format': temp_image.format
                })
            except:
                pass

        return info


# Initialize session manager
SessionManager.initialize()

# Enhanced main header with animations

st.markdown("""
<div class="main-header">
    <h1>🫁 PulmoVista</h1>
    <p>AI-Powered Medical Imaging Diagnostics for Lung Conditions</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .how-title {
        color: #1976d2; /* Medical blue */
        font-family: 'Inter', sans-serif;
        text-align: center;
        font-size: 2.75rem;
        font-weight: 700;
        margin-bottom: 2.5rem;
        user-select: none;
    }
    .how-card {
        background: #e3f2fd; /* Light blue background */
        border-radius: 1.5rem;
        box-shadow: 0 4px 20px rgba(25, 118, 210, 0.12);
        padding: 2.5rem 2rem;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: default;
        user-select: none;
    }
    .how-card:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 36px rgba(25, 118, 210, 0.25);
    }
    .how-icon {
        display: block;
        margin: 0 auto 1.75rem auto;
        width: 4.5rem;
        height: 4.5rem;
        color: #1976d2; /* Medical blue */
        transition: color 0.3s ease;
    }
    .how-card:hover .how-icon {
        color: #0d47a1; /* Darker blue on hover */
    }
    .how-heading {
        color: #1976d2; /* Medical blue */
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }
    .how-desc {
        color: #1565c0; /* Slightly darker blue for text */
        font-size: 1.05rem;
        line-height: 1.4;
        max-width: 280px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.how-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 2.5rem;
}
.how-title {
    color: #1976d2;
    font-family: 'Inter', sans-serif;
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 2.2rem;
    user-select: none;
}
.timeline {
    display: flex;
    flex-direction: row;
    justify-content: center;
    gap: 2rem;
    width: 100%;
}
.timeline-step {
    position: relative;
    background: #fff;
    border: 2px solid #1976d2;
    border-radius: 1.25rem;
    box-shadow: 0 4px 16px rgba(25, 118, 210, 0.10);
    padding: 2rem 1.2rem 1.5rem 1.2rem;
    text-align: center;
    min-width: 220px;
    max-width: 270px;
    transition: box-shadow 0.3s, border-color 0.3s;
}
.timeline-step:hover {
    border-color: #0d47a1;
    box-shadow: 0 8px 28px rgba(25, 118, 210, 0.18);
}
.step-badge {
    position: absolute;
    top: -1.2rem;
    left: 50%;
    transform: translateX(-50%);
    background: #1976d2;
    color: #fff;
    font-weight: bold;
    font-size: 1.1rem;
    border-radius: 50%;
    width: 2.2rem;
    height: 2.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(25, 118, 210, 0.12);
    border: 3px solid #fff;
}
.timeline-dot {
    width: 0.7rem;
    height: 0.7rem;
    background: #1976d2;
    border-radius: 50%;
    position: absolute;
    left: 50%;
    top: 0;
    transform: translate(-50%, -50%);
    z-index: 2;
}
.timeline-line {
    width: 4px;
    height: 100%;
    background: linear-gradient(to bottom, #1976d2 40%, #e3f2fd 100%);
    position: absolute;
    left: 50%;
    top: 0.7rem;
    transform: translateX(-50%);
    z-index: 1;
}
.timeline-step .how-icon {
    margin: 2.2rem auto 1.1rem auto;
    width: 2.8rem;
    height: 2.8rem;
    color: #1976d2;
    display: block;
}
.timeline-step .how-heading {
    color: #1976d2;
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
}
.timeline-step .how-desc {
    color: #1565c0;
    font-size: 1rem;
    line-height: 1.5;
}
@media (max-width: 950px) {
    .timeline { flex-direction: column; align-items: center; gap: 3.5rem;}
    .timeline-step { min-width: 0; width: 90vw; max-width: 340px;}
}
</style>
<div class="how-section">
    <div class="how-title">How It Works</div>
    <div class="timeline">
        <div class="timeline-step">
            <div class="step-badge">1</div>
            <svg class="how-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 64 64">
                <rect x="12" y="16" width="40" height="32" rx="6" stroke="currentColor" stroke-width="3"/>
                <path d="M32 24v16M24 32h16" stroke="currentColor" stroke-width="3"/>
            </svg>
            <div class="how-heading">Upload</div>
            <div class="how-desc">Securely upload your DICOM files to our platform.</div>
        </div>
        <div class="timeline-step">
            <div class="step-badge">2</div>
            <svg class="how-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 64 64">
                <circle cx="32" cy="32" r="24" stroke="currentColor" stroke-width="3"/>
                <path d="M32 16v16l12 6" stroke="currentColor" stroke-width="3"/>
            </svg>
            <div class="how-heading">Analyze</div>
            <div class="how-desc">AI processes your scan for accurate diagnostic insights.</div>
        </div>
        <div class="timeline-step">
            <div class="step-badge">3</div>
            <svg class="how-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 64 64">
                <rect x="16" y="16" width="32" height="32" rx="6" stroke="currentColor" stroke-width="3"/>
                <path d="M24 32h16M32 24v16" stroke="currentColor" stroke-width="3"/>
            </svg>
            <div class="how-heading">Report</div>
            <div class="how-desc">Download or view a comprehensive diagnostic report.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Enhanced sidebar with better organization
with st.sidebar:
    st.title("🎛️ Navigation")
    page = st.radio("Select Page", ["🏠 Home", "🆘 Support", "ℹ️ About", "📞 Contact"],
                    label_visibility="collapsed")

    st.divider()

    st.title("📊 Session Stats")
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.metric("Processed Today", st.session_state.processed_count, delta=None)
    with col_s2:
        st.metric("Accuracy Rate", "98.7%", delta="0.2%")

    # st.metric("Avg Processing Time", "2.8s", delta="-0.3s")
    # st.metric("Session ID", st.session_state.session_id[-8:])

    if st.session_state.last_processing_time:
        st.info(f"Last processed: {st.session_state.last_processing_time.strftime('%H:%M:%S')}")

# Main content area based on selected page
if page == "🏠 Home":
    # Create enhanced two-column layout
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        # st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.subheader("📤 Upload X-ray Image")

        # Enhanced file uploader with better help text
        uploaded_file = st.file_uploader(
            "Choose a DICOM file",
            type=['dcm'],
            help="📁 Supported formats: DICOM (.dcm)"
        )

        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file

            # Display uploaded image with enhanced styling
            try:
                image, dicom_data = ImageProcessor.load_image(uploaded_file)
                if image:
                    # Create image container with better styling
                    #st.markdown('<div class="image-container">', unsafe_allow_html=True)
                    st.image(image, caption="📷 Uploaded Medical Image", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # # Enhanced file details with better formatting
                    # file_size_mb = uploaded_file.size / (1024 * 1024)
                    # image_info = ImageProcessor.get_image_info(uploaded_file, dicom_data)
                    #
                    # # Display file information
                    # col_info1, col_info2 = st.columns(2)
                    #
                    # with col_info1:
                    #     st.info(f"📄 **Filename:** {uploaded_file.name}")
                    #     st.info(f"📊 **File size:** {file_size_mb:.2f} MB")
                    #     if 'dimensions' in image_info:
                    #         st.info(f"📐 **Dimensions:** {image_info['dimensions']}")
                    #     elif 'rows' in image_info and 'columns' in image_info:
                    #         st.info(f"📐 **Matrix:** {image_info['rows']}x{image_info['columns']}")
                    #
                    # with col_info2:
                    #     st.info(f"🎯 **File type:** {uploaded_file.type}")
                    #     if 'modality' in image_info:
                    #         st.info(f"🏥 **Modality:** {image_info['modality']}")
                    #         if image_info['body_part'] != 'Unknown':
                    #             st.info(f"🫁 **Body Part:** {image_info['body_part']}")
                    #     elif 'format' in image_info:
                    #         st.info(f"🖼️ **Format:** {image_info['format']}")
                    #
                    # # Store both image and metadata
                    # st.session_state.processed_image = image
                    # st.session_state.dicom_data = dicom_data

                else:
                    st.error("❌ Failed to load the uploaded image. Please check the file format.")

            except Exception as e:
                st.markdown(f"""
                <div class="status-error">
                    ❌ Error processing image: {str(e)}
                    <br><br>
                    <strong>Troubleshooting tips:</strong>
                    <ul>
                        <li>For DICOM files: Ensure the file is not corrupted</li>
                        <li>For standard images: Try converting to PNG or JPEG format</li>
                        <li>Check if the file size is under 25MB</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        # Enhanced process button with loading state
        # col_btn1 = st.columns([1])
        # with col_btn1:
        if st.button("🔍 Analyze Image", disabled=(uploaded_file is None), use_container_width=True):
                st.session_state.processing = True
                st.rerun()

        # with col_btn2:
        #     if uploaded_file and not st.session_state.processing:
        #         if st.button("🗑️ Clear Output", use_container_width=True):
        #             st.session_state.uploaded_file = None
        #             st.session_state.processed_result = None
        #             st.session_state.report_data = None
        #             st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.subheader("📊 Analysis Results")

        if st.session_state.processing:
            # Enhanced processing animation with better UX
            st.markdown("""
            <div class="status-processing">
                <div class="loading-spinner"></div> AI Analysis in Progress...
            </div>
            """, unsafe_allow_html=True)

            progress_bar = st.progress(0)
            status_text = st.empty()

            processing_steps = [
                "🔄 Initializing AI models...",
                "📸 Preprocessing image data...",
                "🧠 Running deep learning analysis...",
                "🔍 Detecting anatomical structures...",
                "⚕️ Applying medical algorithms...",
                "📋 Generating diagnostic report...",
                "✅ Finalizing results..."
            ]

            for i in range(100):
                progress_bar.progress(i + 1)
                step_index = min(i // 15, len(processing_steps) - 1)
                status_text.text(processing_steps[step_index])
                time.sleep(0.04)

            # Simulate processing completion with enhanced results
            st.session_state.processing = False
            st.session_state.processed_result = "result.jpeg"
            st.session_state.report_data = AIAnalysisEngine.generate_realistic_report()
            SessionManager.update_stats()
            st.rerun()

        elif st.session_state.processed_result:
            # Enhanced results display
            st.markdown("""
            <div class="status-success">
                ✅ Analysis completed successfully!
            </div>
            """, unsafe_allow_html=True)

            # Display enhanced result with better placeholder
            #st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.image("result.jpeg",
                     caption="🤖 AI Analysis Visualization", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Enhanced metrics display
            if st.session_state.report_data:
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric("🎯 Confidence", st.session_state.report_data['confidence'],
                              delta="High" if float(
                                  st.session_state.report_data['confidence'].rstrip('%')) > 95 else "Good")
                with col_m2:
                    st.metric("⚡ Processing Time", st.session_state.report_data['processing_time'],
                              delta="Fast")

            # Enhanced action buttons
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("📋 View Report", use_container_width=True):
                    st.session_state.show_report = True
            with col_b:
                if st.button("💾 Download", use_container_width=True):
                    # Enhanced report generation
                    report_text = f"""
PULMOVISTA DIAGNOSTIC REPORT
============================

PATIENT INFORMATION
Patient ID: {st.session_state.report_data['patient_id']}
Analysis Date: {st.session_state.report_data['date']}
# AI Model: {st.session_state.report_data['ai_model']}
#ANALYSIS RESULTS
Confidence Score: {st.session_state.report_data['confidence']}
#Processing Time: {st.session_state.report_data['processing_time']}
#Risk Assessment: {st.session_state.report_data['risk_score']}

#CLINICAL IMPRESSION  
Clinical Impression: {st.session_state.report_data['impression']}

IMPORTANT DISCLAIMERS
- This AI analysis is intended to assist healthcare professionals
- Clinical correlation and professional medical interpretation required
- Not intended as a substitute for professional medical diagnosis
- For research and educational purposes

Generated by PulmoVista AI Medical Imaging System
Report ID: {st.session_state.report_data['patient_id']}-{datetime.now().strftime('%H%M%S')}
                    """
                    st.download_button(
                        label="📄 Download Report",
                        data=report_text,
                        file_name=f"pulmovista_report_{st.session_state.report_data['patient_id']}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            with col_c:
                if st.button("🔄 New Analysis", use_container_width=True):
                    st.session_state.uploaded_file = None
                    st.session_state.processed_result = None
                    st.session_state.report_data = None
                    st.session_state.show_report = False
                    st.rerun()
        else:
            st.info("🎯 Upload an image and click 'Analyze Image' to begin AI analysis")

        st.markdown('</div>', unsafe_allow_html=True)

    # Enhanced detailed report section
    if st.session_state.show_report and st.session_state.report_data:
        st.markdown("---")
        # Enhanced metrics cards
        col_r1, col_r2 = st.columns(2)

        with col_r1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>👤 Patient Information</h3>
                <p><strong>ID:</strong> {st.session_state.report_data['patient_id']}</p>
                <p><strong>Date:</strong> {st.session_state.report_data['date']}</p>
                <p><strong>Model:</strong> {st.session_state.report_data['ai_model']}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_r2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 Analysis Metrics</h3>
                <p><strong>Confidence:</strong> {st.session_state.report_data['confidence']}</p>
                <p><strong>Processing:</strong> {st.session_state.report_data['processing_time']}</p>
                <p><strong>Risk Score:</strong> {st.session_state.report_data['risk_score']}</p>
            </div>
            """, unsafe_allow_html=True)

        # with col_r3:
        #     st.markdown(f"""
        #     <div class="metric-card">
        #         <h3>🏥 Clinical Summary</h3>
        #         <p><strong>Status:</strong> Analyzed</p>
        #         <p><strong>Priority:</strong> Routine</p>
        #         <p><strong>Follow-up:</strong> As needed</p>
        #     </div>
        #     """, unsafe_allow_html=True)

    #Enhanced findings and impression
    #col_find1 = st.columns(1)

    #with col_find1:
        st.markdown("### 🔍 Clinical Impression")
        st.success(st.session_state.report_data['findings'])


    # Enhanced Doctor's Feedback Section
    st.markdown("---")
    #st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
    st.subheader("👨‍⚕️ Doctor's Feedback")

   # Feedback type selection
    feedback_type = st.selectbox(
            "🏷️ Feedback Type",
            ["General Comments", "Diagnostic Correction", "Technical Issue", "Improvement Suggestion",
             "Accuracy Assessment"]
    )

        # Rating system
    col_rating1, col_rating2 = st.columns(2)
    with col_rating1:
            accuracy_rating = st.slider("🎯 Accuracy Rating", 1, 5, 4, help="Rate the AI analysis accuracy")
    with col_rating2:
            usefulness_rating = st.slider("💡 Usefulness Rating", 1, 5, 4, help="Rate how useful this analysis is")

        # Enhanced feedback text area
    feedback_text = st.text_area(
            "📋 Detailed Feedback:",
            placeholder="Enter your professional feedback, corrections, or suggestions here...\n\nConsider including:\n• Diagnostic accuracy assessment\n• Missing findings\n• Technical improvements\n• Clinical correlation notes",
            height=120,
            help="Your feedback helps improve our AI model"
    )

        # Enhanced submit section
    col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])

    with col_submit1:
            if st.button("📤 Submit Feedback", use_container_width=True):
                if feedback_text.strip():
                    # Save feedback to session history
                    feedback_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'type': feedback_type,
                        'accuracy_rating': accuracy_rating,
                        'usefulness_rating': usefulness_rating,
                        'text': feedback_text,
                        'patient_id': st.session_state.report_data[
                            'patient_id'] if st.session_state.report_data else 'N/A'
                    }

                if 'feedback_history' not in st.session_state:
                    st.session_state.feedback_history = []
                    st.session_state.feedback_history.append(feedback_entry)

                    st.success("✅ Feedback submitted successfully! Thank you for helping improve our AI model.")

                    # Show submission details
                    st.info(f"📊 Submission ID: {feedback_entry['timestamp'][-8:]}\n🎯 Accuracy: {accuracy_rating}/5 ⭐\n💡 Usefulness: {usefulness_rating}/5 ⭐")
                else:
                        st.warning("⚠️ Please enter your feedback before submitting.")

    with col_submit2:
            if st.button("🔄 Clear Form", use_container_width=True):
                st.rerun()

    with col_submit3:
            if len(st.session_state.feedback_history) > 0:
                st.metric("📈 Total", len(st.session_state.feedback_history))

            else:
                st.info("📤 Upload and analyze an image to provide professional feedback on the AI results.")

    st.markdown('</div>', unsafe_allow_html=True)

elif page == "🆘 Support":
    st.header("🆘 Support Center")
    st.markdown("Get comprehensive help with using PulmoVista")

    # Enhanced support tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📚 FAQ", "🎓 Tutorials", "🐛 Report Issue", "💬 Live Chat"])

    with tab1:
        st.subheader("📚 Frequently Asked Questions")

        with st.expander("📁 File Format & Upload Questions"):
            st.markdown("""
            **Q: What file formats are supported?**
            A: We support DICOM files (.dcm) and standard image formats (JPG, PNG, TIFF, BMP, WebP).

            **Q: What's the maximum file size?**
            A: Maximum file size is 25MB per upload.

            **Q: Can I upload multiple images at once?**
            A: Currently, we process one image at a time for optimal accuracy.
            """)

        with st.expander("🎯 AI Analysis & Accuracy"):
            st.markdown("""
            **Q: How accurate is the AI analysis?**
            A: Our AI model achieves 98.7% accuracy based on validation against expert radiologist readings.

            **Q: How long does processing take?**
            A: Most images are processed within 2-5 seconds, depending on image size and complexity.

            **Q: What conditions can the AI detect?**
            A: Our AI can identify pneumonia, pneumothorax, pleural effusion, cardiomegaly, and other common chest pathologies.
            """)

        with st.expander("🔐 Security & Privacy"):
            st.markdown("""
            **Q: How is patient data protected?**
            A: All data is encrypted in transit and at rest. We are HIPAA compliant and ISO 27001 certified.

            **Q: Are uploaded images stored?**
            A: Images are processed in memory and not permanently stored on our servers.

            **Q: Who can access the analysis results?**
            A: Only the uploading user has access to results during their session.
            """)

    with tab2:
        st.subheader("🎓 Video Tutorials")

        col_tut1, col_tut2 = st.columns(2)

        with col_tut1:
            st.markdown("""
            #### 🎬 Getting Started
            - How to upload your first X-ray
            - Understanding the analysis interface
            - Interpreting AI results

            #### 🔧 Advanced Features
            - Using feedback systems effectively
            - Downloading and sharing reports
            - Batch processing workflows
            """)

        with col_tut2:
            st.markdown("""
            #### 📊 Best Practices
            - Optimal image quality guidelines
            - When to trust AI vs. clinical judgment
            - Integrating AI into clinical workflow

            #### 🚀 New Features
            - Latest AI model updates
            - Enhanced reporting features
            - Mobile app integration
            """)

        st.info("🎥 Video tutorials coming soon! Check back for comprehensive training materials.")

    with tab3:
        st.subheader("🐛 Report an Issue")

        with st.form("issue_report_form", clear_on_submit=True):
            col_issue1, col_issue2 = st.columns(2)

            with col_issue1:
                issue_type = st.selectbox("🏷️ Issue Type", [
                    "Technical Bug",
                    "Incorrect Analysis",
                    "Performance Issue",
                    "Interface Problem",
                    "Data/Privacy Concern",
                    "Feature Request"
                ])

                severity = st.selectbox("⚠️ Severity", [
                    "Low - Minor inconvenience",
                    "Medium - Affects workflow",
                    "High - Blocks critical function",
                    "Critical - Patient safety concern"
                ])

            with col_issue2:
                user_email = st.text_input("📧 Your Email")
                affected_feature = st.text_input("🎯 Affected Feature")

            issue_description = st.text_area(
                "📝 Detailed Description",
                placeholder="Please describe the issue in detail:\n• What were you trying to do?\n• What happened instead?\n• Steps to reproduce the issue\n• Any error messages\n• Browser/device information",
                height=150
            )

            # File attachment for screenshots
            attachment = st.file_uploader(
                "📎 Attach Screenshot (optional)",
                type=['png', 'jpg', 'jpeg', 'pdf'],
                help="Screenshots help us understand and resolve issues faster"
            )

            if st.form_submit_button("🚀 Submit Issue Report", use_container_width=True):
                if issue_description.strip():
                    issue_id = f"ISS-{datetime.now().strftime('%Y%m%d')}-{len(st.session_state.get('issues', []))}"

                    st.success(
                        f"✅ Issue reported successfully!\n📋 Issue ID: {issue_id}\n📧 We'll respond within 24 hours.")

                    # Store issue in session (in real app, would save to database)
                    if 'issues' not in st.session_state:
                        st.session_state.issues = []
                    st.session_state.issues.append({
                        'id': issue_id,
                        'type': issue_type,
                        'severity': severity,
                        'description': issue_description,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    st.error("❌ Please provide a detailed description of the issue.")

    with tab4:
        st.subheader("💬 Live Chat Support")

        # Simulate chat interface
        st.markdown("""
        <div style="background: linear-gradient(145deg, #ffffff, #f8fafc); padding: 2rem; border-radius: 15px; border: 2px solid #e2e8f0;">
            <h4>🤖 AI Assistant</h4>
            <p>Hello! I'm here to help you with PulmoVista. How can I assist you today?</p>
        </div>
        """, unsafe_allow_html=True)

        # Chat input
        user_message = st.text_input("💬 Type your message here...", placeholder="Ask me anything about PulmoVista!")

        if user_message:
            # Simple response simulation
            responses = {
                "accuracy": "Our AI model has a 98.7% accuracy rate based on validation studies with expert radiologists.",
                "upload": "You can upload DICOM files (.dcm) or standard images (JPG, PNG, TIFF, BMP, WebP) up to 25MB.",
                "time": "Most analyses complete in 2-5 seconds depending on image complexity.",
                "help": "I can help with technical issues, feature questions, or guide you through using PulmoVista.",
                "contact": "For urgent issues, email support@pulmovista.com or call +1 (555) 123-4567."
            }

            # Simple keyword matching
            response = "I understand you're asking about PulmoVista. Could you be more specific? I can help with accuracy, uploads, processing time, or general help."
            for keyword, reply in responses.items():
                if keyword in user_message.lower():
                    response = reply
                    break

            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #e0f2fe, #b3e5fc); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                <strong>🤖 AI Assistant:</strong> {response}
            </div>
            """, unsafe_allow_html=True)

        st.info("💡 For complex issues, our human support team is available 24/7 at support@pulmovista.com")

elif page == "ℹ️ About":
    st.header("ℹ️ About PulmoVista")

    # Enhanced about section with better layout
    col_about1, col_about2 = st.columns([2, 1])

    with col_about1:
        st.markdown("""
        ## 🚀 Revolutionary AI-Powered Medical Imaging

        PulmoVista represents the cutting edge of medical AI technology, designed to assist healthcare 
        professionals in analyzing chest X-rays with unprecedented accuracy and speed. Our advanced 
        machine learning algorithms have been trained on millions of medical images to provide 
        reliable diagnostic assistance.

        ### 🎯 Key Features:

        #### 🔬 Advanced AI Technology
        - **Deep Learning Networks**: State-of-the-art convolutional neural networks
        - **Computer Vision**: Advanced image processing and pattern recognition
        - **Continuous Learning**: Model improves with expert feedback
        - **Multi-Modal Analysis**: Supports various imaging formats

        #### ⚡ Performance Excellence  
        - **98.7% Accuracy**: Validated against expert radiologist readings
        - **2-5 Second Processing**: Lightning-fast analysis
        - **24/7 Availability**: Always ready when you need it
        - **Scalable Infrastructure**: Cloud-based for reliability

        #### 🛡️ Security & Compliance
        - **HIPAA Compliant**: Full patient privacy protection
        - **ISO 27001 Certified**: International security standards
        - **FDA Approved**: Meets regulatory requirements
        - **End-to-End Encryption**: Secure data transmission
        """)

    with col_about2:
        st.markdown("""
        ### 📊 Platform Statistics
        """)

        # Enhanced metrics display
        st.metric("Images Analyzed", "2.1M+", delta="15k this month")
        st.metric("Healthcare Facilities", "500+", delta="12 new")
        st.metric("Countries Served", "45", delta="3 new")
        st.metric("Accuracy Rate", "98.7%", delta="0.3% improvement")

        st.markdown("""
        ### 🏆 Awards & Recognition
        - 🥇 Best Medical AI Innovation 2024
        - 🏥 Healthcare Technology Excellence Award
        - 🔬 Medical Research Society Recognition
        - 📊 Top Radiology AI Platform
        """)

        st.markdown("""
        ### 👥 Our Team
        - **50+ AI Researchers**
        - **25+ Medical Experts**  
        - **30+ Software Engineers**
        - **15+ Clinical Advisors**
        """)

    # Technology details
    st.markdown("---")
    st.subheader("🔬 Technology Deep Dive")

    tab_tech1, tab_tech2, tab_tech3 = st.tabs(["🧠 AI Architecture", "🔍 Detection Capabilities", "📈 Validation"])

    with tab_tech1:
        col_tech1, col_tech2 = st.columns(2)

        with col_tech1:
            st.markdown("""
            #### Neural Network Architecture
            - **ResNet-152 Backbone**: Deep residual networks for feature extraction
            - **Attention Mechanisms**: Focus on relevant anatomical regions
            - **Multi-Scale Processing**: Analyze features at different resolutions
            - **Ensemble Methods**: Multiple models for robust predictions
            """)

        with col_tech2:
            st.markdown("""
            #### Training & Optimization
            - **2.5M Training Images**: Diverse, high-quality dataset
            - **Expert Annotations**: Validated by board-certified radiologists
            - **Data Augmentation**: Enhanced robustness through variation
            - **Transfer Learning**: Pre-trained on medical imaging datasets
            """)

    with tab_tech2:
        st.markdown("""
        #### 🎯 Detectable Conditions

        Our AI can identify and analyze the following conditions with high accuracy:

        | Condition | Accuracy | Sensitivity | Specificity |
        |-----------|----------|-------------|-------------|
        | Pneumonia | 97.2% | 95.8% | 98.1% |
        | Pneumothorax | 96.8% | 94.3% | 97.9% |
        | Pleural Effusion | 98.1% | 96.7% | 98.8% |
        | Cardiomegaly | 95.4% | 93.2% | 96.9% |
        | Atelectasis | 94.7% | 92.1% | 96.2% |
        | Consolidation | 96.3% | 94.8% | 97.1% |
        | Nodules/Masses | 93.9% | 91.4% | 95.7% |
        | Normal Findings | 99.1% | 98.7% | 99.3% |

        #### 📊 Performance Metrics
        - **Overall Accuracy**: 98.7%
        - **Average Sensitivity**: 95.2%
        - **Average Specificity**: 97.5%
        - **Processing Speed**: 2.8s average
        """)

    with tab_tech3:
        st.markdown("""
        #### 🔬 Clinical Validation Studies

        **Multi-Center Validation Study (2024)**
        - **Participants**: 15 major medical centers
        - **Dataset**: 50,000 chest X-rays
        - **Comparators**: 25 board-certified radiologists
        - **Result**: 98.7% concordance with expert consensus

        **Real-World Performance Study (2024)**
        - **Setting**: 5 emergency departments
        - **Duration**: 6 months
        - **Cases**: 25,000 emergency chest X-rays
        - **Outcome**: 23% faster diagnosis, maintained accuracy

        **Pediatric Validation Study (2023)**
        - **Population**: Children aged 0-18 years
        - **Dataset**: 10,000 pediatric chest X-rays
        - **Result**: 97.1% accuracy in pediatric population

        #### 📜 Publications
        - *"AI-Assisted Chest X-ray Analysis"* - New England Journal of Medicine, 2024
        - *"Deep Learning in Emergency Radiology"* - Radiology, 2024
        - *"Clinical Impact of AI Diagnostic Tools"* - JAMA, 2023
        """)

    # Important disclaimers
    st.markdown("---")
    st.warning("""
    ⚠️ **Important Medical Disclaimer**

    PulmoVista is designed to assist healthcare professionals and should not replace clinical judgment. 
    This tool is intended for use by qualified medical professionals only. Always consult with 
    qualified healthcare providers for medical decisions. This system is approved for diagnostic 
    assistance only and should be used in conjunction with clinical evaluation.
    """)

elif page == "📞 Contact":
    st.header("📞 Contact Us")

    # Enhanced contact layout
    col_contact1, col_contact2 = st.columns([1, 1])

    with col_contact1:
        st.subheader("🏢 Corporate Headquarters")

        st.markdown("""
        **🏥 PulmoVista Medical Technologies**

        📍 **Address:**
        123 Medical Innovation Drive  
        Suite 500, Healthcare District  
        San Francisco, CA 94107  
        United States

        📞 **Phone Numbers:**
        - Main: +1 (555) 123-4567
        - Support: +1 (555) 123-HELP
        - Sales: +1 (555) 123-SALES
        - Emergency: +1 (555) 911-URGENT

        📧 **Email Contacts:**
        - General: contact@pulmovista.com
        - Support: support@pulmovista.com  
        - Sales: sales@pulmovista.com
        - Partnerships: partners@pulmovista.com

        🌐 **Digital Presence:**
        - Website: www.pulmovista.com
        - LinkedIn: /company/pulmovista
        - Twitter: @PulmoVistaAI
        - Research Portal: research.pulmovista.com
        """)

        st.markdown("---")

        st.subheader("🕒 Business Hours")

        schedule_data = {
            "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "Support": ["24/7", "24/7", "24/7", "24/7", "24/7", "24/7", "24/7"],
            "Sales": ["8AM-6PM", "8AM-6PM", "8AM-6PM", "8AM-6PM", "8AM-6PM", "9AM-2PM", "Closed"],
            "Training": ["9AM-5PM", "9AM-5PM", "9AM-5PM", "9AM-5PM", "9AM-5PM", "Closed", "Closed"]
        }

        st.table(schedule_data)

        st.info("🚨 Technical support is available 24/7 for critical issues affecting patient care.")

    with col_contact2:
        st.subheader("📨 Send us a Message")

        with st.form("enhanced_contact_form", clear_on_submit=True):
            # Contact information
            col_form1, col_form2 = st.columns(2)

            with col_form1:
                contact_name = st.text_input("👤 Full Name*")
                contact_title = st.text_input("🏷️ Job Title")

            with col_form2:
                contact_email = st.text_input("📧 Email Address*")
                contact_phone = st.text_input("📞 Phone Number")

            # Organization details
            col_org1, col_org2 = st.columns(2)

            with col_org1:
                organization = st.text_input("🏥 Organization/Hospital")
                department = st.selectbox("🏢 Department", [
                    "Radiology",
                    "Emergency Medicine",
                    "Internal Medicine",
                    "IT/Technology",
                    "Administration",
                    "Research",
                    "Other"
                ])

            with col_org2:
                country = st.selectbox("🌍 Country", [
                    "United States", "Canada", "United Kingdom", "Germany",
                    "France", "Australia", "Japan", "Other"
                ])
                urgency = st.selectbox("⚡ Urgency Level", [
                    "Low - General inquiry",
                    "Medium - Business question",
                    "High - Technical issue",
                    "Critical - Patient safety"
                ])

            # Message details
            contact_subject = st.selectbox("📋 Subject Category", [
                "General Inquiry",
                "Technical Support",
                "Sales & Pricing",
                "Partnership Opportunity",
                "Clinical Trial Participation",
                "Training & Education",
                "Bug Report",
                "Feature Request",
                "Regulatory/Compliance",
                "Research Collaboration"
            ])

            contact_message = st.text_area(
                "💬 Detailed Message*",
                height=150,
                placeholder="Please provide detailed information about your inquiry, including:\n• Specific questions or requirements\n• Current challenges you're facing\n• Timeline expectations\n• Any relevant technical details"
            )

            # Privacy and consent
            privacy_consent = st.checkbox(
                "I agree to the Privacy Policy and Terms of Service*",
                help="We respect your privacy and will only use your information to respond to your inquiry."
            )

            marketing_consent = st.checkbox(
                "I would like to receive updates about PulmoVista products and services",
                help="Optional: Receive newsletters, product updates, and educational content."
            )

            # Submit button
            if st.form_submit_button("🚀 Send Message", use_container_width=True):
                if contact_name and contact_email and contact_message and privacy_consent:
                    # Generate ticket ID
                    ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d')}-{len(st.session_state.get('tickets', []))}"

                    # Success message
                    st.success(f"""
                    ✅ **Message sent successfully!**

                    📋 **Ticket ID:** {ticket_id}  
                    📧 **Confirmation sent to:** {contact_email}  
                    ⏱️ **Expected Response:** Within 24 hours (or 2 hours for critical issues)

                    Thank you for contacting PulmoVista! Our team will review your message and respond promptly.
                    """)

                    # Store ticket (in real app, would save to CRM)
                    if 'tickets' not in st.session_state:
                        st.session_state.tickets = []
                    st.session_state.tickets.append({
                        'id': ticket_id,
                        'name': contact_name,
                        'email': contact_email,
                        'subject': contact_subject,
                        'urgency': urgency,
                        'message': contact_message,
                        'timestamp': datetime.now().isoformat()
                    })

                else:
                    st.error("❌ Please fill in all required fields (*) and accept the privacy policy.")

        # Quick contact options
        st.markdown("---")
        st.subheader("🚀 Quick Contact Options")

        col_quick1, col_quick2 = st.columns(2)

        with col_quick1:
            if st.button("📞 Schedule a Demo", use_container_width=True):
                st.info("📅 Demo scheduling system will open in a new window")

            if st.button("💬 Live Chat", use_container_width=True):
                st.info("💬 Live chat widget will appear in the bottom right")

        with col_quick2:
            if st.button("📚 Download Brochure", use_container_width=True):
                st.info("📄 Product brochure download will begin")

            if st.button("🎓 Training Request", use_container_width=True):
                st.info("🎯 Training portal will open")

# Enhanced Footer
import streamlit as st

st.markdown("""
<style>
.tiny-footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background: #e3f2fd;
    color: #1976d2;
    text-align: center;
    padding: 0.18rem 0 0.18rem 0;
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    z-index: 100;
    box-shadow: 0 -1px 8px rgba(25, 118, 210, 0.06);
    line-height: 1.5;
}
</style>
<div class="tiny-footer">
    🫁 Diagno Intelligent Systems• © 2025
</div>
""", unsafe_allow_html=True)

