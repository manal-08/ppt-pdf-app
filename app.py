import streamlit as st
from pptx import Presentation
from fpdf import FPDF
import io

st.set_page_config(page_title="مُحوّل العروض والصور", layout="centered")
st.title("📄 محول PPTX والصور إلى PDF")

tab1, tab2 = st.tabs(["📊 عرض تقديمي PPTX", "📐 صورة عمليات رياضية"])

with tab1:
    st.subheader("استخراج الفقرات من ملف PPTX")
    uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت", type=["pptx"])
    
    if uploaded_ppt and st.button("استخراج وتحويل إلى PDF"):
        prs = Presentation(uploaded_ppt)
        text_runs = []
        
        for slide_idx, slide in enumerate(prs.slides, start=1):
            text_runs.append(f"--- الشريحة {slide_idx} ---")
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        if paragraph.text.strip():
                            text_runs.append(paragraph.text.strip())
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=10)
        
        for line in text_runs:
            # تقطيع الأسطر الطويلة جداً لتجنب خطأ المساحة الأفقية
            words = line.split()
            current_line = ""
            for word in words:
                safe_word = word.encode('latin-1', 'replace').decode('latin-1')
                if pdf.get_string_width(current_line + " " + safe_word) < 180:
                    current_line += (" " + safe_word) if current_line else safe_word
                else:
                    pdf.multi_cell(0, 8, txt=current_line)
                    current_line = safe_word
            if current_line:
                pdf.multi_cell(0, 8, txt=current_line)
        
        pdf_output = pdf.output()
        
        st.success("تم الاستخراج بنجاح!")
        st.download_button(
            label="⬇️ تحميل ملف PDF",
            data=bytes(pdf_output),
            file_name="extracted_content.pdf",
            mime="application/pdf"
        )

with tab2:
    st.subheader("قراءة المعادلات الرياضية من الصور")
    uploaded_img = st.file_uploader("اختر صورة تحتوي على معادلات", type=["jpg", "png", "jpeg"])
    
    if uploaded_img:
        st.image(uploaded_img, caption="الصورة المرفوعة", use_container_width=True)
        st.info("💡 لقراءة المعادلات الرياضية بدقة عالية، يمكن إضافة مفتاح Mathpix API أو OpenAI Vision مستقبلاً.")
