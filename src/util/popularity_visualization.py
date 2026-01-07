import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from streamlit_echarts import st_echarts

# Configure font (no need for Chinese font now)
plt.rcParams['axes.unicode_minus'] = False

'''
Objective: 
To investigate the relationship between the format of anime (such as TV series, OVA, movies, etc.) and its popularity. By analyzing the high popularity rates and average popularity of different formats, determine which format is more likely to become popular.

Data Processing: 
1, This function does not handle missing values separately. Since the previous analysis revealed that there are no missing values in the "format" column, no processing is carried out.
2, Group by format, aggregate and calculate the sample size, the average high prevalence rate (the mean of is_high_pop) and the average prevalence for each group.
3, Sort the results in descending order based on the proportion of high prevalence, which is conducive to subsequent visual comparison.

Conclusion: 
TV format dominates with the highest high popularity ratio (41.2%) and the highest average popularity, far exceeding other formats. MOVIE format ranks second but with a significant gap (high popularity ratio ~20%). Formats like OVA, ONA, TV_SHORT, and SPECIAL have low high popularity ratios (all <15%), while MUSIC format has almost no high-popularity works—consistent with its niche focus on music content, which struggles to attract a broad audience.

Analyzing the reasons: 
Different formats correspond to distinct production models and audience expectations. TV format benefits from fixed weekly updates that build sustained audience engagement, broad accessibility via streaming/TV networks, and flexible storytelling length. MOVIE format relies on high production values but has limited exposure due to theatrical release constraints. Niche formats like OVA/ONA target dedicated fanbases with shorter or irregular releases, limiting mainstream reach. MUSIC format, focused on music performances (e.g., music videos, concert recordings), has an extremely narrow audience—appealing primarily to existing fans of specific artists rather than general anime viewers, resulting in minimal popularity.
'''
def format_popularity_analysis(df):
    # ========== Analysis 1: Impact of Anime Format on Popularity ==========
    st.subheader("1. Anime Format vs Popularity")
    # Statistics on "high popularity ratio" and "average popularity" for each format
    format_stats = df.groupby("format").agg({
        "is_high_pop": ["count", "mean"],  # count=total in format, mean=high popularity ratio (0-1)
        "popularity": "mean"  # average popularity for the format
    }).round(3)
    format_stats.columns = ["Total Count", "High Popularity Ratio", "Average Popularity"]
    format_stats = format_stats.sort_values("High Popularity Ratio", ascending=False)

    # Visualization: dual-axis chart (high popularity ratio + average popularity)
    format_list = format_stats.index.tolist()
    high_pop_ratio = (format_stats["High Popularity Ratio"] * 100).tolist()  # Convert to percentage
    avg_popularity = format_stats["Average Popularity"].astype(int).tolist()

    format_options = {
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["High Popularity Ratio(%)", "Average Popularity"]},
        "grid": {"bottom": "20%"},
        "xAxis": {"type": "category", "data": format_list, "axisLabel": {"rotate": -45}},
        "yAxis": [
            {"type": "value", "name": "High Popularity Ratio(%)", "max": 100},
            {"type": "value", "name": "Average Popularity", "position": "right"}
        ],
        "series": [
            {"name": "High Popularity Ratio(%)", "type": "bar", "data": high_pop_ratio, "color": "#FF6B6B"},
            {"name": "Average Popularity", "type": "line", "yAxisIndex": 1, "data": avg_popularity, "color": "#4ECDC4"}
        ]
    }
    st_echarts(options=format_options, height="400px")

    # Conclusion prompt
    st.success(
        f"Conclusion: TV format dominates with the highest high popularity ratio (41.2%) and the highest average popularity, far exceeding other formats. MOVIE format ranks second but with a significant gap (high popularity ratio ~20%). Formats like OVA, ONA, TV_SHORT, and SPECIAL have low high popularity ratios (all <15%), while MUSIC format has almost no high-popularity works—consistent with its niche focus on music content, which struggles to attract a broad audience."
    )

