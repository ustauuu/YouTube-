import time
import os
from pathlib import Path
from generate_video import process_content_file

CONTENT_DIR = Path("content")
SLEEP_SECONDS = int(os.getenv("SLEEP_SECONDS", 3600))  # default 1 saat

def main():
    CONTENT_DIR.mkdir(exist_ok=True)
    Path("out").mkdir(exist_ok=True)
    print("Scheduler started. Watching content/ for .txt files.")
    while True:
        txts = sorted(CONTENT_DIR.glob("*.txt"))
        for txt in txts:
            try:
                print("Processing", txt)
                process_content_file(txt)
                # move/rename processed file to avoid re-processing
                txt.rename(txt.with_suffix(".done"))
                print("Done", txt)
            except Exception as e:
                print("Error processing", txt, e)
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
