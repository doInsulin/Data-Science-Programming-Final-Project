import streamlit as st
from store.anime_store import AnimeStore
import util.source_visualization as sv

# ========== 页面标题 + 数据读取 ==========
st.title("Source Analysis")

try:
    store = AnimeStore()
    df = store.df
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()


# ========== 分析 1 ==========
sv.plot_source_year_analysis(df)

sv.plot_source_genre_analysis(df)

sv.plot_source_score_analysis(df)
