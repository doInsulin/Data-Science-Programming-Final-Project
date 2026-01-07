# pages/search.py
import streamlit as st
import pandas as pd
from store.anime_store import AnimeStore
from store.fill_value_search import fill_anime_missing_values
from util.load_icon import load_icon_base64




HEAT_ICON_SRC = f"data:image/png;base64,{load_icon_base64('public/icon/redu.png')}"
smiley_icon_base64 = f"data:image/png;base64,{load_icon_base64('public/icon/xiaolian.png')}"
neutral_icon_base64 = f"data:image/png;base64,{load_icon_base64('public/icon/yiban.png')}"
crying_icon_base64 = f"data:image/png;base64,{load_icon_base64('public/icon/kulian.png')}"
# ========== 1. 获取数据（单例，只加载一次） ==========
try:
    store = AnimeStore()
    # 获取原始数据
    anime_df = store.df
    original_count = len(anime_df)
    
    # 调用缺失值填充函数处理数据
    anime_df = fill_anime_missing_values(anime_df)
    
except FileNotFoundError as e:
    st.error(f"❌ {e}") 
    st.stop()
except ValueError as e:
    # 捕获填充函数中可能的空数据异常
    st.error(f"❌ 数据处理失败：{e}")
    st.stop()

# ========== 2. 页面配置 ==========
st.set_page_config(page_title="动漫搜索页", layout="wide")
st.title("Discover Your Next Favorite Anime! 🔍")

# ========== 2.5 注入全局CSS（关键！） ==========
try:
    with open("src/css/anime_card.css", "r", encoding="utf-8") as f:
         css = f.read()

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ 未找到 css/anime_card.css，使用默认样式")

# ========== 3. 筛选条件区域 ==========
with st.container(border=True):
    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
    with col1:
        search_keyword = st.text_input("SEARCH", placeholder="Title, studio, tag...")
    with col2:
        # 生成所有独立标签（去重 + 排序）
        all_genres = set()
        for g in anime_df["genres"].dropna():
            all_genres.update(g.split('|'))
        # 转为列表并排序
        genre_list = sorted(list(all_genres))
        genres_option = st.selectbox("GENRES", genre_list, index=0)
    with col3:
        year_option = st.selectbox("YEAR", ["Any"] + sorted(anime_df["seasonYear"].dropna().unique()), index=0)
    with col4:
        season_option = st.selectbox("SEASON", ["Any"] + sorted(anime_df["season"].unique()), index=0)
    with col5:
        format_option = st.selectbox("FORMAT", ["Any"] + sorted(anime_df["format"].unique()), index=0)

with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        status_option = st.selectbox("STATUS", ["Any"] + sorted(anime_df["status"].unique()), index=0)
        min_year = int(anime_df["seasonYear"].dropna().min())
        max_year = int(anime_df["seasonYear"].dropna().max())
        year_range = st.slider("YEAR RANGE", min_year, max_year, (min_year, max_year))
        tag_keyword = st.text_input("TAG CONTAINS", placeholder="Psychological, Time Travel...")
        high_score = st.checkbox("Only show anime with average score ≥ 80")
    with col2:
        source_option = st.selectbox("SOURCE", ["Any"] + sorted(anime_df["source"].unique()), index=0)
        episodes_max = st.slider("EPISODES (Up to 100)", 0, 100, 100)
    with col3:
        studio_keyword = st.text_input("STUDIO", placeholder="e.g. Bones, MAPPA...")
        duration_max = st.slider("DURATION (Up to 150 minutes)", 0, 150, 150)

# ========== 4. 筛选逻辑 ==========
filtered_df = anime_df.copy()

if search_keyword:
    filtered_df = filtered_df[
        filtered_df["title_native"].str.contains(search_keyword, case=False, na=False) |
        filtered_df["mainStudio"].str.contains(search_keyword, case=False, na=False) |
        filtered_df["tags"].str.contains(search_keyword, case=False, na=False)
    ]
if genres_option != "Any":
    filtered_df = filtered_df[
        filtered_df["genres"].str.contains(genres_option, case=False, na=False)
    ]
if year_option != "Any":
    filtered_df = filtered_df[filtered_df["seasonYear"] == int(year_option)]
if season_option != "Any":
    filtered_df = filtered_df[filtered_df["season"] == season_option]
if format_option != "Any":
    filtered_df = filtered_df[filtered_df["format"] == format_option]
if status_option != "Any":
    filtered_df = filtered_df[filtered_df["status"] == status_option]
if source_option != "Any":
    filtered_df = filtered_df[filtered_df["source"] == source_option]
if studio_keyword:
    filtered_df = filtered_df[filtered_df["mainStudio"].str.contains(studio_keyword, case=False, na=False)]
filtered_df = filtered_df[(filtered_df["seasonYear"] >= year_range[0]) & (filtered_df["seasonYear"] <= year_range[1])]
filtered_df = filtered_df[filtered_df["episodes"] <= episodes_max]
filtered_df = filtered_df[filtered_df["duration"] <= duration_max]
if tag_keyword:
    filtered_df = filtered_df[filtered_df["tags"].str.contains(tag_keyword, case=False, na=False)]
