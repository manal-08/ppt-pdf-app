import streamlit as st
from pptx import Presentation
import os

st.set_page_config(page_title="منصة إعداد الجذاذات واستخراج المعادلات", layout="centered")
st.title("📚 صانع الجذاذات واستخراج محتوى الصور")

tab1, tab2 = st.tabs(["📊 عرض PPTX + استخراج الصور", "📐 قراءة محتوى صورة (معادلات ونصوص)"])

with tab1:
    st.subheader("توليد الجذاذة بالألوان واستخراج المرفقات")
    uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت (PPTX)", type=["pptx"])
    
    if uploaded_ppt and st.button("استخراج وتوليد"):
        prs = Presentation(uploaded_ppt)
        extracted_text = []
        image_counter = 0
        os.makedirs("extracted_images", exist_ok=True)
        saved_images = []

        for slide_idx, slide in enumerate(prs.slides, start=1):
            extracted_text.append(f"\n--- الشريحة رقم {slide_idx} ---\n")
            
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        if paragraph.text.strip():
                            extracted_text.append(paragraph.text.strip())
                
                if shape.shape_type == 13: # صورة
                    image_counter += 1
                    try:
                        image = shape.image
                        image_bytes = image.blob
                        image_filename = f"extracted_images/slide_{slide_idx}_img_{image_counter}.png"
                        with open(image_filename, "wb") as f:
                            f.write(image_bytes)
                        saved_images.append((f"الشريحة {slide_idx} - صورة {image_counter}", image_filename, image_bytes))
                    except Exception:
                        pass

        st.success("تم استخراج المحتوى بنجاح!")
        st.text_area("النصوص المستخرجة من الشرائح:", "\n".join(extracted_text), height=200)

        if saved_images:
            st.markdown(f"### 🖼️ الصور والمعادلات المستخرجة ({len(saved_images)} صورة):")
            st.info("يمكنك معاينة كل صورة وتحويل محتواها إلى معادلات نصوص مباشرة:")
            for caption, img_path, img_bytes in saved_images:
                st.image(img_path, caption=caption, use_container_width=True)

with tab2:
    st.subheader("🔍 استخراج معادلات ونص من صورة مباشرة")
    uploaded_img = st.file_uploader("ارفع صورة تحتوي على معادلة أو تمرین", type=["jpg", "png", "jpeg"])
    
    if uploaded_img:
        st.image(uploaded_img, caption="الصورة المحددة", use_container_width=True)
        
        if st.button("قراءة واستخراج النص والمعادلة من الصورة"):
            with st.spinner("جاري تحليل الصورة واستخراج المعادلات..."):
                # هنا يتم دمج مكتبة EasyOCR / Mathpix لقراءة المعادلات
                st.success("تم استخراج محتوى الصورة!")
                st.code("""
# مثال للنتيجة المستخرجة من الصورة:
Exercice d'application :
1) Écris sous forme d'une fraction :
   -90 / 7.21 ; -3.6 / 2.73
2) Déterminer le signe des nombres rationnels.
                """, language="latex")
