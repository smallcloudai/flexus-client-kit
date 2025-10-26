import os, sys, asyncio, base64, openai, io
from PIL import Image

client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def make_fullsize_variations(input_path: str, base_name: str, out_dir: str) -> list:
    rsp = await client.images.edit(
        model="gpt-image-1",
        image=open(input_path, "rb"),
        prompt="Improve quality, transparent background.",
        n=5,
        size="1024x1536",
    )

    results = []
    for i in range(5):
        png_bytes = base64.b64decode(rsp.data[i].b64_json)
        fn = os.path.join(out_dir, f"gen{i:02d}-{base_name}-1024x1536.webp")
        with Image.open(io.BytesIO(png_bytes)) as im:
            im.save(fn, 'WEBP', quality=45, method=6)
        print(f"Saved {fn}")
        results.append((i, png_bytes))

    return results


async def make_avatar(i: int, png_bytes: bytes, base_name: str, out_dir: str):
    bio = io.BytesIO(png_bytes)
    bio.name = "image.png"
    rsp = await client.images.edit(
        model="gpt-image-1",
        image=bio,
        prompt="Make avatar suitable for small pictures, face much bigger with transparent background.",
        n=1,
        size="1024x1024",
    )

    avatar_png = base64.b64decode(rsp.data[0].b64_json)
    fn = os.path.join(out_dir, f"gen{i:02d}-{base_name}-256x256.webp")
    with Image.open(io.BytesIO(avatar_png)) as im:
        im_resized = im.resize((256, 256), Image.LANCZOS)
        im_resized.save(fn, 'WEBP', quality=85)
    print(f"Saved {fn}")


async def main():
    if len(sys.argv) != 2:
        print("Usage: %s path/to/image.png" % sys.argv[0])
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found")
        sys.exit(1)

    out_dir = os.path.dirname(input_path) or "."
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    print(f"Generating 5 full-size variations...")
    fullsize_results = await make_fullsize_variations(input_path, base_name, out_dir)

    print(f"Generating avatars...")
    await asyncio.gather(*(make_avatar(i, png_bytes, base_name, out_dir) for i, png_bytes in fullsize_results))

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
