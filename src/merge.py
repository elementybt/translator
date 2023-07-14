import configparser
import os
import ffmpeg

print("\nStarting merging process.")

# Pull settings from config.ini
base_path = os.path.dirname(__file__)
config_path = os.path.abspath(os.path.join(base_path, "..", "config.ini"))
config = configparser.ConfigParser()
config.read(config_path)
config_settings = config["Settings"]

# Set vars from config.ini and setup variables
input_file_list = []
output_path = os.path.abspath(os.path.join(base_path, "..", "output/"))
input_path = os.path.abspath(os.path.join(base_path, "..", "input/"))

# Extensions to search for
extensions = (".mp4",".mkv",".wmv",".mov",".avi",".flv",".webm",".ts",".mpeg2",".mp3",".m4a",".flac",".wav",".wma",".aac",".ogg")
audio_extensions = (".mp3",".m4a",".flac",".wav",".wma",".aac",".ogg")

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

# Main merge block
for file in input_file_list:
    file_base_name = os.path.basename(file)
    print(f"\nProcessing file {current_file} of {total_files} ({file_base_name}):")

    # Find corresponding translation file
    translation_file = os.path.join(
        output_path,
        f"{os.path.splitext(file_base_name)[0]}.translation.ass",
    )
    if os.path.exists(translation_file):
        print(f"Matching translation: {translation_file}")

        output_file_name = os.path.join(
            output_path,
            f"{os.path.splitext(file_base_name)[0]}.mkv",
        )

        # Determine if we're working with video or audio
        if file.endswith(audio_extensions):
            print(f"{file} is audio. Creating video with translation file.")

            probe = ffmpeg.probe(file, select_streams='v')
            if probe["streams"]:
                print("Cover art found, extracting.")
                cover_file = os.path.join(
                    output_path,
                    f"{os.path.splitext(file_base_name)[0]}.cover.jpg",
                )
                os.system(f'ffmpeg.exe -v error -stats -i {file} -filter:v scale=640:-1 -an {cover_file} -y')
            else:
                print("No cover art found, using default.")
                cover_file = os.path.join(
                    output_path,
                    "..",
                    "cover.jpg"
                )

            audio_duration = ffmpeg.probe(file)['format']['duration']
            os.system(f'ffmpeg.exe -v error -stats -loop 1 -t "{audio_duration}" -i "{cover_file}" -i "{file}" -i "{translation_file}" -c:v libx264 -tune stillimage -c:a copy -metadata:s:a:0 language=Japanese -metadata:s:s:0 language=English -disposition:s:s:0 forced "{output_file_name}" -y')
        else:
            print(f"{file_base_name} is a video. Merging translation file.")
            os.system(f'ffmpeg.exe -v error -stats -i "{file}" -i "{translation_file}" -c:v copy -c:a copy -metadata:s:a:0 language=Japanese -metadata:s:s:0 language=English -disposition:s:s:0 forced "{output_file_name}" -y')

        print(f"Saved: {output_file_name}")
        current_file += 1
    else:
        print(f"This file has no translation file, skipping it.")
        current_file += 1
        continue

print("\nMerging done. The files can be found in the output directory.")


#     os.system(f'ffmpeg.exe -i "{audio_file}" -i "{subtitle_file}" -c:v copy -c:a copy -metadata:s:a:0 language=Japanese -metadata:s:s:0 language=English -disposition:s:s:0 forced "{file_with_mkv_ext}" -y')
#     os.system(f'ffmpeg.exe -loop 1 -t "{audio_duration}" -i image.jpg -i "{audio_file}" -i "{subtitle_file}" -c:a copy -metadata:s:a:0 language=Japanese -metadata:s:s:0 language=English -disposition:s:s:0 forced "{file_with_mkv_ext}" -y')
