import io
import fitz  # PyMuPDF
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import streamlit as st

st.set_page_config(page_title="صانع الجذاذات التفاعلي", layout="centered")

st.markdown("<h2 style='text-align: center; color: #2c3e50;'>📝 صانع الجذاذات (معاينة الشرائح وتوليد PDF)</h2>", unsafe_allow_html=True)
st.write("---")

# رفع ملف الـ PDF
uploaded_file = st.file_uploader("📥 ارفعي ملف الـ PDF الأصلي:", type=[".pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    total_pages = len(pdf_doc)
    st.success(f"✅ تم تحميل الـ PDF بنجاح ({total_pages} صفحة).")

    # إعدادات القص
    st.markdown("### ✂️ إعدادات قص الهوامش للشرائح")
    col1, col2 = st.columns(2)
    with col1:
        crop_left = st.slider("القص يسار (%)", 0, 30, 0) / 100.0
        crop_top = st.slider("القص أعلى (%)", 0, 30, 0) / 100.0
    with col2:
        crop_right = st.slider("القص يمين (%)", 0, 30, 0) / 100.0
        crop_bottom = st.slider("القص أسفل (%)", 0, 30, 0) / 100.0

    st.write("---")
    st.markdown("### 👁️ معاينة الشرائح واحدة تلو الأخرى (تجاهل الشريحة الأولى)")

    # إدارة التنقل بين الشرائح (البدء من الشريحة الثانية أي الفهرس 1)
    if 'preview_idx' not in st.session_state:
        st.session_state.preview_idx = 1 if total_pages > 1 else 0

    # أزرار التنقل (السابق / التالي)
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if st.button("⬅️ الشريحة السابقة") and st.session_state.preview_idx > 1:
            st.session_state.preview_idx -= 1
            st.rerun()
    with nav_col2:
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>الشريحة المعروضة: {st.session_state.preview_idx + 1} من {total_pages}</p>", unsafe_allow_html=True)
    with nav_col3:
        if st.button("الشريحة التالية ➡️") and st.session_state.preview_idx < total_pages - 1:
            st.session_state.preview_idx += 1
            st.rerun()

    # عرض الشريحة الحالية بعد القص
    current_page = pdf_doc[st.session_state.preview_idx]
    pix = current_page.get_pixmap(dpi=120)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    width, height = img.size
    p_left = width * crop_left
    p_top = height * crop_top
    p_right = width * (1 - crop_right)
    p_bottom = width * (1 - crop_bottom)
    
    preview_img = img.crop((p_left, p_top, p_right, p_bottom))
    st.image(preview_img, use_column_width=True)

    st.write("---")

    # زر التوليد النهائي لملف الـ PDF
    if st.button("📄 قص كل الشرائح وإنشاء الجذاذات (تنزيل PDF النهائي)", use_container_width=True):
        with st.spinner("جاري معالجة وقص جميع الشرائح وإزالة الخلفية البيضاء..."):
            try:
                cropped_images = []

                # بدء المعالجة من الشريحة الثانية (فهرس 1) حتى النهاية
                start_p = 1 if total_pages > 1 else 0

                for page_num in range(start_p, total_pages):
                    p = pdf_doc[page_num]
                    p_pix = p.get_pixmap(dpi=150)
                    p_img = Image.open(io.BytesIO(p_pix.tobytes("png")))
                    
                    w, h = p_img.size
                    l = w * crop_left
                    t = h * crop_top
                    r = w * (1 - crop_right)
                    b = h * (1 - crop_bottom)
                    
                    cropped_img = p_img.crop((l, t, r, b))
                    
                    # تفريغ الخلفية البيضاء وجعلها شفافة
                    cropped_img = cropped_img.convert("RGBA")
                    datas = cropped_img.getdata()
                    new_data = []
                    for item in datas:
                        if item[0] > 235 and item[1] > 235 and item[2] > 235:
                            new_data.append((255, 255, 255, 0))
                        else:
                            new_data.append(item)
                    cropped_img.putdata(new_data)
                    
                    img_byte_arr = io.BytesIO()
                    cropped_img.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)
                    cropped_images.append(img_byte_arr)

                # بناء ملف الـ PDF النهائي (شريحتين في كل صفحة جذاذة)
                output_pdf_io = io.BytesIO()
                pdf_output_doc = SimpleDocTemplate(
                    output_pdf_io,
                    pagesize=landscape(A4),
                    rightMargin=12, leftMargin=12, topMargin=12, bottomMargin=12
                )
                
                story = []
                images_per_slide = 2
                
                for i in range(0, len(cropped_images), images_per_slide):
                    slide1_io = cropped_images[i]
                    slide2_io = cropped_images[i + 1] if i + 1 < len(cropped_images) else None

                    img1 = RLImage(slide1_io, width=430, height=135, preserveAspectRatio=True)
                    
                    if slide2_io:
                        img2 = RLImage(slide2_io, width=430, height=135, preserveAspectRatio=True)
                        contenu_content = [img1, Spacer(1, 8), img2]
                    else:
                        contenu_content = [img1]

                    data = [
                        [
                            Paragraph("<b>Séance</b>", getSampleStyleSheet()['Normal']),
                            Paragraph("<b>Durée</b>", getSampleStyleSheet()['Normal']),
                            Paragraph("<b>Contenu</b>", getSampleStyleSheet()['Normal']),
                            Paragraph("<b>Rôle de l'enseignant</b>", getSampleStyleSheet()['Normal']),
                            Paragraph("<b>Rôle de l'apprenant</b>", getSampleStyleSheet()['Normal']),
                            Paragraph("<b>Observation</b>", getSampleStyleSheet()['Normal'])
                        ],
                        [
                            "", "",
                            contenu_content,
                            "", "", ""
                        ]
                    ]

                    col_widths = [45, 45, 445, 90, 90, 90]
                    table = Table(data, colWidths=col_widths)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e6edf5')),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    
                    story.append(table)
                    if i + images_per_slide < len(cropped_images):
                        story.append(PageBreak())

                pdf_output_doc.build(story)
                output_pdf_io.seek(0)

                st.success("✨ تم إنشاء ملف الجذاذات بنجاح!")
                st.download_button(
                    label="📥 اضغطي هنا لتحميل ملف الجذاذة (PDF)",
                    data=output_pdf_io,
                    file_name="Fiche_Pedagogique.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء المعالجة: {e}")
                
