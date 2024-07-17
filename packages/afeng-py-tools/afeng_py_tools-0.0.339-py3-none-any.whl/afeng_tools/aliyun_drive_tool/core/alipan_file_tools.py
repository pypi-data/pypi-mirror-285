from aligo import BaseShareFile


def is_folder(alipan_file: BaseShareFile) -> bool:
    """是否是文件夹"""
    return alipan_file.type == 'folder'


def is_file(alipan_file: BaseShareFile) -> bool:
    """是否是文件"""
    return not is_folder(alipan_file)


def is_audio(alipan_file: BaseShareFile) -> bool:
    """是否是音频"""
    return alipan_file.category == 'audio'


def is_video(alipan_file: BaseShareFile) -> bool:
    """是否是视频"""
    return alipan_file.category == 'video'


def is_doc(alipan_file: BaseShareFile) -> bool:
    """是否是文档"""
    return alipan_file.category == 'doc'


def is_image(alipan_file: BaseShareFile) -> bool:
    """是否是图片"""
    return alipan_file.category == 'image'


