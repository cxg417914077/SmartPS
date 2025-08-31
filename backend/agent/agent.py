from pydantic_ai import Agent
from pydantic import BaseModel
from PIL import Image
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


class Output(BaseModel):
    image_path: str

ollama_model = OpenAIChatModel(
    # model_name='modelscope.cn/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF:UD-TQ1_0',
    model_name='modelscope.cn/unsloth/gpt-oss-20b-GGUF:Q2_K',
    provider=OpenAIProvider(base_url='http://127.0.0.1:11434/v1')
)


agent = Agent(
    ollama_model,
    system_prompt=(
    """
    你是一个高度智能的AI助手，你的任务是基于用户问题，严谨地、一步一步地解决问题。
    """,
    )
)


@agent.tool_plain
def img_resize(image_path: str, width: int, height: int) -> str:
    """
    Resize an image to the specified width and height.

    Args:
        image_path (str): The local file path of the input image
        width (int): The target width for the resized image
        height (int): The target height for the resized image

    Returns:
        str: The resized image path
    """
    # Open the input image from file path
    img = Image.open(image_path)

    # Resize the image using LANCZOS resampling algorithm for high quality
    resized_img = img.resize((width, height), Image.Resampling.LANCZOS)

    # Save the resized image to new file path
    resized_img.save(image_path)
    img.close()
    resized_img.close()
    return image_path


@agent.tool_plain
def img_crop(image_path: str, left: int, upper: int, right: int, lower: int) -> str:
    """
    Crop an image to the specified box.

    Args:
        image_path (str): The local file path of the input image
        left (int): The x-coordinate of the left edge of the crop box
        upper (int): The y-coordinate of the upper edge of the crop box
        right (int): The x-coordinate of the right edge of the crop box
        lower (int): The y-coordinate of the lower edge of the crop box

    Returns:
        str: The resized image path
    """
    # Load the image from file path
    img = Image.open(image_path)

    # Crop the image to the specified bounding box
    cropped_img = img.crop((left, upper, right, lower))

    cropped_img.save(image_path)
    img.close()
    cropped_img.close()
    return image_path


@agent.tool_plain
def img_rotate(image_path: str, angle: float) -> str:
    """
    Rotate an image by a specified angle and return the rotated image data.

    Args:
        image_path (str): The local file path of the input image
        angle (float): The rotation angle in degrees. Positive values indicate
                      counter-clockwise rotation, negative values indicate clockwise rotation

    Returns:
        str: The resized image path
    """
    # Load the image from file path
    img = Image.open(image_path)

    # Rotate the image by the specified angle, expand=True ensures the entire
    # rotated image is visible without cropping
    rotated_img = img.rotate(angle, expand=True)

    rotated_img.save(image_path)
    img.close()
    rotated_img.close()
    return image_path


if __name__ == '__main__':
    result_sync = agent.run_sync(
        '从 /Users/chengxuguang/code/SmartPS/123.png 这张图的中间扣一个500x500的图',
    )
    print(result_sync.output)