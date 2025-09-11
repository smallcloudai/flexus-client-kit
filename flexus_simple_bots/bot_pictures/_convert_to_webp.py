import os
import argparse
from PIL import Image


def convert_to_webp(input_dir):
    png_files = [f for f in os.listdir(input_dir) if f.endswith('.png')]

    for filename in png_files:
        print(f"Processing {filename}...")

        filepath = os.path.join(input_dir, filename)
        with Image.open(filepath) as im:
            webp_filename = os.path.join(input_dir, filename.replace('.png', '.webp'))
            im.save(
                webp_filename,
                'WEBP',
                quality=45,
                method=6,
                lossless=False,
                )
            print(f"Saved {webp_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PNG files to WebP format")
    parser.add_argument("dir", help="Directory containing PNG files to convert")

    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"Error: {args.dir} is not a valid directory")
        exit(1)

    convert_to_webp(args.dir)
