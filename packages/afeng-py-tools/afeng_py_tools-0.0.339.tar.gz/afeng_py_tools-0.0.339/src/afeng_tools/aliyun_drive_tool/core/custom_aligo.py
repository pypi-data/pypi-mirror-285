"""扩展实现彻底删除文件功能"""
from typing import List

from aligo import Aligo, BatchRequest, BatchSubRequest


class CustomAligo(Aligo):
    """自定义 aligo """
    V3_FILE_DELETE = '/v3/file/delete'

    def delete_file(self, file_id: str, drive_id: str = None) -> bool:
        """删除文件"""
        drive_id = drive_id or self.default_drive_id
        response = self.post(self.V3_FILE_DELETE, body={
            'drive_id': drive_id,
            'file_id': file_id
        })
        return response.status_code == 204

    def batch_delete_files(self, file_id_list: List[str], drive_id: str = None):
        """批量删除文件"""
        drive_id = drive_id or self.default_drive_id
        result = self.batch_request(BatchRequest(
            requests=[BatchSubRequest(
                id=file_id,
                url='/file/delete',
                body={
                    'drive_id': drive_id,
                    'file_id': file_id
                }
            ) for file_id in file_id_list]
        ), dict)
        return list(result)

    def clear_recyclebin(self, drive_id: str = None):
        """清空回收站"""
        drive_id = drive_id or self.default_drive_id
        response = self.post('/v2/recyclebin/clear', body={
            'drive_id': drive_id
        })
        return response.status_code == 202


if __name__ == '__main__':
    ali = CustomAligo()

    # x = ali.delete_file('646604d56d3ee7cfe2654b4as9ed4xse59cf76')
    # print(x)

    # 清空回收站
    # ll = ali.get_recyclebin_list()
    # rr = ali.batch_delete_files([f.file_id for f in ll])

    # 新的清空回收站方法，异步的
    rr = ali.clear_recyclebin()
    print(rr)