'''
Objective: 
Analyze the influence of the original source of anime (such as comics, novels, original works, etc.) on its popularity. By comparing the high popularity rates of different sources, determine which original basis is more likely to give rise to popular anime.

Data Processing: 
1, Delete rows in the "source" column that have missing values. Since the missing values mainly come from less popular and niche anime, deleting them will not affect the overall analysis trend.
2, Group by source, calculate the high prevalence rate and average prevalence for each group.
3, Sort the results in descending order based on the proportion of high prevalence, and highlight the sources with significant contributions.

Conclusion: 
Anime adapted from LIGHT_NOVEL has the highest high popularity ratio (50.4%), followed by MANGA. Sources like ORIGINAL, OTHER, and VIDEO_GAME have much lower ratios (especially VIDEO_GAME, which ranks last). This confirms that works adapted from mature source materials (especially light novels and manga) with existing fan bases and complete content frameworks are far more likely to become popular.

Analyzing the reasons: 
Different source materials have distinct advantages in fan base and adaptation potential: 
- LIGHT_NOVEL: Typically has rich world-building, detailed character settings, and a dedicated core fan base; its text-based storytelling leaves flexible space for animation adaptation.
- MANGA: Has pre-existing visual storyboards (panels) that lower adaptation costs, plus a broad, established readership.
- ORIGINAL: Lacks a pre-existing fan base and requires building story/worldview from scratch, increasing the risk of failing to resonate with audiences.
- VIDEO_GAME: Often faces challenges like adapting fragmented game plots to linear animation, or mismatching fan expectations for game IPs.
'''
def source_popularity_analysis(df):
    # ========== Analysis 2: Impact of Source Material on Popularity ==========
    st.subheader("2. Source Material vs Popularity")
    source_df = df.dropna(subset=["source"])

    # Statistics on high popularity ratio for each source
    source_stats = source_df.groupby("source").agg({
        "is_high_pop": "mean",
        "popularity": "mean"
    }).round(3)
    source_stats.columns = ["High Popularity Ratio", "Average Popularity"]
    source_stats = source_stats.sort_values("High Popularity Ratio", ascending=False)

    # Visualization: bar chart (high popularity ratio)
    source_options = {
        "tooltip": {"trigger": "axis", "formatter": "{b}: {c}%"},
        "xAxis": {"type": "category", "data": source_stats.index.tolist(), "axisLabel": {"rotate": -45}},
        "yAxis": {"type": "value", "name": "High Popularity Ratio(%)", "max": 100},
        "series": [{"name": "High Popularity Ratio(%)", "type": "bar",
                    "data": (source_stats["High Popularity Ratio"] * 100).tolist(),
                    "color": "#9B59B6"}]
    }
    st_echarts(options=source_options, height="400px", key='differ source by bar')

    # Conclusion prompt
    top_source = source_stats.index[0]
    st.success(
        f"Conclusion: Anime adapted from LIGHT_NOVEL has the highest high popularity ratio (50.4%), followed by MANGA. Sources like ORIGINAL, OTHER, and VIDEO_GAME have much lower ratios (especially VIDEO_GAME, which ranks last). This confirms that works adapted from mature source materials (especially light novels and manga) with existing fan bases and complete content frameworks are far more likely to become popular."
    )

