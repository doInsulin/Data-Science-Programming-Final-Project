import streamlit as st
import util.popularity_visualization as vl
from store.anime_store import AnimeStore

# ========== 页面标题 + 获取数据 ==========
try:
    store = AnimeStore()
    anime_df = store.df
    original_count = len(anime_df)
except FileNotFoundError as e:
    st.error(f"❌ {e}")
    st.stop()

# ========== 调用可视化函数 ==========
vl.plot_popularity_analysis(anime_df)
