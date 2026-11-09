import io
import fitz  # PyMuPDF
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import streamlit as st

st.set_page_config(page_title="صانع الجذاذات التفاعلي", layout="centered")

st.markdown("<h2 style='text-align: center; color: #2c3e50;'>📝 صانع الجذاذات التلقائي (شريحتان في كل صفحة)</h2>", unsafe_allow_html=True)
st.write("---")

# رفع ملف الـ PDF
uploaded_file = st.file_uploader("📥 ارفعي ملف الـ PDF الأصلي:", type=[".pdf"])

# أدوات التحكم الجانبية للقص تماماً مثل نسخة المتصفح
st.sidebar.header("✂️ أدوات قص الهوامش")
crop_left = st.sidebar.slider("القص يسار (%)", 0, 30, 0) / 100.0
crop_right = st.sidebar.slider("القص يمين (%)", 0, 30, 0) / 100.0
crop_top = st.sidebar.slider("القص أعلى (%)", 0, 30, 0) / 100.0
crop_bottom = st.sidebar.slider("القص أسفل (%)", 0, 30, 0) / 100.0

if uploaded_file is not None:
    if st.button("📄 قص الشرائح وإنشاء الجذاذة (تنزيل PDF)", use_container_width=True):
        with st.spinner("جاري معالجة وقص الشرائح وإزالة الخلفية البيضاء..."):
            try:
                pdf_bytes = uploaded_file.read()
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                cropped_images = []

                # تجاهل الشريحة الأولى تماماً والبدء من الصفحة الثانية
                start_page = 1 if len(doc) > 1 else 0

                for page_num in range(start_page, len(doc)):
                    page = doc[page_num]
                    pix = page.get_pixmap(dpi=150)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    
                    width, height = img.size
                    left = width * crop_left
                    top = height * crop_top
                    right = width * (1 - crop_right)
                    bottom = height * (1 - crop_bottom)
                    
                    # قص الصورة حسب القيم المحددة
                    cropped_img = img.crop((left, top, right, bottom))
                    
                    # تفريغ الخلفية البيضاء وجعلها شفافة تماماً
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

                # إنشاء ملف الـ PDF النهائي بتنسيق A4 Landscape وتصميم الجذاذة
                output_pdf_io = io.BytesIO()
                pdf_doc = SimpleDocTemplate(
                    output_pdf_io,
                    pagesize=landscape(A4),
                    rightMargin=12, leftMargin=12, topMargin=12, bottomMargin=12
                )
                
                story = []
                images_per_slide = 2  # فرض شريحتين (2) فقط في كل صفحة جذاذة
                
                for i in range(0, len(cropped_images), images_per_slide):
                    slide1_io = cropped_images[i]
                    slide2_io = cropped_images[i + 1] if i + 1 < len(cropped_images) else None

                    # ضبط مقاس الصور لتملأ الخانة بوضوح ودون تداخل
                    img1 = RLImage(slide1_io, width=430, height=135, preserveAspectRatio=True)
                    
                    if slide2_io:
                        img2 = RLImage(slide2_io, width=430, height=135, preserveAspectRatio=True)
                        contenu_content = [img1, Spacer(1, 8), img2]
                    else:
                        contenu_content = [img1]

                    # هيكل جدول الجذاذة المطابق للنموذج المطلوب
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
                    
                    # الانتقال لصفحة جديدة إذا كانت هناك شرائح متبقية
                    if i + images_per_slide < len(cropped_images):
                        story.append(PageBreak())

                pdf_doc.build(story)
                output_pdf_io.seek(0)

                st.success("✨ تم إعداد الملف بنجاح!")
                
                # زر تحميل ملف الـ PDF الناتج
                st.download_button(
                    label="📥 اضغطي هنا لتحميل ملف الجذاذة (PDF)",
                    data=output_pdf_io,
                    file_name="Fiche_Pedagogique.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء المعالجة: {e}")
                                      
