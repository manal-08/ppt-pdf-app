import streamlit as st
from pptx import Presentation
import os
import base64

st.set_page_config(page_title="صانع الجذاذات الرياضية الرسمي", layout="wide")
st.title("📚 صانع الجذاذات الرياضية - التقسيم التلقائي للصفحات")

uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت الخاص بالدرس (PPTX)", type=["pptx"])

if uploaded_ppt and st.button("توليد الجذاذة بالصفحات المنظمة"):
    with st.spinner("جاري تحليل الدرس وتوزيعه على صفحات A4 منظمة..."):
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

        # تصميم جدول أفقي مع تقسيم تلقائي للأسطر على صفحات متعددة عند الطباعة
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
                    background-color: #555;
                    margin: 0;
                    padding: 10px;
                    display: flex;
                    justify-content: center;
                }
                .a4-page {
                    background-color: #ffffff;
                    width: 297mm;
                    min-height: 210mm;
                    padding: 10mm;
                    margin: 10px auto;
                    box-shadow: 0 0 10px rgba(0,0,0,0.3);
                    box-sizing: border-box;
                    font-family: Arial, sans-serif;
                    direction: ltr;
                    color: #000000;
                    font-size: 13px;
                    page-break-after: always; /* فصل الصفحات تلقائياً */
                }
                table.fiche-table {
                    width: 100%;
                    border-collapse: collapse;
                    table-layout: fixed;
                }
                table.fiche-table th, table.fiche-table td {
                    border: 1px solid #000000;
                    padding: 8px;
                    vertical-align: top;
                    box-sizing: border-box;
                }
                table.fiche-table th {
                    background-color: #f2f2f2;
                    text-align: center;
                    font-size: 12px;
                    font-weight: bold;
                    color: #333;
                }
                .col-seance { width: 7%; text-align: center; }
                .col-duree { width: 7%; text-align: center; }
                .col-contenu { width: 52%; }
                .col-ens { width: 11%; }
                .col-app { width: 11%; }
                .col-obs { width: 12%; }

                .content-line {
                    margin: 6px 0;
                    line-height: 1.4;
                }
                .slide-image {
                    max-width: 40%;
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
                    .a4-page { box-shadow: none; margin: 0; page-break-after: always; }
                }
            </style>
        </head>
        <body>
        """

        # تقسيم المحتوى إلى أجزاء (مثلاً كل 12 عنصراً في صفحة لضمان عدم الاكتظاظ)
        chunk_size = 12
        chunks = [all_elements[i:i + chunk_size] for i in range(0, len(all_elements), chunk_size)]
        if not chunks:
            chunks = [[]]

        for chunk in chunks:
            html_content += """
            <div class="a4-page">
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

            for el_type, text_or_img in chunk:
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
            """

        html_content += """
        </body>
        </html>
        """

        st.success("تم توزيع الجذاذة وتنسيقها على صفحات A4 متسلسلة بنجاح!")
        
        st.markdown("### 📄 معاينة الجذاذة النهائية:")
        st.components.v1.html(html_content, height=700, scrolling=True)

        st.download_button(
            label="⬇️ تحميل الجذاذة كملف HTML (جاهز للطباعة وتوزيعه على صفحات PDF)",
            data=html_content.encode('utf-8'),
            file_name="Jadad_Multi_Pages.html",
            mime="html"
                            )
                
