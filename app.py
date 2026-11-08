import streamlit as st
from pptx import Presentation
import os
import base64
from PIL import Image, ImageOps
import io

st.set_page_config(page_title="صانع الجذاذات الرياضية الرسمي", layout="wide")
st.title("📚 صانع الجذاذات الرياضية - التصوير المباشر للشرائح")

uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت الخاص بالدرس (PPTX)", type=["pptx"])

if uploaded_ppt and st.button("توليد الجذاذة بالشرائح الكاملة والنظيفة"):
    with st.spinner("جاري استخراج وتحويل الشرائح وتبييض خلفياتها..."):
        prs = Presentation(uploaded_ppt)
        slide_images_base64 = []

        # استخراج كافة الصور والرسومات المكونة للشريحة ودمجها كصورة موحدة للشريحة
        for slide_idx, slide in enumerate(prs.slides, start=1):
            # إنشاء لوحة بيضاء تمثل الشريحة بأبعاد 16:9
            slide_canvas = Image.new("RGB", (1280, 720), "WHITE")
            
            shapes_found = False
            for shape in slide.shapes:
                if shape.shape_type == 13: # صور أو كتل مرسومة
                    try:
                        img_bytes = shape.image.blob
                        img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
                        
                        # تبييض أي خلفية ملونة أو قالب محيط بالصورة
                        temp_bg = Image.new("RGBA", img.size, "WHITE")
                        temp_bg.paste(img, (0, 0), img)
                        img_rgb = temp_bg.convert("RGB")
                        
                        # لصق المحتوى في لوحة الشريحة البيضاء
                        slide_canvas.paste(img_rgb, (0, 0))
                        shapes_found = True
                    except Exception:
                        pass
            
            # إذا وجدت محتويات في الشريحة، نحفظها كصورة نظيفة
            buffer = io.BytesIO()
            slide_canvas.save(buffer, format="PNG")
            encoded_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
            slide_images_base64.append(f"data:image/png;base64,{encoded_img}")

        # دمج كل شريحتين معاً في صفحة واحدة
        paired_slides = [slide_images_base64[i:i + 2] for i in range(0, len(slide_images_base64), 2)]

        html_content = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <style>
                @page {
                    size: A4 landscape;
                    margin: 5mm;
                }
                body {
                    background-color: #555;
                    margin: 0;
                    padding: 10px;
                    font-family: Arial, sans-serif;
                    direction: ltr;
                    color: #000000;
                }
                .print-bar {
                    text-align: center;
                    margin-bottom: 15px;
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
                    width: 287mm;
                    height: 198mm;
                    padding: 8mm;
                    margin: 0 auto 20px auto;
                    box-sizing: border-box;
                    box-shadow: 0 0 10px rgba(0,0,0,0.3);
                    page-break-after: always;
                }
                table.fiche-table {
                    width: 100%;
                    height: 100%;
                    border-collapse: collapse;
                    table-layout: fixed;
                }
                table.fiche-table th, table.fiche-table td {
                    border: 1px solid #000000;
                    padding: 6px;
                    vertical-align: top;
                    box-sizing: border-box;
                }
                table.fiche-table th {
                    background-color: #f8f9fa;
                    text-align: center;
                    font-size: 11px;
                    font-weight: bold;
                    color: #000;
                }
                .col-seance { width: 7%; text-align: center; }
                .col-duree { width: 7%; text-align: center; }
                .col-contenu { width: 52%; text-align: center; }
                .col-ens { width: 11%; }
                .col-app { width: 11%; }
                .col-obs { width: 12%; }

                .slide-img-block {
                    width: 100%;
                    max-height: 82mm;
                    object-fit: contain;
                    display: block;
                    margin: 4px auto;
                    background: #ffffff;
                }
                .slide-sep {
                    border-bottom: 1px dashed #bbb;
                    margin: 6px 0;
                }
                @media print {
                    .print-bar { display: none; }
                    body { background: #ffffff; padding: 0; }
                    .page-card { box-shadow: none; width: 100%; height: 100vh; padding: 0; margin: 0; }
                }
            </style>
        </head>
        <body>
            <div class="print-bar">
                <button class="btn-pdf" onclick="window.print()">📥 حفظ / طباعة ملف PDF (شريحتان بالصفحة)</button>
            </div>
        """

        for page_idx, slide_pair in enumerate(paired_slides, start=1):
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

            for idx, slide_img in enumerate(slide_pair):
                if idx > 0:
                    html_content += '<div class="slide-sep"></div>'
                html_content += f'<img src="{slide_img}" class="slide-img-block">'

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

        st.success("تم تجهيز الجذاذة بنجاح بالشرائح الكاملة والخلفية البيضاء!")
        st.components.v1.html(html_content, height=680, scrolling=True)

        st.download_button(
            label="⬇️ تحميل الجذاذة (HTML جاهز للحفظ كـ PDF)",
            data=html_content.encode('utf-8'),
            file_name="Jadad_Perfect_Slides.html",
            mime="html"
                                )
        
