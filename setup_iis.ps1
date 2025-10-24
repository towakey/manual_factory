# Windows IIS 環境用セットアップスクリプト
# 管理者権限で実行してください

# エラー時に停止
$ErrorActionPreference = "Stop"

# カラー関数
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host ""
}

# プロジェクトルート
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# 管理者権限チェック
function Test-Administrator {
    Write-Header "管理者権限チェック"
    
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    $isAdmin = $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $isAdmin) {
        Write-Error-Custom "このスクリプトは管理者権限で実行する必要があります"
        Write-Info "PowerShellを右クリック → 管理者として実行"
        exit 1
    }
    
    Write-Success "管理者権限で実行中"
}

# Pythonチェック
function Test-Python {
    Write-Header "Pythonバージョンチェック"
    
    try {
        $pythonVersion = python --version 2>&1
        Write-Info $pythonVersion
        
        $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
        if ($versionMatch) {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 7)) {
                Write-Error-Custom "Python 3.7以上が必要です"
                return $false
            }
        }
        
        Write-Success "Python OK"
        return $true
    }
    catch {
        Write-Error-Custom "Pythonがインストールされていません"
        Write-Info "https://www.python.org/downloads/ からダウンロードしてください"
        return $false
    }
}

# IIS機能チェックとインストール
function Install-IISFeatures {
    Write-Header "IIS機能チェック"
    
    $iisFeatures = @(
        "IIS-WebServerRole",
        "IIS-WebServer",
        "IIS-CommonHttpFeatures",
        "IIS-CGI",
        "IIS-ISAPIExtensions",
        "IIS-ISAPIFilter"
    )
    
    foreach ($feature in $iisFeatures) {
        $installed = Get-WindowsOptionalFeature -Online -FeatureName $feature -ErrorAction SilentlyContinue
        
        if ($installed -and $installed.State -eq "Enabled") {
            Write-Success "$feature は既にインストール済み"
        }
        else {
            Write-Warning-Custom "$feature をインストール中..."
            Enable-WindowsOptionalFeature -Online -FeatureName $feature -All -NoRestart
            Write-Success "$feature をインストールしました"
        }
    }
}

# ディレクトリ作成
function New-Directories {
    Write-Header "ディレクトリ作成"
    
    $directories = @(
        "$ProjectRoot\uploads\images",
        "$ProjectRoot\database"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Success "作成: $dir"
        }
        else {
            Write-Info "既に存在: $dir"
        }
    }
}

# データベース初期化
function Initialize-Database {
    Write-Header "データベース初期化"
    
    $dbPath = "$ProjectRoot\database\manual_factory.db"
    $initScript = "$ProjectRoot\database\init_db.py"
    
    if (-not (Test-Path $initScript)) {
        Write-Error-Custom "初期化スクリプトが見つかりません: $initScript"
        return $false
    }
    
    if (Test-Path $dbPath) {
        $response = Read-Host "既存のデータベースが見つかりました。再作成しますか? (yes/no)"
        if ($response -ne "yes") {
            Write-Warning-Custom "データベース初期化をスキップしました"
            return $true
        }
        Remove-Item $dbPath -Force
    }
    
    try {
        $process = Start-Process -FilePath "python" -ArgumentList $initScript -WorkingDirectory "$ProjectRoot\database" -Wait -NoNewWindow -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-Success "データベース初期化完了"
            Write-Info "初期管理者: admin@example.com / admin123"
            return $true
        }
        else {
            Write-Error-Custom "データベース初期化エラー"
            return $false
        }
    }
    catch {
        Write-Error-Custom "データベース初期化エラー: $_"
        return $false
    }
}

