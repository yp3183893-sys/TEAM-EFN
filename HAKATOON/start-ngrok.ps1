$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Error "ngrok no está instalado o no está en PATH. Instala ngrok y vuelve a intentarlo."
    exit 1
}

Write-Host "Iniciando ngrok con el archivo de configuración: $root\ngrok.yml"
ngrok start --config "$root\ngrok.yml" --all
