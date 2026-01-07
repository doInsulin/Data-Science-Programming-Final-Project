import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_echarts import st_echarts
from pyecharts import options as opts
from pyecharts.charts import Pie, Bar, Boxplot
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


# ---------------- 数据预处理工具 ----------------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
                    .str.lower()
                    .str.replace(" ", "_")
                    .str.replace("(", "")
                    .str.replace(")", "")
                    .str.replace("-", "_")
    )
    return df


def clean_text(x):
    if pd.isna(x):
        return x
    x = str(x)
    return (
        x.replace("\n", " ")
            .replace("<i>", "")
            .replace("</i>", "")
            .replace("<br>", " ")
            .strip()
    )


def parse_genres(x):
    if pd.isna(x):
        return []
    return [g.strip() for g in str(x).split(",") if g.strip()]


def preprocess_anime_df(df: pd.DataFrame, write_cleaned_path: str = None) -> pd.DataFrame:
    """
    对输入 DataFrame 执行统一列名、文本清洗、数值与日期字段标准化、genres 解析、以及一些派生字段计算。

    :param df: 原始 DataFrame
    :param write_cleaned_path: 如果给出，则把清洗后的 DataFrame 写为 CSV（可选）
    :return: 清洗并派生字段后的 DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df 必须为 pandas.DataFrame")

    df_hist = normalize_columns(df)

    # 文本字段清理
    for col in ["title_romaji", "title_english", "title_native", "description"]:
        if col in df_hist.columns:
            df_hist[col] = df_hist[col].apply(clean_text)

    # 数值字段处理
    num_cols = ["id", "idmal", "episodes", "duration", "averagescore",
                "meanscore", "favourites", "popularity"]
    for col in num_cols:
        if col in df_hist.columns:
            df_hist[col] = pd.to_numeric(df_hist[col], errors="coerce")

    # 日期字段格式标准化
    for col in ["startdate", "enddate"]:
        if col in df_hist.columns:
            df_hist[col] = pd.to_datetime(df_hist[col], errors="coerce")

    # Genres 解析
    if "genres" in df_hist.columns:
        df_hist["genres"] = df_hist["genres"].apply(parse_genres)

    # 是否续作
    if "title_romaji" in df_hist.columns:
        df_hist["is_sequel"] = df_hist["title_romaji"].str.contains(
            "Season|2nd|3rd|II|III|IV|V|VI",
            case=False, na=False
        )
    else:
        df_hist["is_sequel"] = False

    # Genre 数量
    if "genres" in df_hist.columns:
        df_hist["genre_count"] = df_hist["genres"].apply(len)
    else:
        df_hist["genre_count"] = 0

    # 内容量（episodes * duration）
    if "episodes" in df_hist.columns and "duration" in df_hist.columns:
        df_hist["total_duration"] = df_hist["episodes"] * df_hist["duration"]

    # 上映年份
    if "startdate" in df_hist.columns:
        df_hist["start_year"] = df_hist["startdate"].dt.year

    # 制作公司强弱（大小写不敏感匹配）
    big_studios = ["MAPPA", "ufotable", "Bones", "CloverWorks", "A-1 Pictures",
                    "Kyoto Animation", "WIT Studio", "MADHOUSE"]
    big_upper = [s.upper() for s in big_studios]
    if "mainstudio" in df_hist.columns:
        df_hist["is_big_studio"] = df_hist["mainstudio"].fillna("").astype(str).str.upper().isin(big_upper)
    else:
        df_hist["is_big_studio"] = False

    if write_cleaned_path:
        try:
            df_hist.to_csv(write_cleaned_path, index=False)
        except Exception:
            # 不阻塞主流程，仅记录到 Streamlit（如果在页面中调用）
            try:
                st.warning(f"无法写出清洗文件到 {write_cleaned_path}")
            except Exception:
                pass

    return df_hist

# ---------------- 预处理工具结束 ----------------
def plot_studio_capacity_pie(anime_df, top_n: int = 10):
    """
    返回一个 Plotly 饼图（Top N 工作室 vs Other）及 Top N 的计数 Series。

    :param anime_df: DataFrame，包含工作室字段（支持列名 `mainStudio` 或 `mainstudio`，不区分大小写）
    :param top_n: int，计算 Top N 工作室
    :return: (fig, top_series)  fig 为 plotly.graph_objects.Figure，top_series 为 pandas.Series
    """
    if not isinstance(anime_df, pd.DataFrame):
        raise TypeError("anime_df 必须是 pandas.DataFrame")

    # 先预处理数据，确保列名/字段统一
    df = preprocess_anime_df(anime_df)

    df["mainstudio"] = df["mainstudio"].fillna("Unknown")

    df = df.assign(
        mainstudio=df["mainstudio"].str.split(",")
    ).explode("mainstudio")

    df["mainstudio"] = df["mainstudio"].str.strip()
    df = df[df["mainstudio"].str.lower() != "unknown"]

    studio_counts = df["mainstudio"].value_counts()

    # 使用固定的 Top10 列表（按用户要求）
    fixed_top10 = [
        "J.C.STAFF",
        "Toei Animation",
        "TMS Entertainment",
        "OLM",
        "A-1 Pictures",
        "Sunrise",
        "Studio DEEN",
        "Production I.G",
        "LIDENFILMS",
        "MAPPA",
    ]

    # 归一化函数：只保留字母数字并小写，便于匹配不同写法
    def _norm(name: str) -> str:
        if not isinstance(name, str):
            return ""
        return "".join(ch.lower() for ch in name if ch.isalnum())

    fixed_norm = {_norm(s) for s in fixed_top10}
    # 按归一化后判断是否属于固定 top10
    df["studio_group"] = df["mainstudio"].apply(lambda x: "Top 10 Studios" if _norm(x) in fixed_norm else "Other Studios")

    group_counts = df["studio_group"].value_counts()    

    labels = group_counts.index.tolist()
    values = group_counts.values.tolist()

    fig = go.Figure(
        data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            pull=[0.06] * len(labels),
            textinfo="percent+label",
            hoverinfo="label+value+percent",
            insidetextorientation="radial",
            marker=dict(line=dict(color="black", width=2))
        )]
    )

    fig.update_layout(
        title=f"Top{top_n} Studio vs Other",
        template="plotly_white",
        paper_bgcolor="rgba(245,245,245,1)",
        plot_bgcolor="rgba(245,245,245,1)",
        clickmode="event+select",
        showlegend=True
    )

    # 为了返回固定 Top10 的计数（按给定顺序），构造按 fixed_top10 的统计结果
    counts_map = { _norm(s): 0 for s in fixed_top10 }
    for name, cnt in studio_counts.items():
        n = _norm(name)
        if n in counts_map:
            counts_map[n] += int(cnt)

    top_counts_list = [counts_map[_norm(s)] for s in fixed_top10]
    top_series = pd.Series(data=top_counts_list, index=fixed_top10)

    return fig, top_series


def plot_top10_studio_source_composition(anime_df, top_n: int = 10):
    """
    绘制 Top N 工作室按 source 的构成（水平堆叠条形图），返回 plotly Figure 与按 studio/source 聚合的表格。

    :param anime_df: DataFrame，包含工作室和 source 字段（支持大小写变体）
    :param top_n: int，选择 Top N 工作室
    :return: (fig, studio_source_counts_df)  fig 为 plotly Figure，studio_source_counts_df 为聚合 DataFrame
    """
    if not isinstance(anime_df, pd.DataFrame):
        raise TypeError("anime_df 必须是 pandas.DataFrame")

    # 先预处理数据
    df = preprocess_anime_df(anime_df)

    # 查找主制作方列与 source 列（不区分大小写）
    col_map = {c.lower(): c for c in df.columns}
    main_col = col_map.get("mainstudio")
    source_col = col_map.get("source")
    if main_col is None:
        raise ValueError("数据中未找到工作室列（期望列名 mainStudio 或 mainstudio）")
    if source_col is None:
        raise ValueError("数据中未找到 source 列（期望列名 source）")

    df[main_col] = df[main_col].fillna("Unknown")
    df[source_col] = df[source_col].fillna("Unknown")

    # 合并 Unknown / Other（统一为 'Other'）
    df[source_col] = df[source_col].astype(str).str.strip().str.lower()
    df[source_col] = df[source_col].replace({"unknown": "Other", "other": "Other"})

    # 拆分多个 studio
    df_exploded = df.assign(**{main_col: df[main_col].str.split(",")}).explode(main_col)
    df_exploded[main_col] = df_exploded[main_col].str.strip()
    df_exploded = df_exploded[df_exploded[main_col].str.lower() != "unknown"]

    # 使用固定的 Top10 公司列表（只统计这十个公司）
    fixed_top10 = [
        "J.C.STAFF",
        "Toei Animation",
        "TMS Entertainment",
        "OLM",
        "A-1 Pictures",
        "Sunrise",
        "Studio DEEN",
        "Production I.G",
        "LIDENFILMS",
        "MAPPA",
    ]

    # 归一化函数：保留字母数字并小写，便于匹配不同写法
    def _norm(name: str) -> str:
        if not isinstance(name, str):
            return ""
        return "".join(ch.lower() for ch in name if ch.isalnum())

    fixed_norm = {_norm(s) for s in fixed_top10}

    # 为匹配便利，添加一列 studio_norm
    df_exploded = df_exploded.copy()
    df_exploded["studio_norm"] = df_exploded[main_col].apply(lambda x: _norm(x))

    # 只保留固定 Top10 的记录
    df_topN = df_exploded[df_exploded["studio_norm"].isin(fixed_norm)].copy()

    # 把 studio 列映射为固定显示名（按 fixed_top10 中的规范名称）
    norm_to_name = { _norm(s): s for s in fixed_top10 }
    df_topN[main_col] = df_topN["studio_norm"].map(norm_to_name)

    studio_source_counts = (
        df_topN.groupby([main_col, source_col])
        .size()
        .reset_index(name="count")
    )

    # 保持固定顺序（只包含数据中存在的那些），用于 category_orders
    studio_order = [s for s in fixed_top10 if s in df_topN[main_col].unique()]

    fig = px.bar(
        studio_source_counts,
        x="count",
        y=main_col,
        color=source_col,
        orientation="h",
        category_orders={main_col: studio_order},
        title=f"Top {top_n} Anime Studios – Source Composition"
    )
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend_title_text="Source Type",
        margin=dict(l=120)
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Source: %{fullData.name}<br>Titles: %{x}<extra></extra>"
    )

    return fig, studio_source_counts


def plot_trend_anime_vs_studios(file_path: str = None, df: pd.DataFrame = None,
                                 start_year: int = 2016, end_year: int = 2025):
    """
    绘制年度趋势：每年动漫作品数量 与 每年活跃工作室数量（双轴折线图），返回 plotly Figure 与趋势数据 DataFrame。

    参数说明：
    - file_path: 可选，CSV 文件路径（当 df 未提供时读取）
    - df: 可选，已加载的 DataFrame（优先使用 df）
    - start_year, end_year: 年份区间

    返回：(fig, trend_df)
    """
    # 读取或复制数据
    if df is None:
        if file_path is None:
            raise ValueError("必须提供 file_path 或 df 中的一个")
        # 让 pandas 抛出 FileNotFoundError 或其它读取异常，由调用方捕获
        df_trend = pd.read_csv(file_path)
    else:
        df_trend = df.copy()

    # 使用已有的预处理函数以规范列名/日期/数值
    df_trend = preprocess_anime_df(df_trend)

    # 确保存在 start_year（preprocess 会在有 startdate 时填充 start_year）
    if "start_year" not in df_trend.columns:
        # 尝试从任意可能的列提取年份（兼容老字段名）
        if "startdate" in df_trend.columns:
            df_trend["start_year"] = df_trend["startdate"].dt.year
        else:
            df_trend["start_year"] = pd.NA

    # 过滤时间区间
    df_trend = df_trend[df_trend["start_year"].between(start_year, end_year)]

    # 规范并拆分 mainstudio
    if "mainstudio" not in df_trend.columns:
        raise ValueError("数据中缺少 'mainstudio' 列，无法计算工作室统计")

    df_trend["mainstudio"] = df_trend["mainstudio"].fillna("Unknown")
    df_trend = df_trend.assign(mainstudio=df_trend["mainstudio"].str.split(",")).explode("mainstudio")
    df_trend["mainstudio"] = df_trend["mainstudio"].astype(str).str.strip()
    df_trend = df_trend[df_trend["mainstudio"].str.lower() != "unknown"]

    # 计算每年动漫作品数（按 id 去重）和每年活跃工作室数（去重 mainstudio）
    anime_per_year = (
        df_trend.groupby("start_year")["id"].nunique().reset_index(name="anime_count")
    )
    studio_per_year = (
        df_trend.groupby("start_year")["mainstudio"].nunique().reset_index(name="studio_count")
    )

    trend = pd.merge(anime_per_year, studio_per_year, on="start_year", how="outer").fillna(0)
    trend = trend.sort_values("start_year")

    # 绘图（双轴折线）
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["start_year"],
        y=trend["anime_count"],
        name="Anime Output",
        mode="lines+markers",
        yaxis="y1"
    ))
    fig.add_trace(go.Scatter(
        x=trend["start_year"],
        y=trend["studio_count"],
        name="Active Studios",
        mode="lines+markers",
        yaxis="y2"
    ))

    fig.update_layout(
        title=f"Anime Industry Scale Trend ({start_year}–{end_year})",
        xaxis=dict(title="Year"),
        yaxis=dict(title="Anime Series Count"),
        yaxis2=dict(title="Active Studios Count", overlaying="y", side="right"),
        template="plotly_white",
        legend=dict(x=0.01, y=0.99)
    )

    return fig, trend


def plot_isekai_trends(df: pd.DataFrame = None, file_path: str = None,
                       start_year: int = 2016, end_year: int = 2025):
    """
    绘制 Isekai 与 Top10 标签的年度趋势对比图（主图 + 右下角子图）。

    参数：
    - df: 已加载的 DataFrame（优先使用）
    - file_path: CSV 文件路径（当 df 未提供时读取）
    - start_year, end_year: 年份区间

    返回：(fig, year_tag_counts, isekai_count)
    """
    from collections import Counter
    import numpy as np

    # 读取或复制数据
    if df is None:
        if file_path is None:
            raise ValueError("必须提供 file_path 或 df 中的一个")
        df = pd.read_csv(file_path)
    else:
        df = df.copy()

    # 预处理：确保存在 start_year 和 tag_list
    df = preprocess_anime_df(df)

    # 处理 tags 列表
    df['tag_list'] = df['tags'].fillna('').apply(lambda x: x.split('|') if x else [])

    # 生成 is_isekai 标记
    df['is_isekai'] = df['tag_list'].apply(lambda x: 1 if 'Isekai' in x else 0)

    # 排除关键词
    exclude_keywords = ["Male", "Female", "Cast"]
    def is_excluded(tag):
        return any(keyword in tag for keyword in exclude_keywords)

    # 计算 Top10 标签
    all_tags = Counter(
        tag for tags in df['tag_list'] for tag in tags
        if tag and not is_excluded(tag)
    )
    top10 = [t for t, _ in all_tags.most_common(10)]
    if "Isekai" not in top10:
        top10.append("Isekai")

    # 准备主图数据
    df_filtered = df.copy()
    df_filtered['tag_list'] = df_filtered['tag_list'].apply(
        lambda tags: [t for t in tags if not is_excluded(t)]
    )
    year_tag_counts = (
        df_filtered.explode('tag_list')
                   .groupby(['start_year', 'tag_list'])
                   .size()
                   .unstack(fill_value=0)
    )

    # 过滤到指定年份区间
    year_tag_counts = year_tag_counts.loc[start_year:end_year]

    # 准备子图数据
    isekai_count = df.groupby('start_year')['is_isekai'].sum().reset_index()
    isekai_count = isekai_count[
        (isekai_count['start_year'] >= start_year) &
        (isekai_count['start_year'] <= end_year)
    ]

    # 创建图表
    fig = go.Figure()

    # 记录 2025 年 Isekai 值（用于箭头指向）
    isekai_2025_val = 0

    # 绘制主图（左侧）
    for tag in top10:
        if tag in year_tag_counts.columns:
            if tag == "Isekai":
                try:
                    isekai_2025_val = year_tag_counts.loc[end_year, tag]
                except KeyError:
                    isekai_2025_val = 0

                fig.add_trace(go.Scatter(
                    x=year_tag_counts.index,
                    y=year_tag_counts[tag],
                    mode='lines+markers',
                    name=tag,
                    line=dict(width=5, color='red'),
                    marker=dict(size=8),
                    zorder=10
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=year_tag_counts.index,
                    y=year_tag_counts[tag],
                    mode='lines+markers',
                    name=tag,
                    opacity=0.5,
                    line=dict(width=2)
                ))

    # 绘制子图（右下角）
    fig.add_trace(go.Scatter(
        x=isekai_count['start_year'],
        y=isekai_count['is_isekai'],
        mode='lines+markers',
        name='Isekai Volume',
        xaxis='x2',
        yaxis='y2',
        line=dict(color='blue', width=2),
        marker=dict(size=5),
        showlegend=False
    ))

    # 布局设置
    fig.update_layout(
        title=f"Top 10 Tags vs Isekai Trends ({start_year}–{end_year})",
        width=1300,
        height=650,
        template="plotly_white",

        # 主图坐标轴
        xaxis=dict(domain=[0, 0.72], title="Year"),
        yaxis=dict(title="Tag Frequency"),

        # 子图坐标轴
        xaxis2=dict(
            domain=[0.78, 0.98],
            anchor='y2', title="Year", dtick=2
        ),
        yaxis2=dict(
            domain=[0.1, 0.35],
            anchor='x2', title="Total Count"
        ),

        # 图例设置
        legend=dict(
            x=0.78,
            y=1.0,
            xanchor="left",
            yanchor="top",
            orientation="v",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="LightGrey",
            borderwidth=1
        )
    )

    # 添加注释和箭头
    fig.add_annotation(
        text="Isekai Anime Count",
        xref="paper", yref="paper",
        x=0.88, y=0.38,
        showarrow=False,
        font=dict(size=12, color="blue", weight="bold"),
        xanchor="center"
    )

    # 箭头：指向 2025 年 Isekai 数据点
    if isekai_2025_val > 0:
        fig.add_annotation(
            x=end_year, y=isekai_2025_val,
            xref="x", yref="y",
            ax=90,
            ay=10,
            axref="pixel", ayref="pixel",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2,
            arrowcolor="black", opacity=0.8, standoff=4
        )

    return fig, year_tag_counts, isekai_count


def plot_isekai_wordcloud(df: pd.DataFrame = None, file_path: str = None,
                          width: int = 1200, height: int = 800):
    """
    生成 Isekai 动漫标签的词云（基于 TF-IDF 向量化）。

    参数：
    - df: 已加载的 DataFrame（优先使用）
    - file_path: CSV 文件路径（当 df 未提供时读取）
    - width, height: 词云宽高

    返回：(fig, tfidf_rank)  fig 为 matplotlib figure，tfidf_rank 为 TF-IDF 得分 DataFrame
    """
    import re
    from sklearn.feature_extraction.text import TfidfVectorizer
    from wordcloud import WordCloud

    # 读取或复制数据
    if df is None:
        if file_path is None:
            raise ValueError("必须提供 file_path 或 df 中的一个")
        df = pd.read_csv(file_path)
    else:
        df = df.copy()

    # 筛选 Isekai 动漫
    isekai_df = df[df["tags"].str.contains("Isekai", case=False, na=False)]

    if isekai_df.empty:
        raise ValueError("数据中未找到包含 Isekai 标签的作品")

    # 清洗标签
    def clean_tags(tag_str):
        if pd.isna(tag_str):
            return ""
        tag_str = re.sub(r"[\[\]'\" ]", "", tag_str)
        tag_str = tag_str.replace("|", " ")
        return tag_str.lower()

    isekai_df = isekai_df.copy()
    isekai_df["clean_tags"] = isekai_df["tags"].apply(clean_tags)

    # TF-IDF 向量化
    vectorizer = TfidfVectorizer(max_features=500, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(isekai_df["clean_tags"])
    feature_names = vectorizer.get_feature_names_out()

    # 计算 TF-IDF 得分
    tfidf_scores = np.asarray(tfidf_matrix.mean(axis=0)).ravel()

    tfidf_rank = pd.DataFrame({
        "word": feature_names,
        "score": tfidf_scores
    }).sort_values(by="score", ascending=False)

    # 生成词云
    wordcloud = WordCloud(
        width=width,
        height=height,
        background_color="white"
    ).generate(" ".join(isekai_df["clean_tags"]))

    # 创建 matplotlib figure
    fig = plt.figure(figsize=(width / 100, height / 100))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)

    return fig, tfidf_rank

