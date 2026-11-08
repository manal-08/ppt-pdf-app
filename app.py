import streamlit as st
from pptx import Presentation
import os
import easyocr

@st.cache_resource
def load_reader():
    return easyocr.Reader(['fr', 'en'])

reader = load_reader()

st.set_page_config(page_title="صانع الجذاذات الرياضية الذكي", layout="centered")
st.title("📚 منصة توليد الجذاذات الرياضية من الباوربوينت")

uploaded_ppt = st.file_uploader("اختر ملف الباوربوينت (PPTX)", type=["pptx"])

if uploaded_ppt and st.button("توليد الجذاذة وترتيبها"):
    with st.spinner("جاري استخراج النصوص والمعادلات وتنسيق الجذاذة..."):
        prs = Presentation(uploaded_ppt)
        all_content = []
        
        os.makedirs("temp_slides_img", exist_ok=True)

        for slide_idx, slide in enumerate(prs.slides, start=1):
            all_content.append(("TITLE_SLIDE", f"--- الشريحة رقم {slide_idx} ---"))
            
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        txt = paragraph.text.strip()
                        if txt:
                            all_content.append(("TEXT", txt))
                
                elif shape.shape_type == 13:
                    try:
                        image_bytes = shape.image.blob
                        img_path = f"temp_slides_img/slide_{slide_idx}_img.png"
                        with open(img_path, "wb") as f:
                            f.write(image_bytes)
                        
                        results = reader.readtext(img_path)
                        for (_, text, _) in results:
                            if text.strip():
                                all_content.append(("TEXT", text.strip()))
                    except Exception:
                        pass

        # بناء محتوى HTML منسق بالألوان المطلوبة تماماً
        html_content = """
        <div style="font-family: Arial, sans-serif; direction: ltr; padding: 20px; background-color: #fff; color: #000;">
        """

        for el_type, text in all_content:
            if el_type == "TITLE_SLIDE":
                html_content += f"<h3 style='color: #646464; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 20px;'>{text}</h3>"
                continue

            color = "#000000"  # أسود افتراضي
            weight = "normal"

            # الألوان البيداغوجية حسب طلبك:
            if any(text.startswith(roman) for roman in ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]):
                color = "#C80000"  # أحمر للعناوين الرومانية
                weight = "bold"
            elif any(text.startswith(f"{i})") or text.startswith(f"{i} -") for i in range(1, 15)):
                color = "#008000"  # أخضر للعناوين العادية
                weight = "bold"
            elif "Règle" in text or "Regle" in text:
                color = "#800080"  # بنفسجي للقواعد
                weight = "bold"
            elif any(k in text for k in ["Activité", "Activite", "Exemple", "Exemples", "Définition", "Definition", "Remarque"]):
                color = "#0066CC"  # أزرق سماوي
                weight = "bold"
            elif "Propriété" in text or "Propriete" in text:
                color = "#FF8000"  # برتقالي للخاصيات
                weight = "bold"
            elif any(k in text for k in ["Application", "Exercice", "Exercices"]):
                color = "#8B4513"  # بني للتطبيقات
                weight = "bold"

            html_content += f"<p style='color: {color}; font-weight: {weight}; margin: 5px 0;'>{text}</p>"

        html_content += "</div>"

        st.success("تم توليد الجذاذة بنجاح وبجميع الألوان المطلوبة!")
        
        # عرض الجذاذة مباشرة على الشاشة بشكل جميل
        st.markdown("### 📄 معاينة الجذاذة النهائية:")
        st.markdown(html_content, unsafe_allow_html=True)

        # زر تحميل النتيجة كملف HTML (يمكن فتحه وطباعته كـ PDF من المتصفح مباشرة)
        st.download_button(
            label="⬇️ تحميل الجذاذة كملف (جاهز للطباعة)",
            data=html_content.encode('utf-8'),
            file_name="Jadad_Mathematiques_Pro.html",
            mime="text/html"
        )
