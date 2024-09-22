import os
from PIL import Image, ImageEnhance
import argparse

def adjust_brightness(image, brightness_value):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(brightness_value)

def adjust_temperature(image, temperature_value):
    # Simulación simple de ajuste de temperatura.
    # Ajustar el color rojo y azul de la imagen para simular el cambio de temperatura.
    r, g, b = image.split()
    r = r.point(lambda i: i + temperature_value)
    b = b.point(lambda i: i - temperature_value)
    return Image.merge('RGB', (r, g, b))

def process_images(folder_path, brightness_adjust, temperature_adjust):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_path = os.path.join(folder_path, filename)
            image = Image.open(image_path)
            print(f"Processing {filename}...")
            image = adjust_brightness(image, brightness_adjust)
            image = adjust_temperature(image, temperature_adjust)
            output_path = os.path.join(folder_path, f"processed_{filename}")
            image.save(output_path)
            print(f"Saved processed image as {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adjust brightness and temperature of images in a folder.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing images.")
    parser.add_argument("--brightness", type=float, default=0.8, help="Brightness adjustment factor (default is -20%).")
    parser.add_argument("--temperature", type=int, default=50, help="Temperature adjustment value (default is 50).")

    args = parser.parse_args()

    brightness_adjust = args.brightness
    temperature_adjust = args.temperature

    process_images(args.folder_path, brightness_adjust, temperature_adjust)

