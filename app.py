import streamlit as st
from pptx import Presentation
from pptx.util import Inches
import os
import base64
from PIL import Image
import io

st.set_page_config(page_title="صانع الجذاذات الرياضية المراحل", layout="wide")

st.title("📚 صانع الجذاذات الرياضية - النظام ذو الزرين المنفصلين")
st.markdown("---")

# تبويب أو خيارين للعملية بوضوح
tab1, tab2 = st.tabs(["الخطوة 1: تحويل وتجميع العرض كصور", "الخطوة 2: صنع الجذاذة PDF الرسمية"])

# -------------------------------------------------------------
# الزر الأول: أخذ الشريحة كاملة كما هي وتحويلها لصور وتجميعها في PPTX جديد
# -------------------------------------------------------------
with tab1:
    st.subheader("🖼️ المرحلة الأولى: تحويل الشرائح بالكامل إلى صور وتجميعها في عرض جديد")
    uploaded_ppt_step1 = st.file_uploader("📥 ارفع ملف الباوربوينت الأصلي:", type=["pptx"], key="step1_file")

    if uploaded_ppt_step1 and st.button("🚀 تحويل الشرائح بالكامل وتكوين عرض PPTX جديد"):
        with st.spinner("جاري تحويل كل شريحة كصورة كاملة وإعادة تجميعها..."):
            prs = Presentation(uploaded_ppt_step1)
            new_prs = Presentation()
            new_prs.slide_width = Inches(13.33)
            new_prs.slide_height = Inches(7.5)
            blank_layout = new_prs.slide_layouts[6]

            extracted_images = []

            for slide in prs.slides:
                slide_shapes_bytes = []
                for shape in slide.shapes:
                    if shape.shape_type == 13:  # صورة أو محتوى مرئي
                        try:
                            slide_shapes_bytes.append(shape.image.blob)
                        except Exception:
                            pass
                
                if slide_shapes_bytes:
                    # أخذ الشريحة بالكامل كما هي دون قص
                    full_slide_blob = max(slide_shapes_bytes, key=len)
                    extracted_images.append(full_slide_blob)
                    
                    # إضافتها للشريحة الجديدة في العرض الجديد
                    new_slide = new_prs.slides.add_slide(blank_layout)
                    image_stream = io.BytesIO(full_slide_blob)
                    new_slide.shapes.add_picture(image_stream, 0, 0, width=new_prs.slide_width, height=new_prs.slide_height)

            # حفظ العرض الجديد في الذاكرة لتنزيله
            output_stream = io.BytesIO()
            new_prs.save(output_stream)
            new_pptx_data = output_stream.getvalue()

            st.success(f"✅ تم تحويل {len(extracted_images)} شريحة بالكامل وتجميعها في عرض تقديمي جديد بنجاح!")
            
            st.download_button(
                label="⬇️ تحميل العرض التقديمي الجديد (صور كاملة بدون قص)",
                data=new_pptx_data,
                file_name="Lesson_Full_Slides_Images.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )

# -------------------------------------------------------------
# الزر الثاني: أخذ العرض الجديد، إزالة الخلفية، والاحتفاظ بالنصوص والمعادلات لإنتاج الجذاذة PDF
# -------------------------------------------------------------
with tab2:
    st.subheader("📄 المرحلة الثانية: صنع الجذاذة الرسمية من العرض الجديد")
    uploaded_ppt_step2 = st.file_uploader("📥 ارفع العرض التقديمي الجديد (الذي قمت بتحميله في الخطوة الأولى):", type=["pptx"], key="step2_file")
    
    # شريط التحكم لقص الهوامش وإزالة القوالب الزخرفية الخلفية
    crop_margin = st.slider("✂️ نسبة إزالة الإطار المزخرف والخلفية من الأطراف (%):", min_value=0, max_value=25, value=8, key="step2_slider")

    if uploaded_ppt_step2 and st.button("🚀 صنع الجذاذة PDF (شريحتان بالصفحة)"):
        with st.spinner("جاري إزالة الخلفيات الزخرفية والاحتفاظ بالمعادلات وتنسيق الجذاذة..."):
            prs = Presentation(uploaded_ppt_step2)
            clean_slides_b64 = []

            for slide in prs.slides:
                slide_blobs = []
                for shape in slide.shapes:
                    if shape.shape_type == 13:
                        try:
                            slide_blobs.append(shape.image.blob)
                        except Exception:
                            pass
                
                if slide_blobs:
                    blob = max(slide_blobs, key=len)
                    try:
                        img = Image.open(io.BytesIO(blob)).convert("RGB")
                        w, h = img.size

                        # إزالة القالب والخلفية المزخرفة عبر قص الأطراف والتركيز على المحتوى الداخلي (المعادلات والنصوص)
                        left = int(w * (crop_margin / 100.0))
                        top = int(h * (crop_margin / 100.0))
                        right = int(w * (1 - crop_margin / 100.0))
                        bottom = int(h * (1 - crop_margin / 100.0))

                        cropped_img = img.crop((left, top, right, bottom))

                        buffer = io.BytesIO()
                        cropped_img.save(buffer, format="PNG")
                        encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        clean_slides_b64.append(f"data:image/png;base64,{encoded}")
                    except Exception:
                        pass

            if not clean_slides_b64:
                st.error("لم يتم العثور على شرائح معالجة. تأكدي من رفع الملف الصحيح.")
            else:
                # تجميع كل شريحتين معاً في صفحة أفقية A4 واحدة
                paired_slides = [clean_slides_b64[i:i + 2] for i in range(0, len(clean_slides_b64), 2)]

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
                                r>
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

                st.success("✨ تم إنشاء الجذاذة الرسمية بنجاح مع الاحتفاظ الكامل بالمعادلات والكسور وإزالة الخلفيات المزخرفة!")
                st.components.v1.html(html_content, height=680, scrolling=True)

                st.download_button(
                    label="⬇️ تحميل الجذاذة نهائياً (HTML جاهز للحفظ كـ PDF)",
                    data=html_content.encode('utf-8'),
                    file_name="Jadada_Fiche_Pedagogique.html",
                    mime="html"
                )

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
        
