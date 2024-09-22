import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageStat, ImageDraw, ImageFont
import argparse

# Ruta al archivo Haarcascade
CASCADE_PATH = r'venv\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml'

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


def adjust_bronze(image, bronze_percentage):
    # Adjust to give a more tanned effect by increasing red and green slightly
    r, g, b = image.split()
    r = r.point(lambda i: i + (bronze_percentage / 100) * 255 * 0.1)  # Adjust red channel slightly
    g = g.point(lambda i: i + (bronze_percentage / 100) * 255 * 0.1)  # Adjust green channel slightly
    return Image.merge('RGB', (r, g, b))


def apply_adjustments_on_region(image, region, brightness_adjust, temperature_adjust, bronze_adjust):
    # Crop the region from the image
    region_image = image.crop(region)

    # Apply adjustments on the region
    region_image = adjust_brightness(region_image, brightness_adjust)
    region_image = adjust_temperature(region_image, temperature_adjust)
    region_image = adjust_bronze(region_image, bronze_adjust)

    # Paste the adjusted region back onto the original image
    image.paste(region_image, region)
    return image


def detect_face(image):
    # Convert image to grayscale for face detection
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        print("No face detected.")
        return None

    # Assuming we take the first detected face
    x, y, w, h = faces[0]
    return (x, y, x + w, y + h)


def create_comparison_image(original_image, processed_image, filename, body_adjustments, face_adjustments):
    # Combina las dos imágenes en una sola con etiquetas
    combined_width = original_image.width + processed_image.width
    combined_height = max(original_image.height, processed_image.height)
    combined_image = Image.new('RGB', (combined_width, combined_height))

    combined_image.paste(original_image, (0, 0))
    combined_image.paste(processed_image, (original_image.width, 0))

    draw = ImageDraw.Draw(combined_image)

    # Definir la fuente y tamaño del texto
    font = ImageFont.truetype("arial", 40)  # Puedes ajustar el tamaño de la fuente aquí

    # Etiquetas
    draw.text((10, 10), "Original", fill="white", font=font)
    draw.text((original_image.width + 10, 10), "Procesada", fill="white", font=font)

    # Agregar información sobre los ajustes aplicados
    adjustment_text = (
        f"Cuerpo - Brillo: {body_adjustments['brightness'] * 100:.1f}%, Temp: {body_adjustments['temperature']:.1f}, Bronceado: {body_adjustments['bronze']:.1f}%\n"
        f"Cara - Brillo: {face_adjustments['brightness'] * 100:.1f}%, Temp: {face_adjustments['temperature']:.1f}, Bronceado: {face_adjustments['bronze']:.1f}%"
    )
    draw.text((original_image.width + 10, 60), adjustment_text, fill="white", font=font)

    # Guardar la imagen combinada en la carpeta comparadas
    if not os.path.exists(COMPARED_FOLDER):
        os.makedirs(COMPARED_FOLDER)

    comparison_path = os.path.join(COMPARED_FOLDER, f"compared_{filename}")
    combined_image.save(comparison_path)
    print(f"Saved comparison image as {comparison_path}")


def process_images(body_adjustments, face_adjustments):
    # Crear el directorio para las imágenes procesadas y comparadas si no existen
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)

    if not os.path.exists(COMPARED_FOLDER):
        os.makedirs(COMPARED_FOLDER)

    corrected_image = Image.open(CORRECTED_IMAGE_PATH)
    original_image = Image.open(ORIGINAL_IMAGE_PATH)

    # Cálculo automático de ajustes si no se proporcionan
    auto_brightness_adjust = calculate_brightness_difference(corrected_image, original_image)
    auto_temperature_adjust = calculate_temperature_difference(corrected_image, original_image)
    auto_bronze_adjust = 0  # Podrías definir un ajuste predeterminado para bronceado

    # Aplica valores automáticos si los parámetros no fueron proporcionados
    body_adjustments = {
        'brightness': body_adjustments.get('brightness', auto_brightness_adjust),
        'temperature': body_adjustments.get('temperature', auto_temperature_adjust),
        'bronze': body_adjustments.get('bronze', auto_bronze_adjust)
    }

    face_adjustments = {
        'brightness': face_adjustments.get('brightness', auto_brightness_adjust),
        'temperature': face_adjustments.get('temperature', auto_temperature_adjust),
        'bronze': face_adjustments.get('bronze', auto_bronze_adjust)
    }

    for filename in os.listdir(RESOURCES_FOLDER):
        if filename.lower().endswith(
                ('.png', '.jpg', '.jpeg', '.bmp', '.gif')) and filename != "procesadas" and filename != "comparadas":
            image_path = os.path.join(RESOURCES_FOLDER, filename)
            image = Image.open(image_path)
            print(f"Processing {filename}...")

            # Convert the PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            face_region = detect_face(cv_image)

            if face_region:
                # Apply adjustments on the entire body first
                processed_image = adjust_brightness(image, body_adjustments['brightness'])
                processed_image = adjust_temperature(processed_image, body_adjustments['temperature'])
                processed_image = adjust_bronze(processed_image, body_adjustments['bronze'])

                # Apply specific adjustments on the face
                processed_image = apply_adjustments_on_region(processed_image, face_region,
                                                              face_adjustments['brightness'],
                                                              face_adjustments['temperature'],
                                                              face_adjustments['bronze'])
            else:
                print(f"No face detected in {filename}, applying body adjustments to the entire image.")
                # If no face is detected, apply body adjustments to the entire image
                processed_image = adjust_brightness(image, body_adjustments['brightness'])
                processed_image = adjust_temperature(processed_image, body_adjustments['temperature'])
                processed_image = adjust_bronze(processed_image, body_adjustments['bronze'])

            output_path = os.path.join(PROCESSED_FOLDER, filename)
            processed_image.save(output_path)
            print(f"Saved processed image as {output_path}")

            # Crear y guardar la imagen comparativa
            create_comparison_image(image, processed_image, filename, body_adjustments, face_adjustments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Adjust brightness, temperature, and bronze effect for body and face separately in images.")

    # Parámetros para el cuerpo
    parser.add_argument("--body_brightness", type=float, help="Additional brightness percentage to add to the body.")
    parser.add_argument("--body_temperature", type=float, help="Additional temperature percentage to add to the body.")
    parser.add_argument("--body_bronze", type=float, help="Additional bronze percentage to add to the body.")

    # Parámetros para la cara
    parser.add_argument("--face_brightness", type=float, help="Additional brightness percentage to add to the face.")
    parser.add_argument("--face_temperature", type=float, help="Additional temperature percentage to add to the face.")
    parser.add_argument("--face_bronze", type=float, help="Additional bronze percentage to add to the face.")

    args = parser.parse_args()

    body_adjustments = {
        'brightness': args.body_brightness,
        'temperature': args.body_temperature,
        'bronze': args.body_bronze
    }

    face_adjustments = {
        'brightness': args.face_brightness,
        'temperature': args.face_temperature,
        'bronze': args.face_bronze
    }

    process_images(body_adjustments, face_adjustments)
