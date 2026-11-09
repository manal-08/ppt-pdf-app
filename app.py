import io
import fitz  # PyMuPDF
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import streamlit as st

st.set_page_config(page_title="صانع الجذاذات التفاعلي", layout="centered")

st.title("📝 صانع الجذاذات التلقائي من PDF")
st.write("ارفعي ملف الـ PDF الخاص بالدرس، وسيقوم التطبيق بقص الشرائح، إزالة الخلفية، وتوزيع شريحتين في كل صفحة جذاذة.")

# زر لرفع ملف الـ PDF
uploaded_file = st.file_uploader("📥 اختر ملف الـ PDF", type=[".pdf"])

# إعدادات القص (هوامش يسار، يمين، أعلى، أسفل)
st.sidebar.header("✂️ إعدادات القص")
crop_left = st.sidebar.slider("القص من اليسار (%)", 0, 30, 0) / 100.0
crop_right = st.sidebar.slider("القص من اليمين (%)", 0, 30, 0) / 100.0
crop_top = st.sidebar.slider("القص من الأعلى (%)", 0, 30, 0) / 100.0
crop_bottom = st.sidebar.slider("القص من الأسفل (%)", 0, 30, 0) / 100.0

if uploaded_file is not None:
    if st.button("🚀 معالجة الملف وإنشاء الجذاذة"):
        with st.spinner("جاري المعالجة وقص الشرائح..."):
            try:
                # قراءة ملف الـ PDF المرفوع
                pdf_bytes = uploaded_file.read()
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                cropped_images = []

                # تجاهل الشريحة الأولى تماماً والبدء من الثانية
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
                    
                    # قص الصورة
                    cropped_img = img.crop((left, top, right, bottom))
                    
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

                # إنشاء ملف الـ PDF النهائي في الذاكرة
                output_pdf_io = io.BytesIO()
                pdf_doc = SimpleDocTemplate(
                    output_pdf_io,
                    pagesize=landscape(A4),
                    rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10
                )
                
                story = []
                
                # وضع شريحتين (2) في كل صفحة جذاذة
                for i in range(0, len(cropped_images), 2):
                    slide1_io = cropped_images[i]
                    slide2_io = cropped_images[i+1] if i + 1 < len(cropped_images) else None

                    img1 = RLImage(slide1_io, width=420, height=130, preserveAspectRatio=True)
                    
                    if slide2_io:
                        img2 = RLImage(slide2_io, width=420, height=130, preserveAspectRatio=True)
                        contenu_content = [img1, Spacer(1, 6), img2]
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

                    col_widths = [45, 45, 440, 90, 90, 90]
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
                    if i + 2 < len(cropped_images):
                        story.append(PageBreak())

                pdf_doc.build(story)
                output_pdf_io.seek(0)

                st.success("✨ تم إنشاء الجذاذة بنجاح!")
                
                # زر تحميل ملف الـ PDF الناتج
                st.download_button(
                    label="📥 تحميل ملف الجذاذة (PDF)",
                    data=output_pdf_io,
                    file_name="Fiche_Pedagogique.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء المعالجة: {e}")