'''
Objective: 
Compare the type distribution differences between popular anime and ordinary anime, identify the types that account for a significantly higher proportion in the high-popularity group, and clarify which types are the core elements of popular anime.

Data processing: 
1, Delete rows with missing values in the "genres" column; since all the missing values are for unpopular anime, deleting them will enable us to focus on the valid data.
2, Split the multi-value type (explode("genres")), and split the comma-separated multi-type into single-row single-type entries
3, Split the multi-value type (explode("genres")), and split the comma-separated multi-type into single-row single-type to calculate the proportion (normalized count) of each type in the high-popularity group and the ordinary group.
4, Select the 15 types with the highest occurrence frequency in the total dataset as the comparison benchmark, ensuring that the analysis focuses on the mainstream types.

Conclusion: 
Certain genres (such as Action, Fantasy, Comedy, etc.) account for a larger proportion in the high-popularity group, being the core genres that are likely to give rise to popular anime; niche genres (such as mecha, sports) have a lower proportion and should be used with caution.

Analyzing the reasons: 
Genres such as Romance and Supernatural have significantly higher proportions in the high-popularity group, serving as core genres that tend to produce popular anime. Comedy, though common, has a higher proportion in the normal group and is not a core driver of high popularity. Niche genres (like Mecha, Psychological) have low proportions in both groups and should be used cautiously for mainstream popular works.'''
def genres_popularity_analysis(df, high_pop_df, normal_pop_df):
    # ========== 4. Analysis 3: Impact of Anime Genres on Popularity ==========
    df = df.dropna(subset=["genres"])
    high_pop_df = high_pop_df.dropna(subset=["genres"]) # High popularity group
    normal_pop_df = normal_pop_df.dropna(subset=["genres"]) # Normal group

    st.subheader("3. Anime Genres vs Popularity")
    # Split multiple genres and compare ratios in high popularity/normal groups
    # Genre distribution in high popularity group
    high_pop_genres = high_pop_df.explode("genres")["genres"].value_counts(normalize=True) * 100
    # Genre distribution in normal group
    normal_pop_genres = normal_pop_df.explode("genres")["genres"].value_counts(normalize=True) * 100
    # Compare top 15 common genres
    common_genres = df.explode("genres")["genres"].value_counts().head(15).index.tolist()
    genre_compare = pd.DataFrame({
        "High Popularity Group(%)": high_pop_genres[common_genres].fillna(0),
        "Normal Group(%)": normal_pop_genres[common_genres].fillna(0)
    }).round(1)

    # Visualization: dual bar chart comparison
    genre_options = {
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["High Popularity Group(%)", "Normal Group(%)"]},
        "grid": {"bottom": "25%"},
        "xAxis": {"type": "category", "data": common_genres, "axisLabel": {"rotate": -45}},
        "yAxis": {"type": "value", "name": "Genre Ratio(%)"},
        "series": [
            {"name": "High Popularity Group(%)", "type": "bar",
             "data": genre_compare["High Popularity Group(%)"].tolist(),
             "color": "#E74C3C"},
            {"name": "Normal Group(%)", "type": "bar", "data": genre_compare["Normal Group(%)"].tolist(),
             "color": "#3498DB"}
        ]
    }
    st_echarts(options=genre_options, height="500px", key='differ genres by bar')

    # Identify genres with significantly higher ratio in high popularity group
    high_impact_genres = genre_compare[
        genre_compare["High Popularity Group(%)"] - genre_compare["Normal Group(%)"] > 5].index.tolist()
    st.success(
        f"Conclusion: Certain genres (such as Action, Fantasy, Comedy, etc.) account for a larger proportion in the high-popularity group, being the core genres that are likely to give rise to popular anime; niche genres (such as mecha, sports) have a lower proportion and should be used with caution."
    )

'''
Objective: 
Analyze the influence of production companies on the popularity of anime, focusing on the major companies with a large number of works, and calculate their high popularity rates. Then, determine the correlation between the strength of the production companies and their popularity.

Data Processing：
1, Delete the rows with missing values in the "mainStudio" column. Since the missing values all come from unpopular works, deleting them will not affect the analysis.
2, Split the multi-valued column (explode("mainStudio") and count the number of works for each studio
3, Select mainstream studio with a total number of selected works being 20 or more (excluding the influence of niche studios)

Conclusion: 
Among mainstream studios, diomedéa has the highest high popularity ratio (52.4%). Top studios (including diomedéa, bones, etc.) generally maintain significantly higher high popularity ratios: this confirms that studios with strong production capabilities, rich industry resources, and established audience reputation are far more likely to create popular anime, with studio strength being a key contributor to anime popularity.

Analyzing the reasons: 
Top studios (e.g., diomedéa, bones) typically possess mature production teams, stable high-quality project partnerships, and a keen grasp of market-preferred content styles. Their technical expertise, industry resource access, and accumulated audience trust allow them to consistently deliver works that align with viewer preferences—directly boosting their works’ likelihood of becoming popular.'''
def studios_popularity_analysis(df):
    # ========== 5. Analysis 4: Impact of Studios on Popularity ==========
    df = df.dropna(subset=["mainStudio"])

    st.subheader("4. Animation Studios vs Popularity")
    # Filter top studios with ≥20 animated works
    studio_count = df.explode("mainStudio")["mainStudio"].value_counts()
    major_studios = studio_count[studio_count >= 20].index.tolist()

    # Statistics on high popularity ratio for each studio
    studio_stats = {}
    for studio in major_studios:
        studio_anime = df[df["mainStudio"].apply(lambda x: studio in x)]
        if len(studio_anime) < 20:
            continue
        high_pop_ratio = studio_anime["is_high_pop"].mean()
        studio_stats[studio] = {
            "High Popularity Ratio": high_pop_ratio,
            "Number of Works": len(studio_anime),
            "Average Popularity": studio_anime["popularity"].mean()
        }
    # 按高流行占比降序排序，并保留前15个工作室（核心修改）
    studio_stats = pd.DataFrame(studio_stats).T.sort_values("High Popularity Ratio", ascending=False).round(3)
    top15_studios = studio_stats.head(15)  # 只取前15名

    # Visualization: 只显示前15个工作室
    if not top15_studios.empty:  # 基于前15名数据可视化
        studio_options = {
            "tooltip": {"trigger": "axis", "formatter": "{b}: {c}%"},
            "xAxis": {
                "type": "category",
                "data": top15_studios.index.tolist(),  # 前15名工作室名称
                "axisLabel": {"rotate": -45}
            },
            "yAxis": {"type": "value", "name": "High Popularity Ratio(%)", "max": 100},
            "series": [{
                "name": "High Popularity Ratio(%)",
                "type": "bar",
                "data": (top15_studios["High Popularity Ratio"] * 100).tolist(),  # 前15名的占比数据
                "color": "#F39C12"
            }]
        }
        st_echarts(options=studio_options, height="500px", key='different studio by bar')

        st.success(
            f"Conclusion: Among mainstream studios, diomedéa has the highest high popularity ratio (52.4%). Top studios (including diomedéa, bones, etc.) generally maintain significantly higher high popularity ratios: this confirms that studios with strong production capabilities, rich industry resources, and established audience reputation are far more likely to create popular anime, with studio strength being a key contributor to anime popularity."
        )


