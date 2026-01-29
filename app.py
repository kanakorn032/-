import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px

# 1. การตั้งค่าพื้นฐาน
st.set_page_config(page_title="AI Smart Finance", layout="centered")
st.title("💎 AI Smart Finance")
st.subheader("บันทึกการเงินและวิเคราะห์ด้วย AI (ข้อมูลบันทึกลง Sheet)")

# 2. เชื่อมต่อ API Key (ดึงจาก Secrets)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("กรุณาตั้งค่า GOOGLE_API_KEY ใน Secrets")

# 3. จัดการข้อมูลใน Session State (สำรองไว้ในเครื่องชั่วคราว)
if 'history' not in st.session_state:
    st.session_state.history = []

# --- ส่วนของการบันทึกข้อมูล ---
with st.form("finance_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        item_name = st.text_input("📝 รายการ", placeholder="เช่น ค่าข้าว")
        amount = st.number_input("💰 จำนวนเงิน", min_value=0, step=1)
    with col2:
        category = st.selectbox("📁 หมวดหมู่", ["🍴 อาหาร", "🚗 เดินทาง", "🏠 ของใช้", "✨ อื่นๆ"])
        item_type = st.radio("🏷️ ประเภท", ["รายจ่าย", "รายรับ"], horizontal=True)
    
    submit_button = st.form_submit_button("➕ บันทึกข้อมูล")

if submit_button and item_name:
    new_data = {
        "รายการ": item_name,
        "จำนวนเงิน": amount,
        "ประเภท": item_type,
        "หมวดหมู่": category
    }
    st.session_state.history.append(new_data)
    st.success(f"บันทึก {item_name} เรียบร้อยแล้ว!")

# --- ส่วนการแสดงผลและคำนวณ ---
