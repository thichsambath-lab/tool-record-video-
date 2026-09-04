import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import os
import shutil
import requests
import threading
import re

# Default downloads directory
DEFAULT_DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "Media Downloader")

def is_ffmpeg_installed():
    return shutil.which("ffmpeg") is not None

class MediaDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎥 Media Downloader")
        self.root.geometry("600x420")
        self.root.resizable(False, False)
        
        # Styling
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        
        # Main Frame
        main_frame = ttk.Frame(root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎥 Media Downloader", font=("Helvetica", 18, "bold"))
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ttk.Label(main_frame, text="Download your favorite videos and audio from YouTube, TikTok, Facebook, and Instagram.")
        subtitle_label.pack(pady=(0, 20))
        
        if not is_ffmpeg_installed():
            warning_label = ttk.Label(main_frame, text="⚠️ `ffmpeg` is not found. Audio conversion to MP3 requires ffmpeg.", foreground="red")
            warning_label.pack(pady=(0, 10))
            
        # URL Input
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(url_frame, text="🔗 URL:").pack(side=tk.LEFT, padx=(0, 10))
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=50)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Save Directory Selection
        save_frame = ttk.Frame(main_frame)
        save_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(save_frame, text="📁 Save To:").pack(side=tk.LEFT, padx=(0, 10))
        self.save_dir_var = tk.StringVar(value=DEFAULT_DOWNLOADS_DIR)
        self.save_entry = ttk.Entry(save_frame, textvariable=self.save_dir_var, width=40)
        self.save_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.browse_btn = ttk.Button(save_frame, text="Browse", command=self.browse_folder)
        self.browse_btn.pack(side=tk.LEFT)
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Download Options", padding="10 10 10 10")
        options_frame.pack(fill=tk.X, pady=10)
        
        self.format_var = tk.StringVar(value="Video (MP4)")
        ttk.Radiobutton(options_frame, text="Video (MP4)", variable=self.format_var, value="Video (MP4)").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(options_frame, text="Audio Only (MP3)", variable=self.format_var, value="Audio Only (MP3)").pack(side=tk.LEFT, padx=20)
        
        # Download Button
        self.download_btn = ttk.Button(main_frame, text="🚀 Download Now", command=self.start_download)
        self.download_btn.pack(pady=20)
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Helvetica", 10, "italic"))
        self.status_label.pack(pady=5)
        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.save_dir_var.get())
        if folder:
            self.save_dir_var.set(folder)

    def download_tiktok(self, url, is_audio):
        try:
            api_url = "https://www.tikwm.com/api/"
            self.root.after(0, self.status_var.set, "Fetching TikTok video details...")
            response = requests.get(api_url, params={'url': url, 'hd': 1})
            data = response.json()
            
            if data.get("code") != 0:
                self.root.after(0, messagebox.showerror, "Error", f"TikTok API Error: {data.get('msg')}")
                return False
                
            title = data["data"].get("title", "tiktok_video")
            title = "".join(x for x in title if x.isalnum() or x in " -_")[:50]
            if not title.strip():
                title = "tiktok_video"
                
            if is_audio:
                media_url = data["data"].get("music")
                ext = "mp3"
            else:
                media_url = data["data"].get("hdplay") or data["data"].get("play")
                ext = "mp4"
                
            if not media_url:
                self.root.after(0, messagebox.showerror, "Error", "Could not find media link.")
                return False
                
            self.root.after(0, self.status_var.set, f"Downloading: {title}...")
            
            media_res = requests.get(media_url, stream=True)
            media_res.raise_for_status()
            
            save_dir = self.save_dir_var.get()
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            output_file = os.path.join(save_dir, f"{title}.{ext}")
            with open(output_file, 'wb') as f:
                for chunk in media_res.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            return True
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"An error occurred while downloading from TikTok: {str(e)}")
            return False

    def my_hook(self, d):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', 'N/A')
            speed_str = d.get('_speed_str', 'N/A')
            eta_str = d.get('_eta_str', 'N/A')
            
            # Clean ANSI escape sequences that yt-dlp might output
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            percent_str = ansi_escape.sub('', percent_str).strip()
            
            msg = f"Downloading... {percent_str} (Speed: {speed_str}, ETA: {eta_str})"
            self.root.after(0, self.status_var.set, msg)
        elif d['status'] == 'finished':
            self.root.after(0, self.status_var.set, "Download finished, processing...")

    def download_media(self, url, is_audio):
        if "tiktok.com" in url.lower():
            return self.download_tiktok(url, is_audio)
            
        save_dir = self.save_dir_var.get()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        output_tmpl = os.path.join(save_dir, "%(title)s.%(ext)s")
            
        ydl_opts = {
            'outtmpl': output_tmpl,
            'noplaylist': True,
            'progress_hooks': [self.my_hook],
            'quiet': True,
            'no_warnings': True
        }
        
        if is_audio:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            })
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.root.after(0, self.status_var.set, "Extracting info...")
                # Extract info to get title before downloading
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                self.root.after(0, self.status_var.set, f"Starting download: {title}")
                
                # Start download
                error_code = ydl.download([url])
                return error_code == 0
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"An error occurred: {str(e)}")
            return False

    def process_download(self, url, is_audio):
        try:
            success = self.download_media(url, is_audio)
            if success:
                self.root.after(0, self.status_var.set, "✅ Download completed successfully!")
                self.root.after(0, messagebox.showinfo, "Success", "Media downloaded successfully!")
            else:
                self.root.after(0, self.status_var.set, "❌ Download failed.")
        finally:
            self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.url_entry.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.save_entry.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.browse_btn.config(state=tk.NORMAL))

    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please paste a valid URL first.")
            return
            
        is_audio = (self.format_var.get() == "Audio Only (MP3)")
        if is_audio and not is_ffmpeg_installed():
            messagebox.showerror("Error", "Cannot convert to MP3 because ffmpeg is not installed. Please select Video (MP4) format.")
            return
            
        self.download_btn.config(state=tk.DISABLED)
        self.url_entry.config(state=tk.DISABLED)
        self.save_entry.config(state=tk.DISABLED)
        self.browse_btn.config(state=tk.DISABLED)
        self.status_var.set("🚀 Starting download...")
        
        # Run download in a separate thread so GUI doesn't freeze
        thread = threading.Thread(target=self.process_download, args=(url, is_audio))
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaDownloaderApp(root)
    root.mainloop()
