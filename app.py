import streamlit as st
import streamlit.components.v1 as st_components
import cloudinary
import cloudinary.uploader
import cloudinary.search
import random
import os
from dotenv import load_dotenv

from categories import get_display_names, get_tag_name
from components import get_flip_card_html

# --------- 頁面設定 ---------
st.set_page_config(
    page_title="攝影構圖分類器 (Photography Composition Classifier)",
    page_icon="📷",
    layout="wide"
)

# --------- 初始化 Cloudinary ---------
# 嘗試從 Streamlit Secrets 讀取，若沒有則嘗試 .env 檔案
load_dotenv()

try:
    if "cloudinary" in st.secrets:
        cloudinary.config(
            cloud_name=st.secrets["cloudinary"]["cloud_name"],
            api_key=st.secrets["cloudinary"]["api_key"],
            api_secret=st.secrets["cloudinary"]["api_secret"],
            secure=True
        )
    else:
        cloudinary.config(
            cloud_name=os.getenv("CLOUD_NAME"),
            api_key=os.getenv("API_KEY"),
            api_secret=os.getenv("API_SECRET"),
            secure=True
        )
        
    config = cloudinary.config()
    if not config.api_key or config.api_key == "YOUR_API_KEY":
        has_credentials = False
    else:
        has_credentials = True
except Exception as e:
    has_credentials = False

def init_session_state():
    # 紀錄各個分類的快取照片 URL，避免每次重新整理畫面都去呼叫 API
    if 'image_cache' not in st.session_state:
        st.session_state.image_cache = {}

init_session_state()

# --------- Backend Helper Functions ---------
def get_all_images_by_tag(tag, force_refresh=False):
    """從 Cloudinary 依據標籤找出所有照片(最多50張)"""
    if not has_credentials:
        return []
        
    if not force_refresh and tag in st.session_state.image_cache:
        # 兼容之前快取只存字串或單一 dict 的情況
        cached = st.session_state.image_cache[tag]
        if isinstance(cached, list):
            return cached
        elif isinstance(cached, dict) and 'url' in cached:
            return [cached]
        elif isinstance(cached, str):
            return [{'url': cached, 'public_id': None}]
        return cached if isinstance(cached, list) else []
        
    try:
        # Search API 預設抓近期 50 張有該標籤的照片
        result = cloudinary.Search().expression(f"tags={tag} AND resource_type:image").max_results(50).execute()
        images = result.get('resources', [])
        
        data_list = []
        for img in images:
            data_list.append({
                'url': img.get('secure_url'), 
                'public_id': img.get('public_id')
            })
            
        st.session_state.image_cache[tag] = data_list
        return data_list
    except Exception as e:
        st.warning(f"取得照片時發生錯誤: {e}")
        return []

# --------- UI Layout ---------
st.title("📷 攝影構圖分類與圖庫")

if not has_credentials:
    st.error("⚠️ 尚未設定 Cloudinary 憑證。請確保 `.streamlit/secrets.toml` 或 `.env` 中已提供正確的金鑰。")

tab1, tab2, tab3 = st.tabs(["🖼️ 構圖藝廊 (Gallery)", "🗂️ 照片管理 (Manage)", "📤 上傳照片 (Upload)"])

with tab3:
    st.header("上傳新的照片並分類")
    
    uploaded_file = st.file_uploader("請選擇一張照片...", type=["jpg", "png", "jpeg", "webp"])
    selected_composition = st.selectbox("這張照片屬於哪一種構圖？", get_display_names())
    
    if st.button("🚀 上傳至圖庫", type="primary"):
        if not has_credentials:
            st.error("請先設定 Cloudinary 憑證！")
        elif uploaded_file is None:
            st.warning("請先選擇一張照片！")
        else:
            with st.spinner('上傳中，請稍候...'):
                try:
                    tag_name = get_tag_name(selected_composition)
                    # 讀取檔案內容
                    file_bytes = uploaded_file.getvalue()
                    
                    # 執行 Cloudinary 上傳，並附上標籤
                    response = cloudinary.uploader.upload(
                        file_bytes, 
                        tags=[tag_name]
                    )
                    
                    st.success(f"✅ 上傳成功！已歸類為：{selected_composition}")
                    st.image(response.get('secure_url'), caption="您上傳的照片", use_container_width=True)
                    
                    # 清除該標籤的快取，讓下次能抓到新圖
                    if tag_name in st.session_state.image_cache:
                        del st.session_state.image_cache[tag_name]
                        
                except Exception as e:
                    st.error(f"❌ 上傳失敗: {e}")

with tab2:
    st.header("管理圖庫照片")
    manage_category = st.selectbox("選擇要管理的構圖分類：", get_display_names(), key="manage_category")
    manage_tag = get_tag_name(manage_category)
    
    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("🔄 重新載入"):
            get_all_images_by_tag(manage_tag, force_refresh=True)
            st.rerun()
            
    images = get_all_images_by_tag(manage_tag)
    if not images:
        st.info("此分類尚無照片。")
    else:
        st.write(f"共找到 {len(images)} 張照片：")
        manage_cols = st.columns(4)
        for idx, img_data in enumerate(images):
            with manage_cols[idx % 4]:
                st.image(img_data['url'], use_container_width=True)
                if st.button("🗑️ 刪除", key=f"del_{img_data['public_id']}", use_container_width=True):
                    try:
                        cloudinary.uploader.destroy(img_data['public_id'])
                        get_all_images_by_tag(manage_tag, force_refresh=True)
                        st.rerun()
                    except Exception as e:
                        st.error(f"刪除失敗: {e}")

with tab1:
    st.header("探索各種攝影構圖")
    st.write("點擊下方的卡片，每次翻面都會自動給您隨機的驚喜！")
    
    categories = get_display_names()
    
    # 使用 3 欄的網格排列
    cols_per_row = 3
    
    for i in range(0, len(categories), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(categories):
                display_name = categories[i + j]
                tag_name = get_tag_name(display_name)
                
                with col:
                    # 取得該標籤的所有照片 URLs
                    img_data_list = get_all_images_by_tag(tag_name)
                    urls = [img['url'] for img in img_data_list] if img_data_list else []
                    
                    # 產生翻牌卡的 HTML，傳入 urls 陣列交由前端隨機抽取
                    card_html = get_flip_card_html(
                        front_text=display_name, 
                        back_image_urls=urls, 
                        no_image_text="尚無照片"
                    )
                    
                    # 透過 st_components 渲染在畫面上
                    st_components.html(card_html, height=320)
