import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pro Post Creator 4:5", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d0d0d; color: white; }
    stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Pro Post Creator (4:5 Edition)")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎨 Editing Panel")

uploaded_file = st.sidebar.file_uploader("1. Upload Image", type=["jpg", "png", "jpeg"])

text_input = st.sidebar.text_area("2. Text Content", 
    value="HE REIGNED ENGLAND FOR [56 YEARS], REBUILT THE {WESTMINSTER ABBEY}, AND ESTABLISHED THE [FIRST PARLIAMENT]. {KING HENRY III, 1216}.",
    height=150)

st.sidebar.markdown("💡 `[Red]` | `{Yellow}`")

vignette_strength = st.sidebar.slider("3. Vignette Strength", 0.0, 1.0, 0.5)
shadow_height = st.sidebar.slider("4. Bottom Shadow Height", 0, 1000, 600)
font_size = st.sidebar.slider("5. Font Size", 20, 150, 65)
text_y = st.sidebar.slider("6. Text Vertical Pos", 500, 1300, 1050)

font_choice = st.sidebar.selectbox("7. Font Style", ["Montserrat-Bold", "Georgia", "Courier"])

col_norm = st.sidebar.color_picker("Normal Text", "#FFFFFF")
col_h1 = st.sidebar.color_picker("Highlight 1 [ ]", "#FF5050")
col_h2 = st.sidebar.color_picker("Highlight 2 { }", "#D48B0C")

# --- IMAGE PROCESSING FUNCTIONS ---

def apply_effects(image, vignette, s_height, s_opacity=0.95):
    # 1. Resize & Center Crop to 1080x1350 (4:5)
    target_w, target_h = 1080, 1350
    img = ImageOps.fit(image, (target_w, target_h), centering=(0.5, 0.5))
    
    # 2. Add Bottom Shadow (Linear Gradient)
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for i in range(s_height):
        alpha = int((i / s_height) * (s_opacity * 255))
        draw_ov.line([(0, target_h - i), (target_w, target_h - i)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    # 3. Apply Vignette
    # Create radial gradient
    x, y = np.ogrid[:target_h, :target_w]
    center_y, center_x = target_h // 2, target_w // 2
    # Adjusting the mask to be darker at corners
    mask = (np.sqrt((x - center_y)**2 + (y - center_x)**2))
    mask = mask / mask.max()
    mask = np.clip(mask * vignette * 2, 0, 1)
    mask = (mask * 255).astype(np.uint8)
    
    vignette_mask = Image.fromarray(mask).convert("L")
    black_img = Image.new("RGBA", img.size, (0, 0, 0, 255))
    img = Image.composite(black_img, img, vignette_mask)
    
    return img

def render_text(image, text, f_size, y_start, font_name, c_norm, c_h1, c_h2):
    draw = ImageDraw.Draw(image)
    
    # Try to load font, fallback to default
    try:
        font = ImageFont.truetype(f"{font_name}.ttf", f_size)
    except:
        font = ImageFont.load_default()

    margin = 80
    max_width = 1000
    current_x = margin
    current_y = y_start
    
    words = text.upper().split()
    
    for word in words:
        active_color = c_norm
        clean_word = word
        
        # Color Logic
        if '[' in word or ']' in word:
            active_color = c_h1
            clean_word = word.replace('[','').replace(']','')
        elif '{' in word or '}' in word:
            active_color = c_h2
            clean_word = word.replace('{','').replace('}','')
            
        # Measure word
        bbox = draw.textbbox((0, 0), clean_word + " ", font=font)
        w_w = bbox[2] - bbox[0]
        
        # Wrapping
        if current_x + w_w > max_width:
            current_x = margin
            current_y += f_size + 20
            
        draw.text((current_x, current_y), clean_word, font=font, fill=active_color)
        current_x += w_w
        
    return image

# --- MAIN APP EXECUTION ---

if uploaded_file:
    base_img = Image.open(uploaded_file)
    
    # Apply Image Effects
    processed_img = apply_effects(base_img, vignette_strength, shadow_height)
    
    # Render Text
    final_post = render_text(processed_img, text_input, font_size, text_y, font_choice, col_norm, col_h1, col_h2)
    
    # Preview
    st.image(final_post, caption="Final 4:5 Post Preview", use_column_width=True)
    
    # Download Button
    buf = io.BytesIO()
    final_post.convert("RGB").save(buf, format="JPEG", quality=95)
    st.download_button(
        label="⬇️ Download Final Post",
        data=buf.getvalue(),
        file_name="pro_post_45.jpg",
        mime="image/jpeg"
    )
else:
    st.info("Bhai, pehle left side se ek image upload karo!")
    # Show a placeholder image
    st.image("https://via.placeholder.com/1080x1350.png?text=Bhai+Image+Upload+Karo", width=400)
