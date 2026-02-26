import os
import asyncio
import base64
import openai
import argparse
from PIL import Image


client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def process_file(input_file: str, input_dir: str):
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    input_path = os.path.join(input_dir, input_file)

    prompt = "Make avatar suitable for small pictures, face much bigger with transparent background."
    print(f"Processing {input_file}...")

    N = 5
    rsp = await client.images.edit(
        model="gpt-image-1",
        image=open(input_path, "rb"),
        prompt=prompt,
        n=N,
        size="1024x1024",
    )

    for i in range(N):
        # Save original PNG
        output_file = os.path.join(input_dir, f"avatar-{base_name}-{i}-1024x1024.png")
        with open(output_file, "wb") as f:
            f.write(base64.b64decode(rsp.data[i].b64_json))
        print(f"Saved {output_file}")

        # Create 256x256 WebP version
        with Image.open(output_file) as im:
            im_resized = im.resize((256, 256), Image.LANCZOS)
            webp_file = os.path.join(input_dir, f"avatar-{base_name}-{i}-256x256.webp")
            im_resized.save(webp_file, 'WEBP', quality=85)
            print(f"Saved {webp_file}")


async def main():
    parser = argparse.ArgumentParser(description="Generate avatars from PNG images using OpenAI")
    parser.add_argument("dir", help="Directory containing PNG files to process")
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"Error: {args.dir} is not a valid directory")
        exit(1)

    png_files = [f for f in os.listdir(args.dir) if (f.endswith('.png') or f.endswith('.webp')) and not f.startswith('avatar-')]
    if not png_files:
        print(f"No PNG/WEBP files found in {args.dir}")
        exit(1)

    print(f"Found {len(png_files)} PNG/WEBP files to process")

    tasks = [process_file(png_file, args.dir) for png_file in png_files]
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
