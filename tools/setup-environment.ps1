$python = get-command python
$gitDir = git rev-parse --show-toplevel
$venv = "env"

function log {
	param(
		[Parameter(Position=0)]
		$WriteThis,
		[Parameter(Position=1)]
		[switch]$Quiet
	)
	if ($Quiet) { return }
	Write-Host -Fore Cyan $writeThis
}

$pythonVersion = (python --version).split(" ")[1].split(".")
$pythonVersion = [version]::new($pythonVersion[0], $pythonVersion[1])
$requiredVersion = [version]::new(3,7)

if ($pythonVersion -ne $requiredVersion){
	log "This repository expects python $requiredVersion, installed python is $pythonVersion"
	log "Aborting automatic enviroment setup - You may still be able to perform a manual configuration"
	return
}

Push-Location $gitDir
log "Creating virtual environment"
& $python -m venv $venv

log "Activating virtual environment"
. $venv/Scripts/activate
# Update to env python
$python = get-command python

log "Installing requirements"
& $python -m pip install -r requirements.txt


log "Deactivating virtual environment"
deactivate
Pop-Location