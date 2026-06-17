import sys
import subprocess
import os
from yt_dlp import YoutubeDL

def check_ffmpeg():
    """检查 ffmpeg 是否可用"""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def download_tencent_video(url, output_path='./downloads', quality='best'):
    """
    使用 yt-dlp 下载腾讯视频
    :param url: 腾讯视频播放页 URL，例如 https://v.qq.com/x/cover/xxx/xxx.html
    :param output_path: 保存目录
    :param quality: 画质，可选 'best', '1080p', '720p', '480p'
    """
    if not check_ffmpeg():
        print("⚠️ 未找到 ffmpeg，将无法合并音视频。请先安装 ffmpeg 并加入 PATH。")
        print("   下载地址：https://ffmpeg.org/download.html")
        sys.exit(1)

    # yt-dlp 配置
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # 保存文件名模板
        'quiet': False,                                 # 打印下载信息
        'no_warnings': False,
        'ignoreerrors': True,
        'merge_output_format': 'mp4',                   # 合并为 mp4
        'retries': 10,                                  # 重试次数
        'fragment_retries': 10,
    }

    # 根据画质设置格式选择
    if quality == 'best':
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
    elif quality == '1080p':
        ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
    elif quality == '720p':
        ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
    elif quality == '480p':
        ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
    else:
        ydl_opts['format'] = 'best'

    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"开始下载: {url}")
            ydl.download([url])
        print("✅ 下载完成！")
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 示例 URL（请替换为你需要下载的视频链接）
    video_url = "https://v.qq.com/x/cover/mzc00200aaogpgh/g4102dvts3z.html"
    
    # 可选：从命令行参数获取 URL
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
    
    # 下载到当前目录下的 downloads 文件夹
    os.makedirs("downloads", exist_ok=True)
    download_tencent_video(video_url, output_path="downloads", quality="best")