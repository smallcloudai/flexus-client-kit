import os, sys, asyncio, base64, io, json
from pathlib import Path
from PIL import Image
try:
    import xai_sdk
except ImportError:
    xai_sdk = None

_default_client = None


DEFAULT_MODEL = "grok-imagine-image"
DEFAULT_RESOLUTION = "1k"
_STYLE_BANK_MANIFEST = Path(__file__).parent / "bot_pictures" / "style_bank" / "manifest.json"


def create_xai_client(api_key: str | None = None):
    if xai_sdk is None:
        raise RuntimeError("xai-sdk package is required")
    if api_key:
        return xai_sdk.Client(api_key=api_key)
    return xai_sdk.Client()


def _get_default_client():
    global _default_client
    if _default_client is None:
        _default_client = create_xai_client()
    return _default_client


def _image_to_data_url(image_bytes: bytes, mime: str = "image/png") -> str:
    return f"data:{mime};base64,{base64.b64encode(image_bytes).decode('utf-8')}"


def style_bank_manifest() -> list[dict]:
    if not _STYLE_BANK_MANIFEST.exists():
        return []
    with open(_STYLE_BANK_MANIFEST, "r", encoding="utf-8") as f:
        rows = json.load(f)
    if not isinstance(rows, list):
        raise ValueError(f"Bad style-bank manifest: {_STYLE_BANK_MANIFEST}")
    return rows


def default_style_bank_files() -> dict[str, bytes]:
    root = Path(__file__).parent
    files = {}
    for row in style_bank_manifest():
        rel = str(row.get("source_path", "")).strip()
        target_name = str(row.get("target_name", "")).strip()
        if not rel or not target_name:
            continue
        path = root / rel
        if not path.exists():
            continue
        files[target_name] = path.read_bytes()
    return files


async def _sample_image(
    xclient,
    *,
    prompt: str,
    image_urls: list[str],
    resolution: str = DEFAULT_RESOLUTION,
) -> bytes:
    kwargs = {
        "prompt": prompt,
        "model": DEFAULT_MODEL,
        "aspect_ratio": None,
        "resolution": resolution,
        "image_format": "base64",
    }
    image_urls = image_urls[:5]
    if len(image_urls) == 1:
        kwargs["image_url"] = image_urls[0]
    else:
        kwargs["image_urls"] = image_urls

    def _api_call():
        return xclient.image.sample(**kwargs)

    rsp = await asyncio.to_thread(_api_call)
    return rsp.image


def _save_fullsize_webp_bytes(png_bytes: bytes, quality: int = 85) -> tuple[bytes, tuple[int, int]]:
    out = io.BytesIO()
    with Image.open(io.BytesIO(png_bytes)) as im:
        im = make_transparent(im)
        im.save(out, "WEBP", quality=quality, method=6)
        size = im.size
    return out.getvalue(), size


def _save_avatar_256_webp_bytes(avatar_png_bytes: bytes, quality: int = 85) -> tuple[bytes, tuple[int, int]]:
    out = io.BytesIO()
    with Image.open(io.BytesIO(avatar_png_bytes)) as im:
        im = make_transparent(im)
        s = min(im.size)
        cx, cy = im.size[0] // 2, im.size[1] // 2
        im = im.crop((cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2)).resize((256, 256), Image.LANCZOS)
        im.save(out, "WEBP", quality=quality, method=6)
        size = im.size
    return out.getvalue(), size


async def generate_avatar_assets_from_idea(
    *,
    input_image_bytes: bytes,
    description: str,
    style_reference_images: list[bytes],
    api_key: str,
    count: int = 5,
) -> list[dict]:
    if not description or not description.strip():
        raise ValueError("description is required")
    if count < 1 or count > 10:
        raise ValueError("count must be in range [1, 10]")

    xclient = create_xai_client(api_key)
    refs = [_image_to_data_url(input_image_bytes)]
    refs += [_image_to_data_url(x) for x in style_reference_images]
    refs = refs[:5]

    fullsize_prompt = (
        f"{description.strip()}. "
        "Create a full-size variation of the character on pure solid bright green background (#00FF00)."
    )
    avatar_prompt = (
        f"{description.strip()}. "
        "Make avatar suitable for small pictures, face much bigger exactly in the center, "
        "use a pure solid bright green background (#00FF00)."
    )

    async def _one(i: int):
        fullsize_png = await _sample_image(xclient, prompt=fullsize_prompt, image_urls=refs)
        fullsize_webp, fullsize_size = _save_fullsize_webp_bytes(fullsize_png)

        avatar_png = await _sample_image(
            xclient,
            prompt=avatar_prompt,
            image_urls=[_image_to_data_url(fullsize_png)],
        )
        avatar_webp_256, avatar_size_256 = _save_avatar_256_webp_bytes(avatar_png)
        return {
            "index": i,
            "fullsize_webp": fullsize_webp,
            "fullsize_size": fullsize_size,
            "avatar_webp_256": avatar_webp_256,
            "avatar_size_256": avatar_size_256,
        }

    return await asyncio.gather(*[_one(i) for i in range(count)])


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
            return _get_default_client().image.sample(
                prompt="Make variations of the charactor on solid bright green background (#00FF00).",
                model=DEFAULT_MODEL,
                image_url=image_url,
                aspect_ratio=None,  # does not work for image edit
                resolution=DEFAULT_RESOLUTION,
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
        return _get_default_client().image.sample(
            prompt="Make avatar suitable for small pictures, face much bigger exactly in the center, use a pure solid bright green background (#00FF00).",
            model=DEFAULT_MODEL,
            image_url=image_url,
            aspect_ratio=None,  # does not work for image edit
            resolution=DEFAULT_RESOLUTION,
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
