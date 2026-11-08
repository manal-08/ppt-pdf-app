import streamlit as st
from pptx import Presentation
import io
from PIL import Image

st.set_page_config(page_title="معاينة القص والتحكم بالشرائح", layout="wide")

st.title("🔍 أداة معاينة القص والتحكم المباشر بالشريحة")
st.markdown("---")

uploaded_file = st.file_uploader("📥 ارفع ملف الباوربوينت (PPTX):", type=["pptx"])

if uploaded_file:
    # قراءة الشرائح واستخراج صور الأشكال الموجودة فيها لتعرض للمعاينة
    image_bytes = None
    try:
        prs = Presentation(uploaded_file)
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.shape_type == 13: # صورة داخل الشريحة
                    image_bytes = shape.image.blob
                    break
            if image_bytes:
                break
    except Exception as e:
        st.error(fحدث خطأ أثناء قراءة الملف: {e}")

    if image_bytes:
        original_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = original_img.size

        st.subheader("🎛️ لوحة التحكم في مساحة القص (مثل الهاتف)")
        
        col1, col2 = st.columns(2)
        with col1:
            crop_left = st.slider("قص من اليسار (%):", 0, 30, 8)
            crop_top = st.slider("قص من الأعلى (%):", 0, 30, 8)
        with col2:
            crop_right = st.slider("قص من اليمين (%):", 0, 30, 8)
            crop_bottom = st.slider("قص من الأسفل (%):", 0, 30, 8)

        # حساب أبعاد القص بالبكسل
        left_px = int(w * (crop_left / 100.0))
        top_px = int(h * (crop_top / 100.0))
        right_px = w - int(w * (crop_right / 100.0))
        bottom_px = h - int(h * (crop_bottom / 100.0))

        cropped_img = original_img.crop((left_px, top_px, right_px, bottom_px))

        st.markdown("### 👀 معاينة مباشرة لما بعد القص:")
        st.image(cropped_img, caption="هكذا ستظهر الشريحة بعد إزالة الإطار المزخرف", use_column_width=True)
        
        st.success("✅ الآن تظهر لكِ المعاينة مباشرة! حركي المؤشرات للأعلى لتجربة القص بدقة، وعندما تضبط معكِ، أخبريني لنعتمد هذه القيم وننتقل للخطوة النهائية!")
    else:
        st.warning("⚠️ لم يتم العثور على صورة داخل الشرائح. يرجى التأكد من أن ملف الـ PPTX يحتوي على خلفية أو صور شرائح.")
        
