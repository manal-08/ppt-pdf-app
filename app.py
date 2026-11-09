import io
import fitz  # PyMuPDF
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import streamlit as st

st.set_page_config(page_title="منظم شرائح الرياضيات", layout="wide", initial_sidebar_state="collapsed")

# 🎨 لمسات CSS لتجميل الألوان والواجهة بالكامل
st.markdown("""
<style>
    /* خلفية الصفحة وتحسين الخطوط */
    .stApp {
        background-color: #f8fafc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* تصميم بطاقات الخطوة الأولى */
    .upload-card {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
        border: 2px dashed #8b5cf6;
        text-align: center;
        margin: 20px auto;
        max-width: 650px;
    }
    
    /* عناوين جذابة */
    .main-title {
        color: #4c1d95;
        font-weight: 800;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-title {
        color: #6b7280;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    /* تخصيص زر الاستمرار والتوليد */
    .stButton>button {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        color: white !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        padding: 12px 28px !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4) !important;
        background: linear-gradient(135deg, #6d28d9 0%, #5b21b6 100%);
    }

    /* تحسين أشرطة التمرير الخاصة بالقص */
    div[data-baseweb="slider"] {
        padding-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# إدارة حالة الانتقال بين الصفحات
if 'step' not in st.session_state:
    st.session_state.step = 1

# ==========================================
# الصفحة الأولى: رفع الملف وتصميم جذاب
# ==========================================
if st.session_state.step == 1:
    st.markdown("<h1 class='main-title'>📐 منصة إعداد جذاذات الرياضيات</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>قم برفع ملف الدرس لتوليد جذاذة مقصوصة ومنظمة بدقة عالية</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='upload-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #6d28d9; margin-bottom: 15px;'>📤 اختر ملف الـ PDF الخاص بالدرس</h3>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=[".pdf"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        st.session_state.pdf_bytes = uploaded_file.read()
        st.markdown("<div style='color: #059669; font-weight: bold; margin: 15px 0;'>✅ تم تحميل الملف بنجاح! جاهز للانتقال للخطوة التالية.</div>", unsafe_allow_html=True)
        
        st.write("")
        if st.button("Continue / الانتقال لقص الشرائح ➔"):
            st.session_state.step = 2
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# الصفحة الثانية: المعاينة، أزرار القص، وتوليد PDF
# ==========================================
elif st.session_state.step == 2:
    
    # 1. زر توليد الجذاذة النهائي في الأعلى بعرض ممتاز
    top_col1, top_col2, top_col3 = st.columns([1, 2, 1])
    with top_col2:
        if st.button("✨ توليد وتنزيل جذاذة الـ PDF النهائية ✨"):
            with st.spinner("جاري قص الشرائح وتوليد الملف بحجم ممتد ونظيف..."):
                try:
                    pdf_doc = fitz.open(stream=st.session_state.pdf_bytes, filetype="pdf")
                    total_pages = len(pdf_doc)
                    
                    c_left = st.session_state.get('crop_left', 0) / 100.0
                    c_top = st.session_state.get('crop_top', 0) / 100.0
                    c_right = st.session_state.get('crop_right', 0) / 100.0
                    c_bottom = st.session_state.get('crop_bottom', 0) / 100.0

                    cropped_images = []
                    start_p = 1 if total_pages > 1 else 0

                    for page_num in range(start_p, total_pages):
                        p = pdf_doc[page_num]
                        p_pix = p.get_pixmap(dpi=200)
                        p_img = Image.open(io.BytesIO(p_pix.tobytes("png")))
                        
                        w, h = p_img.size
                        l = w * c_left
                        t = h * c_top
                        r = w * (1.0 - c_right)
                        b = h * (1.0 - c_bottom)
                        
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
                        cropped_images.append(img_byte_arr)

                    output_pdf_io = io.BytesIO()
                    pdf_output_doc = SimpleDocTemplate(
                        output_pdf_io,
                        pagesize=landscape(A4),
                        rightMargin=8, leftMargin=8, topMargin=8, bottomMargin=8
                    )
                    
                    story = []
                    images_per_page = 3
                    styles = getSampleStyleSheet()
                    
                    for i in range(0, len(cropped_images), images_per_page):
                        slide1_io = cropped_images[i]
                        slide2_io = cropped_images[i + 1] if i + 1 < len(cropped_images) else None
                        slide3_io = cropped_images[i + 2] if i + 2 < len(cropped_images) else None

                        img1 = RLImage(slide1_io, width=350, height=145)
                        contenu_content = [img1]

                        if slide2_io:
                            img2 = RLImage(slide2_io, width=350, height=145)
                            contenu_content.extend([Spacer(1, 4), img2])
                            
                        if slide3_io:
                            img3 = RLImage(slide3_io, width=350, height=145)
                            contenu_content.extend([Spacer(1, 4), img3])

                        data = [
                            [
                                Paragraph("<b>Séance</b>", styles['Normal']),
                                Paragraph("<b>Durée</b>", styles['Normal']),
                                Paragraph("<b>Contenu (Éléments du cours)</b>", styles['Normal']),
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

                        col_widths = [60, 60, 360, 115, 115, 116]
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
                        if i + images_per_page < len(cropped_images):
                            story.append(PageBreak())

                    pdf_output_doc.build(story)
                    output_pdf_io.seek(0)

                    st.success("🎉 تم توليد جذاذة الـ PDF بنجاح!")
                    st.download_button(
                        label="📥 اضغطي هنا لتنزيل ملف الـ PDF الجاهز",
                        data=output_pdf_io,
                        file_name="Jadada_Maths_Clean.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء التوليد: {e}")

    st.write("---")
    
    # 2. عرض معاينة الشرائح على اليسار وعناصر القص على اليمين
    pdf_doc = fitz.open(stream=st.session_state.pdf_bytes, filetype="pdf")
    total_pages = len(pdf_doc)

    col_preview, col_controls = st.columns([2, 1])

    with col_controls:
        st.markdown("<h3 style='color: #4c1d95;'>✂️ التحكم في القص</h3>", unsafe_allow_html=True)
        st.write("اضبطي المقاسات ليتم تطبيقها على كل الشرائح:")
        
        st.session_state.crop_left = st.slider("القص يسار (%)", 0, 30, 0)
        st.session_state.crop_right = st.slider("القص يمين (%)", 0, 30, 0)
        st.session_state.crop_top = st.slider("القص أعلى (%)", 0, 30, 0)
        st.session_state.crop_bottom = st.slider("القص أسفل (%)", 0, 30, 0)

    with col_preview:
        st.markdown("<h3 style='color: #4c1d95;'>👁️ معاينة الشريحة الحالية</h3>", unsafe_allow_html=True)
        
        if 'preview_idx' not in st.session_state:
            st.session_state.preview_idx = 1 if total_pages > 1 else 0

        nav1, nav2, nav3 = st.columns([1, 2, 1])
        with nav1:
            if st.button("⬅️ الشريحة السابقة") and st.session_state.preview_idx > 1:
                st.session_state.preview_idx -= 1
                st.rerun()
        with nav2:
            st.markdown(f"<h4 style='text-align: center; color: #6d28d9;'>الشريحة {st.session_state.preview_idx + 1} من {total_pages}</h4>", unsafe_allow_html=True)
        with nav3:
            if st.button("الشريحة التالية ➡️") and st.session_state.preview_idx < total_pages - 1:
                st.session_state.preview_idx += 1
                st.rerun()

        current_page = pdf_doc[st.session_state.preview_idx]
        pix = current_page.get_pixmap(dpi=150)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        w, h = img.size
        l = w * (st.session_state.crop_left / 100.0)
        t = h * (st.session_state.crop_top / 100.0)
        r = w * (1.0 - st.session_state.crop_right / 100.0)
        b = h * (1.0 - st.session_state.crop_bottom / 100.0)
        
        preview_img = img.crop((l, t, r, b))
        st.image(preview_img, use_column_width=True)

    st.write("---")
    if st.button("🔙 العودة لرفع ملف آخر", use_container_width=False):
        st.session_state.step = 1
        st.rerun()
