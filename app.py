import streamlit as st
from pptx import Presentation
from fpdf import FPDF
import os

st.set_page_config(page_title="منصة إعداد الجذاذاات الرياضية", layout="centered")
st.title("📚 صانع الجذاذاات الرياضية الملونة")

st.markdown("""
تطبيق خاص بتحويل عروض الباوربوينت إلى **جذاذة PDF مرتبة ومنسقة** حسب المعايير البيداغوجية (ألوان مخصصة للعناوين، القواعد، الخاصيات، والأمثلة).
""")

uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت الخاص بالدرس (PPTX)", type=["pptx"])

if uploaded_ppt and st.button("توليد الجذاذة بالألوان المطلوبة"):
    prs = Presentation(uploaded_ppt)
    
    # إعداد ملف ال PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=10)
    
    for slide_idx, slide in enumerate(prs.slides, start=1):
        # عنوان الشريحة أو رقمها
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(200, 0, 0) # أحمر
        pdf.multi_cell(0, 8, txt=f"--- الشريحة رقم {slide_idx} ---")
        pdf.set_text_color(0, 0, 0) # إعادة اللون للأسود
        
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    text = paragraph.text.strip()
                    if not text:
                        continue
                    
                    # تحديد الألوان بناءً على الكلمات المفتاحية أو التنسيق
                    # افتراضياً اللون الأسود
                    r, g, b = 0, 0, 0
                    is_bold = False
                    
                    # الألوان حسب طلبك:
                    if text.startswith("I") or text.startswith("II") or text.startswith("III") or text.startswith("IV"):
                        r, g, b = 200, 0, 0      # أحمر (العناوين الرومانية)
                        is_bold = True
                    elif any(text.startswith(f"{i})") for i in range(1, 10)):
                        r, g, b = 0, 128, 0     # أخضر (العناوين العادية)
                        is_bold = True
                    elif "Règle" in text:
                        r, g, b = 128, 0, 128   # بنفسجي
                        is_bold = True
                    elif any(k in text for k in ["Activité", "Exemple", "Définition", "Exemples"]):
                        r, g, b = 0, 102, 204   # أزرق سماوي
                        is_bold = True
                    elif "Propriété" in text:
                        r, g, b = 255, 128, 0   # برتقالي
                        is_bold = True
                    elif any(k in text for k in ["Application", "Exercice"]):
                        r, g, b = 139, 69, 19   # بني
                        is_bold = True
                    
                    pdf.set_font("Helvetica", "B" if is_bold else "", 10)
                    pdf.set_text_color(r, g, b)
                    
                    # تنظيف النص ليتوافق مع ترميز FPDF
                    safe_text = text.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 7, txt=safe_text)
                    
        pdf.ln(3) # مسافة بسيطة بين الشرائح

    # حفظ ملف ال PDF الناتج
    pdf_output = pdf.output()
    
    st.success("تم توليد الجذاذة بنجاح وبالألوان المطلوبة!")
    
    st.download_button(
        label="⬇️ تحميل الجذاذة بصيغة PDF",
        data=bytes(pdf_output),
        file_name="Jadad_Mathematiques.pdf",
        mime="application/pdf"
    )
