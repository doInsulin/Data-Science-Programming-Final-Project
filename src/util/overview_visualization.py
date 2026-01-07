import streamlit as st
from streamlit_echarts import st_echarts
import json
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

def plot_anime_visualizations(anime_df):
    """
    Plot anime data visualizations
    :param anime_df: Dataset obtained from data_manager
    """
    # 数据处理：提取并去除“format”列中的缺失值
    visual_data = anime_df[["format"]].dropna()

    # 统计不同动漫类型的数量并转为原生数据类型
    type_counts = visual_data["format"].value_counts()
    type_list = type_counts.index.tolist()  # 获取动漫类型的列表
    count_list = type_counts.values.tolist()  # 获取对应的数量列表

    # ========== 1. 饼图：不同动漫类型的分布 ==========

    # 该图显示了不同动漫类型的占比情况
    # 数据处理：通过value_counts统计类型频率并转化为ECharts所需的格式
    pie_data = [{"name": t, "value": v} for t, v in type_counts.items()]
    pie_options = {
        "tooltip": {"trigger": "item"},  # 鼠标悬停时显示详细信息
        "series": [
            {
                "name": "Anime Type",
                "type": "pie",
                "radius": ["40%", "70%"],  # 设置为环形饼图（更美观）
                "data": pie_data,
                "label": {"show": True, "formatter": "{b}: {c} ({d}%)"},  # 显示标签和百分比
            }
        ],
        "color": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],  # 配色方案
    }
    st_echarts(options=pie_options, height="400px", key='distribution of different types by pie')

    # ========== 2. 条形图：不同动漫类型的比较 ==========

    # 该图展示了不同类型动漫的数量对比
    # 数据处理：使用value_counts统计数量，生成适合条形图的格式
    bar_options = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "xAxis": {
            "type": "category",
            "data": type_list,
            "axisLabel": {
                "interval": 0  # 强制显示所有标签
            }
        },
        "yAxis": {"type": "value", "name": "Count"},
        "series": [{
            "name": "Anime Count",
            "type": "bar",
            "data": count_list,
            "color": ["#4ECDC4"],
            "label": {
                "show": True,  # 显示条形图上的数值
                "position": "top",  # 显示在条形图上方
                "formatter": "{c}",  # 显示数值
                "fontSize": 12,  # 数值字体大小
                "color": "#333"  # 数值字体颜色
            }
        }],
        "grid": {"left": "3%", "right": "3%", "bottom": "20%", "containLabel": True}
    }
    st_echarts(options=bar_options, height="400px", key='distribution of different types by bar')


def plot_genre_analysis(anime_df):
    """Analyze average popularity and average score for each Genre (vertical chart + Top10 + lowercase column adaptation)"""
    st.subheader("Analysis of Popularity & Score by Anime Genre (Top 10)")

    # 数据预处理：去除缺失值并分割“genres”列，生成每个类型对应的行
    df = anime_df[["genres", "popularity", "averageScore"]].dropna()
    df["genres"] = df["genres"].str.split("|")
    df_exploded = df.explode("genres").reset_index(drop=True)
    df_exploded = df_exploded[df_exploded["genres"] != ""].reset_index(drop=True)

    if len(df_exploded) == 0:
        st.warning("No valid Genre data!")
        return

    # 按照平均受欢迎度排序并取前10个动漫类型
    genre_stats = df_exploded.groupby("genres").agg({
        "popularity": "mean",  # 计算每个类型的平均受欢迎度
        "averageScore": "mean"  # 计算每个类型的平均评分
    }).reset_index()
    genre_stats = genre_stats.sort_values("popularity", ascending=False).head(10)

    # 数据转换：将数据转换为适合绘图的格式
    genre_list = genre_stats["genres"].tolist()
    avg_popularity = genre_stats["popularity"].astype(int).tolist()
    avg_score = genre_stats["averageScore"].round(2).tolist()

    # ========== 3. 双轴垂直图配置（解决X轴文本遮挡） ==========

    options = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"}
        },
        "legend": {
            "data": ["Average Popularity", "Average Score"],
            "top": 0
        },
        "grid": {
            "left": "3%",
            "right": "10%",
            "bottom": "40%",  # 调整底部空间以避免X轴文本重叠
            "containLabel": True
        },
        "xAxis": [
            {
                "type": "category",
                "data": genre_list,
                "axisLabel": {
                    "interval": 0,  # 强制显示所有标签
                    "rotate": -30,  # 旋转文本，避免重叠
                    "align": "center",  # 文本居中对齐
                    "margin": 30,  # 增加文本与X轴的间距
                    "overflow": "break"  # 自动换行长文本
                }
            }
        ],
        "yAxis": [
            {
                "type": "value",
                "name": "Average Popularity",
                "min": 0,
                "axisLabel": {"formatter": "{value}"}
            },
            {
                "type": "value",
                "name": "Average Score",
                "min": 50,
                "max": 100,
                "axisLabel": {"formatter": "{value} pts"},
                "position": "right",
                "offset": 0
            }
        ],
        "series": [
            {
                "name": "Average Popularity",
                "type": "bar",
                "data": avg_popularity,
                "itemStyle": {"color": "#4ECDC4"},
                "label": {"show": True, "position": "top", "formatter": "{c}"}
            },
            {
                "name": "Average Score",
                "type": "line",
                "yAxisIndex": 1,
                "data": avg_score,
                "itemStyle": {"color": "#FF6B6B"},
                "symbol": "circle",
                "label": {"show": True, "position": "bottom", "formatter": "{c}"}
            }
        ]
    }
    st_echarts(options=options, height="600px", key='distribution of different types')

    # ========== 4. Top 10 Genre Details Table ==========

    st.subheader("Top 10 Popular Genres Details")
    st.dataframe(
        genre_stats.rename(columns={
            "genres": "Anime Genre",
            "popularity": "Average Popularity",
            "averageScore": "Average Score"
        }),
        use_container_width=True
    )

