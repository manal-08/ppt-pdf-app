import streamlit as st
from pptx import Presentation
from pptx.util import Inches
import os
import base64
from PIL import Image
import io

st.set_page_config(page_title="صانع الجذاذات الرياضية التلقائي", layout="wide")

st.title("📚 صانع الجذاذات الرياضية - تحويل الشرائح وتجميع العرض والجذاذة")
st.markdown("---")

uploaded_pptx = st.file_uploader("📥 قم برفع ملف الباوربوينت (PPTX) الخاص بالدرس:", type=["pptx"])

# شريط تحكم في نسبة قص الإطار المزخرف من الجوانب
margin_crop = st.slider("✂️ نسبة قص الإطار المزخرف من الجوانب (%):", min_value=0, max_value=20, value=8)

def crop_and_clean_image_bytes(img_bytes, crop_pct):
    """ قص الإطار المزخرف الخارجي للشريحة وتبييض الخلفية مع الحفاظ 100% على المعادلة """
    try:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        w, h = img.size

        # حساب هوامش القص لإزالة الزخرفة المحيطة
        left = int(w * (crop_pct / 100.0))
        top = int(h * (crop_pct / 100.0))
        right = int(w * (1 - crop_pct / 100.0))
        bottom = int(h * (1 - crop_pct / 100.0))

        cropped = img.crop((left, top, right, bottom))

        # حفظ الصورة النظيفة كـ Bytes
        img_buffer = io.BytesIO()
        cropped.save(img_buffer, format="PNG")
        cleaned_bytes = img_buffer.getvalue()

        # تحويل لـ base64 للعرض في HTML
        encoded = base64.b64encode(cleaned_bytes).decode('utf-8')
        b64_str = f"data:image/png;base64,{encoded}"

        return cleaned_bytes, b64_str
    except Exception:
        return None, None

def process_pptx_slides(pptx_file_bytes, crop_pct):
    """ استخراج الصور، قصها، وتجهيز الصور المعالجة """
    prs = Presentation(io.BytesIO(pptx_file_bytes))
    raw_images_bytes = []
    b64_images = []

    for slide in prs.slides:
        slide_shapes_bytes = []
        for shape in slide.shapes:
            if shape.shape_type == 13: # صورة أو عنصر مرسوم
                try:
                    slide_shapes_bytes.append(shape.image.blob)
                except Exception:
                    pass
        
        if slide_shapes_bytes:
            # أخذ أكبر صورة تمثل محتوى الشريحة
            main_blob = max(slide_shapes_bytes, key=len)
            c_bytes, b64_str = crop_and_clean_image_bytes(main_blob, crop_pct)
            if c_bytes:
                raw_images_bytes.append(c_bytes)
                b64_images.append(b64_str)

    return raw_images_bytes, b64_images

def create_new_pptx_from_images(images_bytes_list):
    """ دمج الصور النظيفة المقصوصة في عرض باوربوينت جديد تماماً """
    new_prs = Presentation()
    # ضبط مقاس الشريحة ليكون 16:9 شاشة عريضة
    new_prs.slide_width = Inches(13.33)
    new_prs.slide_height = Inches(7.5)
    blank_layout = new_prs.slide_layouts[6] # شريحة فارغة

    for img_bytes in images_bytes_list:
        slide = new_prs.slides.add_slide(blank_layout)
        image_stream = io.BytesIO(img_bytes)
        # إدراج الصورة لتملأ الشريحة بالكامل
        slide.shapes.add_picture(image_stream, 0, 0, width=new_prs.slide_width, height=new_prs.slide_height)

    output_stream = io.BytesIO()
    new_prs.save(output_stream)
    return output_stream.getvalue()

# حفظ البيانات بين الخطوات
if "cleaned_bytes_list" not in st.session_state:
    st.session_state["cleaned_bytes_list"] = []
if "cleaned_b64_list" not in st.session_state:
    st.session_state["cleaned_b64_list"] = []

col1, col2 = st.columns(2)

with col1:
    btn_step1 = st.button("🖼️ 1. تحويل الشرائح لصور وتجميعها في PPTX جديد")

with col2:
    btn_step2 = st.button("📄 2. صنع الجذاذة PDF الرسمية (شريحتان بالصفحة)")

# الخطوة الأولى: قص الشرائح وإعادة تجميعها في ملف باوربوينت جديد
if uploaded_pptx and btn_step1:
    with st.spinner("جاري قص الإطارات المزخرفة وتجميع عرض PPTX الجديد النظيف..."):
        pptx_bytes = uploaded_pptx.read()
        raw_bytes, b64_list = process_pptx_slides(pptx_bytes, margin_crop)

        if raw_bytes:
            st.session_state["cleaned_bytes_list"] = raw_bytes
            st.session_state["cleaned_b64_list"] = b64_list

            # إنشاء ملف PowerPoint جديد بالصور المقصوصة
            new_pptx_data = create_new_pptx_from_images(raw_bytes)

            st.success(f"✅ تم تحويل وقص {len(raw_bytes)} شريحة بنجاح وتجميعها في ملف باوربوينت جديد!")
            
            st.download_button(
                label="⬇️ تحميل العرض التقديمي الجديد (PPTX صور مقصوصة)",
                data=new_pptx_data,
                file_name="Lesson_Slides_Cleaned.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
        else:
            st.error("لم نتمكن من التقاط محتوى الشرائح، يُرجى التأكد من رفع ملف PPTX رسمي.")

# الخطوة الثانية: صنع ملف الجذاذة PDF بنفس الصور المقصوصة
if btn_step2:
    b64_list = st.session_state.get("cleaned_b64_list", [])

    # في حال اضطرت الأستاذة للضغط على الزر الثاني مباشرة
    if not b64_list and uploaded_pptx:
        with st.spinner("جاري معالجة الملف مباشرة لإنشاء الجذاذة..."):
            pptx_bytes = uploaded_pptx.read()
            raw_bytes, b64_list = process_pptx_slides(pptx_bytes, margin_crop)
            st.session_state["cleaned_bytes_list"] = raw_bytes
            st.session_state["cleaned_b64_list"] = b64_list

    if not b64_list:
        st.warning("⚠️ يُرجى رفع ملف الباوربوينت الـ PPTX أولاً!")
    else:
        # تجميع كل شريحتين في صفحة A4 Landscape واحدة
        paired_slides = [b64_list[i:i + 2] for i in range(0, len(b64_list), 2)]

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
                    border-bottom: 1px dashed #ccc;
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

        html_content += "</body></html>"

        st.success("✨ تم إنشاء الجذاذة الرسمية بنجاح!")
        st.components.v1.html(html_content, height=680, scrolling=True)

        st.download_button(
            label="⬇️ تحميل الجذاذة (HTML جاهز للحفظ كـ PDF)",
            data=html_content.encode('utf-8'),
            file_name="Jadada_Math_Final.html",
            mime="html"
            )
        
