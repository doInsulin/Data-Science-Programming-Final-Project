import pandas as pd
from streamlit_echarts import st_echarts
import streamlit as st

import pandas as pd
from streamlit_echarts import st_echarts
import streamlit as st




def plot_source_year_analysis(df):
    """
    Source vs Year Trend Line Chart (2016–2025)
    """

    st.info(
    """
    Six main sources of anime production have been identified:
    1. **LIGHT NOVEL**: Adapted from a series of illustrated prose novels.  
    2. **MANGA**: Adapted from Japanese comic books or graphic novels.  
    3. **ORIGINAL**: Created specifically for anime without a prior published source.  
    4. **OTHER**: Derived from sources such as live-action films, real-world events, or non-Japanese media.  
    5. **VIDEO GAME**: Adapted from console, PC, or mobile games.  
    6. **VISUAL NOVEL**: Adapted from interactive, narrative-driven video games with minimal gameplay.
    """
)
    st.subheader("1. Anime Production Trend by Source (2016–2025)")

    # ---------- 数据过滤 ----------
    df_filtered = df[
        (df["seasonYear"] >= 2016) &
        (df["seasonYear"] <= 2025) &
        (df["source"].notna())
    ].copy()

    # ---------- 分组统计 ----------
    source_year = (
        df_filtered
        .groupby(["seasonYear", "source"])
        .size()
        .reset_index(name="count")
    )

    # 透视为 matrix，便于画图
    pivot = (
        source_year
        .pivot(index="seasonYear", columns="source", values="count")
        .fillna(0)
    )

    # Echarts 数据准备
    years = pivot.index.tolist()
    series = []

    for source in pivot.columns:
        series.append({
            "name": source,
            "type": "line",
            "data": pivot[source].tolist(),
            "symbol": "circle",
        })

    # ---------- Echarts 配置 ----------
    options = {
        "tooltip": {"trigger": "axis"},
        "legend": {"data": list(pivot.columns)},
        "xAxis": {
            "type": "category",
            "data": years,
            "axisLabel": {"rotate": 0}
        },
        "yAxis": {"type": "value"},
        "series": series,
        "grid": {"left": 60, "right": 20, "bottom": 50, "top": 50}
    }

    # ---------- 渲染 ----------
    st_echarts(options=options, height="500px")

    st.markdown(
    """
    <div style="
        background-color: #E9F7EC;
        padding: 15px 20px;
        border-radius: 10px;
        color: #2E7D32;
        font-size: 16px;
        line-height: 1.6;
    ">
    <b>Conclusion:</b> Over the past decade, the anime industry has consistently shifted towards adaptation-driven production, primarily relying on low-risk, established IPs from manga and light novels. This strategic focus within the production committee system has resulted in a stable output for adaptations and a corresponding decline in original works, reflecting a broader industry preference for commercial predictability over creative experimentation.
    </div>
    """,
    unsafe_allow_html=True
)




from streamlit_echarts import st_echarts
import pandas as pd
import numpy as np

from streamlit_echarts import st_echarts


from streamlit_echarts import st_echarts
import numpy as np

def plot_interactive_heatmap(residuals):

    # categories order
    sources = residuals.index.tolist()
    genres = residuals.columns.tolist()

    # 1) reverse y-axis order (so top->bottom reversed)
    sources_reversed = list(reversed(sources))

    # 2) Build data as [genre, source, value] (use category names, not indices)
    data = []
    for src in sources_reversed:
        for gen in genres:
            val = float(residuals.loc[src, gen])
            # ECharts accepts [xCategory, yCategory, value]
            data.append([gen, src, val])

    # 3) ECharts options
    options = {

        "grid": {
            # leave more left margin so y labels fully visible; bottom for x labels
            "left": "1%",   # increase if labels still clipped
            "right": "5%",
            "top": "8%",
            "bottom": "22%", 
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "data": genres,
            "axisLabel": {
                "rotate": 45,
                "interval": 0,
                "formatter": {"type": "function", "value": "function (value) { return value.length>12 ? value.slice(0,12)+'...' : value; }"}
            },
            "splitArea": {"show": False}
        },
        "yAxis": {
            "type": "category",
            "data": sources_reversed,
            "axisLabel": {
                # 不旋转 y 标签，增加字体大小/对齐
                "fontSize": 12,
                "interval": 0,
                "align": "right"
            },
            "inverse": False,  # 已用 sources_reversed 顺序，不需要 inverse
            "splitArea": {"show": False}
        },
        "visualMap": {
            # 色阶范围自动取 residuals 的 min/max
            "min": float(np.nanmin(residuals.values)),
            "max": float(np.nanmax(residuals.values)),
            "calculable": True,
            "orient": "horizontal",
            "left": "center",
            "bottom": "6%",
            "inRange": {
                # coolwarm-like blue->white->red
                "color": ["#3b4cc0", "#ffffff", "#b40426"]
            }
        },
        "series": [{
            "name": "Residuals",
            "type": "heatmap",
            "data": data,
            "label": {"show": False},
            "emphasis": {"itemStyle": {"shadowBlur": 10}}
        }]
    }

    # render
    st_echarts(options=options, height="650px")