if high_score:
    filtered_df = filtered_df[filtered_df["averageScore"] >= 80]

# ========== 5. 分页设置 ==========
PAGE_SIZE = 20  # 每页显示数量
total_items = len(filtered_df)
total_pages = max(1, (total_items + PAGE_SIZE - 1) // PAGE_SIZE)

# 初始化当前页（从1开始）
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# 页码控制函数
def go_to_page(page):
    if 1 <= page <= total_pages:
        st.session_state.current_page = page

# ========== 6. 渲染当前页 ==========
current_page = st.session_state.current_page
start_idx = (current_page - 1) * PAGE_SIZE
end_idx = min(start_idx + PAGE_SIZE, total_items)
current_batch = filtered_df.iloc[start_idx:end_idx]

st.subheader(f"Results (Page {current_page} of {total_pages} | {total_items} titles)")

if len(current_batch) > 0:
    cols = st.columns(4)
    for idx, (_, row) in enumerate(current_batch.iterrows()):
        with cols[idx % 4]:
            anime_link = f"https://anilist.co/anime/{row['id']}"
            
            title_native = str(row.get("title_native", "") or "")  # 本土标题（如日文原名）
            
            
            # 判断是否使用英文标题，如果英文标题为空则使用罗马音标题
            
            
            genres = str(row.get("genres") or "")
            tags_list = [g.strip() for g in genres.split("|") if g.strip()]
            hover_tags_html = "".join(
                f'<span class="hover-tag">{g}</span>'
                for g in tags_list[:6]
            )

            # 🔥 热度（这里用 popularity；你也可以换成 trending）
            heat_value = int(row.get("popularity", 0))

            # 最右一列加上 hover-left 类 -> 悬浮卡片改到左边
            wrapper_class = "anime-card-wrapper"
            if idx % 4 == 3:  # 0,1,2,3 -> 第四张是最右一列
                wrapper_class += " hover-left"

            card_html = f'''
<a href="{anime_link}" target="_blank" style="text-decoration: none;">
<div class="{wrapper_class}">
<div class="anime-card">
<h5>{title_native}</h5> <!-- Title as native Japanese or Romaji -->
<span class="score-badge">Score {row['averageScore']}</span>
<span class="year-badge">{row['seasonYear']}</span>
<p class="meta">{row['season']} season · {row['episodes']} eps × {row['duration']}m · {row['mainStudio']}</p>

</div>
<div class="anime-hover-card">
  <div class="hover-header">
    <div class="hover-title">{title_native}</div> <!-- Display the full title here -->
    <div class="hover-heat">
      <img src="{HEAT_ICON_SRC}" class="heat-icon" />
      <span class="heat-label">Heat</span>
      <span class="heat-value">{heat_value}</span>
    </div>
  </div>
  
  <!-- Add startDate and endDate -->
  <div class="hover-meta">Aired: {row['startDate']} to {row['endDate']} · {row['episodes']} episodes</div>
  
  <!-- Add status -->
  <div class="hover-meta">Status: {row['status']}</div>
  
  <!-- Add emoji based on score -->
  <div class="hover-score">
    <img src="{smiley_icon_base64 if row['averageScore'] > 80 else neutral_icon_base64 if 50 <= row['averageScore'] <= 80 else crying_icon_base64}" alt="Score Icon" class="score-icon" />
    <span>{row['averageScore']}</span>
  </div>
  
  <div class="hover-tags">{hover_tags_html}</div>
  <div class="hover-extra">ID: {row['id']} · MAL ID: {row['idMal']}</div>
</div>
</div>
</a>
'''

            st.markdown(card_html, unsafe_allow_html=True)
else:
    st.info("未找到符合条件的动漫，请调整筛选条件~")






# ========== 7. 分页栏 ==========
st.divider()

col_prev, col_nums, col_next = st.columns([1, 3, 1])

# ← 上一页
with col_prev:
    if st.button("← Prev", disabled=(current_page <= 1), use_container_width=True):
        go_to_page(current_page - 1)
        st.rerun()

# 页码按钮（动态生成，最多显示7个：当前页±3）
with col_nums:
    page_buttons = st.columns(7)
    # 计算显示范围
    start_page = max(1, current_page - 3)
    end_page = min(total_pages, start_page + 6)
    if end_page - start_page < 6:
        start_page = max(1, end_page - 6)
    
    page_range = list(range(start_page, end_page + 1))
    
    for i, page in enumerate(page_range):
        if i < len(page_buttons):
            with page_buttons[i]:
                if st.button(
                    str(page), 
                    disabled=(page == current_page),
                    key=f"page_{page}",
                    use_container_width=True
                ):
                    go_to_page(page)
                    st.rerun()

# → 下一页
with col_next:
    if st.button("Next →", disabled=(current_page >= total_pages), use_container_width=True):
        go_to_page(current_page + 1)
        st.rerun()

# 额外控制：跳转到首页/末页
col_first, col_last = st.columns(2)
with col_first:
    if st.button("« First", disabled=(current_page == 1), use_container_width=True):
        go_to_page(1)
        st.rerun()
with col_last:
    if st.button("Last »", disabled=(current_page == total_pages), use_container_width=True):
        go_to_page(total_pages)
        st.rerun()