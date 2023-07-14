import warnings
warnings.filterwarnings("ignore", message=".*The 'nopython' keywo*")
import configparser
import os
import pysubs2
from sys import exit
from tqdm import tqdm, TqdmWarning

print("\nStarting transcription process.")

# Pull settings from config.ini
base_path = os.path.dirname(__file__)
config_path = os.path.abspath(os.path.join(base_path, "..", "config.ini"))
config = configparser.ConfigParser()
config.read(config_path)
config_whisper = config["Whisper"]
config_settings = config["Settings"]

# Set vars from config.ini and setup variables
input_file_list = []
output_path = os.path.abspath(os.path.join(base_path, "..", "output/"))
input_path = os.path.abspath(os.path.join(base_path, "..", "input/"))
model_size = config_whisper["Model"]
whisper_type = config_whisper["Type"]
use_cuda = config_whisper.getboolean("CUDA")

# Early exit if CUDA files are missing
if use_cuda == True:
    if not os.path.exists(os.path.join(base_path, "cublas64_11.dll")):
        exit("ERROR: Missing CUDA files. Please read the README!")

# Create missing dirs
if not os.path.exists(output_path):
    os.makedirs(output_path)
if not os.path.exists(input_path):
    os.makedirs(input_path)

# Early exit if stuff is in output folder
# if os.listdir(output_path):
#     question = "\nWARNING: There are files in the output folder already.\nDo you want to continue and possbily overwrite files?"
#     reply = None
#     while reply not in ("y", "n"):
#         reply = input(f"{question} [y/n]: ").lower()
#     if reply == "n":
#         exit("NOTICE: Exiting due to files being found in output directory.")

# Import correct Whisper type
if whisper_type == "stable-ts":
    import stable_whisper
elif whisper_type == "faster-whisper":
    from faster_whisper import WhisperModel
else:
    exit("ERROR: Improper WhisperType setting in config.ini")
print(f"Using Whisper: {whisper_type}")

# Extensions to search for
extensions = (".mp4",".mkv",".wmv",".mov",".avi",".flv",".webm",".ts",".mpeg2",".mp3",".m4a",".flac",".wav",".wma",".aac",".ogg")

# Find audio/video files to transcribe
for file in os.listdir(input_path):
    if file.endswith(extensions):
        input_file_list.append(os.path.join(input_path, file))

total_files = len(input_file_list)
current_file = 1
print(f"Found {total_files} file(s) to process.")
os.chdir(base_path)

# Setup subtitle styling
sub_style = pysubs2.SSAStyle(
    fontname=config_settings["SubFont"],
    fontsize=config_settings["SubSize"],
    primarycolor=config_settings["SubPrimaryColor"],
    secondarycolor=config_settings["SubSecondaryColor"],
    bold=config_settings["SubBold"],
    italic=config_settings["SubItalic"],
    outline=config_settings["SubOutline"],
    shadow=config_settings["SubShadow"],
    marginv=config_settings["SubMarginV"],
)

# Main transcription block
if whisper_type == "stable-ts":
    if use_cuda == True:
        model = stable_whisper.load_model(model_size, "cuda")
    else:
        model = stable_whisper.load_model(model_size)

    for file in input_file_list:
        base_file_name = os.path.basename(file)
        print(f"Processing file {current_file} of {total_files} ({base_file_name}):")
        
        # Run the transcription
        result = model.transcribe(
            file,
            language=config_whisper["Language"],
            suppress_ts_tokens=False,
            vad=config_whisper.getboolean("VAD"),
            condition_on_previous_text=config_whisper.getboolean("ConditionOnPreviousText")
        )

        # Set output file name based on input file
        file_name = os.path.join(
            output_path,
            f"{os.path.splitext(base_file_name)[0]}.transcription.ass",
        )

        # Save the subs
        subs = pysubs2.load_from_whisper(stable_whisper.WhisperResult.segments_to_dicts(result))
        subs.styles["Default"] = sub_style
        subs.info["ScaledBorderAndShadow"] = "no"
        subs.save(file_name)
        print(f"Saved: {file_name}")
        current_file += 1

elif whisper_type == "faster-whisper":
    if use_cuda == True:
        model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
    else:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

    for file in input_file_list:
        base_file_name = os.path.basename(file)
        print(f"\nProcessing file {current_file} of {total_files} ({base_file_name}):")

        # Run the transcription
        segments, info = model.transcribe(
            file,
            beam_size=5,
            language=config_whisper["Language"],
            vad_filter=config_whisper.getboolean("VAD"),
            condition_on_previous_text=config_whisper.getboolean("ConditionOnPreviousText")
        )

        # Progressbar setup
        warnings.filterwarnings("ignore", category=TqdmWarning)
        result = []
        timestamps = 0.0
        total_duration = round(info.duration, 2)
        with tqdm(total=total_duration, unit=" audio seconds") as pbar:
            for s in segments:
                segment_dict = {"start": s.start, "end": s.end, "text": s.text}
                result.append(segment_dict)
                pbar.update(s.end - timestamps)
                timestamps = s.end
            if timestamps < info.duration:  # silence at the end of the audio
                pbar.update(info.duration - timestamps)

        # Set output file name based on input file
        file_name = os.path.join(
            output_path,
            f"{os.path.splitext(base_file_name)[0]}.transcription.ass",
        )

        # Save the subs
        subs = pysubs2.load_from_whisper(result)
        subs.styles["Default"] = sub_style
        subs.info["ScaledBorderAndShadow"] = "no"
        subs.save(file_name)
        print(f"Saved: {file_name}")
        current_file += 1

print("\nTranscription done. The files can be found in the output directory.")
