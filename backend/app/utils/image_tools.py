import base64
import tempfile
from io import BytesIO
from PIL import Image
from pydantic import BaseModel


class ImageSize(BaseModel):
    """
    图片尺寸信息
    """
    width: int
    height: int

class ImageInfo(ImageSize):
    """
    图片信息
    """
    file_name: str


def save_image_from_base64(image_base64: str, upload_directory: str) -> ImageInfo:
    """
    从base64字符串保存图片到指定目录

    Args:
        image_base64: base64编码的图片数据
        upload_directory: 上传目录路径

    Returns:
        保存的文件路径
    """
    image_data = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_data))
    width, height = image.size
    temp_file_name = tempfile.mktemp(suffix='.png', prefix='temp_', dir=upload_directory)
    image.save(temp_file_name)
    image.close()
    return ImageInfo(file_name=temp_file_name, width=width, height=height)


def scale_image_dimensions(width: int, height: int, max_size: int = 1664) -> ImageSize:
    """
    将图片的宽度和高度按比例缩放到小于等于指定的最大尺寸

    Args:
        width: 原始宽度
        height: 原始高度
        max_size: 最大尺寸限制，默认为1664

    Returns:
        调整后的(宽度, 高度)元组
    """
    if width > max_size or height > max_size:
        ratio = min(max_size / width, max_size / height)
        width = int(width * ratio)
        height = int(height * ratio)
    return ImageSize(width=width, height=height)