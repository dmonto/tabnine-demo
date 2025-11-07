
# Standard library imports
import datetime
import logging
import os
from io import BytesIO

# Third-party imports
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# --- Logger Configuration ---
# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set the minimum level for the logger

# Create a file handler to log messages to a file
# This will capture all logs from INFO level upwards
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)

# Create a console handler to show only critical errors on the screen
# This will show only ERROR and CRITICAL messages
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
# Avoid adding handlers if they already exist (e.g., in interactive sessions)
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# --- Configuration ---
# Load environment variables from a .env file
load_dotenv()

# Configure the Gemini API key from environment variables
s_api_key = os.environ.get("GOOGLE_API_KEY")
if not s_api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")
genai.configure(api_key=s_api_key)

# --- Constants ---
S_MODEL_NAME = "gemini-2.5-flash-image-preview" # Using a standard and versatile model
S_OUTPUT_DIR = "generated_images"

def add_watermark(image, text, font_path="arial.ttf", font_size_ratio=0.05, opacity=128):
    """
    Añade una marca de agua de texto a una imagen.

    Args:
        image (PIL.Image.Image): La imagen a la que se añadirá la marca de agua.
        text (str): El texto de la marca de agua.
        font_path (str): La ruta a la fuente TrueType.
        font_size_ratio (float): El tamaño de la fuente como una proporción del ancho de la imagen.
        opacity (int): La opacidad de la marca de agua (0-255).

    Returns:
        PIL.Image.Image: La imagen con la marca de agua.
    """
    # Crea una copia de la imagen para dibujar sobre ella
    watermark_image = image.copy().convert("RGBA")
    # Crea una capa transparente para el texto
    text_layer = Image.new("RGBA", watermark_image.size, (255, 255, 255, 0))

    # Carga la fuente
    try:
        font_size = int(watermark_image.width * font_size_ratio)
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Fuente no encontrada en {font_path}. Usando fuente por defecto.")
        font = ImageFont.load_default()

    # Crea el objeto de dibujo
    draw = ImageDraw.Draw(text_layer)

    # Calcula la posición del texto (esquina inferior derecha)
    _, _, text_width, text_height = draw.textbbox((0, 0), text, font=font)
    margin = int(watermark_image.width * 0.02)
    x = watermark_image.width - text_width - margin
    y = watermark_image.height - text_height - margin

    # Dibuja el texto con la opacidad deseada
    draw.text((x, y), text, font=font, fill=(255, 255, 255, opacity))

    # Combina la capa de texto con la imagen original
    return Image.alpha_composite(watermark_image, text_layer).convert("RGB")

def generate_image(s_prompt, l_image_paths):
    """
    Generates an image using the Gemini API based on a prompt and input images.

    Args:
        s_prompt (str): The text prompt for image generation.
        l_image_paths (list): A list of paths to input images.

    Returns:
        str: The file path of the generated image, or an error message.
    """
    # Validate parameters to ensure they meet requirements
    assert isinstance(s_prompt, str) and s_prompt, "Prompt must be a non-empty string."
    assert isinstance(l_image_paths, list), "Image paths must be a list."

    try:
        logger.info("Attempting to generate image with prompt: '%s'", s_prompt)
        # Initialize the generative model
        model = genai.GenerativeModel(S_MODEL_NAME)

        # Prepare the images and the prompt to be sent to the model
        l_images = [Image.open(path) for path in l_image_paths]
        l_contents = [s_prompt, *l_images]
        
        # Call the API to generate content
        response = model.generate_content(contents=l_contents)

        # Ensure the output directory exists
        os.makedirs(S_OUTPUT_DIR, exist_ok=True)

        # Find the first image part in the API response
        image_part = None
        for part in response.parts:
            if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith("image/"):
                image_part = part.inline_data
                break

        # If an image is found, save it to a file
        if image_part:
            # Convert image data to bytes and open with Pillow
            img_bytes = image_part.data
            img = Image.open(BytesIO(img_bytes))
            
            # Add watermark to the generated image
            img_with_watermark = add_watermark(img, "Curso Tabnine")

            # Create a unique filename using a timestamp
            s_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            s_output_path = os.path.join(S_OUTPUT_DIR, f"generated_{s_timestamp}.png")
            
            # Save the image and return its path
            img_with_watermark.save(s_output_path, "PNG")
            logger.info("Successfully generated and saved image to %s", s_output_path)
            return s_output_path
        else:
            # Handle cases where the API did not return an image
            logger.warning("API response did not contain an image. Full response: %s", response.text)
            return "Error: No image data received from API."

    except Exception as e:
        # Catch and log any exceptions during the API call or image processing
        logger.critical("An error occurred during Gemini API call: %s", e, exc_info=True)
        return f"Error: {e}"
