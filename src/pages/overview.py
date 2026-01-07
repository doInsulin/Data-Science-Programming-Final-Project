import streamlit as st
import util.overview_visualization as over_vl
from store.anime_store import AnimeStore

# Page title and layout configuration
st.set_page_config(page_title="Anime Data Analysis", layout="wide")
st.title("**Anime Data Analysis Dashboard**")

# Brief introduction
st.markdown("""
    Welcome to the **Anime Data Analysis Dashboard**. This platform provides a series of visualizations aimed at offering insights into various aspects of anime data, 
    including trends across different genres, platforms, and studios. 
   
    Through this dashboard, users will be able to explore key patterns, relationships, and trends within the anime industry, providing a clear and interactive method of data exploration.
""")

# Sidebar navigation
st.sidebar.header("**Navigation**")
st.sidebar.markdown("""
    - **Anime Overview Visualization**: An overview of trends and statistics from the anime dataset.
    - **Genre Analysis**: A detailed breakdown of the most popular anime genres and their distributions.
    - **Studio and Platform Partnerships Analysis**: An examination of the collaboration dynamics between anime studios and platforms.
""")

# Load data
try:
    store = AnimeStore()
    anime_df = store.df
    original_count = len(anime_df)
except FileNotFoundError as e:
    st.error(f"❌ Error: {e}")
    st.stop()

# ========== Visualization Section ==========

# Anime overview visualization
st.header("**Anime Overview Visualization**")
st.markdown("This section provides a high-level view of the anime dataset, visualizing key trends and statistics across different parameters.")
over_vl.plot_anime_visualizations(anime_df)

# Add a separator between sections
st.markdown("<hr>", unsafe_allow_html=True)

# Genre analysis
st.header("**Genre Analysis**")
st.markdown("In this section, we explore the distribution of anime genres to reveal the most popular genres within the dataset.")
over_vl.plot_genre_analysis(anime_df)

# Add a separator between sections
st.markdown("<hr>", unsafe_allow_html=True)

# Studio and platform partnerships analysis
st.header("**Studio and Platform Partnerships Analysis**")
st.markdown("This analysis focuses on the relationships between anime studios and platforms, highlighting key collaborations that drive trends in the industry.")
over_vl.plot_studio_platform_partnerships(anime_df)

# Add a separator between sections
st.markdown("<hr>", unsafe_allow_html=True)

# Data download option
st.sidebar.header("**Download Data**")
st.sidebar.markdown("""
    Simply click the button below to obtain the file.
""")
st.sidebar.download_button(
    label="Download Full Anime Dataset",
    data=anime_df.to_csv(index=False).encode('utf-8'),
    file_name="anime_data.csv",
    mime="text/csv"
)

# Closing message
st.markdown("""
    These visualizations provide valuable insights into anime trends and help guide your analysis. 
    Feel free to interact with the charts, adjust any filters, and further explore the data.
""")
