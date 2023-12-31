These sets of scripts allow for easy automatic batch transcribing, translating, and subtitling of any video or audio file.
You will need Python installed, I have only tested on 3.10.6.

# Installation:
1. Git clone somewhere low on the drive (e.g. C:\Translator or D:\Translator):  
`git clone https://github.com/elementybt/translator.git`  
If you don't know git then download this repository and unzip it:  
https://github.com/elementybt/translator/archive/refs/heads/main.zip

2. You MUST have FFmpeg in your PATH. If you do not then you have to download FFmpeg and place `ffmpeg.exe` and `ffprobe.exe` in the Translator `src` folder. You can download it from the FFmpeg website or directly with this link (the exe files are in the ffmpeg-master-latest-win64-gpl/bin folder):
https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip

3. Open Terminal (preferred) or Powershell window in the Translator directory.
**Note:** Run the following to stop the message that pops up whenever you run the ps1 files: `dir .\* | Unblock-File`

4. Run `.\setup.ps1`

5. Edit the `config.ini` file, you have to change the Sugoi directory setting to point to your base Sugoi location.

6. (Optional, but highly recommended) Follow the guide below to setup CUDA for much faster speeds if you have an Nvidia card.

7. Put video and audio files into the input folder. Maybe start with just 1 to make sure everything is working correctly.

8. In the Terminal, run `.\transcription.ps1`. The first run will take longer due to it downloading a model. If it works correctly then you can run `.\translation.ps1`. Finally run `.\merge.ps1` to get the final video. All of the files will be in the output folder.

9. Once you've determined it's working correctly, you can use `.\all.ps1` to run all of the steps at once.

# Intial GPU setup:
1. Install CUDA and CUDNN. Not going to guide you through this, search online for how to do it. I always suggest sticking with CUDA
11.8. If you're on CUDA 11.8 and need CUDNN, you can get it straight from this link:  
https://developer.download.nvidia.com/compute/redist/cudnn/v8.8.0/local_installers/11.8/cudnn_8.8.0.121_windows.exe  
If you need CUDNN and are not on CUDA 11.8, you will have to find it yourself in this directory:  
https://developer.download.nvidia.com/compute/redist/cudnn/

2. There's two separate GPU instructions below here for Whisper and for Sugoi.

# Whisper GPU setup:
1. Download cuBLAS.and.cuDNN.7z from here:  
https://github.com/Purfview/whisper-standalone-win/releases/tag/libs

2. Extract those files into the Translator `src` directory.

3. Open config.ini and set CUDA under Whisper to true.

# Sugoi GPU setup:
1. Get the CUDA installer from the Sugoi Toolkit Discord and set it up for Ctranslate2. Check the pins in #sugoi-japanese-translator.

2. Open config.ini and set CUDA under Sugoi to true.

# FAQ:
* CUDA isn't working!
You HAVE to install CUDA AND CUDNN before they will work. You also HAVE to install the CUDA patch for Sugoi translator (found in the Discord) if you want it to work.

* Bad/slow/other issues with transcription?  
Mess around with the Whisper settings in the config.ini, they can make a huge difference.

* Transcribing is slow?  
Switch WhisperType in config.ini to faster-whisper. It's A LOT faster but might not be as accurate.

* I want to edit the translation and remake the video?  
Edit the filename.translation.ass file however you want and then run merge.ps1

* Do I need to keep the transcription.ass, translation.ass, and cover.jpg files?  
No, they're not needed unless you want to edit and merge them again, you can delete them if you want.

* Why do audio files take longer to merge than video files?  
Have to encode a whole new video with the audio files, where as with the video files you can just copy the audio and video without having to encode.