# Check and Install Python and Dependencies script
# Usage: ./setup_env.ps1

Write-Host "Started Environment Check..." -ForegroundColor Cyan

# 1. Check Python installation
$pythonInstalled = $false
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python is installed: $pythonVersion" -ForegroundColor Green
        $pythonInstalled = $true
    }
} catch {
    # Ignored
}

if (-not $pythonInstalled) {
    Write-Host "Python is NOT installed." -ForegroundColor Yellow
    $install = Read-Host "Do you want to install Python via Winget? (Y/N)"
    if ($install -eq 'Y' -or $install -eq 'y') {
        Write-Host "Installing Python (this may require admin privileges checks)..."
        winget install -e --id Python.Python.3.12
        
        # Refresh env vars for current session is tricky in script, might need restart
        Write-Host "Python installed. Please restart your terminal/PowerShell session and run this script again." -ForegroundColor Red
        exit
    } else {
        Write-Host "Please install Python manually to proceed." -ForegroundColor Red
        exit
    }
}

# 2. Check Pip (usually comes with Python)
Write-Host "Checking pip..."
python -m pip --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pip seems to be missing. Attempting to ensure pip..."
    python -m ensurepip --default-pip
}

# 3. Check Python Version Manager
Write-Host "Checking for Python Version Manager..."
$uvInstalled = Get-Command uv -ErrorAction SilentlyContinue
$pyenvInstalled = Get-Command pyenv -ErrorAction SilentlyContinue
$condaInstalled = Get-Command conda -ErrorAction SilentlyContinue

if ($uvInstalled) {
    Write-Host "✓ uv is installed (Recommended)." -ForegroundColor Green
} elseif ($pyenvInstalled) {
    Write-Host "✓ pyenv is installed." -ForegroundColor Green
} elseif ($condaInstalled) {
    Write-Host "✓ conda is installed." -ForegroundColor Green
} else {
    Write-Host "✗ No Python version manager found (uv, pyenv, or conda)." -ForegroundColor Yellow
    Write-Host "  Recommendation: Install 'uv' for fast Python management."
    
    $installUv = Read-Host "Do you want to install uv via Winget? (Y/N)"
    if ($installUv -eq 'Y' -or $installUv -eq 'y') {
        winget install -e --id astral-sh.uv
        Write-Host "uv installed." -ForegroundColor Green
    }
}

# 4. Check and Fix PATH for Python Scripts
# Many tools (sqlfluff, dbt) install to the Scripts folder.
Write-Host "Checking Python Scripts directory in PATH..."
try {
    $scriptsPath = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
    if ($scriptsPath) {
        $scriptsPath = $scriptsPath.Trim()
        Write-Host "Python Scripts Path: $scriptsPath" -ForegroundColor Gray
        
        # Normalize paths for comparison
        $normScriptsPath = [System.IO.Path]::GetFullPath($scriptsPath).TrimEnd('\')
        $inPath = $false
        
        $env:PATH.Split(';') | ForEach-Object {
            try {
                if ([System.IO.Path]::GetFullPath($_).TrimEnd('\') -eq $normScriptsPath) {
                    $inPath = $true
                }
            } catch {
                # Ignore invalid paths in PATH
            }
        }

        if (-not $inPath) {
            Write-Host "Warning: Scripts directory is NOT in your PATH." -ForegroundColor Yellow
            Write-Host "Adding it to the current session PATH..."
            $env:PATH = "$scriptsPath;$env:PATH"
            
            Write-Host "To make this permanent, run in PowerShell:" -ForegroundColor White
            Write-Host "   [Environment]::SetEnvironmentVariable('Path', `"`$env:Path;$scriptsPath`", 'User')" -ForegroundColor Cyan
        } else {
            Write-Host "Scripts directory is correctly in PATH." -ForegroundColor Green
        }
    }
} catch {
    Write-Host "Could not determine Script path automatically." -ForegroundColor Red
}

# 4. Install/Update Script Dependencies
# The python script uses verification libraries like 'packaging' (optional but good) or dbt/sqlfluff management.
# We'll just ensure 'requests' is installed if we decide to use it, although the current python script uses standard libs.
# However, let's update pip itself just in case.
Write-Host "Updating pip..."
python -m pip install --upgrade pip --quiet

Write-Host "Dependencies check complete." -ForegroundColor Green
Write-Host "You can now run the Python skill manager." -ForegroundColor Green
