import streamlit as st
from pptx import Presentation
import os
import base64

st.set_page_config(page_title="صانع الجذاذات الرياضية الرسمي", layout="wide")
st.title("📚 صانع الجذاذات الرياضية - تصميم الجدول الأفقي (A4 Landscape)")

uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت الخاص بالدرس (PPTX)", type=["pptx"])

if uploaded_ppt and st.button("توليد الجذاذة بتصميم الجدول الرسمي"):
    with st.spinner("جاري بناء الجذاذة وتنسيق المحتوى..."):
        prs = Presentation(uploaded_ppt)
        all_elements = []
        
        os.makedirs("extracted_slide_images", exist_ok=True)
        img_counter = 0

        for slide_idx, slide in enumerate(prs.slides, start=1):
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        txt = paragraph.text.strip()
                        if txt:
                            all_elements.append(("TEXT", txt))
                
                elif shape.shape_type == 13:
                    try:
                        image_bytes = shape.image.blob
                        if len(image_bytes) < 3000:
                            continue
                            
                        img_counter += 1
                        img_filename = f"extracted_slide_images/slide_{slide_idx}_img_{img_counter}.png"
                        with open(img_filename, "wb") as f:
                            f.write(image_bytes)
                        
                        with open(img_filename, "rb") as img_file:
                            encoded_img = base64.b64encode(img_file.read()).decode('utf-8')
                        img_tag = f"data:image/png;base64,{encoded_img}"
                        
                        all_elements.append(("IMAGE", img_tag))
                    except Exception:
                        pass

        # تصميم A4 Landscape مستقر مع تكرار ترويسة الجدول تلقائياً عند الطباعة
        html_content = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <style>
                @page {
                    size: A4 landscape;
                    margin: 10mm;
                }
                body {
                    background-color: #f0f0f0;
                    margin: 0;
                    padding: 20px;
                    font-family: Arial, sans-serif;
                    direction: ltr;
                    color: #000000;
                }
                .page-container {
                    background-color: #ffffff;
                    width: 100%;
                    max-width: 280mm;
                    margin: 0 auto;
                    padding: 15mm;
                    box-sizing: border-box;
                    box-shadow: 0 0 10px rgba(0,0,0,0.15);
                }
                table.fiche-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                table.fiche-table th, table.fiche-table td {
                    border: 1px solid #000000;
                    padding: 8px;
                    vertical-align: top;
                    box-sizing: border-box;
                    word-wrap: break-word;
                }
                table.fiche-table th {
                    background-color: #f2f2f2;
                    text-align: center;
                    font-size: 11px;
                    font-weight: bold;
                    color: #000;
                    height: 30px;
                }
                /* إجبار ترويسة الجدول على الظهور في أعلى كل صفحة جديدة عند الطباعة */
                thead { display: table-header-group; }
                tr { page-break-inside: avoid; }

                .col-seance { width: 6%; text-align: center; }
                .col-duree { width: 6%; text-align: center; }
                .col-contenu { width: 56%; }
                .col-ens { width: 10%; }
                .col-app { width: 10%; }
                .col-obs { width: 12%; }

                .content-line {
                    margin: 5px 0;
                    line-height: 1.4;
                    font-size: 13px;
                }
                .slide-image {
                    max-width: 45%;
                    height: auto;
                    display: block;
                    margin: 8px auto;
                    padding: 2px;
                    background: #ffffff;
                    filter: contrast(120%) brightness(105%);
                    mix-blend-mode: multiply;
                }
                @media print {
                    body { background: none; padding: 0; }
                    .page-container { box-shadow: none; max-width: 100%; padding: 0; }
                }
            </style>
        </head>
        <body>
            <div class="page-container">
                <table class="fiche-table">
                    <thead>
                        <tr>
                            <th class="col-seance">Séance</th>
                            <th class="col-duree">Durée</th>
                            <th class="col-contenu">Contenu</th>
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

        for el_type, text_or_img in all_elements:
            if el_type == "IMAGE":
                html_content += f'<img src="{text_or_img}" class="slide-image">'
                continue

            text = text_or_img
            color = "#000000"
            weight = "normal"

            if any(text.startswith(roman) for roman in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]):
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
        </body>
        </html>
        """

        st.success("تم توليد الجذاذة بنجاح!")
        st.components.v1.html(html_content, height=650, scrolling=True)

        st.download_button(
            label="⬇️ تحميل الجذاذة كملف HTML",
            data=html_content.encode('utf-8'),
            file_name="Jadad_Landscape_Fixed.html",
            mime="html"
        )