# IISハンドラーマッピング設定
function Set-IISHandlerMapping {
    Write-Header "IISハンドラーマッピング設定"
    
    Import-Module WebAdministration
    
    $pythonPath = (Get-Command python).Source
    $siteName = "Default Web Site"
    $appPath = "/manual_factory"
    
    # 仮想ディレクトリまたはアプリケーションを作成
    $fullPath = "IIS:\Sites\$siteName$appPath"
    
    if (-not (Test-Path $fullPath)) {
        Write-Info "仮想ディレクトリを作成中..."
        New-WebVirtualDirectory -Site $siteName -Name "manual_factory" -PhysicalPath $ProjectRoot
        Write-Success "仮想ディレクトリを作成しました"
    }
    else {
        Write-Info "仮想ディレクトリは既に存在します"
    }
    
    # ハンドラーマッピングを追加
    $handlerName = "Python-CGI"
    $handler = Get-WebHandler -Name $handlerName -ErrorAction SilentlyContinue
    
    if ($handler) {
        Write-Info "ハンドラーマッピングは既に存在します"
    }
    else {
        Write-Info "ハンドラーマッピングを追加中..."
        New-WebHandler -Name $handlerName -Path "*.py" -Verb "*" -Modules "CgiModule" -ScriptProcessor "$pythonPath %s %s"
        Write-Success "ハンドラーマッピングを追加しました"
    }
}

# IISパーミッション設定
function Set-IISPermissions {
    Write-Header "パーミッション設定"
    
    $iisUser = "IIS_IUSRS"
    
    $directories = @(
        "$ProjectRoot\database",
        "$ProjectRoot\uploads"
    )
    
    foreach ($dir in $directories) {
        $acl = Get-Acl $dir
        $permission = $iisUser, "Modify", "ContainerInherit,ObjectInherit", "None", "Allow"
        $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
        $acl.SetAccessRule($accessRule)
        Set-Acl $dir $acl
        Write-Success "パーミッション設定: $dir"
    }
}

# web.config作成
function New-WebConfig {
    Write-Header "web.config作成"
    
    $webConfigPath = "$ProjectRoot\web.config"
    
    if (Test-Path $webConfigPath) {
        $response = Read-Host "web.configが既に存在します。上書きしますか? (yes/no)"
        if ($response -ne "yes") {
            Write-Warning-Custom "web.config作成をスキップしました"
            return
        }
    }
    
    $webConfigContent = @"
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <handlers>
            <add name="Python-CGI" path="*.py" verb="*" modules="CgiModule" scriptProcessor="python.exe %s %s" resourceType="Unspecified" requireAccess="Script" />
        </handlers>
        <defaultDocument>
            <files>
                <add value="index.html" />
                <add value="login.html" />
            </files>
        </defaultDocument>
    </system.webServer>
</configuration>
"@
    
    $webConfigContent | Out-File -FilePath $webConfigPath -Encoding UTF8
    Write-Success "web.configを作成しました"
}

# IIS再起動
function Restart-IIS {
    Write-Header "IIS再起動"
    
    try {
        iisreset
        Write-Success "IISを再起動しました"
    }
    catch {
        Write-Error-Custom "IIS再起動エラー: $_"
    }
}

# 次のステップ表示
function Show-NextSteps {
    Write-Header "セットアップ完了"
    
    Write-Host "次のステップ:"
    Write-Host ""
    Write-Host "1. ブラウザでアクセス:"
    Write-Host "   http://localhost/manual_factory/login.html" -ForegroundColor Green
    Write-Host ""
    Write-Host "2. 初期管理者アカウントでログイン:"
    Write-Host "   Email: admin@example.com" -ForegroundColor White
    Write-Host "   Password: admin123" -ForegroundColor White
    Write-Host ""
    Write-Warning-Custom "※パスワードは必ず変更してください"
    Write-Host ""
    Write-Info "トラブルシューティング:"
    Write-Host "  - IISログ: C:\inetpub\logs\LogFiles"
    Write-Host "  - エラーが発生した場合はREADME.mdを参照してください"
    Write-Host ""
}

# メイン処理
function Main {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host "手順書管理システム - Windows IIS セットアップ" -ForegroundColor Blue
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host ""
    
    Test-Administrator
    
    if (-not (Test-Python)) {
        exit 1
    }
    
    Install-IISFeatures
    New-Directories
    Initialize-Database
    Set-IISHandlerMapping
    Set-IISPermissions
    New-WebConfig
    Restart-IIS
    Show-NextSteps
}

# 実行
try {
    Main
}
catch {
    Write-Error-Custom "エラーが発生しました: $_"
    exit 1
}
