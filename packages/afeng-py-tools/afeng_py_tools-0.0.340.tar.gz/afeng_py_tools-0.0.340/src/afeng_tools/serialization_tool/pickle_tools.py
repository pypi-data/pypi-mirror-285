"""
pickle序列化与反序列化工具
"""
import pickle


def save_to_file(obj: object, save_file: str):
    """序列化对象保存到文件"""
    with open(save_file, "wb") as f:
        # 序列化
        pickle.dump(obj, f)


def parse_to_obj(save_file: str):
    """反序列化文件为对象"""
    with open(save_file, "rb") as f:
        # 反序列
        return pickle.load(f)
