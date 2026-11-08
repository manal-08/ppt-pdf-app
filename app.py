import streamlit as st
from pptx import Presentation
import io
import os

st.set_page_config(page_title="مُحوّل العروض والرياضيات", layout="centered")
st.title("📄 محول الشرائح والصور الرياضية")

tab1, tab2 = st.tabs(["📊 عرض تقديمي PPTX (نصوص وصور)", "📐 صور المعادلات الرياضية"])

with tab1:
    st.subheader("استخراج النصوص والرسومات من ملف PPTX")
    uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت", type=["pptx"])
    
    if uploaded_ppt and st.button("استخراج المحتويات"):
        prs = Presentation(uploaded_ppt)
        extracted_text = []
        image_counter = 0
        
        # إنشاء مجلد مؤقت لحفظ الصور المستخرجة
        os.makedirs("extracted_images", exist_ok=True)
        saved_images = []

        for slide_idx, slide in enumerate(prs.slides, start=1):
            extracted_text.append(f"\n--- الشريحة رقم {slide_idx} ---\n")
            
            # استخراج النصوص
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        if paragraph.text.strip():
                            extracted_text.append(paragraph.text.strip())
                
                # استخراج الصور والمعادلات المصورة داخل الشريحة
                if shape.shape_type == 13:  .shape_type 13 is Picture
                    image_counter += 1
                    image = shape.image
                    image_bytes = image.blob
                    image_filename = f"extracted_images/slide_{slide_idx}_img_{image_counter}.png"
                    
                    with open(image_filename, "wb") as f:
                        f.write(image_bytes)
                    saved_images.append((f"الشريحة {slide_idx} - صورة {image_counter}", image_filename))

        full_text = "\n".join(extracted_text)
        
        st.success("تم استخراج النصوص والصور بنجاح!")
        
        # عرض النصوص المستخرجة
        st.markdown("### 📝 النصوص المستخرجة:")
        st.text_area("النصوص:", full_text, height=200)
        
        st.download_button(
            label="⬇️ تحميل النصوص كملف TXT",
            data=full_text.encode('utf-8'),
            file_name="slides_text.txt",
            mime="text/plain"
        )
        
        # عرض الصور المستخرجة من الباوربوينت
        if saved_images:
            st.markdown(f"### 🖼️ الصور والمعادلات المستخرجة ({len(saved_images)} صورة):")
            for caption, img_path in saved_images:
                st.image(img_path, caption=caption, use_container_width=True)

with tab2:
    st.subheader("معالجة وقراءة المعادلات الرياضية من الصور الخارجية")
    uploaded_img = st.file_uploader("اختر صورة تحتوي على معادلات", type=["jpg", "png", "jpeg"])
    
    if uploaded_img:
        st.image(uploaded_img, caption="الصورة المرفوعة", use_container_width=True)
        st.info("💡 هذه المساحة مخصصة لمعاينة وعرض صور المعادلات الرياضية الخاصة بكِ لاستخدامها في التمارين والجذاذات.")
