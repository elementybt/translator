## The following four lines only need to be declared once in your script.
$yes = New-Object System.Management.Automation.Host.ChoiceDescription "&Yes","Description."
$no = New-Object System.Management.Automation.Host.ChoiceDescription "&No","Description."
$options = [System.Management.Automation.Host.ChoiceDescription[]]($yes, $no)

## Use the following each time your want to prompt the use
$title = "Existing venv folder found" 
$message = "Would you like to delete your venv folder and start fresh?"
$result = $host.ui.PromptForChoice($title, $message, $options, 1)
switch ($result) {
  0{
    Write-Host "Deleting venv folder."
    Remove-Item -LiteralPath ".\venv\" -Force -Recurse
  }1{
  }
}

python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install wheel
pip install --force-reinstall "faster-whisper @ https://github.com/guillaumekln/faster-whisper/archive/refs/heads/master.tar.gz"
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -U git+https://github.com/jianfch/stable-ts.git
pip install pysubs2
pip install soundfile
pip install ffmpeg-python
deactivate
Write-Host "Install finished! You can start translating now."