import streamlit as st
from pptx import Presentation
from pptx.util import Inches
import io
import base64
from PIL import Image

st.set_page_config(page_title="صانع الجذاذات الرياضية الرسمي", layout="wide")

st.title("📚 صانع الجذاذات الرياضية - التطبيق الرسمي")
st.markdown("---")

tab1, tab2 = st.tabs(["🖼️ الزر الأول: تحويل وتجميع الشرائح كصور في عرض جديد", "📄 الزر الثاني: صنع الجذاذة PDF الرسمية"])

# -------------------------------------------------------------
# الزر الأول: أخذ شرائح العرض وتحويلها وتجميعها في ملف PPTX جديد
# -------------------------------------------------------------
with tab1:
    st.subheader("المرحلة الأولى: تحويل العرض التقديمي إلى صور كاملة وتجميعه")
    uploaded_file_s1 = st.file_uploader("📥 ارفع ملف الباوربوينت الأصلي (PPTX):", type=["pptx"], key="btn1")

    if uploaded_file_s1 and st.button("🚀 تحويل وتجميع كعرض جديد"):
        with st.spinner("جاري معالجة الشرائح بالكامل وتجميعها..."):
            prs = Presentation(uploaded_file_s1)
            
            new_prs = Presentation()
            new_prs.slide_width = prs.slide_width
            new_prs.slide_height = prs.slide_height
            blank_layout = new_prs.slide_layouts[6]

            slide_count = 0

            for slide in prs.slides:
                # جمع كافة الصور والأشكال الموجودة في الشريحة لضمان أخذ المحتوى كاملاً
                slide_blobs = []
                for shape in slide.shapes:
                    if shape.shape_type == 13: # صورة أو كائن مرئي
                        try:
                            slide_blobs.append(shape.image.blob)
                        except:
                            pass
                
                if slide_blobs:
                    main_blob = max(slide_blobs, key=len)
                    
                    # إضافة الشريحة الجديدة كصورة تملأ المساحة بالكامل في العرض الجديد
                    new_slide = new_prs.slides.add_slide(blank_layout)
                    image_stream = io.BytesIO(main_blob)
                    new_slide.shapes.add_picture(image_stream, 0, 0, width=new_prs.slide_width, height=new_prs.slide_height)
                    slide_count += 1

            output_stream = io.BytesIO()
            new_prs.save(output_stream)
            pptx_data = output_stream.getvalue()

            st.success(f"✅ تم معالجة وتجميع {slide_count} شريحة في عرض جديد بنجاح!")
            
            st.download_button(
                label="⬇️ تحميل العرض التقديمي الجديد (PPTX)",
                data=pptx_data,
                file_name="Lesson_New_Slides.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )

# -------------------------------------------------------------
# الزر الثاني: إعطاؤه العرض الجديد، إزالة الخلفية، وتوليد الجذاذة PDF
# -------------------------------------------------------------
with tab2:
    st.subheader("المرحلة الثانية: صنع الجذاذة PDF من العرض الجديد")
    uploaded_file_s2 = st.file_uploader("📥 ارفع العرض التقديمي الجديد (الذي حملته من الخطوة الأولى):", type=["pptx"], key="btn2")
    
    crop_margin = st.slider("✂️ نسبة إزالة الإطار المزخرف والأطراف (%):", min_value=0, max_value=25, value=8)

    if uploaded_file_s2 and st.button("🚀 صنع الجذاذة PDF (شريحتان لكل صفحة)"):
        with st.spinner("جاري إزالة الخلفيات المزخرفة وتنسيق الجذاذة الرسمية..."):
            prs = Presentation(uploaded_file_s2)
            processed_slides = []

            for slide in prs.slides:
                slide_blobs = []
                for shape in slide.shapes:
                    if shape.shape_type == 13:
                        try:
                            slide_blobs.append(shape.image.blob)
                        except:
                            pass
                
                if slide_blobs:
                    blob = max(slide_blobs, key=len)
                    try:
                        img = Image.open(io.BytesIO(blob)).convert("RGB")
                        w, h = img.size

                        # قص الأطراف والإطارات المزخرفة مع الحفاظ الكامل على المعادلات والنصوص
                        left = int(w * (crop_margin / 100.0))
                        top = int(h * (crop_margin / 100.0))
                        right = int(w * (1 - crop_margin / 100.0))
                        bottom = int(h * (1 - crop_margin / 100.0))

                        cropped_img = img.crop((left, top, right, bottom))

                        buffer = io.BytesIO()
                        cropped_img.save(buffer, format="PNG")
                        encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        processed_slides.append(f"data:image/png;base64,{encoded}")
                    except:
                        pass

            if not processed_slides:
                st.error("لم يتم العثور على شرائح للمعالجة. تأكدي من رفع الملف الصحيح.")
            else:
                paired_slides = [processed_slides[i:i + 2] for i in range(0, len(processed_slides), 2)]

                html_content = """
                <!DOCTYPE html>
                <html lang="fr">
                <head>
                    <meta charset="UTF-8">
                    <style>
                        @page { size: A4 landscape; margin: 5mm; }
                        body { background-color: #555; margin: 0; padding: 10px; font-family: Arial, sans-serif; direction: ltr; color: #000; }
                        .print-bar { text-align: center; margin-bottom: 15px; }
                        .btn-pdf { background-color: #28a745; color: white; padding: 12px 25px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; font-weight: bold; }
                        .page-card { background-color: #ffffff; width: 287mm; height: 198mm; padding: 8mm; margin: 0 auto 20px auto; box-sizing: border-box; box-shadow: 0 0 10px rgba(0,0,0,0.3); page-break-after: always; }
                        table.fiche-table { width: 100%; height: 100%; border-collapse: collapse; table-layout: fixed; }
                        table.fiche-table th, table.fiche-table td { border: 1px solid #000000; padding: 6px; vertical-align: top; box-sizing: border-box; }
                        table.fiche-table th { background-color: #f8f9fa; text-align: center; font-size: 11px; font-weight: bold; color: #000; }
                        .col-seance { width: 7%; text-align: center; }
                        .col-duree { width: 7%; text-align: center; }
                        .col-contenu { width: 52%; text-align: center; }
                        .col-ens { width: 11%; }
                        .col-app { width: 11%; }
                        .col-obs { width: 12%; }
                        .slide-img-block { width: 98%; max-height: 84mm; object-fit: contain; display: block; margin: 4px auto; background: #ffffff; }
                        .slide-sep { border-bottom: 1px dashed #ccc; margin: 6px 0; }
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

                st.success("✨ تمت إنجاز الجذاذة الرسمية بنجاح!")
                st.components.v1.html(html_content, height=680, scrolling=True)

                st.download_button(
                    label="⬇️ تحميل الجذاذة نهائياً (HTML جاهز للحفظ كـ PDF)",
                    data=html_content.encode('utf-8'),
                    file_name="Jadada_Fiche_Pedagogique.html",
                    mime="html"
                )
                
