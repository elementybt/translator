python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install wheel
pip install --force-reinstall "faster-whisper @ https://github.com/guillaumekln/faster-whisper/archive/refs/heads/master.tar.gz"
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -U git+https://github.com/jianfch/stable-ts.git
pip install pysubs2
pip install ffmpeg-python
deactivate
Write-Host "Install finished! You can start translating now."