import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from store.anime_store import AnimeStore
from util.visualization_part1 import (
    plot_studio_capacity_pie,
    plot_top10_studio_source_composition,
    plot_trend_anime_vs_studios,
)

# ========== page title + get data ==========
st.set_page_config(page_title="Studio Capacity Analysis", layout="wide")
st.title("Studio Capacity Analysis")

try:
    store = AnimeStore()
    anime_df = store.df
except FileNotFoundError as e:
    st.error(f"❌ {e}")
    st.stop()

try:
    st.subheader("Top 10 Studios vs. Others")
    st.markdown(
        """
        The Japanese animation industry has flourished in recent years, with a constant stream of new studios emerging. According to data compiled from various sources, there are nearly 500 active animation studios in Japan, roughly double the number around 2000. These new studios have expanded the animation production pool, but production is not concentrated in the hands of a few giants; instead, it exhibits a "long tail" pattern: according to our statistics on animation data from 2016 to 2025, the top ten studios in terms of output produced approximately 23% of all series animations, a relatively low concentration. This means that most animated works are completed by numerous small and medium-sized studios, with the vast majority producing very little each year, some even participating in only one project over several years.
        """
    )
    fig, top_series = plot_studio_capacity_pie(anime_df, top_n=10)
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Top 10 Studios (by number of works)")
    st.table(top_series.rename_axis("studio").reset_index(name="count"))
except ValueError as e:
    st.error(f"数据格式错误：{e}")
except Exception as e:
    st.error(f"绘图时发生错误：{e}")

# ========== Top 10 studios organized by source (horizontally stacked bars) ==========
try:
    fig2, studio_source_df = plot_top10_studio_source_composition(anime_df, top_n=10)
    st.subheader("Source Composition of Works from Top 10 Studios")
    st.markdown(
        """
        In the content composition of leading studios, in addition to the traditional "comics" as the main source, "light novels" and "original" works account for a significant proportion, especially in some studios such as J.C.STAFF and Sunrise. This indicates that studios are paying more attention to the diversification of content sources in their production layout, in order to reduce their dependence on a single IP type and adapt to changes in market demand.
        """
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(
        "*Top 10 studios with the highest output of animated series from 2016 to 2025 (by number of works). It can be seen that no single studio produces significantly more works than the others. The output of the top studios is relatively close, while a large number of small studios in the long tail contribute nearly 80% of the total output.*"
    )
except ValueError as e:
    st.error(f"数据格式错误：{e}")
except Exception as e:
    st.error(f"绘图时发生错误（Source 构成）：{e}")

# ========== Annual Trend Chart: Anime Production vs. Number of Active Studios (2016-2025) ==========
try:
    file_path = "public\\data\\anilist_anime_2016_2025_cleaned.csv"
    fig_trend, trend_df = plot_trend_anime_vs_studios(file_path=file_path, start_year=2016, end_year=2025)
    st.subheader("Annual changes in studio output and animation production (2016–2025)")
    st.markdown(
        """
        Looking at the annual trends, the overall "activity" of studios has increased. In 2016, approximately 141 different studios launched animation series, and this number is projected to rise to approximately 182 by 2025. Although the number of works decreased slightly around 2020 due to the pandemic, the overall trend is an increase in the number of studios participating in production each year. **A large number of new studios are entering the market:** For example, in 2017, approximately 55 studios were "new faces" appearing on the production list for the first time that year, and since then, about 30-40 new companies have joined the production ranks each year. During our observation period (2016–2025), the dataset contains a total of **473** different production companies. This indicates that in addition to established companies, new studios are constantly being established and participating in animation production, supporting the rapidly growing content supply. This reflects both a strong market demand for content and the relatively low barriers to entry in the industry, allowing many small teams to receive outsourcing or collaborative work, thus extending the supply chain.
        """
    )    
    st.plotly_chart(fig_trend, use_container_width=True)
except FileNotFoundError as e:
    st.error(f"❌ 年度趋势数据文件未找到: {file_path}")
except ValueError as e:
    st.error(f"数据格式错误：{e}")
except Exception as e:
    st.error(f"读取年度趋势数据时出错: {e}")
