import asyncio, base64, io, logging
from PIL import Image
import xai_sdk

log = logging.getLogger("avatar_imagine")

DEFAULT_MODEL = "grok-imagine-image"


def _process_image(png_bytes: bytes, target_size: tuple[int, int]) -> tuple[bytes, tuple[int, int]]:
    with Image.open(io.BytesIO(png_bytes)) as im:
        log.info("raw image from API: %dx%d", im.size[0], im.size[1])
        im = make_transparent(im)
        if im.size != target_size:
            im = im.resize(target_size, Image.LANCZOS)
        out = io.BytesIO()
        im.save(out, "WEBP", quality=85, method=6)
        data = out.getvalue()
        log.info("processed image: %dx%d, %d bytes webp", im.size[0], im.size[1], len(data))
        return data, im.size


def _center_crop_square(png_bytes: bytes) -> bytes:
    with Image.open(io.BytesIO(png_bytes)) as im:
        w, h = im.size
        s = min(w, h)
        left = (w - s) // 2
        top = (h - s) // 2
        im = im.crop((left, top, left + s, top + s))
        out = io.BytesIO()
        im.save(out, "PNG")
        return out.getvalue()


def make_transparent(im, fringe_fight: float = 0.30, defringe_radius: int = 4):
    im = im.convert("RGBA")
    pixels = im.load()
    w, h = im.size

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if g > r + 38 and g > b + 38 and g > 140:
                pixels[x, y] = (255, 255, 255, 0)
            elif g > r + 8 and g > b + 8 and g > 85:
                green_bias = g - max(r, b)
                alpha = max(0, int(255 - (green_bias - 8) * 7.5))
                alpha = min(255, alpha)
                g_clean = max(r, int(g * fringe_fight))
                pixels[x, y] = (r, g_clean, b, alpha)

    if defringe_radius > 0:
        import numpy as np
        arr = np.array(im)
        alpha_chan = arr[:, :, 3]
        transparent = alpha_chan < 32
        border = np.zeros_like(transparent)
        for dy in range(-defringe_radius, defringe_radius + 1):
            for dx in range(-defringe_radius, defringe_radius + 1):
                if dy == 0 and dx == 0:
                    continue
                shifted = np.roll(np.roll(transparent, dy, axis=0), dx, axis=1)
                border |= shifted
        fringe_mask = border & (alpha_chan > 128)
        r_ch, g_ch, b_ch = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        rb_avg = ((r_ch.astype(np.int16) + b_ch.astype(np.int16)) // 2).astype(np.uint8)
        g_suppressed = np.minimum(g_ch, np.maximum(rb_avg, (g_ch * fringe_fight).astype(np.uint8)))
        arr[:, :, 1] = np.where(fringe_mask, g_suppressed, g_ch)
        im = Image.fromarray(arr)

    return im


async def _sample_image(
        xclient,
        *,
        prompt: str,
        image_urls: list[str],
        aspect_ratio: str,
        resolution: str
) -> bytes:
    kwargs = {
        "prompt": prompt,
        "model": DEFAULT_MODEL,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "image_format": "base64",
    }
    image_urls = image_urls[:5]
    if len(image_urls) == 1:
        kwargs["image_url"] = image_urls[0]
    elif image_urls:
        kwargs["image_urls"] = image_urls

    log.info("API call: model=%s aspect_ratio=%s resolution=%s refs=%d prompt=%.80s",
             DEFAULT_MODEL, aspect_ratio, resolution, len(image_urls), prompt)

    def _api_call():
        return xclient.image.sample(**kwargs)

    rsp = await asyncio.to_thread(_api_call)
    log.info("API response: %d bytes", len(rsp.image))
    return rsp.image


async def generate_avatar_assets_from_idea(
        *,
        description: str,
        fullsize_refs: list[bytes],
        avatar_refs: list[bytes],
        api_key: str,
) -> list[dict]:
    def _image_to_data_url(image_bytes: bytes, mime: str = "image/png") -> str:
        return f"data:{mime};base64,{base64.b64encode(image_bytes).decode('utf-8')}"

    if not description or not description.strip():
        raise ValueError("description is required")

    xclient = xai_sdk.Client(api_key)
    fullsize_ref_urls = [_image_to_data_url(x) for x in fullsize_refs[:5]]
    avatar_ref_urls = [_image_to_data_url(x) for x in avatar_refs[:5]]

    log.info("fullsize_refs: %d images (%s)", len(fullsize_refs), ", ".join(f"{len(x)}b" for x in fullsize_refs[:5]))
    log.info("avatar_refs: %d images (%s)", len(avatar_refs), ", ".join(f"{len(x)}b" for x in avatar_refs[:5]))

    fullsize_prompt = (
        f"{description.strip()}. "
        f"Use given template images and follow the same style. "
        "Create a full-size variation of the character on pure solid bright green background (#00FF00)."
    )
    avatar_prompt = (
        f"{description.strip()}. "
        "Make avatar suitable for small pictures, face much bigger exactly in the center. Use given template images and follow the same style. "
        "Keep the same character as in the last picture, use a pure solid bright green background (#00FF00)."
    )

    log.info(f"generating fullsize (2:3)...: {fullsize_prompt}")
    fullsize_png = await _sample_image(xclient, prompt=fullsize_prompt, image_urls=fullsize_ref_urls, aspect_ratio="2:3", resolution="2k")
    fullsize_webp, fullsize_size = _process_image(fullsize_png, (1024, 1536))

    fullsize_square_png = _center_crop_square(fullsize_png)
    avatar_input_urls = avatar_ref_urls + [_image_to_data_url(fullsize_square_png)]
    log.info("generating avatar (1:1) with %d refs (%d from bank + 1 cropped fullsize)...: %s", len(avatar_input_urls), len(avatar_ref_urls), avatar_prompt)
    avatar_png = await _sample_image(xclient, prompt=avatar_prompt, image_urls=avatar_input_urls[-5:], aspect_ratio="1:1", resolution="1k")
    avatar_webp_256, avatar_size_256 = _process_image(avatar_png, (256, 256))

    return [{
        "index": 0,
        "fullsize_webp": fullsize_webp,
        "fullsize_size": fullsize_size,
        "avatar_webp_256": avatar_webp_256,
        "avatar_size_256": avatar_size_256,
    }]
