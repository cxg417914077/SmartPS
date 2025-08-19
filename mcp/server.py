from fastmcp import FastMCP
from PIL import Image
from io import BytesIO
import os

mcp = FastMCP("ImageTools")


@mcp.tool()
def img_resize(image_path: str, width: int, height: int) -> bytes:
    """
    Resize an image to the specified width and height.
    
    Args:
        image_path (str): The local file path of the input image
        width (int): The target width for the resized image
        height (int): The target height for the resized image
        
    Returns:
        bytes: The resized image data in PNG format as bytes
    """
    # Open the input image from file path
    img = Image.open(image_path)
    
    # Resize the image using LANCZOS resampling algorithm for high quality
    resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Save the resized image to a byte stream in PNG format
    output_stream = BytesIO()
    resized_img.save(output_stream, format='PNG')
    output_stream.seek(0)
    
    # Return the resized image data as bytes
    return output_stream.getvalue()


@mcp.tool()
def img_crop(image_path: str, left: int, upper: int, right: int, lower: int) -> bytes:
    """
    Crop an image to the specified box.
    
    Args:
        image_path (str): The local file path of the input image
        left (int): The x-coordinate of the left edge of the crop box
        upper (int): The y-coordinate of the upper edge of the crop box
        right (int): The x-coordinate of the right edge of the crop box
        lower (int): The y-coordinate of the lower edge of the crop box
    
    Returns:
        bytes: The cropped image data in PNG format as bytes
    """
    # Load the image from file path
    img = Image.open(image_path)
    
    # Crop the image to the specified bounding box
    cropped_img = img.crop((left, upper, right, lower))
    
    # Save the cropped image to a byte stream in PNG format
    output_stream = BytesIO()
    cropped_img.save(output_stream, format='PNG')
    output_stream.seek(0)
    
    # Return the cropped image bytes
    return output_stream.getvalue()


@mcp.tool()
def img_rotate(image_path: str, angle: float) -> bytes:
    """
    Rotate an image by a specified angle and return the rotated image data.
    
    Args:
        image_path (str): The local file path of the input image
        angle (float): The rotation angle in degrees. Positive values indicate 
                      counter-clockwise rotation, negative values indicate clockwise rotation
    
    Returns:
        bytes: The rotated image data in PNG format as bytes
    """
    # Load the image from file path
    img = Image.open(image_path)
    
    # Rotate the image by the specified angle, expand=True ensures the entire 
    # rotated image is visible without cropping
    rotated_img = img.rotate(angle, expand=True)
    
    # Save the rotated image to a byte stream in PNG format
    output_stream = BytesIO()
    rotated_img.save(output_stream, format='PNG')
    output_stream.seek(0)
    
    # Return the image byte data
    return output_stream.getvalue()


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)