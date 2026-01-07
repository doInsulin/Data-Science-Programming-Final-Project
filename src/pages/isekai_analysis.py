import streamlit as st
import pandas as pd
import numpy as np
from store.anime_store import AnimeStore
from util.visualization_part1 import plot_isekai_trends, plot_isekai_wordcloud

# ========== 页面标题 + 获取数据 ==========
st.set_page_config(page_title="The Rise of Isekai Anime", layout="wide")
st.title("The Rise of Isekai Anime")

try:
    store = AnimeStore()
    anime_df = store.df
except FileNotFoundError as e:
    st.error(f"❌ {e}")
    st.stop()

# ========== Top 10 tags and Isekai trends (2016–2025) ==========
try:
    st.subheader("Top 10 tags and Isekai trends (2016–2025)")
    fig, year_tag_counts, isekai_count = plot_isekai_trends(
        df=anime_df, start_year=2016, end_year=2025
    )
    
    st.markdown(
        """
        When exploring the evolution of anime content trends over the past decade, the rise of the isekai genre is an unavoidable topic. By breaking down and analyzing the tags in our dataset, we found that isekai works, unlike genres such as School and Magic, have shown a significant growth trend over the past ten years.
        """
    )
  
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        st.plotly_chart(fig, use_container_width=False)
    st.markdown(
        """
        *The chart shows the frequency changes of the Top 10 tags (red line for Isekai) from 2016 to 2025, as well as the trend of the number of Isekai works in the lower right subplot.*
        """
    )
except ValueError as e:
    st.error(f"数据格式错误：{e}")
except Exception as e:
    st.error(f"绘图时发生错误：{e}")

# ========== Isekai 标签词云 ==========
try:
    st.subheader("Isekai anime tag word cloud")
    fig_wordcloud, tfidf_rank = plot_isekai_wordcloud(df=anime_df)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.pyplot(fig_wordcloud, use_container_width=True)
except ValueError as e:
    st.error(f"数据格式错误：{e}")
except Exception as e:
    st.error(f"生成词云时发生错误：{e}")

# ========== 分析说明 ==========
st.subheader("Top 10 Co-occurring Tags with Isekai")
col1, col2, col3 = st.columns([1.3, 2, 0.5])
with col2:
    st.markdown(
        """
        | Rank | Tag | Count |
        |------|-----|-------|
        | 1 | Magic | 256 |
        | 2 | Male Protagonist | 209 |
        | 3 | Female Protagonist | 174 |
        | 4 | Primarily Female Cast | 140 |
        | 5 | Medieval | 118 |
        | 6 | Female Harem | 114 |
        | 7 | Demons | 109 |
        | 8 | Swordplay | 106 |
        | 9 | Ensemble Cast | 101 |
        | 10 | Heterosexual | 97 |
        """
    )
st.markdown(
    """
    Based on the visualization results of this project and the real-world information we collected, we found that the popularity of the isekai (another world) genre is actually an external manifestation of the **industrialization of Japanese anime**. The content supply for this genre is low-cost and predictable, and its settings are highly modular (protagonist growth, leveling/systems, nation-building/harem/royal path/plot twists, etc.), allowing for the creation of new stories by replacing details within the same worldview template. For publishers looking to quickly attract viewers, this is a shortcut to "rapidly replicating successful elements."

    Furthermore, we observed an explosive growth in the number of isekai works between 2020 and 2021, making it a significant genre in the anime lineup that season. This was primarily due to the strong expansion of streaming platforms during the pandemic, which facilitated cross-cultural dissemination of isekai and fantasy themes (statistics show that "Magic" was the most frequent tag appearing alongside "isekai" in the dataset; the top 10 tags reveal that isekai works are mostly set in medieval magical backgrounds and focus on combat). Furthermore, existing successful examples (such as *Re:Zero* and *That Time I Got Reincarnated as a Slime*) instilled commercial confidence in "replicating successful models."

    However, in recent years, due to the influence of public opinion in the community, the proliferation of isekai (another world) anime has become synonymous with "low quality," which reflects the saturation of the isekai genre. Therefore, it is foreseeable that isekai works will not disappear, but their scale will slowly shrink, and they will not be able to replicate the increasingly prosperous scene of the past decade.
    """
)
