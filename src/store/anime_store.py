# store/anime_store.py
import pandas as pd
from typing import Optional

class AnimeStore:
    # 单例实例
    _instance = None
    # 存储加载的原始数据
    _data: Optional[pd.DataFrame] = None

    def __new__(cls):
        """单例模式：确保全局只有一个AnimeStore实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 实例化时自动加载数据
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        """仅加载原始CSV数据，不做缺失值填充等任何处理"""
        # 避免重复加载数据
        if self._data is not None:
            return
        
        try:
            # 读取原始数据文件（路径保持不变）
            df = pd.read_csv("public/data/anilist_anime_2016_2025.csv")
            # 仅存储原始数据，不做任何填充/类型转换
            self._data = df
        except FileNotFoundError as e:
            # 自定义异常提示，方便定位问题
            raise FileNotFoundError(
                f"数据文件未找到，请检查路径是否正确：public/data/anilist_anime_2016_2025.csv"
            ) from e

    @property
    def df(self) -> pd.DataFrame:
        """获取原始数据的只读副本（防止外部修改内部数据）"""
        if self._data is None:
            raise RuntimeError("数据加载失败，请检查文件是否存在或路径是否正确")
        # 返回副本，避免外部修改原数据
        return self._data.copy()