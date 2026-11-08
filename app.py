import streamlit as st
from pptx import Presentation
import os
import base64
from PIL import Image
import io

st.set_page_config(page_title="صانع الجذاذات الرياضية الرسمي", layout="wide")
st.title("📚 صانع الجذاذات الرياضية - تصدير PDF أبيض ومقسم (شريحتان لكل صفحة)")

uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت الخاص بالدرس (PPTX)", type=["pptx"])

def process_image_remove_background(image_bytes):
    """ معالجة الصور والتأكد من تحويل أي خلفية داكنة أو خاصة بالقالب إلى اللون الأبيض الناصع """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert("RGBA")
        
        # استبعاد الصور الكبيرة جداً التي قد تكون خلفية الشريحة بالكامل
        width, height = img.size
        if width > 800 and height > 450:
            return None

        # إنشاء صورة جديدة بخلفية بيضاء
        new_img = Image.new("RGBA", img.size, "WHITE")
        new_img.paste(img, (0, 0), img)
        final_img = new_img.convert("RGB")
        
        buffer = io.BytesIO()
        final_img.save(buffer, format="PNG")
        encoded_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{encoded_img}"
    except Exception:
        return None

if uploaded_ppt and st.button("توليد الجذاذة بتنسيق PDF المثالي"):
    with st.spinner("جاري تنظيف القوالب والمعادلات وتنظيم شريحتين لكل صفحة..."):
        prs = Presentation(uploaded_ppt)
        slides_data = []

        for slide_idx, slide in enumerate(prs.slides, start=1):
            slide_elements = []
            
            for shape in slide.shapes:
                # استخراج النصوص
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        txt = paragraph.text.strip()
                        if txt:
                            slide_elements.append(("TEXT", txt))
                
                # استخراج الصور وتصفية الخلفيات
                elif shape.shape_type == 13: # Picture
                    try:
                        image_bytes = shape.image.blob
                        # استبعاد الأيقونات الصغيرة جداً أو الصور الضخمة (خلفيات القالب)
                        if len(image_bytes) < 4000 or len(image_bytes) > 250000:
                            continue
                        
                        img_tag = process_image_remove_background(image_bytes)
                        if img_tag:
                            slide_elements.append(("IMAGE", img_tag))
                    except Exception:
                        pass
            
            if slide_elements:
                slides_data.append(slide_elements)

        # تجميع كل شريحتين معاً في صفحة واحدة
        paired_slides = [slides_data[i:i + 2] for i in range(0, len(slides_data), 2)]

        html_content = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <style>
                @page {
                    size: A4 landscape;
                    margin: 8mm;
                }
                body {
                    background-color: #f0f0f0;
                    margin: 0;
                    padding: 10px;
                    font-family: Arial, sans-serif;
                    direction: ltr;
                    color: #000000;
                }
                .print-bar {
                    text-align: center;
                    margin-bottom: 20px;
                }
                .btn-pdf {
                    background-color: #28a745;
                    color: white;
                    padding: 12px 25px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                    font-weight: bold;
                }
                .page-card {
                    background-color: #ffffff;
                    width: 285mm;
                    height: 195mm;
                    padding: 10mm;
                    margin: 0 auto 20px auto;
                    box-sizing: border-box;
                    box-shadow: 0 0 10px rgba(0,0,0,0.15);
                    page-break-after: always;
                    display: flex;
                    flex-direction: column;
                }
                table.fiche-table {
                    width: 100%;
                    height: 100%;
                    border-collapse: collapse;
                    table-layout: fixed;
                    background-color: #ffffff;
                }
                table.fiche-table th, table.fiche-table td {
                    border: 1px solid #000000;
                    padding: 6px 8px;
                    vertical-align: top;
                    box-sizing: border-box;
                    word-wrap: break-word;
                }
                table.fiche-table th {
                    background-color: #ffffff;
                    text-align: center;
                    font-size: 11px;
                    font-weight: bold;
                    color: #000000;
                }
                .col-seance { width: 7%; text-align: center; }
                .col-duree { width: 7%; text-align: center; }
                .col-contenu { width: 52%; }
                .col-ens { width: 11%; }
                .col-app { width: 11%; }
                .col-obs { width: 12%; }

                .slide-divider {
                    border-bottom: 1px dashed #bbb;
                    margin: 12px 0;
                    padding-bottom: 4px;
                }
                .content-line {
                    margin: 4px 0;
                    line-height: 1.35;
                    font-size: 12.5px;
                }
                .math-image {
                    max-width: 45%;
                    height: auto;
                    display: block;
                    margin: 6px auto;
                    background: #ffffff;
                    filter: contrast(110%);
                }
                @media print {
                    .print-bar { display: none; }
                    body { background: #ffffff; padding: 0; }
                    .page-card { 
                        box-shadow: none; 
                        width: 100%; 
                        height: 100vh;
                        padding: 0;
                        margin: 0;
                        page-break-after: always;
                    }
                }
            </style>
        </head>
        <body>
            <div class="print-bar">
                <button class="btn-pdf" onclick="window.print()">📥 حفظ/طباعة ملف PDF (شريحتان في كل صفحة)</button>
            </div>
        """

        for page_idx, page_pair in enumerate(paired_slides, start=1):
            html_content += f"""
            <div class="page-card">
                <table class="fiche-table">
                    <thead>
                        <tr>
                            <th class="col-seance">Séance</th>
                            <th class="col-duree">Durée</th>
                            <th class="col-contenu">Contenu (Page {page_idx})</th>
                            <th class="col-ens">Rôle de l'enseignant</th>
                            <th class="col-app">Rôle de l'apprenant</th>
                            <th class="col-obs">Observation</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="col-seance"></td>
                            <td class="col-duree"></td>
                            <td class="col-contenu">
            """

            for slide_num, slide_elements in enumerate(page_pair):
                if slide_num > 0:
                    html_content += '<div class="slide-divider"></div>'

                for el_type, text_or_img in slide_elements:
                    if el_type == "IMAGE":
                        html_content += f'<img src="{text_or_img}" class="math-image">'
                        continue

                    text = text_or_img
                    color = "#000000"
                    weight = "normal"

                    # تلوين عناوين الرياضيات بيداغوجياً
                    if any(text.startswith(r) for r in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]):
                        color = "#C80000"
                        weight = "bold"
                    elif any(text.startswith(f"{i})") or text.startswith(f"{i} -") for i in range(1, 15)):
                        color = "#008000"
                        weight = "bold"
                    elif "Règle" in text or "Regle" in text:
                        color = "#800080"
                        weight = "bold"
                    elif any(k in text for k in ["Activité", "Activite", "Exemple", "Exemples", "Définition", "Definition", "Remarque"]):
                        color = "#0066CC"
                        weight = "bold"
                    elif "Propriété" in text or "Propriete" in text:
                        color = "#FF8000"
                        weight = "bold"
                    elif any(k in text for k in ["Application", "Exercice", "Exercices"]):
                        color = "#8B4513"
                        weight = "bold"

                    html_content += f'<div class="content-line" style="color: {color}; font-weight: {weight};">{text}</div>'

            html_content += """
                            </td>
                            <td class="col-ens"></td>
                            <td class="col-app"></td>
                            <td class="col-obs"></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """

        html_content += """
        </body>
        </html>
        """

        st.success("تم تجهيز الجذاذة بنجاح مع إزالة خلفيات القوالب وتخصيص شريحتين لكل صفحة!")
        st.components.v1.html(html_content, height=680, scrolling=True)

        st.download_button(
            label="⬇️ تحميل ملف الجذاذة (HTML جاهز للطباعة كـ PDF)",
            data=html_content.encode('utf-8'),
            file_name="Jadad_Math_2Slides_PerPage.html",
            mime="html"
        )
