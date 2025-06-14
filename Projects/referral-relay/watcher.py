import os, time, requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

FOLDER = os.path.expanduser("~/referral_zips")
NETLIFY_TOKEN = os.getenv("NETLIFY_TOKEN")
SITE = "stalwart-kangaroo-dd7c11.netlify.app"

class ZipHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".zip"):
            return
        filename = os.path.basename(event.src_path)
        with open(event.src_path, "rb") as f:
            files = {"file": (f"referrals/{filename}", f.read())}
            res = requests.post(
                f"https://api.netlify.com/api/v1/sites/{SITE}/deploys",
                headers={"Authorization": f"Bearer {NETLIFY_TOKEN}"},
                files=files
            )
            if res.status_code in [200, 201]:
                print(f"✅ Uploaded: https://{SITE}/referrals/{filename}")
            else:
                print(f"❌ Upload failed for {filename}: {res.status_code} → {res.text}")

observer = Observer()
observer.schedule(ZipHandler(), FOLDER, recursive=False)
observer.start()
print(f"👀 Watching: {FOLDER}")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