'''
Objective: 
Analyze the impact of the number of episodes on anime popularity by comparing the distribution of episode counts between high-popularity and ordinary anime, and identify the optimal episode range for popular works.

Data Processing: 
1. Filter invalid values in the "episodes" column: remove missing values and 0 values to exclude abnormal data samples.
2. Bin the episode counts into 5 intervals: [0,12,24,48,100,inf), which helps compare distributions across different length ranges.
3. Calculate the proportion (normalized count) of each episode interval in both high-popularity and normal groups to highlight distribution differences between the two groups.

Conclusion: 
The high-popularity group is dominated by anime with 13-24 episodes (seasonal length), while the normal group has a higher proportion of 1-12 episode works. This indicates that 13-24 episodes (standard seasonal anime length) is the optimal range for creating popular works—striking a balance between content richness and audience retention.

Analyzing the reasons: 
Episode count correlates with content rhythm and audience commitment:
- 13-24 eps (typical seasonal anime length): Balances story completeness and pacing, can maintain audience engagement throughout the season (hence dominates the high-popularity group).
- 1-12 eps (short-form anime): Often lacks sufficient content depth to resonate with a broad audience, so it’s more common in the normal group.
- Longer episodes (25+ eps): Require sustained high-quality storytelling and production, which is harder to maintain, so they account for a small share in both groups.
'''
def episodes_popularity_analysis(high_pop_df, normal_pop_df):
    # 6.1 Comparison of episode distribution
    high_pop_df = high_pop_df[
        (high_pop_df["episodes"].notna())  # 排除空值（空白）
        & (high_pop_df["episodes"] != 0)  # 排除值为0的行
        ]
    normal_pop_df = normal_pop_df[
        (normal_pop_df["episodes"].notna())
        & (normal_pop_df["episodes"] != 0)
        ]

    st.subheader("Comparison of Episode Distribution")
    episodes_bins = [0, 12, 24, 48, 100, float("inf")]
    episodes_labels = ["1-12 eps", "13-24 eps", "25-48 eps", "49-100 eps", "100+ eps"]
    high_pop_df["episodes_bin"] = pd.cut(high_pop_df["episodes"], bins=episodes_bins, labels=episodes_labels,
                                         right=False)
    normal_pop_df["episodes_bin"] = pd.cut(normal_pop_df["episodes"], bins=episodes_bins, labels=episodes_labels,
                                           right=False)

    episodes_stats = pd.DataFrame({
        "High Popularity Group": high_pop_df["episodes_bin"].value_counts(normalize=True) * 100,
        "Normal Group": normal_pop_df["episodes_bin"].value_counts(normalize=True) * 100
    }).fillna(0).round(1)

    episodes_options = {
        "tooltip": {"trigger": "item"},
        "legend": {
            "bottom": 0,  # Place legend at bottom to avoid blocking pie chart
            "orient": "horizontal"  # Arrange legend horizontally
        },
        "series": [
            # High popularity group pie chart: left side
            {
                "name": "High Popularity",
                "type": "pie",
                "data": [{"name": k, "value": v} for k, v in episodes_stats["High Popularity Group"].items()],
                "center": ["25%", "50%"],  # Independent position: left half
                "radius": ["30%", "60%"]  # Pie chart size
            },
            # Normal group pie chart: right side
            {
                "name": "Normal",
                "type": "pie",
                "data": [{"name": k, "value": v} for k, v in episodes_stats["Normal Group"].items()],
                "center": ["75%", "50%"],  # Independent position: right half
                "radius": ["30%", "60%"]
            }
        ]
    }
    st_echarts(options=episodes_options, height="300px", key="episodes_dist")
    st.success(
        f"Conclusion: The high-popularity group is dominated by anime with 13-24 episodes (seasonal length), while the normal group has a higher proportion of 1-12 episode works. This indicates that 13-24 episodes (standard seasonal anime length) is the optimal range for creating popular works—striking a balance between content richness and audience retention."
    )


