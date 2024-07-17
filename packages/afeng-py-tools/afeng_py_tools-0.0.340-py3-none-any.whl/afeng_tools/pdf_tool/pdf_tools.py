"""
pip install pymupdf
"""
import os
from typing import Optional

from pydantic import BaseModel
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas
# PyMuPDF 的导入名称
import fitz


class PdfTextItem(BaseModel):
    x: int
    y: int
    text: str


class PdfImageItem(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    x: int
    y: int
    image: ImageReader
    image_width: Optional[int] = None
    image_height: Optional[int] = None


def create_canvas(pdf_file: str, page_size: tuple[float, float] = letter, bottom_up: int = 0) -> Canvas:
    """创建一个PDF画布，默认设置页面大小为letter，并且横放"""
    return canvas.Canvas(pdf_file, pagesize=page_size, bottomup=bottom_up)


def save_canvas(pdf_canvas: Canvas):
    """保存 Canvas """
    pdf_canvas.save()


def create_new_page(pdf_canvas: Canvas, item_list: list[PdfTextItem | PdfImageItem],
                    ttf_file: str = r'C:\Windows\Fonts\SimHei.ttf',
                    stroke_color_rgb: tuple[float, float, float] = (0.2, 0.5, 0.3),
                    fill_color_rgb: tuple[float, float, float] = (0, 0, 0),
                    font_size: int = 12,
                    line_height: int = 20,
                    is_end: bool = False):
    """
    添加内容
    :param pdf_canvas:
    :param item_list:
    :param ttf_file:
    :param stroke_color_rgb:
    :param fill_color_rgb:
    :param font_size:
    :param line_height: 行高
    :param is_end：是否是结尾页
    :return:
    """
    # 注册中文字体
    pdfmetrics.registerFont(TTFont('SimHei', ttf_file))
    pdf_canvas.setStrokeColorRGB(*stroke_color_rgb)
    pdf_canvas.setFillColorRGB(*fill_color_rgb)
    # 设置字体和字号
    pdf_canvas.setFont('SimHei', font_size)
    space_x, space_y = 0, 0
    for tmp_item in item_list:
        if isinstance(tmp_item, PdfImageItem):
            # 图片大小
            img_width, img_height = tmp_item.image.getSize()
            if tmp_item.image_width:
                img_width = tmp_item.image_width
            if tmp_item.image_height:
                img_height = tmp_item.image_height
            # 将图片添加到PDF中，指定位置和大小
            pdf_canvas.drawImage(tmp_item.image, tmp_item.x, tmp_item.y, width=img_width, height=img_height)
        elif isinstance(tmp_item, PdfTextItem):
            if tmp_item.x >= letter[0]:
                space_x = space_x + letter[0]
                tmp_item.x = tmp_item.x - space_x + 10
                tmp_item.y = tmp_item.y + font_size
            if tmp_item.y >= letter[1]:
                if space_y + letter[1] <= tmp_item.y + line_height * 2:
                    space_y = space_y + letter[1]
                    pdf_canvas.showPage()
                    pdf_canvas.setStrokeColorRGB(*stroke_color_rgb)
                    pdf_canvas.setFillColorRGB(*fill_color_rgb)
                    # 设置字体和字号
                    pdf_canvas.setFont('SimHei', font_size)
                while tmp_item.y - space_y - line_height < 0:
                    space_y = space_y - line_height
                tmp_item.y = tmp_item.y - space_y + line_height
            tmp_item.text = tmp_item.text.replace('\t', '    ')
            # 添加文字
            pdf_canvas.drawString(tmp_item.x, tmp_item.y, tmp_item.text)
    if not is_end:
        # 显示当前页面并准备下一页（以此类推可以添加更多页）
        pdf_canvas.showPage()
    return pdf_canvas


def merger(input_pdf_list: list[str], out_pdf: str, start_page_num:int=0) -> str:
    """
    合并pdf
    :param input_pdf_list: 需要合并的pdf文件列表
    :param out_pdf: 合并后的pdf
    :param start_page_num: 起始页码
    :return: 合并后的pdf
    """

    # 创建一个新的 PDF 文档对象
    merged_pdf = fitz.open()
    toc_list = []
    # 遍历要合并的 PDF 文件列表
    for input_pdf in input_pdf_list:
        # 打开当前 PDF 文件
        with fitz.open(input_pdf) as src_pdf:
            # 获取目录
            tmp_toc = src_pdf.get_toc()
            for entry in tmp_toc:
                # 目录级别
                level = entry[0]
                # 目录标题
                title = entry[1]
                # 目录所在页码
                page_number = entry[2]

                # [页码, 标题， 目录level]
                toc_list.append([level, title, start_page_num+page_number])
            # 添加到新文档的末尾
            merged_pdf.insert_pdf(src_pdf)
            start_page_num = start_page_num + src_pdf.page_count

    merged_pdf.set_toc(toc_list)
    # 保存合并后的 PDF 文件
    merged_pdf.save(out_pdf)

    # 关闭合并后的 PDF 文档对象
    merged_pdf.close()
    return out_pdf

if __name__ == '__main__':
    root_path = os.path.dirname(__file__)
    cover_pdf = os.path.join(root_path, 'cover.pdf')
    pdf_canvas = create_canvas(cover_pdf)
    # 加载图片
    img = ImageReader('input/cover.jpg')
    image_width, image_height = letter
    create_new_page(pdf_canvas,
                              item_list=[PdfImageItem(x=0, y=0, image=img,
                                                                image_width=image_width,
                                                                image_height=image_height)], is_end=True)


    # line_list = file_tools.read_file_lines(os.path.join(os.path.dirname(__file__), 'input/目录.TXT'))
    #
    # pdf_tools.create_new_page(pdf_canvas, item_list=[pdf_tools.PdfTextItem(x=50, y=20 * (index + 1), text=tmp_line)
    #                                                  for index, tmp_line in enumerate(line_list)])
    save_canvas(pdf_canvas)

    pdf_list = [cover_pdf]
    # pdf文件存放路径
    input_path = os.path.join(root_path, 'input')
    # 将待拼接的pdf文件以绝对路径的形式放在一个列表里
    pdf_list.extend(sorted([os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith('.pdf')]))
    merger(pdf_list, 'output/LINUX与UNIX Shell编程指南.pdf', start_page_num=0)