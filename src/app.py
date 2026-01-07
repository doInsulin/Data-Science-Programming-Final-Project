import streamlit as st

# 1. 定义页面列表（先实例化 Page 对象）
search_page = st.Page("pages/search.py", title="Search")
overview_page = st.Page("pages/overview.py", title="Overview")
popularityAnalysis_page = st.Page("pages/popularityAnalysis.py", title="Popularity Analysis")
capacityAnalysis_page = st.Page("pages/capacityAnalysis.py", title="Capacity Analysis")
sourceAnalysis_page = st.Page("pages/sourceAnalysis.py", title="Source Analysis")
isekai_analysis_page = st.Page("pages/isekai_analysis.py", title="Isekai Analysis")
Prediction_page = st.Page("pages/prediction.py", title="Prediction")
pages = [search_page, overview_page, popularityAnalysis_page, capacityAnalysis_page, sourceAnalysis_page , isekai_analysis_page, Prediction_page]

# 初始化全局Session State，存储页面数据
if "page_data" not in st.session_state:
    st.session_state.page_data = {"Search": None, "Overview": None, "Popularity Analysis": None, "Capacity Analysis": None}

# 2. 渲染导航，直接传入 Page 对象作为默认选中项（1.52.0 推荐写法）
current_page = st.navigation(pages)  # 关键：传对象而非字符串

# 3. 运行选中的页面
current_page.run()