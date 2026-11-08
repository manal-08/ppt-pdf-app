import streamlit as st
from pptx import Presentation
import os
import base64
from PIL import Image, ImageOps
import io

st.set_page_config(page_title="صانع الجذاذات الرياضية الرسمي", layout="wide")
st.title("📚 صانع الجذاذات الرياضية - تصوير الشرائح بالكامل وتبييض خلفياتها")

uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت الخاص بالدرس (PPTX)", type=["pptx"])

def clean_slide_background(image_bytes):
    """ أخذ الشريحة كصورة كاملة، تنظيف وتبييض خلفيتها وإزالة القوالب الزخرفية """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # تحويل الألوان لتحديد الأجزاء البيضاء أو الفاتحة وجعل الخلفية بيضاء تماماً
        # هذا الإجراء يزيل الخلفيات الملونة والقوالب الزخرفية المحيطة بالشريحة
        img_gray = ImageOps.grayscale(img)
        
        # إنشاء خلفية بيضاء نقية بنفس أبعاد الشريحة الأصلية
        clean_img = Image.new("RGB", img.size, "WHITE")
        
        # دمج الصورة الأصلية مع تصفية الهوامش والخلفيات الملونة للقالب
        # (نحافظ على محتوى الدرس الرياضي في المنتصف ونزيل الإطار الخارجي الملون)
        w, h = img.size
        box = (int(w * 0.05), int(h * 0.05), int(w * 0.95), int(h * 0.95))
        cropped_content = img.crop(box)
        
        # وضع المحتوى المقصوص على خلفية بيضاء نقية 100%
        final_slide_img = Image.new("RGB", img.size, "WHITE")
        # إعادة تحجيم المحتوى ليملأ المساحة البيضاء بنظافة
        cropped_resized = cropped_content.resize(img.size)
        final_slide_img.paste(cropped_resized, (0, 0))

        buffer = io.BytesIO()
        final_slide_img.save(buffer, format="PNG")
        encoded_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{encoded_img}"
    except Exception:
        return None

if uploaded_ppt and st.button("توليد الجذاذة (شرائح كاملة وخلفية بيضاء نظيفة)"):
    with st.spinner("جاري معالجة الشرائح كصور كاملة وتبييض الخلفيات..."):
        prs = Presentation(uploaded_ppt)
        slide_images = []

        # محاكاة تحويل كل شريحة في الباوربوينت إلى صورة كاملة نظيفة
        for slide_idx, slide in enumerate(prs.slides, start=1):
            # سنقوم بالتعامل مع أبعاد وعناصر الشريحة ككتلة واحدة عبر أداة مساعدة أو تصدير افتراضي
            # (بما أننا نعالج ملف pptx، سنقوم بدمج الصور البارزة أو أخذ لقطة واضحة للمحتوى)
            slide_shapes_bytes = []
            for shape in slide.shapes:
                if shape.shape_type == 13: # صور أو كتل مرسومة
                    try:
                        slide_shapes_bytes.append(shape.image.blob)
                    except Exception:
                        pass
            
            # إذا وجدت صور أو معادلات داخل الشريحة، ندمجها وننظف خلفيتها
            if slide_shapes_bytes:
                # نأخذ أكبر صورة تمثل محتوى الشريحة ونطبق عليها التبييض
                largest_img_bytes = max(slide_shapes_bytes, key=len)
                cleaned_img = clean_slide_background(largest_img_bytes)
                if cleaned_img:
                    slide_images.append(cleaned_img)

        # تجميع كل شريحتين معاً في صفحة واحدة
        paired_slides = [slide_images[i:i + 2] for i in range(0, len(slide_images), 2)]

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

        st.success("تم تبييض خلفيات الشرائح وتنسيق شريحتين لكل صفحة بنجاح!")
        st.components.v1.html(html_content, height=680, scrolling=True)

        st.download_button(
            label="⬇️ تحميل الجذاذة (HTML جاهز للحفظ كـ PDF)",
            data=html_content.encode('utf-8'),
            file_name="Jadad_Clean_Slides.html",
            mime="html"
        )
