import streamlit as st
from pptx import Presentation
import io
from PIL import Image

st.set_page_config(page_title="معاينة القص والتحكم بالشرائح", layout="wide")

st.title("🔍 أداة معاينة القص والتحكم المباشر بالشرائح")
st.markdown("---")

uploaded_file = st.file_uploader("📥 ارفع ملف الباوربوينت (PPTX) أو صورة الشريحة:", type=["pptx", "png", "jpg"])

if uploaded_file:
    # استخراج صورة الشريحة الأولى أو الثانية للمعاينة
    image_bytes = None
    if uploaded_file.name.endswith(".pptx"):
        prs = Presentation(uploaded_file)
        if prs.slides:
            for shape in prs.slides[0].shapes: # نستعرض الشريحة الأولى كمثال للمعاينة
                if shape.shape_type == 13:
                    image_bytes = shape.image.blob
                    break
    else:
        image_bytes = uploaded_file.read()

    if image_bytes:
        original_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = original_img.size

        st.subheader("🎛️ لوحة التحكم في مساحة القص")
        
        # أشرطة تحكم دقيقة لكل جانب على حدة (مثل أداة القص في الهاتف)
        col1, col2 = st.columns(2)
        with col1:
            crop_left = st.slider("قص من اليمين / اليسار (أفقي %):", 0, 30, 8)
            crop_top = st.slider("قص من الأعلى (رأسي %):", 0, 30, 8)
        with col2:
            crop_right = st.slider("قص من اليمين (أفقي %):", 0, 30, 8)
            crop_bottom = st.slider("قص من الأسفل (رأسي %):", 0, 30, 8)

        # تطبيق القص بناءً على اختياركِ الفوري
        left_px = int(w * (crop_left / 100.0))
        top_px = int(h * (crop_top / 100.0))
        right_px = w - int(w * (crop_right / 100.0))
        bottom_px = h - int(h * (crop_bottom / 100.0))

        cropped_img = original_img.crop((left_px, top_px, right_px, bottom_px))

        st.markdown("### 👀 معاينة مباشرة لما بعد القص:")
        st.image(cropped_img, caption="نتيجة القص الحالية (تأكدي أن المعادلات والكسور واضحة وغير منقوصة)", use_column_width=True)
        
        st.success("✅ جربي تحريك المؤشرات بالأعلى واطلعي على الصورة بالأسفل حتى تصلي للمقاس المثالي الذي يزيل الإطار المزخرف ويبقي على محتوى الدرس كاملاً. عندما تضبط معكِ، أخبريني لنعتمد هذه القيم وننتقل للخطوة التالية مباشرة!")
        