# ========== 第二部分：Source × Genre 卡方检验 + 热力图 ==========
def plot_source_genre_analysis(df):
    import streamlit as st
    import pandas as pd
    import numpy as np
    import scipy.stats as stats
    import seaborn as sns
    import matplotlib.pyplot as plt
    import ast

    # 标题（样式与分析1一致）
    st.subheader("2. Source × Genre Statistical Relationship Analysis")

    # ------------------------------------
    # 数据预处理
    # ------------------------------------
    major_sources = ["MANGA", "LIGHT_NOVEL", "ORIGINAL", "VIDEO_GAME", "VISUAL_NOVEL"]
    df = df[df["source"].isin(major_sources)]

    def parse_genres(x):
        try:
            lst = ast.literal_eval(x)
            if isinstance(lst, list) and len(lst) > 0:
                return lst[0].split("|")
        except:
            return []
        return []


    df["genres"] = df["genres"].fillna("").astype(str)
    df["genres"] = df["genres"].apply(lambda x: [g.strip() for g in x.split("|") if g.strip()])
    df = df.explode("genres")
    df = df[df["genres"].notna() & (df["genres"] != "")]


    # ------------------------------------
    # 构造 Source × Genre 表
    # ------------------------------------
    table = pd.crosstab(df["source"], df["genres"])

    # ------------------------------------
    # 卡方检验
    # ------------------------------------
    chi2, p, dof, expected = stats.chi2_contingency(table)
    n = table.sum().sum()
    cramers_v = np.sqrt(chi2 / (n * (min(table.shape) - 1)))

    # ---------- 文字说明（蓝色提示框） ----------
    st.info(
        "We conducted a Chi-square independence test to examine whether the distribution of genres "
        "is independent from the anime source type. This test helps determine whether specific genres "
        "tend to appear more frequently in certain source categories than expected by chance."
    )

    # 卡方检验结果表
    st.markdown("### 2.1 Chi-square Test Results")
    st.code(
f"""Chi-square: {chi2}
p-value: {p}
Degrees of freedom: {dof}
Cramér's V: {cramers_v}
""")

    # ---------- 结论说明 ----------

    
    st.markdown(
    """
    <div style="
        background-color: #E9F7EC;
        padding: 15px 20px;
        border-radius: 10px;
        color: #2E7D32;
        font-size: 16px;
        line-height: 1.6;
    ">
    <b>Conclusion:</b> The extremely small p-value (≈ 1e-281) indicates a highly significant dependence between anime source and genre. While the association strength (Cramér's V ≈ 0.19) is modest, it confirms that different source types exhibit distinct genre preferences rather than following a uniform distribution.
    </div>
    """,
    unsafe_allow_html=True)

    # ------------------------------------
    # 热力图（标准化残差）
    # ------------------------------------
    st.markdown("### 2.2 Standardized Residuals Heatmap")

    st.info(
        "Red cells indicate **over-representation**, while blue cells indicate **under-representation**."
    )

    residuals = (table - expected) / np.sqrt(expected)

    fig, ax = plt.subplots(figsize=(16, 8))
    plot_interactive_heatmap(residuals)

    # ---------- 热力图解读 ----------
    st.markdown(
    """
    <div style="
        background-color: #E9F7EC;
        padding: 15px 20px;
        border-radius: 10px;
        color: #2E7D32;
        font-size: 16px;
        line-height: 1.6;
    ">
    <b>Conclusion:</b>The heatmap of standardized residuals highlights significant source–genre preferences:<br><br>
<b>Light Novels (LIGHT_NOVEL)</b> show strong positive residuals in <b>Fantasy</b> and <b>Adventure</b> genres, while negative residuals appear in <b>Mecha</b> or <b>Sports</b>, suggesting these genres are less common due to visual production constraints.<br><br>
<b>Manga (MANGA)</b> distributions are relatively balanced, with only <b>Comedy</b> and <b>Slice-of-life</b> showing notable deviations. Residuals in most genres are small, reflecting broader thematic diversity.<br><br>
<b>Original Works (ORIGINAL)</b> favor genres like <b>Sci-Fi</b> for imaginative storytelling, <b>Mecha</b> for dynamic mechanical visuals, and <b>Music</b> for integrated musical elements that are fully realizable in original projects.<br><br>
<b>Video Games (VIDEO_GAME)</b> favor genres such as <b>Fantasy</b>, <b>Action</b>, and <b>Music</b>, which provide strong auditory and visual stimulation.<br><br>
<b>Visual Novels (VISUAL_NOVEL)</b> though fewer in number, show positive residuals for <b>Psychological</b> and <b>Romance</b> genres, and negative residuals for <b>Action</b> or <b>Sports</b>, reflecting a narrative-driven and emotionally focused content pattern.
    </div>
    """,
    unsafe_allow_html=True)

    

