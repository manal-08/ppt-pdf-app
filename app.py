import streamlit as st
from pptx import Presentation

st.set_page_config(page_title="مُحوّل العروض والصور", layout="centered")
st.title("📄 محول PPTX والصور إلى PDF")

tab1, tab2 = st.tabs(["📊 عرض تقديمي PPTX", "📐 صورة عمليات رياضية"])

with tab1:
    st.subheader("استخراج الفقرات من ملف PPTX وتصديرها")
    uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت", type=["pptx"])
    
    if uploaded_ppt and st.button("استخراج وتحويل"):
        prs = Presentation(uploaded_ppt)
        extracted_text = []
        
        for slide_idx, slide in enumerate(prs.slides, start=1):
            extracted_text.append(f"\n--- الشريحة رقم {slide_idx} ---\n")
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        if paragraph.text.strip():
                            extracted_text.append(paragraph.text.strip())
        
        full_text = "\n".join(extracted_text)
        
        st.success("تم استخراج النصوص بنجاح!")
        st.text_area("النصوص المستخرجة:", full_text, height=300)
        
        st.download_button(
            label="⬇️ تحميل النصوص كملف TXT (جاهز للطباعة كـ PDF)",
            data=full_text.encode('utf-8'),
            file_name="extracted_slides.txt",
            mime="text/plain"
        )

with tab2:
    st.subheader("قراءة المعادلات الرياضية من الصور")
    uploaded_img = st.file_uploader("اختر صورة تحتوي على معادلات", type=["jpg", "png", "jpeg"])
    
    if uploaded_img:
        st.image(uploaded_img, caption="الصورة المرفوعة", use_container_width=True)
        st.info("💡 لقراءة المعادلات الرياضية بدقة عالية، يمكن إضافة مفتاح Mathpix API أو OpenAI Vision مستقبلاً.")
