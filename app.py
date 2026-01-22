import streamlit as st
import google.generativeai as genai
import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px # ตัวทำกราฟสวยๆ

# --- 1. ตั้งค่า AI ---
GOOGLE_API_KEY = "วAIzaSyBQB585MnSECX8Tn0T7dNXimer9isB8Iaw"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. ตั้งค่าหน้าตาเว็บ ---
st.set_page_config(page_title="วางแผนการเงิน", layout="centered")

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("💎 วางแผนการเงิน")
st.caption("บันทึกการเงินและวิเคราะห์ด้วย AI พร้อมกราฟสรุป")

# --- 3. ส่วน Dashboard ตัวเลข ---
total_income = sum(item['จำนวนเงิน'] for item in st.session_state.history if item['ประเภท'] == "รายรับ")
total_expense = sum(item['จำนวนเงิน'] for item in st.session_state.history if item['ประเภท'] == "รายจ่าย")
balance = total_income - total_expense

col_a, col_b, col_c = st.columns(3)
col_a.metric("รายรับทั้งหมด", f"{total_income:,} ฿")
col_b.metric("รายจ่ายทั้งหมด", f"-{total_expense:,} ฿", delta_color="inverse")
col_c.metric("เงินคงเหลือ", f"{balance:,} ฿")

# --- 4. ส่วนบันทึกข้อมูล ---
with st.container():
    st.markdown("### 📝 บันทึกรายการ")
    c1, c2 = st.columns(2)
    with c1:
        item_name = st.text_input("รายการ", placeholder="เช่น ค่าข้าว")
        category = st.selectbox("หมวดหมู่", ["🍴 อาหาร", "🚗 เดินทาง", "🏠 ของใช้", "🎮 บันเทิง", "✨ อื่นๆ"])
    with c2:
        item_amount = st.number_input("จำนวนเงิน", min_value=0, step=1)
        item_type = st.radio("ประเภท", ["รายจ่าย", "รายรับ"], horizontal=True)

    if st.button("➕ บันทึกข้อมูล"):
        if item_name and item_amount > 0:
            st.session_state.history.append({
                "รายการ": item_name,
                "จำนวนเงิน": item_amount,
                "หมวดหมู่": category,
                "ประเภท": item_type
            })
            st.rerun()

# --- 5. ส่วนแสดงกราฟและตาราง (จะโชว์เมื่อมีข้อมูลเท่านั้น) ---
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    
    st.divider()
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📊 สัดส่วนรายจ่าย")
        # กรองเฉพาะรายจ่ายมาทำกราฟ
        expense_df = df[df['ประเภท'] == "รายจ่าย"]
        if not expense_df.empty:
            fig = px.pie(expense_df, values='จำนวนเงิน', names='หมวดหมู่', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("ยังไม่มีข้อมูลรายจ่าย")

    with col_right:
        st.subheader("📋 ประวัติล่าสุด")
        st.dataframe(df.tail(5), hide_index=True)

    # --- 6. ส่วน AI วิเคราะห์ ---
    st.divider()
    if st.button("🚀 ให้ AI วิเคราะห์ภาพรวมการเงิน"):
        all_data = df.to_string() # แปลงตารางเป็นตัวหนังสือให้ AI อ่าน
        prompt = f"วิเคราะห์ข้อมูลการเงินนี้: {all_data} สรุปพฤติกรรมและบอกวิธีประหยัด 3 ข้อ"
        
        with st.status("🔍 AI กำลังประมวลผล..."):
            try:
                response = model.generate_content(prompt)
                st.subheader("💡 คำแนะนำจาก AI")
                st.success(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
