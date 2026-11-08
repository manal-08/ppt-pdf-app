import streamlit as st
from pptx import Presentation
import os
import base64
from PIL import Image
import io

st.set_page_config(page_title="صانع الجذاذات الرياضية الرسمي", layout="wide")

st.title("📚 صانع الجذاذات - القص الدقيق للإطار وتحويل الشرائح لـ PDF")

uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت الخاص بالدرس (PPTX)", type=["pptx"])

# زر لإتاحة تعديل نسبة قص الهامش المزخرف إن أردتِ التحكم فيها
crop_ratio = st.slider("نسبة قص الإطار المزخرف من الجوانب (%)", min_value=0, max_value=20, value=9)

def process_slide_to_clean_image(image_bytes, crop_pct):
    """ أخذ صورة الشريحة، قص الجوانب المزخرفة، والحفاظ على معادلات الدرس """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = img.size

        # حساب هوامش القص المستطيلي بحسب النسبة
        left = int(w * (crop_pct / 100.0))
        top = int(h * (crop_pct / 100.0))
        right = int(w * (1.0 - (crop_pct / 100.0)))
        bottom = int(h * (1.0 - (crop_pct / 100.0)))

        # قص المستطيل الخارجي وتصليح الخلفية
        cropped_img = img.crop((left, top, right, bottom))
        
        # تنقية الألوان الفاتحة وتوحيد الخلفية البيضاء
        data = cropped_img.getdata()
        new_data = []
        for item in data:
            # الألوان القريبة جداً من الأبيض تتحول لأبيض ناصع مع الحفاظ على النص والمعادلات
            if item[0] > 220 and item[1] > 220 and item[2] > 220:
                new_data.append((255, 255, 255))
            else:
                new_data.append(item)
        cropped_img.putdata(new_data)

        buffer = io.BytesIO()
        cropped_img.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{encoded}"
    except Exception:
        return None

# الزر المطلوب لتوليد الجذاذة فور رفع الملف
if uploaded_ppt and st.button("🚀 صنع الجذاذة (قص الإطار المزخرف + شريحتين بالصفحة)"):
    with st.spinner("جاري قص إطار الزينة وتنسيق شرائح الدرس..."):
        prs = Presentation(uploaded_ppt)
        clean_slides = []

        for slide in prs.slides:
            slide_shapes_bytes = []
            for shape in slide.shapes:
                if shape.shape_type == 13: # صورة الشريحة أو العناصر
                    try:
                        slide_shapes_bytes.append(shape.image.blob)
                    except Exception:
                        pass
            
            if slide_shapes_bytes:
                # أخذ الصورة الرئيسية المقابلة للشريحة
                main_bytes = max(slide_shapes_bytes, key=len)
                cleaned_img = process_slide_to_clean_image(main_bytes, crop_ratio)
                if cleaned_img:
                    clean_slides.append(cleaned_img)

        # دمج كل شريحتين متتاليتين في صفحة A4 واحدة
        paired_slides = [clean_slides[i:i + 2] for i in range(0, len(clean_slides), 2)]

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
                    color: #000;
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
                    width: 98%;
                    max-height: 84mm;
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

        st.success("تم توليد الجذاذة بنجاح! اضغطي على زر حفظ PDF بالأسفل.")
        st.components.v1.html(html_content, height=680, scrolling=True)

        st.download_button(
            label="⬇️ تحميل الجذاذة (HTML جاهز للحفظ كـ PDF)",
            data=html_content.encode('utf-8'),
            file_name="Jadada_Math_Final.html",
            mime="html"
        )
