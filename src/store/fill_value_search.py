# utils/data_processor.py
import pandas as pd
from typing import Optional

def fill_anime_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    填充动漫数据中的缺失值，保持原逻辑一致
    :param df: 原始动漫数据DataFrame
    :return: 填充缺失值后的DataFrame
    """
    if df is None or df.empty:
        raise ValueError("输入的DataFrame不能为空")
    
    # 填充缺失值（原逻辑完整迁移）
    filled_df = df.fillna({
        "genres": "Any",
        "seasonYear": 0,
        "season": "Any",
        "format": "Any",
        "status": "Any",
        "source": "Any",
        "episodes": 0,
        "duration": 0,
        "tags": "",
        "mainStudio": ""
    })
    
    # 如果averageScore为空，使用meanScore填充
    filled_df['averageScore'] = filled_df['averageScore'].fillna(filled_df['meanScore'])
    
    # 确保数值列为数字类型
    numeric_cols = ["seasonYear", "episodes", "duration", "averageScore"]
    for col in numeric_cols:
        filled_df[col] = pd.to_numeric(filled_df[col], errors='coerce').fillna(0)
    
    return filled_df