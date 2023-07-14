import os
import time
import pysubs2
import configparser
import requests
from tqdm import tqdm

print("\nStarting translation process.")

# Pull settings from config.ini
base_path = os.path.dirname(__file__)
config_path = os.path.abspath(os.path.join(base_path, "..", "config.ini"))
config = configparser.ConfigParser()
config.read(config_path)
config_sugoi = config["Sugoi"]
config_settings = config["Settings"]

# Set vars from config.ini and setup variables
input_file_list = []
output_path = os.path.abspath(os.path.join(base_path, "..", "output/"))
input_path = os.path.abspath(os.path.join(base_path, "..", "input/"))
translation_server_url = config_sugoi["Server"]
use_cuda = config_sugoi.getboolean("CUDA")

# Extensions to search for
extensions = (".mp4",".mkv",".wmv",".mov",".avi",".flv",".webm",".ts",".mpeg2",".mp3",".m4a",".flac",".wav",".wma",".aac",".ogg")

# Find audio/video files to translate
for file in os.listdir(input_path):
    if file.endswith(extensions):
        input_file_list.append(os.path.join(input_path, file))

total_files = len(input_file_list)
current_file = 1
print(f"Found {total_files} file(s) to process.")
if total_files == 0:
    exit("No files to process, exiting.")

# For FFmpeg to work if placed in src
os.chdir(base_path)

# Poll Sugoi Server until available
print("Attempting to connect to Sugoi Server.")
max_tries = int(config_sugoi["Retries"])
current_try = 1
while True:
    if current_try >= max_tries:
        exit("ERROR: Failed to connect to Sugoi Server.")
    try:
        r = requests.get(translation_server_url, timeout=1)
        
        if r.status_code:
            print("Connected to Sugoi Server.")
            break
    except requests.ConnectionError:
        current_try += 1
        time.sleep(0.5)


# Main translation block
for file in input_file_list:
    file_base_name = os.path.basename(file)
    print(f"\nProcessing file {current_file} of {total_files} ({file_base_name}):")

    # Find corresponding transcription file
    file_name = os.path.join(
        output_path,
        f"{os.path.splitext(file_base_name)[0]}.transcription.ass",
    )
    if os.path.exists(file_name):
        print(f"Matching transcription: {file_name}")

        # Load untranslated subs
        untranslated_subs = pysubs2.load(file_name)

        # Translation batching loop
        print("Translating...")
        translated_text = []
        i = 0
        batch = int(config_sugoi["Batch"])
        with tqdm(total=len(untranslated_subs), unit=" lines") as pbar:
            while i < len(untranslated_subs):
                iterate_max = i + batch
                if i + batch > len(untranslated_subs):
                    iterate_max = len(untranslated_subs)

                text_to_be_translated = []
                for x in range(i, iterate_max):
                    text_to_be_translated.append(untranslated_subs[x].text)

                # Send text to translation server
                translation = requests.post(
                    translation_server_url,
                    json={
                        "content": text_to_be_translated,
                        "message": "translate sentences",
                    },
                )
                translated_text.extend(translation.json())
                pbar.update(iterate_max - i)
                i = i + batch

        # Replace original subs with translated
        i = 0
        for line in untranslated_subs:
            line.text = translated_text[i]
            i += 1

        # Save translated subs
        output_file_name = os.path.join(
            output_path,
            f"{os.path.splitext(file_base_name)[0]}.translation.ass",
        )
        untranslated_subs.save(output_file_name)
        print(f"Saved: {output_file_name}")
        current_file += 1

    else:
        print(f"This file has no transcription file, skipping it.")
        current_file += 1
        continue

print("\nTranslation done. The files can be found in the output directory.")
