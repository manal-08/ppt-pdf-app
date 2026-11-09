import io
import fitz  # PyMuPDF
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import streamlit as st

st.set_page_config(page_title="مستخرج محتوى الدروس والرياضيات", layout="centered")

st.markdown("<h2 style='text-align: center; color: #2c3e50;'>📚 استخراج الشرائح والنصوص والمعادلات الرياضية</h2>", unsafe_allow_html=True)
st.write("---")

uploaded_file = st.file_uploader("📥 ارفعي ملف الـ PDF الأصلي:", type=[".pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    total_pages = len(pdf_doc)
    st.success(f"✅ تم تحميل الـ PDF بنجاح ({total_pages} صفحة).")

    st.markdown("### ✂️ إعدادات قص الهوامش للشرائح")
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

    # معاينة الشريحة الحالية بدقة عالية
    current_page = pdf_doc[st.session_state.preview_idx]
    pix = current_page.get_pixmap(dpi=150)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    width, height = img.size
    p_left = width * crop_left
    p_top = height * crop_top
    p_right = width * (1 - crop_right)
    p_bottom = height * (1 - crop_bottom)
    
    preview_img = img.crop((p_left, p_top, p_right, p_bottom))
    st.image(preview_img, use_column_width=True)

    st.write("---")

    if st.button("📄 استخراج الشرائح والنصوص والمعادلات في ملف PDF جديد", use_container_width=True):
        with st.spinner("جاري استخراج المحتوى والشرائح بدقة..."):
            try:
                output_pdf_io = io.BytesIO()
                pdf_output_doc = SimpleDocTemplate(
                    output_pdf_io,
                    pagesize=A4,
                    rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
                )
                
                story = []
                styles = getSampleStyleSheet()
                text_style = ParagraphStyle(
                    'MathContent',
                    parent=styles['Normal'],
                    fontSize=11,
                    leading=16,
                    alignment=0
                )

                start_p = 1 if total_pages > 1 else 0

                for page_num in range(start_p, total_pages):
                    p = pdf_doc[page_num]
                    
                    # استخراج النصوص والمعادلات المتاحة في الصفحة
                    text_content = p.get_text("text").strip()
                    
                    # معالجة وقص صورة الشريحة للحفاظ على المعادلات المرسومة
                    p_pix = p.get_pixmap(dpi=200)
                    p_img = Image.open(io.BytesIO(p_pix.tobytes("png")))
                    
                    w, h = p_img.size
                    l = w * crop_left
                    t = h * crop_top
                    r = w * (1 - crop_right)
                    b = h * (1 - crop_bottom)
                    
                    cropped_img = p_img.crop((l, t, r, b))
                    
                    # تفريغ الخلفية البيضاء
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

                    # إضافة عنوان أو رقم الشريحة
                    story.append(Paragraph(f"<b>--- الشريحة / الصفحة {page_num + 1} ---</b>", styles['Heading2']))
                    story.append(Spacer(1, 6))

                    # إضافة صورة الشريحة (التي تحوي المعادلات والأشكال الرياضية)
                    slide_img = RLImage(img_byte_arr, width=450, height=220)
                    story.append(slide_img)
                    story.append(Spacer(1, 10))

                    # إذا وجد نص مستخرج، نضيفه أسفل الصورة
                    if text_content:
                        story.append(Paragraph("<b>النصوص والمعادلات المستخرجة:</b>", styles['Normal']))
                        story.append(Spacer(1, 4))
                        story.append(Paragraph(text_content.replace('\n', '<br/>'), text_style))
                    
                    story.append(Spacer(1, 15))
                    story.append(PageBreak())

                pdf_output_doc.build(story)
                output_pdf_io.seek(0)

                st.success("✨ تم استخراج الشرائح والمحتوى الرياضي بنجاح!")
                st.download_button(
                    label="📥 تحميل ملف المحتوى المستخرج (PDF)",
                    data=output_pdf_io,
                    file_name="Cours_Et_Mathematiques.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء المعالجة: {e}")
                
