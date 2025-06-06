import streamlit as st
import time
import numpy as np
import tensorflow as tf
import warnings
from PIL import Image


# Suppress retracing warning
warnings.filterwarnings("ignore", category=UserWarning, message=r"tf.function retracing")

import streamlit as st

st.set_page_config(page_title="PulmoVista", layout="wide")

# Custom Navbar with HTML + CSS
st.markdown("""
<style>
.navbar {
    background-color: #3b5bfd;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 5px;
}
.navbar .logo {
    font-weight: 700;
    font-size: 1.5rem;
    color: white;
}
.navbar .logo span {
    margin-right: 10px;
}
.navbar a {
    text-decoration: none;
    color: white;
    margin: 0 15px;
    font-weight: 500;
    font-size: 1.1rem;
}
.navbar a:hover {
    text-decoration: underline;
}
</style>

<div class="navbar">
    <div class="logo"><span>🫁</span>PulmoVista</div>
    <div>
        <a href="#home">🏠 Home</a>
        <a href="#analytics">📊 Analytics</a>
        <a href="#support">🆘 Support</a>
        <a href="#about">ℹ️ About</a>
        <a href="#contact">📞 Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Just to simulate sections (optional)
st.markdown("### 🏠 Home", unsafe_allow_html=True)
st.write("Welcome to PulmoVista!")

st.markdown("### 📊 Analytics", unsafe_allow_html=True)
st.write("Your diagnostic and performance metrics.")

st.markdown("### 🆘 Support", unsafe_allow_html=True)
st.write("Get help or report issues.")

st.markdown("### ℹ️ About", unsafe_allow_html=True)
st.write("About the PulmoVista system.")

st.markdown("### 📞 Contact", unsafe_allow_html=True)
st.write("Reach out to us here.")


# Title
st.title("Deep Learning Image Classifier")

# Upload Image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

# Initialize progress bar and status
progress_bar = st.progress(0)
status_text = st.empty()

# Load model once at the start (outside logic block)
@st.cache_resource
def load_model():
    model_path = "model_inc_V3_50d_ADAM_sq_aug_score3_Female_os_nos_8b.h5"
    model = tf.keras.models.load_model(model_path, compile=False)
    return model

model = load_model()

if uploaded_file is not None:
    # Display image
    image_pil = Image.open(uploaded_file)
    st.image(image_pil, caption="Uploaded Image", use_container_width=True)

    # Step 1: Preprocessing
    status_text.text("Step 1: Preprocessing image...")


    img_size = 299
    uploaded_file.seek(0)  # rewind to start
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (img_size, img_size))
    image = img.astype('float32') / 255.0
    image = np.expand_dims(image, axis=0)
    progress_bar.progress(30)

    # Step 2: Predict
    status_text.text("Step 2: Running model inference...")
    time.sleep(1)  # Optional: just to slow down for UI experience
    y_pred = np.argmax(model.predict(image, verbose=0), axis=1)
    prediction = y_pred[0]
    progress_bar.progress(100)

    # Step 3: Display result
    status_text.text("Prediction completed.")
    st.success(f"Prediction Result: {prediction}")

