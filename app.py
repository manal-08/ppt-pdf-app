import streamlit as st
from pptx import Presentation
import os

st.set_page_config(page_title="صانع الجذاذات الرياضية الذكي", layout="centered")
st.title("📚 منصة توليد الجذاذات الرياضية الرسمية")

uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت الخاص بالدرس (PPTX)", type=["pptx"])

if uploaded_ppt and st.button("توليد الجذاذة بتصميم A4"):
    with st.spinner("جاري تنسيق الجذاذة بالمقاسات والألوان المطلوبة..."):
        prs = Presentation(uploaded_ppt)
        all_content = []
        
        for slide_idx, slide in enumerate(prs.slides, start=1):
            all_content.append(("TITLE_SLIDE", f"--- الشريحة رقم {slide_idx} ---"))
            
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        txt = paragraph.text.strip()
                        if txt:
                            all_content.append(("TEXT", txt))

        # تصميم صفحة A4 بيضاء نقية ومنسقة بدقة للطباعة
        html_content = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    background-color: #555;
                    margin: 0;
                    padding: 20px;
                    display: flex;
                    justify-content: center;
                }
                .a4-page {
                    background-color: #ffffff;
                    width: 210mm;
                    min-height: 297mm;
                    padding: 20mm;
                    margin: auto;
                    box-shadow: 0 0 10px rgba(0,0,0,0.3);
                    box-sizing: border-box;
                    font-family: Arial, sans-serif;
                    direction: ltr;
                    color: #000000;
                    font-size: 14px;
                    line-height: 1.5;
                }
                h3.slide-title {
                    color: #646464;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 4px;
                    margin-top: 20px;
                    font-size: 15px;
                }
                p.content-line {
                    margin: 6px 0;
                }
                @media print {
                    body { background: none; padding: 0; }
                    .a4-page { box-shadow: none; width: 100%; padding: 10mm; }
                }
            </style>
        </head>
        <body>
            <div class="a4-page">
                <h2 style="text-align: center; color: #333; margin-bottom: 20px;">Fiche Pédagogique - Mathématiques</h2>
        """

        for el_type, text in all_content:
            if el_type == "TITLE_SLIDE":
                html_content += f'<h3 class="slide-title">{text}</h3>'
                continue

            color = "#000000"  # الأسود لباقي الفقرات
            weight = "normal"

            # تطبيق الألوان البيداغوجية حسب طلبك:
            if any(text.startswith(roman) for roman in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]):
                color = "#C80000"  # أحمر عناوين للأرقام الرومانية
                weight = "bold"
            elif any(text.startswith(f"{i})") or text.startswith(f"{i} -") for i in range(1, 15)):
                color = "#008000"  # أخضر للعناوين العادية
                weight = "bold"
            elif "Règle" in text or "Regle" in text:
                color = "#800080"  # بنفسجي للقواعد
                weight = "bold"
            elif any(k in text for k in ["Activité", "Activite", "Exemple", "Exemples", "Définition", "Definition", "Remarque"]):
                color = "#0066CC"  # أزرق سماوي للأنشطة والتعريفات والأمثلة
                weight = "bold"
            elif "Propriété" in text or "Propriete" in text:
                color = "#FF8000"  # برتقالي للخاصيات
                weight = "bold"
            elif any(k in text for k in ["Application", "Exercice", "Exercices"]):
                color = "#8B4513"  # بني للتطبيقات والتمارين
                weight = "bold"

            html_content += f'<p class="content-line" style="color: {color}; font-weight: {weight};">{text}</p>'

        html_content += """
            </div>
        </body>
        </html>
        """

        st.success("تم توليد الجذاذة بتصميم A4 والألوان البيداغوجية بنجاح!")
        
        # معاينة الجذاذة داخل الإطار
        st.markdown("### 📄 معاينة الجذاذة (بمقاسات A4 وخلفية بيضاء):")
        st.components.v1.html(html_content, height=600, scrolling=True)

        # زر التحميل المباشر
        st.download_button(
            label="⬇️ تحميل الجذاذة كملف HTML (اضغط Ctrl+P للطباعة كـ PDF)",
            data=html_content.encode('utf-8'),
            file_name="Jadad_A4_Mathematiques.html",
            mime="text/html"
        )
