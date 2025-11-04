# Script PowerShell para obter arquivos modificados
param(
    [string]$ProjectDir,
    [string]$Hours,
    [string]$ExcludeList,
    [string]$OutputFile
)

try {
    # Obter arquivos modificados nas últimas X horas
    $cutoffTime = (Get-Date).AddHours(-[int]$Hours)
    
    $modifiedFiles = Get-ChildItem -Path $ProjectDir -Recurse -File | 
        Where-Object { $_.LastWriteTime -gt $cutoffTime } | 
        ForEach-Object { $_.FullName }
    
    # Aplicar exclusões se o arquivo de exclusão existir
    if (Test-Path $ExcludeList) {
        $excludePatterns = Get-Content $ExcludeList | Where-Object { $_.Trim() -ne "" }
        
        foreach ($pattern in $excludePatterns) {
            $modifiedFiles = $modifiedFiles | Where-Object { $_ -notlike "*$pattern*" }
        }
    }
    
    # Salvar lista de arquivos modificados
    $modifiedFiles | Out-File -FilePath $OutputFile -Encoding UTF8
    
    Write-Host "Arquivos modificados encontrados: $($modifiedFiles.Count)"
    Write-Host "Lista salva em: $OutputFile"
    
} catch {
    Write-Error "Erro ao processar arquivos modificados: $($_.Exception.Message)"
    exit 1
}
