import os, sys, asyncio, base64, io
from PIL import Image
import xai_sdk

client = xai_sdk.Client()


def make_transparent(im, fringe_fight: float = 0.30, defringe_radius: int = 4):
    """Green-screen chroma key with fringe cleanup.
    - fringe_fight: green spill suppression (lower = more aggressive, 0.40 default)
    - defringe_radius: pixels around the transparent edge to desaturate green from (0 to skip)"""
    im = im.convert("RGBA")
    pixels = im.load()
    w, h = im.size

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]

            if g > r + 38 and g > b + 38 and g > 140:
                # Strong background green → fully transparent
                pixels[x, y] = (255, 255, 255, 0)

            elif g > r + 8 and g > b + 8 and g > 85:
                # Transition zone — wider catch than before
                green_bias = g - max(r, b)
                alpha = max(0, int(255 - (green_bias - 8) * 7.5))
                alpha = min(255, alpha)
                g_clean = max(r, int(g * fringe_fight))
                pixels[x, y] = (r, g_clean, b, alpha)

    # Second pass: defringe — suppress green on opaque pixels near transparent ones
    if defringe_radius > 0:
        import numpy as np
        arr = np.array(im)
        alpha_chan = arr[:, :, 3]
        # Mask of fully/mostly transparent pixels
        transparent = alpha_chan < 32
        # Dilate the transparent mask to find border pixels
        border = np.zeros_like(transparent)
        for dy in range(-defringe_radius, defringe_radius + 1):
            for dx in range(-defringe_radius, defringe_radius + 1):
                if dy == 0 and dx == 0:
                    continue
                shifted = np.roll(np.roll(transparent, dy, axis=0), dx, axis=1)
                border |= shifted
        # Border pixels that are themselves opaque — these are the fringe candidates
        fringe_mask = border & (alpha_chan > 128)
        r_ch, g_ch, b_ch = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        # Suppress green toward the average of R and B
        rb_avg = ((r_ch.astype(np.int16) + b_ch.astype(np.int16)) // 2).astype(np.uint8)
        g_suppressed = np.minimum(g_ch, np.maximum(rb_avg, (g_ch * fringe_fight).astype(np.uint8)))
        arr[:, :, 1] = np.where(fringe_mask, g_suppressed, g_ch)
        im = Image.fromarray(arr)

    return im


async def make_fullsize_variations(input_path: str, base_name: str, out_dir: str) -> list:
    with open(input_path, "rb") as f:
        raw = f.read()
    image_data = base64.b64encode(raw).decode("utf-8")
    image_url = f"data:image/png;base64,{image_data}"

    async def generate_one(i):
        def api_call():
            return client.image.sample(
                prompt="Make variations of the charactor on solid bright green background (#00FF00).",
                model="grok-imagine-image",
                image_url=image_url,
                aspect_ratio=None,  # does not work for image edit
                resolution="1k",
                image_format="base64"
            )
        rsp = await asyncio.to_thread(api_call)
        png_bytes = rsp.image

        with Image.open(io.BytesIO(png_bytes)) as im:
            im = make_transparent(im)
            fn = os.path.join(out_dir, f"i{i:02d}-{base_name}-{im.size[0]}x{im.size[1]}.webp")
            im.save(fn, 'WEBP', quality=85, method=6)
            print(f"Saved {fn}")
        return (i, png_bytes)

    tasks = [generate_one(i) for i in range(5)]
    return await asyncio.gather(*tasks)


async def make_avatar(i: int, png_bytes: bytes, base_name: str, out_dir: str):
    image_url = f"data:image/png;base64,{base64.b64encode(png_bytes).decode('utf-8')}"

    def api_call():
        return client.image.sample(
            prompt="Make avatar suitable for small pictures, face much bigger exactly in the center, use a pure solid bright green background (#00FF00).",
            model="grok-imagine-image",
            image_url=image_url,
            aspect_ratio=None,  # does not work for image edit
            resolution="1k",
            image_format="base64"
        )
    rsp = await asyncio.to_thread(api_call)
    avatar_png = rsp.image

    with Image.open(io.BytesIO(avatar_png)) as im:
        im = make_transparent(im)
        fn_intermediate = os.path.join(out_dir, f"i{i:02d}-{base_name}-avatar-{im.size[0]}x{im.size[1]}.webp")
        im.save(fn_intermediate, 'WEBP', quality=85)
        s = min(im.size)
        cx, cy = im.size[0] // 2, im.size[1] // 2
        im_cropped = im.crop((cx - s//2, cy - s//2, cx + s//2, cy + s//2)).resize((256, 256), Image.LANCZOS)
        fn = os.path.join(out_dir, f"i{i:02d}-{base_name}-avatar-{im_cropped.size[0]}x{im_cropped.size[1]}.webp")
        im_cropped.save(fn, 'WEBP', quality=85)
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
