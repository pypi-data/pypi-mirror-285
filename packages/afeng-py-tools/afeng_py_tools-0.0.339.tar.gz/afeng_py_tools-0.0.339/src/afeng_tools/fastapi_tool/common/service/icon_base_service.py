from afeng_tools.fastapi_tool.common.enum import IconTypeEnum


def get_icon_code(icon_type: IconTypeEnum, icon_value: str, alt: str = '', image_src: str = None) -> str | None:
    """获取icon代码"""
    if image_src:
        return f'<img data-src="{image_src}" data-type="image" referrer="no-referrer" referrerpolicy="no-referrer" alt="{alt}" title="{alt}"/>'
    if not icon_value:
        return None
    if icon_type == IconTypeEnum.svg_icon or icon_type == IconTypeEnum.font_icon:
        return icon_value
    elif icon_type == IconTypeEnum.resource_icon:
        return f'<img data-src="/resource/public/{icon_value}" data-type="image" referrer="no-referrer" referrerpolicy="no-referrer" alt="{alt}" title="{alt}" />'
    else:
        return f'<img data-src="{icon_value}" data-type="image" referrer="no-referrer" referrerpolicy="no-referrer" alt="{alt}" title="{alt}"/>'