'''
Objective: 
Explore the relationship between episode duration and anime popularity by comparing the duration distribution between high-popularity and ordinary anime, and determine the preferred duration range for popular works.

Data Processing: 
1. Filter invalid values in the "duration" column: remove missing values and 0 values to exclude abnormal data samples.
2. Bin the duration into 4 intervals: [0,15,25,45,inf), matching common anime duration types.
3. Calculate the proportion (normalized count) of each duration interval in both high-popularity and normal groups to compare duration preferences between the two groups.

Conclusion: 
The high-popularity group is overwhelmingly dominated by 16-25 minute episodes (standard TV length), while the normal group has a large proportion of ≤15 minute works. This confirms that 16-25 minutes is the optimal duration for popular anime: it matches mainstream viewing habits and provides enough space for engaging storytelling, whereas shorter/longer durations are far less likely to drive widespread popularity.

Analyzing the reasons: 
Episode duration ties closely to audience viewing habits and content completeness:
- 16-25 min (standard TV anime length): Fits daily viewing rhythms (e.g., weekly 20-minute episodes), balances concise pacing and sufficient narrative depth—this is why it dominates the high-popularity group.
- ≤15 min (short-form anime): Typically has limited storytelling space (often fragmented or lightweight content), making it harder to resonate with broad audiences—hence its high proportion in the normal group.
- Longer durations (>25 min): Mostly apply to special formats (e.g., OVAs, movies), which have narrower release/consumption scenarios, so they account for small shares in both groups.
'''
def duration_popularity_analysis(high_pop_df, normal_pop_df):
    high_pop_df = high_pop_df[
        (high_pop_df["duration"].notna())  # 排除空值（空白）
        & (high_pop_df["duration"] != 0)  # 排除值为0的行
        ]
    normal_pop_df = normal_pop_df[
        (normal_pop_df["duration"].notna())
        & (normal_pop_df["duration"] != 0)
        ]

    # 6.2 Comparison of episode duration
    st.subheader("Comparison of Episode Duration Distribution")
    duration_bins = [0, 15, 25, 45, float("inf")]
    duration_labels = ["≤15 min", "16-25 min", "26-45 min", ">45 min"]
    high_pop_df["duration_bin"] = pd.cut(high_pop_df["duration"], bins=duration_bins, labels=duration_labels,
                                         right=False)
    normal_pop_df["duration_bin"] = pd.cut(normal_pop_df["duration"], bins=duration_bins, labels=duration_labels,
                                           right=False)

    duration_stats = pd.DataFrame({
        "High Popularity Group": high_pop_df["duration_bin"].value_counts(normalize=True) * 100,
        "Normal Group": normal_pop_df["duration_bin"].value_counts(normalize=True) * 100
    }).fillna(0).round(1)

    duration_options = {
        "tooltip": {"trigger": "item"},
        "legend": {
            "bottom": 0,
            "orient": "horizontal"
        },
        "series": [
            # High popularity group pie chart: left
            {
                "name": "High Popularity",
                "type": "pie",
                "data": [{"name": k, "value": v} for k, v in duration_stats["High Popularity Group"].items()],
                "center": ["25%", "50%"],
                "radius": ["30%", "60%"]
            },
            # Normal group pie chart: right
            {
                "name": "Normal",
                "type": "pie",
                "data": [{"name": k, "value": v} for k, v in duration_stats["Normal Group"].items()],
                "center": ["75%", "50%"],
                "radius": ["30%", "60%"]
            }
        ]
    }
    st_echarts(options=duration_options, height="300px", key="duration_dist")
    st.success(
        f"Conclusion: The high-popularity group is overwhelmingly dominated by 16-25 minute episodes (standard TV length), while the normal group has a large proportion of ≤15 minute works. This confirms that 16-25 minutes is the optimal duration for popular anime: it matches mainstream viewing habits and provides enough space for engaging storytelling, whereas shorter/longer durations are far less likely to drive widespread popularity."
    )