# 获取流媒体平台信息的清洗函数，1.首先清理掉无效字符串例如空值，然后通过字段名site解析JSON提取平台名称.2.依次统计前10名工作室与流媒体平台的合作次数，生成热力图

def clean_external_links(external_links_json):
    """Clean and extract valid streaming platform information"""
    if isinstance(external_links_json, str):
        try:
            clean_json = external_links_json.strip()
            clean_json = clean_json.replace('NaN', 'null')  
            links = json.loads(clean_json)  # Convert to JSON
            platforms = [link['site'] for link in links if 'site' in link]
            return platforms
        except (json.JSONDecodeError, TypeError):
            return []  # Return an empty list if unable to parse
    return []  # Return an empty list if not a valid string

def plot_studio_platform_partnerships(anime_df):
    """Display top 10 studios and their streaming platform partnerships"""
    st.subheader("Top 10 Studios and Streaming Platform Partnerships")

    # Get top 10 studios by anime production count
    top_10_studios = anime_df['mainStudio'].value_counts().head(10).index.tolist()
    
    # Create data structure to store partnerships
    studio_platform_data = []

    # Count collaborations between studios and streaming platforms
    for studio in top_10_studios:
        studio_data = anime_df[anime_df['mainStudio'] == studio]
        
        # Extract streaming platforms for each anime (one anime can have multiple platforms)
        for _, row in studio_data.iterrows():
            platforms = clean_external_links(row['externalLinks_json'])
            for platform in platforms:
                studio_platform_data.append((studio, platform))

    # Create DataFrame for platform counts
    studio_platform_counts = pd.DataFrame(studio_platform_data, columns=['studio', 'platform'])
    platform_counts = studio_platform_counts.groupby(['studio', 'platform']).size().reset_index(name='count')

    # Create pivot table to use for heatmap
    heatmap_data = platform_counts.pivot(index="studio", columns="platform", values="count").fillna(0)

    # Plot interactive heatmap using Plotly
    fig = px.imshow(
        heatmap_data,
        labels={'x': 'Platform', 'y': 'Studio', 'color': 'Partnership Count'},
        color_continuous_scale='YlGnBu',
        title="Heatmap of Studio and Streaming Platform Partnerships",
        aspect="auto"
    )

    fig.update_layout(
        xaxis={'side': 'top', 'tickangle': 45},
        yaxis={'showgrid': False},
        title_x=0.5,
        title_y=0.95,
        width=1000,  # Adjust width and height for better fit
        height=600
    )

    # Display the interactive Plotly heatmap
    st.plotly_chart(fig)