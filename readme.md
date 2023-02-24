# Video extension converter

Convert any video extension in directory 

## Installation
```bash
git clone https://github.com/Mateodioev/video-extension-converter.git
cd video-extension-converter
```

```bash
pip install ffmpeg-python colorama
```

## Execute

```bash
python video_convert.py --help
```

### Arguments

- `-i ` Video extension source. Default ts
- `-o` Video extension target. Default mp4

### Execute as command

#### Linux:

Make file executable
```bash
chmod +x video_convert.py
```

Create a simbolic link in a directory that is include in your path, like `/usr/local/bin`
```bash
sudo ln -s video_convert.py /usr/local/bin/video_convert
```
Restart your shell and execute the command
```bash
video_convert -h
```