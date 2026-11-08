import streamlit as st
from pptx import Presentation
import os
import base64
from PIL import Image, ImageEnhance
import io

st.set_page_config(page_title="صانع الجذاذات الرياضية الرسمي", layout="wide")
st.title("📚 صانع الجذاذات الرياضية - التصوير الكامل للشرائح مع تبييض الخلفية")

uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت الخاص بالدرس (PPTX)", type=["pptx"])

def process_slide_to_clean_image(shape_images):
    """ دمج وتصفية عناصر الشريحة للحصول على صورة بيضاء نقية تحتوي المحتوى فقط """
    try:
        # إنشاء خلفية بيضاء بمقاسات الشريحة القياسية
        combined_img = Image.new("RGB", (1000, 562), "WHITE")
        
        for img_bytes in shape_images:
            try:
                img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
                w, h = img.size
                
                # استبعاد الصور الكبيرة جداً التي تمثل خلفية القالب
                if w > 850 and h > 480:
                    continue
                
                # تحويل الخلفيات الشفافة أو الملصقة إلى بيضاء وتصحيح التباين
                temp_img = Image.new("RGBA", img.size, "WHITE")
                temp_img.paste(img, (0, 0), img)
                temp_rgb = temp_img.convert("RGB")
                
                # تضخيم النقاء والتأكد من إزالة أي أثر ملون للخلفية
                enhancer = ImageEnhance.Contrast(temp_rgb)
                temp_rgb = enhancer.enhance(1.2)
                
                # لصق المحتوى المصفى على الصفحة البيضاء
                combined_img.paste(temp_rgb, (0, 0))
            except Exception:
                pass

        buffer = io.BytesIO()
        combined_img.save(buffer, format="PNG")
        encoded_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{encoded_img}"
    except Exception:
        return None

if uploaded_ppt and st.button("توليد الجذاذة بالشرائح النظيفة (شريحتان لكل صفحة)"):
    with st.spinner("جاري تحويل وتصفية الشرائح وتثبيت التنسيق..."):
        prs = Presentation(uploaded_ppt)
        slides_clean_images = []

        for slide_idx, slide in enumerate(prs.slides, start=1):
            slide_shapes_bytes = []
            
            for shape in slide.shapes:
                if shape.shape_type == 13: # صورة أو معادلة مدمجة
                    try:
                        image_bytes = shape.image.blob
                        # استبعاد الأيقونات الصغرى
                        if len(image_bytes) > 2500:
                            slide_shapes_bytes.append(image_bytes)
                    except Exception:
                        pass
            
            # معالجة الشريحة وإرجاع صورتها النظيفة
            cleaned_slide_img = process_slide_to_clean_image(slide_shapes_bytes)
            if cleaned_slide_img:
                slides_clean_images.append(cleaned_slide_img)

        # دمج كل شريحتين معاً في قائمة واحدة
        paired_slides = [slides_clean_images[i:i + 2] for i in range(0, len(slides_clean_images), 2)]

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
                    max-width: 95%;
                    max-height: 85mm;
                    height: auto;
                    display: block;
                    margin: 5px auto;
                    background: #ffffff;
                    filter: contrast(115%) brightness(102%);
                    mix-blend-mode: multiply;
                }
                .slide-sep {
                    border-bottom: 1px dashed #ccc;
                    margin: 8px 0;
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

        st.success("تم تحويل وتبييض الشرائح وتنسيق شريحتين لكل صفحة بنجاح!")
        st.components.v1.html(html_content, height=680, scrolling=True)

        st.download_button(
            label="⬇️ تحميل الجذاذة (HTML جاهز للحفظ كـ PDF)",
            data=html_content.encode('utf-8'),
            file_name="Jadad_2Slides_Clean.html",
            mime="html"
        )
ue)

        st.download_button(
            label="⬇️ تحميل ملف الجذاذة (HTML جاهز للطباعة كـ PDF)",
            data=html_content.encode('utf-8'),
            file_name="Jadad_Math_2Slides_PerPage.html",
            mime="html"
        )