'''
Objective: 
Investigate the correlation between anime scores and popularity through a scatter plot, and verify whether high-quality works (high scores) are more likely to be popular.

Data Processing: 
1. Handle missing values in the "averageScore" column: fill empty values with "meanScore", and directly delete rows that are still empty after filling.
2. Construct scatter plot data: extract scores, popularity, and high-popularity labels (1/0), converting them to native Python types to ensure JSON serialization compatibility.
3. Use full data for visualization without sampling to maintain data integrity.

Conclusion: 
There is a clear positive correlation between anime scores and popularity: the high-popularity group (red points) is almost entirely concentrated in the high-score region (mostly ≥70), while the normal group (teal points) is clustered in the low-score region. This confirms that content quality (as reflected by scores) is a critical factor in driving popularity—ensuring high-quality content is key to creating popular anime.

Analyzing the reasons: 
Scores directly reflect audience evaluation of core quality (storytelling, animation, character design, etc.). High-scoring works are more likely to receive positive word-of-mouth, platform recommendation resources, and sustained audience engagement—these factors collectively drive higher popularity. Conversely, low-scoring works struggle to form effective spread, so they remain in the low-popularity group.
'''
def score_popularity_analysis(df):
    # ========== 处理评分空值并过滤无效数据 ==========
    df["averageScore"] = df["averageScore"].fillna(df["meanScore"])  # 用meanScore填充空值
    df = df.dropna(subset=["averageScore"])  # 移除仍为空的行

    st.subheader("Score vs Popularity (Scatter Plot)")
    # 移除抽样，直接使用全量数据（约5000个样本）
    full_df = df  # 全量数据

    # 重构散点数据：[评分, 流行度, 高流行标记(1/0)]
    scatter_data = [
        [
            float(row["averageScore"]),  # 确保为原生float
            int(row["popularity"]),  # 确保为原生int
            1 if row["is_high_pop"] else 0  # 用数字标记类型（JSON可序列化）
        ]
        for _, row in full_df.iterrows()  # 遍历全量数据
    ]

    scatter_options = {
        "xAxis": {"type": "value", "name": "Average Score"},
        "yAxis": {"type": "value", "name": "Popularity"},
        # 颜色映射（高流行=红色，普通=蓝色）
        "visualMap": {
            "type": "piecewise",
            "dimension": 2,  # 基于第3列（0/1）映射颜色
            "pieces": [
                {"value": 1, "label": "High Popularity", "color": "#FF6B6B"},
                {"value": 0, "label": "Normal", "color": "#4ECDC4"}
            ],
            "show": True,
            "top": "bottom"
        },
        "series": [{
            "type": "scatter",
            "data": scatter_data,
            "symbolSize": 4,  # 缩小点的大小（5000点建议4-6，避免重叠）
            "itemStyle": {"opacity": 0.6}  # 降低透明度（避免密集区域过暗）
        }]
    }
    # 显示全量数据散点图（增加高度适配更多点）
    st_echarts(options=scatter_options, height="500px", key="score_vs_pop_scatter_full")

    # 结论
    st.success(
        "Conclusion: There is a clear positive correlation between anime scores and popularity: the high-popularity group (red points) is almost entirely concentrated in the high-score region (mostly ≥70), while the normal group (teal points) is clustered in the low-score region. This confirms that content quality (as reflected by scores) is a critical factor in driving popularity—ensuring high-quality content is key to creating popular anime."
    )


