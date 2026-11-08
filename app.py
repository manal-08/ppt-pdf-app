import streamlit as st
import fitz  # PyMuPDF
from pptx import Presentation
from pptx.util import Inches
from PIL import Image
import io

st.set_page_config(page_title="تحويل PDF إلى PPTX مع القص", layout="wide")

st.title("🎯 تحويل صفحات PDF إلى عرض PPTX جديد مع التحكم بالقص")
st.write("ارفعي ملف الـ PDF، وسيقوم التطبيق بعرض الصفحات كاملة بنصوصها ومعادلاتها، ثم يمكنكِ قص الهوامش وتصديرها كعرض باوربوينت جديد!")

uploaded_pdf = st.file_uploader("📥 ارفعي ملف الـ PDF هنا:", type=["pdf"])

if uploaded_pdf:
    # قراءة صفحات الـ PDF وتحويلها إلى صور PIL
    pdf_bytes = uploaded_pdf.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=150) # تحويل الصفحة إلى صورة عالية الجودة
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        images.append(img)
    
    st.success(f"✅ تم قراءة {len(images)} صفحة من ملف الـ PDF بنجاح!")
    
    # المعاينة والتحكم بالقص عبر الشريحة الأولى
    first_img = images[0]
    w, h = first_img.size

    st.markdown("---")
    st.subheader("🎛️ لوحة التحكم في قص الهوامش (معاينة حية)")
    
    col1, col2 = st.columns(2)
    with col1:
        crop_left = st.slider("✂️ القص من اليسار (%):", 0, 30, 0)
        crop_top = st.slider("✂️ القص من الأعلى (%):", 0, 30, 0)
    with col2:
        crop_right = st.slider("✂️ القص من اليمين (%):", 0, 30, 0)
        crop_bottom = st.slider("✂️ القص من الأسفل (%):", 0, 30, 0)

    # حساب أبعاد القص بالبكسل
    left_px = int(w * (crop_left / 100.0))
    top_px = int(h * (crop_top / 100.0))
    right_px = w - int(w * (crop_right / 100.0))
    bottom_px = h - int(h * (crop_bottom / 100.0))

    cropped_preview = first_img.crop((left_px, top_px, right_px, bottom_px))

    st.markdown("### 👀 معاينة للصفحة الأولى بعد القص:")
    st.image(cropped_preview, caption="تأكدي من وضوح كافة النصوص والمعادلات الرياضية", use_column_width=True)

    st.markdown("---")
    if st.button("🚀 تطبيق القص وتوليد عرض PPTX جديد"):
        with st.spinner("جاري قص كافة الصفحات وإنشاء ملف الباوربوينت..."):
            prs = Presentation()
            # ضبط مقاس الشريحة ليكون 16:9 أفقياً
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)
            blank_slide_layout = prs.slide_layouts[6]

            for img in images:
                sw, sh = img.size
                l = int(sw * (crop_left / 100.0))
                t = int(sh * (crop_top / 100.0))
                r = sw - int(sw * (crop_right / 100.0))
                b = sh - int(sh * (crop_bottom / 100.0))
                
                c_img = img.crop((l, t, r, b))
                
                # حفظ الصورة المقصوصة في الذاكرة
                img_buf = io.BytesIO()
                c_img.save(img_buf, format="PNG")
                img_buf.seek(0)
                
                # إضافة الشريحة وتثبيت الصورة المقصوصة بداخلها
                slide = prs.slides.add_slide(blank_slide_layout)
                slide.shapes.add_picture(img_buf, 0, 0, width=prs.slide_width, height=prs.slide_height)
            
            # حفظ العرض الجديد في الذاكرة لتوفير زر التحميل
            pptx_buf = io.BytesIO()
            prs.save(pptx_buf)
            pptx_buf.seek(0)
            
            st.success("✨ تم إنشاء العرض الجديد بنجاح!")
            st.download_button(
                label="📥 تحميل العرض التقديمي الجديد (.pptx)",
                data=pptx_buf,
                file_name="Converted_Slides.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
            
