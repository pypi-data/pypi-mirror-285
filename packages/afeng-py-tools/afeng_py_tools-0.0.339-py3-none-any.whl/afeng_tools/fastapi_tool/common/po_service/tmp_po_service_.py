from afeng_tools.fastapi_tool.common.po_service.base_po_service import PoService


class TmpSortPoService(PoService):
    """
    使用示例：tmp_sort_po_service = TmpSortPoService(app_info.db_code, TmpSortInfoPo)
    使用步骤如下：
        1、使用查询参数生成 unique_code
        2、使用 unique_code 查询是否已经有缓存排序数据
            tmp_po_list = tmp_sort_po_service.query_more(TmpSortInfoPo.unique_code == unique_code,
                                                 sort_column='sort_index',
                                                 sort_type=SortTypeEnum.asc)
            - 如果存在，则使用缓存的排序数据
                match_code_list = [tmp.sort_value for tmp in tmp_po_list]
            - 如果不存在，则查询排序后的数据，然后入库
                match_code_list = 根据自己的需要进行查询
                tmp_sort_po_service.add_in_list(unique_code, match_code_list)
        3、将已有的 db_query 和 缓存的排序数据表进行拼接，根据排序表中的索引进行排序
            db_query = db_query.join(TmpSortInfoPo, DocInfoPo.code == TmpSortInfoPo.sort_value,
                        isouter=True).filter(TmpSortInfoPo.unique_code == unique_code)
            db_query = db_query.order_by(TmpSortInfoPo.sort_index.asc())
    """
    _table_name_ = "tmp_sort_info"

    def delete_by_unique_code(self, unique_code: str):
        """通过唯一码删除"""
        return self.delete(self.model_type.unique_code == unique_code)

    def add_in_list(self, unique_code: str, in_data_list: list):
        """添加in列表"""
        tmp_po_list = []
        for index, tmp_in_data in enumerate(in_data_list):
            tmp_po_list.append(self.model_type(
                type_code='default',
                unique_code=unique_code,
                sort_value=str(tmp_in_data),
                sort_index=(index + 1)
            ))
        return self.add_batch(tmp_po_list)