import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

def plot_source_score_analysis(df):
    """
    Score Distribution Analysis by Source
    Includes:
    - Boxplot
    - Violin plot
    """

    st.subheader("3. Score Distribution Analysis by Source")

    # ------------------------------
    # 数据过滤
    # ------------------------------
    major_sources = ["MANGA", "LIGHT_NOVEL", "ORIGINAL", "VIDEO_GAME", "VISUAL_NOVEL"]
    df = df[df["source"].isin(major_sources)]

    df = df[df["averageScore"].notna()].copy()
    df["averageScore"] = df["averageScore"].astype(float)

    # ============================
    # 箱线图
    # ============================
    st.markdown("### 📦 Score Distribution (Boxplot)")

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    sns.boxplot(
        data=df,
        x="source",
        y="averageScore",
        hue="source",
        palette="Set2",
        legend=False,
        ax=ax1
    )
    ax1.set_title("Score Distribution by Source (Boxplot)")
    ax1.set_xlabel("Source")
    ax1.set_ylabel("Average Score")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    st.pyplot(fig1)

    # ============================
    # 小提琴图
    # ============================
    st.markdown("### 🎻 Score Distribution (Violin Plot)")

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.violinplot(
        data=df,
        x="source",
        y="averageScore",
        palette="Set3",
        cut=0,
        ax=ax2
    )
    ax2.set_title("Score Distribution by Source (Violin Plot)")
    ax2.set_xlabel("Source")
    ax2.set_ylabel("Average Score")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    st.pyplot(fig2)

    # ============================
    # 文本结论（蓝色 info 卡片）
    # ============================
    st.markdown(
    """
    <div style="
        background-color: #E9F7EC;
        padding: 15px 20px;
        border-radius: 10px;
        color: #2E7D32;
        font-size: 16px;
        line-height: 1.6;
    ">
    <b>Conclusion:</b> Boxplots and violin plots show that <b>MANGA</b> and <b>LIGHT_NOVEL</b> adaptations have higher average ratings than <b>ORIGINAL</b> works, with relatively small differences between them. This suggests that production companies tend to select strong source material for adaptation. However, <b>MANGA</b> adaptations have many <b>lower outliers</b>, likely because manga plots and artwork usually come from the same creator, resulting in a consistent style and tone while leaving room for reader imagination. When adapted into anime by large production teams, discrepancies between plot and visuals can occur—sometimes called "radical adaptation" by fans—leading to more outliers compared to other sources. <b>ORIGINAL</b> works, produced by studios of varying levels, show a more uniform distribution of ratings. <b>VIDEO_GAME</b> and <b>VISUAL_NOVEL</b> adaptations, while fewer in number, generally cluster around moderate ratings, reflecting niche appeal and adaptation challenges.
    </div>
    """,
    unsafe_allow_html=True)


