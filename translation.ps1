function Get-IniFile 
{  
    param(  
        [parameter(Mandatory = $true)] [string] $filePath  
    )  
    
    $anonymous = "NoSection"
  
    $ini = @{}  
    switch -regex -file $filePath  
    {  
        "^\[(.+)\]$" # Section  
        {  
            $section = $matches[1]  
            $ini[$section] = @{}  
            $CommentCount = 0  
        }  

        "^(;.*)$" # Comment  
        {  
            if (!($section))  
            {  
                $section = $anonymous  
                $ini[$section] = @{}  
            }  
            $value = $matches[1]  
            $CommentCount = $CommentCount + 1  
            $name = "Comment" + $CommentCount  
            $ini[$section][$name] = $value  
        }   

        "(.+?)\s*=\s*(.*)" # Key  
        {  
            if (!($section))  
            {  
                $section = $anonymous  
                $ini[$section] = @{}  
            }  
            $name,$value = $matches[1..2]  
            $ini[$section][$name] = $value  
        }  
    }  

    return $ini  
}

function Stop-Tree {
    Param([int]$ppid)
    Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $ppid } | ForEach-Object { Stop-Tree $_.ProcessId }
    Stop-Process -Id $ppid
}

$ConfigIni = Get-IniFile .\config.ini
$SugoiDir = $ConfigIni.sugoi.directory
Write-Host "`nStarting Sugoi Server in separate command prompt."

if($ConfigIni.sugoi.cuda.ToLower() -eq "true") {
    if(-not (Test-Path "$SugoiDir/Code/backendServer/Program-Backend/Sugoi-Japanese-Translator/offlineTranslation/ct2/flaskServerCt2.py")) {
        Write-Host "ERROR: Unable to find Sugoi CUDA folder. Check the config.ini file and make sure you have installed the Sugoi CUDA patch."
        Exit
    }
    Set-Location -Path "$SugoiDir/Code/backendServer/Program-Backend/Sugoi-Japanese-Translator/offlineTranslation"
    $CMDProcess = Start-Process -WindowStyle Minimized -PassThru cmd.exe -ArgumentList "/K ..\..\..\..\Power-Source\Python39\python.exe ct2\flaskServerCt2.py"
    Set-Location -Path "$PSScriptRoot"
} elseif($ConfigIni.sugoi.cuda.ToLower() -eq "false") {
    if(-not (Test-Path "$SugoiDir/Code/backendServer/Program-Backend/Sugoi-Japanese-Translator/offlineTranslation/activateOfflineTranslationServer.bat")) {
        Write-Host "ERROR: Unable to find Sugoi folder. Check the config.ini file."
        Exit
    }
    Set-Location -Path "$SugoiDir/Code/backendServer/Program-Backend/Sugoi-Japanese-Translator/offlineTranslation"
    $CMDProcess = Start-Process -WindowStyle Minimized -PassThru -FilePath activateOfflineTranslationServer.bat
    Set-Location -Path $PSScriptRoot
} else {
    Write-Host "ERROR: There's a problem with the SugoiCUDA setting in config.ini, please check it first."
    Exit
}

.\venv\Scripts\Activate.ps1
py src\translation.py
deactivate
if(-not($CMDProcess.HasExited)) {
    Stop-Tree $CMDProcess.ID
}