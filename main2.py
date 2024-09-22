import os
from PIL import Image, ImageEnhance, ImageStat

# Constantes
RESOURCES_FOLDER = "resources"
PROCESSED_FOLDER = os.path.join(RESOURCES_FOLDER, "procesadas")
CORRECTED_IMAGE_PATH = "131 OK CORREGIDA.jpg"
ORIGINAL_IMAGE_PATH = "Teatro-131.jpg"


def calculate_brightness_difference(corrected_image, original_image):
    corrected_stat = ImageStat.Stat(corrected_image.convert('L'))
    original_stat = ImageStat.Stat(original_image.convert('L'))

    brightness_corrected = corrected_stat.mean[0]
    brightness_original = original_stat.mean[0]

    brightness_adjust = brightness_corrected / brightness_original
    return brightness_adjust


def calculate_temperature_difference(corrected_image, original_image):
    # Simplified color adjustment by comparing average red and blue channel values
    corrected_stat = ImageStat.Stat(corrected_image)
    original_stat = ImageStat.Stat(original_image)

    red_corrected, green_corrected, blue_corrected = corrected_stat.mean[:3]
    red_original, green_original, blue_original = original_stat.mean[:3]

    # Assume that temperature can be approximated by the ratio of red to blue
    red_blue_ratio_corrected = red_corrected / blue_corrected
    red_blue_ratio_original = red_original / blue_original

    temperature_adjust = (
                                     red_blue_ratio_corrected - red_blue_ratio_original) * 128  # Scale the value to get a noticeable change
    return temperature_adjust


def adjust_brightness(image, brightness_value):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(brightness_value)


def adjust_temperature(image, temperature_value):
    # Adjust temperature by modifying red and blue channels
    r, g, b = image.split()
    r = r.point(lambda i: i + temperature_value)
    b = b.point(lambda i: i - temperature_value)
    return Image.merge('RGB', (r, g, b))


def process_images():
    # Crear el directorio para las imágenes procesadas si no existe
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)

    corrected_image = Image.open(CORRECTED_IMAGE_PATH)
    original_image = Image.open(ORIGINAL_IMAGE_PATH)

    brightness_adjust = calculate_brightness_difference(corrected_image, original_image)
    temperature_adjust = calculate_temperature_difference(corrected_image, original_image)

    for filename in os.listdir(RESOURCES_FOLDER):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) and filename != "procesadas":
            image_path = os.path.join(RESOURCES_FOLDER, filename)
            image = Image.open(image_path)
            print(f"Processing {filename}...")
            image = adjust_brightness(image, brightness_adjust)
            image = adjust_temperature(image, temperature_adjust)
            output_path = os.path.join(PROCESSED_FOLDER, filename)
            image.save(output_path)
            print(f"Saved processed image as {output_path}")


if __name__ == "__main__":
    process_images()
