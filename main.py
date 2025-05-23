import os
import subprocess
import shutil
from datetime import datetime
import pytz
import tempfile
from flask import Flask
import threading  # ✅ Added for background execution

app = Flask(__name__)


def capture_snapshots():
    # Timezone-aware CET/CEST time
    timezone = pytz.timezone("Europe/Warsaw")
    now = datetime.now(timezone)
    date_str = now.strftime("%m-%d")
    time_str = now.strftime("%H%M")

    # ✅ All YouTube streams
    streams = {
        "YT_Poland": "https://www.youtube.com/watch?v=S2L-hzuRX0g",
        "YT_Mechelen1": "https://www.youtube.com/watch?v=xQKCnSsATK0",
        "YT_Mechelen2": "https://www.youtube.com/watch?v=m5HWzP2wNGE",
        "YT_Lokeren": "https://www.youtube.com/watch?v=HUeaYuBLNNQ",
        "YT_TimesSquare": "https://www.youtube.com/watch?v=rnXIjl_Rzy4",
        "YT_Milwaukee": "https://www.youtube.com/watch?v=aYzCutG4MFE",
        "YT_London": "https://www.youtube.com/watch?v=j9Sa4uBGGQ0",
        "YT_NewMexico": "https://www.youtube.com/watch?v=AVfDckwp-Jg",
        "YT_Philadelphia": "https://www.youtube.com/watch?v=RH5fgOcO0jg",
        "YT_Alaska": "https://www.youtube.com/watch?v=h38bnKKIlGY",
        "YT_Somerset": "https://www.youtube.com/watch?v=UAqDarNDrBM",
        "YT_Tokyo": "https://www.youtube.com/watch?v=gFRtAAmiFbE",
        "YT_Kusatsu": "https://www.youtube.com/watch?v=GrEEoEmmrKs",
        "YT_Kabukicho": "https://www.youtube.com/watch?v=EHkMjfMw7oU",
        "YT_LamaiThailand": "https://www.youtube.com/watch?v=Fw9hgttWzIg",
        "YT_Amsterdam": "https://www.youtube.com/watch?v=Gd9d4q6WvUY",
        "YT_Dublin": "https://www.youtube.com/watch?v=u4UZ4UvZXrg",
        "YT_DuffySquare": "https://www.youtube.com/watch?v=iiBTWU2FyFo"
    }

    # 🍪 Workaround: avoid yt-dlp mutating your cookies.txt
    original_cookies_path = "cookies.txt"
    temp_cookies_path = tempfile.mktemp()
    shutil.copyfile(original_cookies_path, temp_cookies_path)

    for name, url in streams.items():
        folder = os.path.join("snapshots", name, date_str)
        os.makedirs(folder, exist_ok=True)
        output_path = os.path.join(folder, f"{time_str}.jpg")

        command = (
            f"yt-dlp --cookies {temp_cookies_path} -f best -o - \"{url}\" "
            f"| ffmpeg -loglevel error -y -i - -frames:v 1 \"{output_path}\"")

        print(f"[{name}] Capturing frame at {date_str} {time_str}...")
        subprocess.call(command, shell=True)

    os.remove(temp_cookies_path)

    print("Uploading to Google Drive...")
    subprocess.call(
        "./rclone_extracted/rclone-v1.69.2-linux-amd64/rclone copy snapshots gdrive_replit:YTSnapshots --config rclone.conf",
        shell=True)
    print("Upload complete.")

    if os.path.exists("snapshots"):
        shutil.rmtree("snapshots")
        print("Local snapshots folder deleted.")


@app.route('/')
def home():
    return "Use /run to capture livestream snapshots."


@app.route('/run')
def run():
    thread = threading.Thread(target=capture_snapshots)  # ✅ Start job in background
    thread.start()
    return "Snapshot job started in background."


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
