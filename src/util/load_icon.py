import base64

def load_icon_base64(path: str) -> str:
    """加载图片并将其转换为base64编码的字符串"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")