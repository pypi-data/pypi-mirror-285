from pytube import YouTube

def YouTube_Download(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        download_url = stream.url
        size = stream.filesize / (1024 * 1024)  # Convert size to MB
        size = f"{size:.2f}M"  # Format size to 2 decimal places
        title = yt.title
        author = yt.author
        thumbnail_url = yt.thumbnail_url
        return {
            "title": title,
            "author": author,
            "url": download_url,
            "size_MB": size,
            "thumbnail_url": thumbnail_url
        }
    except Exception as e:
        return str(e)
