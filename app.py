import streamlit as st
from pptx import Presentation
from fpdf import FPDF
import os
from PIL import Image
import easyocr
import numpy as np

# تهيئة قارئ النصوص للصور (OCR) باللغتين الفرنسية والإنجليزية
@st.cache_resource
def load_reader():
    return easyocr.Reader(['fr', 'en'])

reader = load_reader()

st.set_page_config(page_title="صانع الجذاذات الرياضية الذكي", layout="centered")
st.title("📚 منصة توليد الجذاذات الرياضية من الباوربوينت")

st.markdown("""
رفع عرض الباوربوينت الخاص بالدرس سيقوم بـ:
1. استخراج النصوص العادية ومعالجة صور المعادلات والفقرات بترتيب الشرائح.
2. تنسيق الجذاذة بالألوان البيداغوجية المطلوبة تلقائياً.
3. تصدير ملف PDF جاهز للطباعة.
""")

uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت (PPTX)", type=["pptx"])

if uploaded_ppt and st.button("توليد الجذاذة وتحويلها إلى PDF"):
    with st.spinner("جاري استخراج النصوص وقراءة المعادلات من الصور وتنسيق الجذاذة..."):
        prs = Presentation(uploaded_ppt)
        all_content = []
        
        os.makedirs("temp_slides_img", exist_ok=True)

        for slide_idx, slide in enumerate(prs.slides, start=1):
            slide_elements = []
            slide_elements.append(("TITLE_SLIDE", f"--- الشريحة رقم {slide_idx} ---"))
            
            for shape in slide.shapes:
                # 1. استخراج النصوص العادية المباشرة
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        txt = paragraph.text.strip()
                        if txt:
                            slide_elements.append(("TEXT", txt))
                
                # 2. استخراج وقراءة الصور والمعادلات الموجودة في الشريحة
                elif shape.shape_type == 13: # صورة
                    try:
                        image_bytes = shape.image.blob
                        img_path = f"temp_slides_img/slide_{slide_idx}_img.png"
                        with open(img_path, "wb") as f:
                            f.write(image_bytes)
                        
                        # استخدام OCR لقراءة النص أو المعادلة داخل الصورة
                        results = reader.readtext(img_path)
                        for (_, text, _) in results:
                            if text.strip():
                                slide_elements.append(("TEXT", text.strip()))
                    except Exception:
                        pass
            
            all_content.extend(slide_elements)

        # توليد ملف الـ PDF بالتنسيق والألوان المطلوبة
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=10)

        for el_type, text in all_content:
            if el_type == "TITLE_SLIDE":
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(100, 100, 100)
                safe_txt = text.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 6, txt=safe_txt)
                pdf.ln(2)
                continue

            # تطبيق قواعد الألوان البيداغوجية حسب طلبك:
            r, g, b = 0, 0, 0  # الافتراضي: أسود لباقي الفقرات
            is_bold = False

            # 1. أحمر عناوين للأرقام الرومانية (I, II, III...)
            if text.startswith("I") or text.startswith("V") or text.startswith("X") or "---" in text:
                if any(text.startswith(roman) for roman in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]):
                    r, g, b = 200, 0, 0  # أحمر
                    is_bold = True
            
            # 2. أخضر للعناوين بالأرقام العادية (1, 2...)
            if any(text.startswith(f"{i})") or text.startswith(f"{i} -") for i in range(1, 15)):
                r, g, b = 0, 128, 0  # أخضر
                is_bold = True

            # 3. Règle: بنفسجي
            if "Règle" in text or "Regle" in text:
                r, g, b = 128, 0, 128  # بنفسجي
                is_bold = True

            # 4. Activité, Exemple, Définition: أزرق سماوي
            if any(k in text for k in ["Activité", "Activite", "Exemple", "Exemples", "Définition", "Definition", "Remarque"]):
                r, g, b = 0, 102, 204  # أزرق سماوي
                is_bold = True

            # 5. Propriété: برتقالي
            if "Propriété" in text or "Propriete" in text:
                r, g, b = 255, 128, 0  # برتقالي
                is_bold = True

            # 6. Application, Exercice d'application: بني
            if any(k in text for k in ["Application", "Exercice", "Exercices"]):
                r, g, b = 139, 69, 19  # بني
                is_bold = True

            pdf.set_font("Helvetica", "B" if is_bold else "", 10)
            pdf.set_text_color(r, g, b)
            
            safe_text = text.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 7, txt=safe_text)

        pdf_output = pdf.output()

        st.success("تم توليد الجذاذة بنجاح وبنفس الألوان والترتيب المطلوب!")
        
        st.download_button(
            label="⬇️ تحميل الجذاذة النهائية بصيغة PDF",
            data=bytes(pdf_output),
            file_name="Jadad_Mathematiques_Pro.pdf",
            mime="application/pdf"
        )
