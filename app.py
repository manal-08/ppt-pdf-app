import io
import fitz  # مكتبة PyMuPDF
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

def process_pdf_to_fiche(pdf_path, output_pdf_path, crop_margins=(0, 0, 0, 0)):
    """
    تقرأ ملف PDF، تتجاهل الشريحة الأولى، تقص الهوامش، تزيل الخلفية البيضاء،
    وتضع شريحتين (2) في كل صفحة جذاذة ضمن جدول منظم مرتب.
    crop_margins: (يسار، يمين، أعلى، أسفل) كقيم بين 0 و 0.3 (مثلاً 0.05 تعني 5%)
    """
    doc = fitz.open(pdf_path)
    cropped_images = []

    c_left, c_right, c_top, c_bottom = crop_margins

    # تجاهل الشريحة الأولى تماماً والبدء من الصفحة الثانية (الفهرس 1)
    start_page = 1 if len(doc) > 1 else 0

    for page_num in range(start_page, len(doc)):
        page = doc[page_num]
        
        # تحويل صفحة الـ PDF إلى صورة بجودة عالية
        pix = page.get_pixmap(dpi=150)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        width, height = img.size
        
        # حساب أبعاد القص
        left = width * c_left
        top = height * c_top
        right = width * (1 - c_right)
        bottom = height * (1 - c_bottom)
        
        # قص الصورة
        cropped_img = img.crop((left, top, right, bottom))
        
        # إزالة الخلفية البيضاء وجعلها شفافة
        cropped_img = cropped_img.convert("RGBA")
        datas = cropped_img.getdata()
        new_data = []
        for item in datas:
            # إذا كان اللون أبيض أو قريباً جداً من الأبيض، نجعله شفافاً
            if item[0] > 235 and item[1] > 235 and item[2] > 235:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        cropped_img.putdata(new_data)
        
        # حفظ الصورة المعالجة في الذاكرة
        img_byte_arr = io.BytesIO()
        cropped_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        cropped_images.append(img_byte_arr)

    # إعداد ملف الـ PDF النهائي بتنسيق A4 أفقياً (Landscape)
    pdf_doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=landscape(A4),
        rightMargin=10, leftMargin=10, topMargin=10, bottomMargin=10
    )
    
    story = []
    
    # وضع شريحتين (2) فقط في كل صفحة جذاذة
    for i in range(0, len(cropped_images), 2):
        slide1_io = cropped_images[i]
        slide2_io = cropped_images[i+1] if i + 1 < len(cropped_images) else None

        # إنشاء كائنات الصور لتأخذ عرض خانة Contenu بالكامل دون أن تصغر
        img1 = RLImage(slide1_io, width=420, height=130, preserveAspectRatio=True)
        
        if slide2_io:
            img2 = RLImage(slide2_io, width=420, height=130, preserveAspectRatio=True)
            contenu_content = [img1, Spacer(1, 6), img2]
        else:
            contenu_content = [img1]

        # تصميم جدول الجذاذة المطابق للنموذج المطلوب
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

        # تحديد عرض الأعمدة المناسب لصفحة A4 Landscape
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
        
        # الانتقال لصفحة جديدة إذا كانت هناك شرائح متبقية
        if i + 2 < len(cropped_images):
            story.append(PageBreak())

    pdf_doc.build(story)
    print(f"✅ تم إنشاء ملف الجذاذة بنجاح: {output_pdf_path}")

# طريقة الاستخدام (ضعي اسم ملف الـ PDF الخاص بكِ هنا):
if __name__ == "__main__":
    process_pdf_to_fiche("cours.pdf", "fiche_pedagogique.pdf", crop_margins=(0.02, 0.02, 0.02, 0.02))
        
