---
name: video-processing
description: Video processing reference for yt-dlp, ffmpeg, captions, and publishing
---

## yt-dlp Quick Reference

### Download Best Quality (up to 1080p)
```
yt-dlp -f 'bestvideo[height<=1080]+bestaudio/best[height<=1080]' -o 'output.mp4' "URL"
```

### Extract Subtitles Only
```
yt-dlp --write-auto-sub --sub-lang en --skip-download -o 'subs' "URL"
```

### List Available Formats
```
yt-dlp -F "URL"
```

## ffmpeg Quick Reference

### Extract Clip by Timestamp
```
ffmpeg -i input.mp4 -ss 00:01:30 -to 00:02:15 -c copy clip.mp4
```

### Crop to Vertical (9:16)
```
ffmpeg -i input.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" -c:a copy vertical.mp4
```

### Burn SRT Captions
```
ffmpeg -i input.mp4 -vf "subtitles=captions.srt:force_style='FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,MarginV=40'" output.mp4
```

### Generate Thumbnail
```
ffmpeg -i input.mp4 -ss 00:00:05 -frames:v 1 -q:v 2 thumbnail.jpg
```

### Detect Scene Changes
```
ffmpeg -i input.mp4 -filter:v "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep showinfo
```

### Detect Silence (for segment breaks)
```
ffmpeg -i input.mp4 -af silencedetect=noise=-30dB:d=0.5 -f null - 2>&1 | grep silence
```

## SRT Caption Format
```
1
00:00:01,000 --> 00:00:04,000
First line of caption
eight to twelve words max

2
00:00:04,500 --> 00:00:07,500
Next line of caption
keep under 42 characters
```

## Platform Limits

### Telegram
- Max file size: 50MB
- Supported: MP4, MOV
- Max duration: 60 minutes

### WhatsApp
- Max file size: 16MB
- Supported: MP4
- Max duration: 3 minutes (via API)
- 24-hour messaging window for business API

### YouTube Shorts
- Max duration: 60 seconds
- Aspect ratio: 9:16
- Max resolution: 1080x1920

### TikTok
- Max duration: 10 minutes (recommended: 15-60 seconds)
- Aspect ratio: 9:16
- Max file size: 287.6MB
