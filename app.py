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
    genai.configure(api_key=st.secrets["AIzaSyBQB585MnSECX8Tn0T7dNXimer9isB8Iaw"])
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
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    
    # คำนวณยอดรวม
    total_income = df[df['ประเภท'] == "รายรับ"]['จำนวนเงิน'].sum()
    total_expense = df[df['ประเภท'] == "รายจ่าย"]['จำนวนเงิน'].sum()
    balance = total_income - total_expense

    # แสดง Card สรุป
    c1, c2, c3 = st.columns(3)
    c1.metric("รายรับ", f"{total_income:,} ฿")
    c2.metric("รายจ่าย", f"{total_expense:,} ฿")
    c3.metric("คงเหลือ", f"{balance:,} ฿")

    # กราฟวงกลม
    st.write("---")
    fig = px.pie(df, values='จำนวนเงิน', names='หมวดหมู่', title='สัดส่วนการใช้จ่ายตามหมวดหมู่')
    st.plotly_chart(fig)

    # ตารางรายการ
    st.write("### 📋 ประวัติล่าสุด")
    st.table(df)
    csv = df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 ดาวน์โหลดข้อมูลเป็น Excel (CSV)",
    data=csv,
    file_name='my_finance.csv',
    mime='text/csv',
)

    # --- ปุ่ม AI (ปรับให้เร็วขึ้น) ---
if st.button("🚀 ให้ AI วิเคราะห์สั้นๆ"):
        # ส่งข้อมูลแค่ 5 รายการล่าสุดเพื่อให้ AI ทำงานไว
        recent_data = df.tail(5).to_string()
        prompt = f"วิเคราะห์ข้อมูลนี้: {recent_data} ขอคำแนะนำสั้นๆ 2 ข้อ (ไม่เกิน 50 คำ)"
        
        with st.status("🔍 AI กำลังสรุป..."):
            try:
                response = model.generate_content(prompt)
                st.info(response.text)
            except Exception as e:
                st.error(f"AI Error: {e}")

    # --- ปุ่มรีเซ็ตสีแดง (Reset) ---
    st.write("---")
if st.button("🗑️ ล้างข้อมูลทั้งหมดเพื่อเริ่มใหม่", type="primary"):
        st.session_state.history = []
        st.rerun()

else:
    st.info("ยังไม่มีข้อมูล กรุณากรอกรายการด้านบนครับ")