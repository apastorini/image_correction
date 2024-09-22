import os
from PIL import Image, ImageEnhance, ImageStat, ImageDraw, ImageFont
import argparse

# Constantes
RESOURCES_FOLDER = "resources"
PROCESSED_FOLDER = os.path.join(RESOURCES_FOLDER, "procesadas")
COMPARED_FOLDER = os.path.join(RESOURCES_FOLDER, "comparadas")
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


def create_comparison_image(original_image, processed_image, filename):
    # Combina las dos imágenes en una sola con etiquetas
    combined_width = original_image.width + processed_image.width
    combined_height = max(original_image.height, processed_image.height)
    combined_image = Image.new('RGB', (combined_width, combined_height))

    combined_image.paste(original_image, (0, 0))
    combined_image.paste(processed_image, (original_image.width, 0))

    draw = ImageDraw.Draw(combined_image)
    font = ImageFont.load_default()

    # Etiquetas
    draw.text((10, 10), "Original", fill="white", font=font)
    draw.text((original_image.width + 10, 10), "Procesada", fill="white", font=font)

    # Guardar la imagen combinada en la carpeta comparadas
    if not os.path.exists(COMPARED_FOLDER):
        os.makedirs(COMPARED_FOLDER)

    comparison_path = os.path.join(COMPARED_FOLDER, f"compared_{filename}")
    combined_image.save(comparison_path)
    print(f"Saved comparison image as {comparison_path}")


def process_images(additional_temperature_percentage, additional_brightness_percentage):
    # Crear el directorio para las imágenes procesadas y comparadas si no existen
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)

    if not os.path.exists(COMPARED_FOLDER):
        os.makedirs(COMPARED_FOLDER)

    corrected_image = Image.open(CORRECTED_IMAGE_PATH)
    original_image = Image.open(ORIGINAL_IMAGE_PATH)

    brightness_adjust = calculate_brightness_difference(corrected_image, original_image)
    base_temperature_adjust = calculate_temperature_difference(corrected_image, original_image)

    # Aplicar el porcentaje adicional de temperatura y brillo
    additional_temperature_adjust = base_temperature_adjust * (additional_temperature_percentage / 100)
    total_temperature_adjust = base_temperature_adjust + additional_temperature_adjust

    additional_brightness_adjust = brightness_adjust * (additional_brightness_percentage / 100)
    total_brightness_adjust = brightness_adjust + additional_brightness_adjust

    for filename in os.listdir(RESOURCES_FOLDER):
        if filename.lower().endswith(
                ('.png', '.jpg', '.jpeg', '.bmp', '.gif')) and filename != "procesadas" and filename != "comparadas":
            image_path = os.path.join(RESOURCES_FOLDER, filename)
            image = Image.open(image_path)
            print(f"Processing {filename}...")
            processed_image = adjust_brightness(image, total_brightness_adjust)
            processed_image = adjust_temperature(processed_image, total_temperature_adjust)
            output_path = os.path.join(PROCESSED_FOLDER, filename)
            processed_image.save(output_path)
            print(f"Saved processed image as {output_path}")

            # Crear y guardar la imagen comparativa
            create_comparison_image(image, processed_image, filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adjust brightness and temperature of images in a folder.")
    parser.add_argument("--additional_temperature", type=float, default=0,
                        help="Additional temperature percentage to add (default is 0).")
    parser.add_argument("--additional_brightness", type=float, default=0,
                        help="Additional brightness percentage to add (default is 0).")

    args = parser.parse_args()

    process_images(args.additional_temperature, args.additional_brightness)
