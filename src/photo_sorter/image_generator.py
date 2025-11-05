
from dotenv import load_dotenv
import os
import datetime
from io import BytesIO
from PIL import Image
import google.generativeai as genai

# Load environment variables from a .env file
load_dotenv()

# Configure the Gemini API key
str_api_key = os.environ.get("GOOGLE_API_KEY")
if not str_api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")
genai.configure(api_key=str_api_key)


def generate_image(prompt, image_paths):
    """Generates an image using the Gemini API based on a prompt and input images.

    Args:
        prompt (str): The text prompt for image generation.
        image_paths (list): A list of paths to input images.

    Returns:
        str: The file path of the generated image, or an error message.
    """
#    try:
    model = genai.GenerativeModel("gemini-2.5-flash-image")
    images = [Image.open(image_path) for image_path in image_paths]
    contents = [prompt, *images]
    
    response = model.generate_content(
        contents=contents,
    )
    output_dir = "generated_images"
    os.makedirs(output_dir, exist_ok=True)

    # Assuming the API returns image data in the first part
    # Find the image part in the response
    # Save the image to the output directory and return the file path
    # Note: This assumes the API returns image data in the first part of the response
    image_part = None
    for part in response.parts:
        if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith("image/"):
            image_part = part.inline_data
            break

    if image_part:
        img_bytes = image_part.data
        img = Image.open(BytesIO(img_bytes))
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"generated_{timestamp}.png")
        
        img.save(output_path, "PNG")
        return output_path
    else:
        return "Error: No image data received from API."
'''
    except Exception as e:
        print(f"An error occurred during Gemini API call: {e}")
        return f"Error: {e}"
'''