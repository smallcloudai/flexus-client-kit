import os, asyncio, base64, openai, argparse

client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_PROMPTS = [
"Generate image of a stern mustached detective in a beige trench coat and matching fedora, standing with hands on his coat in a serious pose, wearing glasses and dark shoes, in cartoon 3D style, transparent background."
]


async def make_picture(i: int, prompts: list, outdir: str):
    snake_case = prompts[i].lower().replace(" ", "_").replace("-", "_")[:30]
    fn = f"{outdir}/{i:03d}-{snake_case}-cartoon.png"
    if os.path.exists(fn):
        return
    rsp = await client.images.generate(
        model="gpt-image-1",
        prompt=prompts[i],
        n=1,
        size="1024x1536",
    )
    img = base64.b64decode(rsp.data[0].b64_json)
    with open(fn, "wb") as f:
        f.write(img)
    cmd = "file " + fn   # "file" is a unix command that prints what kind of file that is
    os.system(cmd)


async def main():
    parser = argparse.ArgumentParser(description="Generate images using OpenAI DALL-E")
    parser.add_argument("--prompts-file", "-f", type=str, help="File containing prompts (one per line)")
    parser.add_argument("--outdir", "-o", default="_new_bot_pics", help="Output directory for generated images")
    parser.add_argument("--batch-size", "-b", type=int, default=10, help="Number of images to generate in parallel (default: 10)")

    args = parser.parse_args()
    if args.prompts_file:
        with open(args.prompts_file, 'r') as f:
            image_prompts = [line.strip() for line in f if line.strip()]
    else:
        image_prompts = DEFAULT_PROMPTS

    npics = len(image_prompts)
    os.makedirs(args.outdir, exist_ok=True)

    BATCH_SIZE = 10
    for start_idx in range(0, npics, BATCH_SIZE):
        end_idx = min(start_idx + BATCH_SIZE, npics)
        print(f"Batch {start_idx}:{end_idx}...")
        await asyncio.gather(*(make_picture(i, image_prompts, args.outdir) for i in range(start_idx, end_idx)), return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
