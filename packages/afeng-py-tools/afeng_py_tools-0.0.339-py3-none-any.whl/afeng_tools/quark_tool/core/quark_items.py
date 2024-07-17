from typing import Optional, Any, List

from pydantic import BaseModel, Field


class ShareUser(BaseModel):
    # 如：SUPER_VIP
    member_type: Optional[str] = None
    avatar_url: Optional[str] = None
    nick_name: Optional[str] = None


class ShareToken(BaseModel):
    # 如：英语兔英语词汇音标发音学习
    title: Optional[str] = None
    subscribed: Optional[bool] = None
    stoken: Optional[str] = None
    share_type: Optional[int] = None
    author: Optional[ShareUser] = None
    expired_type: Optional[int] = None
    expired_at: Optional[int] = None
    pwd_id: Optional[str] = None


class PageMetadata(BaseModel):
    check_fid_token: Optional[int] = None
    count: Optional[int] = Field(alias='_count',default=None)
    page: Optional[int] = Field(alias='_page',default=None)
    size: Optional[int] = Field(alias='_size',default=None)
    total: Optional[int] = Field(alias='_total',default=None)


class ShareBaseFile(BaseModel):
    fid: Optional[str] = None
    # 0、文件夹， 1、图片、视频
    file_type: Optional[int] = None
    # "image/png"、 "video/mp4"
    format_type: Optional[str] = None
    # 如： "image"、  "video"
    obj_category: Optional[int] = None
    name_space: Optional[int] = None
    series_dir: Optional[bool] = None
    upload_camera_root_dir: Optional[bool] = None
    fps: Optional[float] = None
    like: Optional[int] = None
    risk_type: Optional[int] = None
    file_name_hl_start: Optional[int] = None
    file_name_hl_end: Optional[int] = None
    duration: Optional[int] = None
    ban: Optional[bool] = None
    cur_version_or_default: Optional[int] = None
    offline_source: Optional[bool] = None
    backup_source: Optional[bool] = None
    save_as_source: Optional[bool] = None
    owner_drive_type_or_default: Optional[int] = None
    dir: Optional[bool] = None
    file: Optional[bool] = None
    extra: Optional[dict[str, Any]] = Field(alias='_extra', default=None, extra=False)


class ShareFileStruct(BaseModel):
    # 示例：saveas
    fir_source: Optional[str] = None
    # 示例：share_save
    sec_source: Optional[str] = None
    # 示例：share_save
    thi_source: Optional[str] = None
    # 示例：android
    platform_source: Optional[str] = None


class ShareFile(ShareBaseFile):
    file_name: Optional[str] = None
    pdir_fid: Optional[str] = None
    category: Optional[int] = None
    size: Optional[int] = None
    status: Optional[int] = None
    tags: Optional[str] = None
    owner_ucid: Optional[str] = None
    share_fid_token: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    last_update_at: Optional[int] = None
    l_created_at: Optional[int] = None
    l_updated_at: Optional[int] = None
    l_shot_at: Optional[int] = None
    # 图片、视频有缩略图
    big_thumbnail: Optional[str] = None
    thumbnail: Optional[str] = None
    # 视频的属性，示例：1080
    video_height: Optional[int] = None
    # 示例：1920
    video_width: Optional[int] = None
    # 示例："super"
    video_max_resolution: Optional[str] = None
    # 示例：-1
    video_rotate: Optional[int] = None
    operated_at: Optional[int] = None
    include_items: Optional[int] = None
    # 示例：ucpro-android:saveas
    source: Optional[str] = None
    # 示例:UCPRO-ANDROID:SAVE_SHARE
    file_source: Optional[str] = None
    # 示例：save_share
    source_display: Optional[str] = None
    name_space: Optional[int] = None
    series_dir: Optional[bool] = None
    upload_camera_root_dir: Optional[bool] = None
    backup_sign: Optional[int] = None
    file_struct: Optional[ShareFileStruct] = None
    extra: Optional[str] = None
    event_extra: Optional[dict[str, Any]] = None
    raw_name_space: Optional[int] = None


class ShareItem(BaseModel):
    title: Optional[str] = None
    path_info: Optional[str] = None
    size: Optional[int] = None
    share_id: Optional[str] = None
    pwd_id: Optional[str] = None
    share_url: Optional[str] = None
    file_num: Optional[int] = None
    first_fid: Optional[str] = None
    first_file: Optional[ShareBaseFile] = None
    share_type: Optional[int] = None
    url_type: Optional[int] = None
    expired_type: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    expired_at: Optional[int] = None
    expired_left: Optional[int] = None
    audit_status: Optional[int] = None
    status: Optional[int] = None
    click_pv: Optional[int] = None
    save_pv: Optional[int] = None
    download_pv: Optional[int] = None
    partial_violation: Optional[bool] = None
    first_layer_file_categories: Optional[List[int]] = None
    is_owner: Optional[int] = None
    download_pvlimited: Optional[bool] = None
    pass


class ShareData(BaseModel):
    is_owner: Optional[int] = None
    share: Optional[ShareItem] = None
    list: Optional[List[ShareFile]] = None
