import io
import fitz  # PyMuPDF
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
import streamlit as st

st.set_page_config(page_title="صانع الجذاذات التفاعلي", layout="centered")

st.markdown("<h2 style='text-align: center; color: #2c3e50;'>📝 صانع الجذاذات الذكي (شريحتان في كل صفحة)</h2>", unsafe_allow_html=True)
st.write("---")

uploaded_file = st.file_uploader("📥 ارفعي ملف الـ PDF الأصلي:", type=[".pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    total_pages = len(pdf_doc)
    st.success(f"✅ تم تحميل الـ PDF بنجاح ({total_pages} صفحة).")

    # إعدادات القص (تم إصلاح وتصحيح معادلة القص من الأسفل بدقة)
    st.markdown("### ✂️ إعدادات قص الهوامش")
    col1, col2 = st.columns(2)
    with col1:
        crop_left = st.slider("القص يسار (%)", 0, 30, 0) / 100.0
        crop_top = st.slider("القص أعلى (%)", 0, 30, 0) / 100.0
    with col2:
        crop_right = st.slider("القص يمين (%)", 0, 30, 0) / 100.0
        crop_bottom = st.slider("القص أسفل (%)", 0, 30, 0) / 100.0

    st.write("---")
    st.markdown("### 👁️ معاينة الشرائح (تجاهل الشريحة الأولى)")

    if 'preview_idx' not in st.session_state:
        st.session_state.preview_idx = 1 if total_pages > 1 else 0

    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if st.button("⬅️ السابقة") and st.session_state.preview_idx > 1:
            st.session_state.preview_idx -= 1
            st.rerun()
    with nav_col2:
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>الشريحة: {st.session_state.preview_idx + 1} / {total_pages}</p>", unsafe_allow_html=True)
    with nav_col3:
        if st.button("التالية ➡️") and st.session_state.preview_idx < total_pages - 1:
            st.session_state.preview_idx += 1
            st.rerun()

    # معاينة الشريحة الحالية
    current_page = pdf_doc[st.session_state.preview_idx]
    pix = current_page.get_pixmap(dpi=120)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    width, height = img.size
    p_left = width * crop_left
    p_top = height * crop_top
    p_right = width * (1 - crop_right)
    p_bottom = height * (1 - crop_bottom) # تصحيح حساب القص السفلي بدقة
    
    preview_img = img.crop((p_left, p_top, p_right, p_bottom))
    st.image(preview_img, use_column_width=True)

    st.write("---")

    if st.button("📄 معالجة وقص الشرائح واستخراج النصوص (تنزيل PDF النهائي)", use_container_width=True):
        with st.spinner("جاري قص الشرائح، استخراج النصوص والمعادلات، وتجهيز الجذاذة..."):
            try:
                cropped_images = []
                extracted_texts = []

                start_p = 1 if total_pages > 1 else 0

                for page_num in range(start_p, total_pages):
                    p = pdf_doc[page_num]
                    
                    # استخراج النصوص والفقرات والمعادلات من صفحة الـ PDF مباشرة
                    text_content = p.get_text("text").strip()
                    extracted_texts.append(text_content if text_content else "محتوى رياضي / شريحة درس")

                    # معالجة وقص الصورة
                    p_pix = p.get_pixmap(dpi=150)
                    p_img = Image.open(io.BytesIO(p_pix.tobytes("png")))
                    
                    w, h = p_img.size
                    l = w * crop_left
                    t = h * crop_top
                    r = w * (1 - crop_right)
                    b = h * (1 - crop_bottom) # تصحيح دقيق لمعادلة القص السفلي
                    
                    cropped_img = p_img.crop((l, t, r, b))
                    
                    # إزالة الخلفية البيضاء وجعلها شفافة
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

                # بناء ملف الـ PDF النهائي للجذاذة
                output_pdf_io = io.BytesIO()
                pdf_output_doc = SimpleDocTemplate(
                    output_pdf_io,
                    pagesize=landscape(A4),
                    rightMargin=12, leftMargin=12, topMargin=12, bottomMargin=12
                )
                
                story = []
                images_per_slide = 2
                styles = getSampleStyleSheet()
                text_style = ParagraphStyle(
                    'MathText',
                    parent=styles['Normal'],
                    fontSize=10,
                    leading=14,
                    alignment=0 # محاذاة يسار أو لغوياً حسب محتوى الرياضيات
                )
                
                for i in range(0, len(cropped_images), images_per_slide):
                    slide1_io = cropped_images[i]
                    slide2_io = cropped_images[i + 1] if i + 1 < len(cropped_images) else None

                    text1 = extracted_texts[i]
                    text2 = extracted_texts[i+1] if i + 1 < len(extracted_texts) else ""

                    img1 = RLImage(slide1_io, width=400, height=120, preserveAspectRatio=True)
                    p1 = Paragraph(text1.replace('\n', '<br/>'), text_style)

                    if slide2_io:
                        img2 = RLImage(slide2_io, width=400, height=120, preserveAspectRatio=True)
                        p2 = Paragraph(text2.replace('\n', '<br/>'), text_style)
                        contenu_content = [p1, Spacer(1, 4), img1, Spacer(1, 8), p2, Spacer(1, 4), img2]
                    else:
                        contenu_content = [p1, Spacer(1, 4), img1]

                    data = [
                        [
                            Paragraph("<b>Séance</b>", styles['Normal']),
                            Paragraph("<b>Durée</b>", styles['Normal']),
                            Paragraph("<b>Contenu & Éléments de Cours</b>", styles['Normal']),
                            Paragraph("<b>Rôle de l'enseignant</b>", styles['Normal']),
                            Paragraph("<b>Rôle de l'apprenant</b>", styles['Normal']),
                            Paragraph("<b>Observation</b>", styles['Normal'])
                        ],
                        [
                            "", "",
                            contenu_content,
                            "", "", ""
                        ]
                    ]

                    col_widths = [40, 40, 455, 85, 85, 85]
                    table = Table(data, colWidths=col_widths)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e6edf5')),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    
                    story.append(table)
                    if i + images_per_slide < len(cropped_images):
                        story.append(PageBreak())

                pdf_output_doc.build(story)
                output_pdf_io.seek(0)

                st.success("✨ تم إنشاء الجذاذة واستخراج النصوص والمعادلات بنجاح!")
                st.download_button(
                    label="📥 تحميل ملف الجذاذة النهائي (PDF)",
                    data=output_pdf_io,
                    file_name="Fiche_Pedagogique_Complete.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء المعالجة: {e}")
    
