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
    has_credentials = True
except Exception as e:
    has_credentials = False

def init_session_state():
    # 紀錄各個分類的快取照片 URL，避免每次重新整理畫面都去呼叫 API
    if 'image_cache' not in st.session_state:
        st.session_state.image_cache = {}

init_session_state()

# --------- Backend Helper Functions ---------
def get_random_image_by_tag(tag, force_refresh=False):
    """從 Cloudinary 依據標籤找出隨機照片"""
    if not has_credentials:
        return None
        
    # 如果且沒有強制更新且已經有快取，就使用快取
    if not force_refresh and tag in st.session_state.image_cache:
        cached = st.session_state.image_cache[tag]
        # 兼容之前快取只存字串的情況
        if isinstance(cached, str):
            return {'url': cached, 'public_id': None}
        return cached
        
    try:
        # Search API 預設抓近期 50 張有該標籤的照片
        result = cloudinary.Search().expression(f"tags={tag} AND resource_type:image").max_results(50).execute()
        images = result.get('resources', [])
        
        if not images:
            st.session_state.image_cache[tag] = None
            return None
            
        random_image = random.choice(images)
        url = random_image.get('secure_url')
        pid = random_image.get('public_id')
        data = {'url': url, 'public_id': pid}
        st.session_state.image_cache[tag] = data
        return data
    except Exception as e:
        st.warning(f"取得照片時發生錯誤: {e}")
        return None

# --------- UI Layout ---------
st.title("📷 攝影構圖分類與圖庫")

if not has_credentials:
    st.error("⚠️ 尚未設定 Cloudinary 憑證。請確保 `.streamlit/secrets.toml` 或 `.env` 中已提供正確的金鑰。")

tab1, tab2 = st.tabs(["🖼️ 構圖藝廊 (Gallery)", "📤 上傳照片 (Upload)"])

with tab2:
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
                    
                    # 清除該標籤的快取，讓下次看藝廊能有機會抽到新圖
                    if tag_name in st.session_state.image_cache:
                        del st.session_state.image_cache[tag_name]
                        
                except Exception as e:
                    st.error(f"❌ 上傳失敗: {e}")

with tab1:
    st.header("探索各種攝影構圖")
    st.write("點擊下方的卡片，即可揭曉該構圖的照片！")
    
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
                    # 取得顯示用照片
                    img_data = get_random_image_by_tag(tag_name)
                    img_url = img_data['url'] if img_data else None
                    public_id = img_data.get('public_id') if img_data else None
                    
                    # 產生翻牌卡的 HTML
                    card_html = get_flip_card_html(
                        front_text=display_name, 
                        back_image_url=img_url, 
                        no_image_text="尚無照片"
                    )
                    
                    # 透過 st_components 渲染在畫面上
                    st_components.html(card_html, height=320)
                    
                    # 提供換一張與刪除的功能
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button(f"🔄 換一張", key=f"refresh_{tag_name}", use_container_width=True):
                            # 強制更新快取並重新整理畫面
                            get_random_image_by_tag(tag_name, force_refresh=True)
                            st.rerun()
                    with btn_col2:
                        # 只有當下有照片時才顯示刪除按鈕
                        if public_id and st.button("🗑️ 刪除", key=f"del_{tag_name}_{public_id}", use_container_width=True):
                            try:
                                # 呼叫 Cloudinary API 刪除照片
                                cloudinary.uploader.destroy(public_id)
                                # 強制更新快取並重新整理畫面
                                get_random_image_by_tag(tag_name, force_refresh=True)
                                st.rerun()
                            except Exception as e:
                                st.error(f"刪除失敗: {e}")
