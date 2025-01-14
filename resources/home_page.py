import streamlit as st
import os

# Image file path
image_path = os.path.join(os.path.dirname(__file__), "./images/finance_image.jpg")

def home_page():
    st.title("Personal Finance")
    if os.path.exists(image_path):
        st.image(image_path, caption="Manage your finances efficiently!", width=400)  # Fixed width
    else:
        st.error(f"Image file not found! {image_path}")