import streamlit as st
from pptx import Presentation
from fpdf import FPDF
import os
import easyocr
import numpy as np

@st.cache_resource
def load_reader():
    return easyocr.Reader(['fr', 'en'])

reader = load_reader()

st.set_page_config(page_title="صانع الجذاذات الرياضية الذكي", layout="centered")
st.title("📚 منصة توليد الجذاذات الرياضية من الباوربوينت")

uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت (PPTX)", type=["pptx"])

if uploaded_ppt and st.button("توليد الجذاذة وتحويلها إلى PDF"):
    with st.spinner("جاري استخراج النصوص والمعادلات وتنسيق الجذاذة..."):
        prs = Presentation(uploaded_ppt)
        all_content = []
        
        os.makedirs("temp_slides_img", exist_ok=True)

        for slide_idx, slide in enumerate(prs.slides, start=1):
            all_content.append(("TITLE_SLIDE", f"--- الشريحة رقم {slide_idx} ---"))
            
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        txt = paragraph.text.strip()
                        if txt:
                            all_content.append(("TEXT", txt))
                
                elif shape.shape_type == 13:
                    try:
                        image_bytes = shape.image.blob
                        img_path = f"temp_slides_img/slide_{slide_idx}_img.png"
                        with open(img_path, "wb") as f:
                            f.write(image_bytes)
                        
                        results = reader.readtext(img_path)
                        for (_, text, _) in results:
                            if text.strip():
                                all_content.append(("TEXT", text.strip()))
                    except Exception:
                        pass

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=9)

        for el_type, text in all_content:
            if el_type == "TITLE_SLIDE":
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(100, 100, 100)
                safe_txt = text.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 5, txt=safe_txt)
                pdf.ln(1)
                continue

            r, g, b = 0, 0, 0
            is_bold = False

            if any(text.startswith(roman) for roman in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]):
                r, g, b = 200, 0, 0
                is_bold = True
            elif any(text.startswith(f"{i})") or text.startswith(f"{i} -") for i in range(1, 15)):
                r, g, b = 0, 128, 0
                is_bold = True
            elif "Règle" in text or "Regle" in text:
                r, g, b = 128, 0, 128
                is_bold = True
            elif any(k in text for k in ["Activité", "Activite", "Exemple", "Exemples", "Définition", "Definition", "Remarque"]):
                r, g, b = 0, 102, 204
                is_bold = True
            elif "Propriété" in text or "Propriete" in text:
                r, g, b = 255, 128, 0
                is_bold = True
            elif any(k in text for k in ["Application", "Exercice", "Exercices"]):
                r, g, b = 139, 69, 19
                is_bold = True

            pdf.set_font("Helvetica", "B" if is_bold else "", 9)
            pdf.set_text_color(r, g, b)
            
            # تقطيع الكلمات الطويلة لمنع حدوث خطأ المساحة
            words = text.split()
            current_line = ""
            for word in words:
                safe_word = word.encode('latin-1', 'replace').decode('latin-1')
                if pdf.get_string_width(current_line + " " + safe_word) < 180:
                    current_line += (" " + safe_word) if current_line else safe_word
                else:
                    pdf.multi_cell(0, 6, txt=current_line)
                    current_line = safe_word
            if current_line:
                pdf.multi_cell(0, 6, txt=current_line)

        pdf_output = pdf.output()

        st.success("تم توليد الجذاذة بنجاح وبدون أخطاء!")
        st.download_button(
            label="⬇️ تحميل الجذاذة بصيغة PDF",
            data=bytes(pdf_output),
            file_name="Jadad_Mathematiques_Pro.pdf",
            mime="application/pdf"
        )