'''
Motivation:
The production and investment decisions in the animation industry heavily rely on the judgment of "popular elements". Small production teams often fail to produce successful works due to deviations in selection or production direction.
This project aims to quantify "which characteristics determine the popularity of animation" through data analysis, providing a practical decision-making basis for producers and investors:
- Clearly define the core characteristics such as formats, original works, and types with high popularity probability
- Avoid creative directions with low cost-effectiveness (such as niche formats and unpopular original works)

Data processing & Feature engineering:
1. Core feature selection: Extract 7 key dimensions (format, original work, type, production company, number of episodes, duration, rating) from the raw data, eliminate irrelevant fields (such as release date, region, etc.), and focus on the core elements influencing popularity;
2. Multi-value column processing (feature splitting): Split multi-value columns separated by pipe symbols (such as "genres", "mainStudio") into list format, supporting subsequent aggregation analysis based on individual types or companies;
3. High-popularity label construction (feature derivation): Use the 80th percentile of popularity as a threshold, divide the works into "high-popularity group (top 20%)" and "ordinary group", serving as the core label for comparative analysis;
4. Outlier/missing value handling: Each sub-function specifically filters out invalid values (such as 0 values or null values for episode number/duration). As missing values are concentrated in unpopular works(It has been demonstrated in DataMissingAnalyse.ipynb), directly deleting them does not affect the core trend;
5. Feature binning (discretization): Divide episode numbers (1-12/13-24, etc.) and durations (≤15/16-25, etc.) into intervals, converting continuous features into business-interpretable discrete categories;
6. Proportion normalization: Calculate the "high-popularity proportion" for dimensions such as type/format, eliminating the analysis bias caused by differences in sample size.

Conclusion:
Producing "13-24 episode TV anime adapted from Light Novel (or Manga)", with core genres of Romance/Supernatural/Action, produced by top studios (e.g., diomedéa), ensuring 16-25 minutes per episode and an average score ≥70, is the optimal combination to create a highly popular anime work.
'''
def plot_popularity_analysis(anime_df):
    # Keep core analysis columns (adjust according to your CSV column names, ensure lowercase)
    core_cols = ["title_romaji", "format", "genres", "source", "season", "mainStudio",
                 "episodes", "duration", "averageScore", 'meanScore', "popularity"]
    df = anime_df[core_cols]
    # 1. Process multi-value columns (genres/studios separated by pipes)
    df["genres"] = df["genres"].str.split("|")
    df["mainStudio"] = df["mainStudio"].str.split("|")

    # 2. Define "high popularity group" (top 20% popularity)
    high_pop_threshold = int(df["popularity"].quantile(0.8))  # 80th percentile as threshold
    df["is_high_pop"] = df["popularity"] >= high_pop_threshold

    high_pop_df = df[df["is_high_pop"]]  # High popularity group
    normal_pop_df = df[~df["is_high_pop"]]  # Normal group

    # Page title
    st.title("What Makes an Anime Popular? — Popularity Factor Analysis")
    st.info(
        f"Highly Popular Anime Definition: popularity ≥ {high_pop_threshold} (top 20%), total {len(high_pop_df)} titles")

    format_popularity_analysis(df)
    source_popularity_analysis(df)
    genres_popularity_analysis(df, high_pop_df, normal_pop_df)
    studios_popularity_analysis(df)
    episodes_popularity_analysis(high_pop_df, normal_pop_df)
    duration_popularity_analysis(high_pop_df, normal_pop_df)
    score_popularity_analysis(df)


    # ========== 7. Final Summary: Feature Combination of Popular Anime ==========
    st.subheader("Final Summary: Core Feature Combination of Highly Popular Anime")
    st.markdown("""
    | Feature Dimension | Recommended High Popularity Features | Not Recommended Features |
    |-------------------|--------------------------------------|--------------------------|
    | **Format**        | TV (highest high popularity ratio, 41.2%) | OVA/ONA/MUSIC (extremely low popularity ratio) |
    | **Source**        | Light Novel (highest ratio, 50.4%), Manga (second) | Video Game/Original (lowest popularity ratio) |
    | **Genres**        | Romance, Supernatural, Action | Comedy (high in normal group), Mecha/Psychological (niche) |
    | **Studios**       | Top studios (e.g., diomedéa, bones) | Small studios |
    | **Episodes**      | 13-24 episodes (seasonal length, dominant in high-pop group) | 100+ episodes |
    | **Duration**      | 16-25 minutes/episode (standard TV, overwhelming in high-pop group) | ≤15 minutes (short-form), >45 minutes (except movies) |
    | **Score**         | Average score ≥70 (core of high-pop group) | Score <60 (clustered in normal group) |

    **Core Recommendation**: Producing "13-24 episode TV anime adapted from Light Novel (or Manga)", with core genres of Romance/Supernatural/Action, produced by top studios (e.g., diomedéa), ensuring 16-25 minutes per episode and an average score ≥70, is the optimal combination to create a highly popular anime work.
    """)