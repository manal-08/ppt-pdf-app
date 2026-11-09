import streamlit as st
from PIL import Image
import easyocr
import numpy as np

# إعداد صفحة التطبيق
st.set_page_config(page_title="مستخرج النص والمعادلات من الصور", layout="centered")

st.markdown("<h2 style='text-align: center; color: #2c3e50;'>🔍 قراءة واستخراج المحتوى الرياضي من الصور</h2>", unsafe_allow_html=True)
st.write("---")

# تحميل نموذج التعرف البصري (يدعم الإنجليزية والفرنسية والرموز الرياضية)
@st.cache_resource
def load_reader():
    # 'en' و 'fr' ممتازان لقراءة الرموز الرياضية والأسس والمعادلات والفرنسية
    return easyocr.Reader(['en', 'fr'], gpu=False)

with st.spinner("جاري تجهيز محرك القراءة والذكاء الاصطناعي..."):
    reader = load_reader()

# زر لرفع الصورة
uploaded_image = st.file_uploader("📥 ارفعي صورة الشريحة أو التمرين الرياضي هنا:", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    # فتح الصورة وعرضها في شاشة المعاينة
    image = Image.open(uploaded_image)
    
    st.markdown("### 👁️ شاشة المعاينة للصورة المرفوعة:")
    st.image(image, use_column_width=True)
    
    st.write("---")
    
    # زر لبدء عملية الاستخراج
    if st.button("🚀 استخراج النصوص والمعادلات من الصورة", use_container_width=True):
        with st.spinner("جاري قراءة وتحليل محتوى الصورة الرياضي..."):
            try:
                # تحويل الصورة إلى مصفوفة مناسبة للمحرك
                image_np = np.array(image)
                
                # استخراج النصوص والرموز
                results = reader.readtext(image_np)
                
                # تجميع النصوص المستخرجة
                extracted_text_lines = []
                for (bbox, text, prob) in results:
                    # تصفية النتائج الضعيفة لضمان دقة عالية
                    if prob > 0.2: 
                        extracted_text_lines.append(text)
                
                full_extracted_text = "\n".join(extracted_text_lines)
                
                st.success("✨ تم استخراج المحتوى بنجاح!")
                
                # عرض النص المستخرج في مربع قابل للنسخ
                st.markdown("### 📝 المحتوى المستخرج (النصوص والمعادلات):")
                st.text_area("يمكنك نسخه واستخدامه مباشرة:", value=full_extracted_text, height=200)

            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء قراءة الصورة: {e}")
