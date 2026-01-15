# Skills Manager Utility

This set of tools helps you manage and install VS Code Skills (also known as Agent Skills) from a shared repository (`wshobson/agents`). It handles repository cloning, skill extraction, and dependency management (like `dbt` or `sqlfluff`).

## 1. Quick Start

### Prerequisites
*   Windows (PowerShell)
*   Git installed

### Step 1: Environment Setup
Before running the installer for the first time on a new machine, run the environment check script. This ensures Python is installed and the `Scripts` folder is in your PATH.

Run in PowerShell:
```powershell
.\setup_env.ps1
```
*If prompted, follow instructions to fix your PATH or install Python.*

### Step 2: Install or Update Skills
Run the installation script in interactive mode:
```bash
python install_skills.py
```
1.  **Select Location**:
    *   `Global`: Recommended for skills you use in all projects (installs to `~/.vscode/skills`).
    *   `Project`: Installs to `./skills` in the current folder.
2.  **Select Skills**:
    *   Enter the numbers of the skills you want (e.g., `1 2`).
    *   Or type `A` to install/update all available skills.

### Non-Interactive (CI/CD or Automated)
You can run the script with arguments to skip prompts:
```bash
# Install all skills to the current project
python install_skills.py --project-install --yes

# Update all currently installed skills (check-only mode)
python install_skills.py --check-updates --global-install
```

## 2. Configuration

### Adding New Skills
To add a new skill to the installer, you do **not** need to modify the Python code. Just edit `skills.json`.

1.  Open `skills.json`.
2.  Add a new entry to the `skills` object:
    *   **Key**: The folder name you want for the local installation.
    *   **Value**: The relative path to the skill inside the source repository (`wshobson/agents`).

**Example `skills.json`:**
```json
{
    "repo_url": "https://github.com/wshobson/agents.git",
    "skills": {
        "sql-optimization-patterns": "plugins/developer-essentials/skills/sql-optimization-patterns",
        "dbt-transformation-patterns": "plugins/data-engineering/skills/dbt-transformation-patterns",
        "NEW-SKILL-NAME": "plugins/path/to/remote/skill" 
    }
}
```

### Adding New Dependencies
If a new skill requires specific Python tools (like `dbt`, `black`, `ruff`):

1.  Open `install_skills.py`.
2.  Locate the `manage_dependencies` function.
3.  Add a generic check for `requirements.txt` (already handled) or specific logic for the new skill.

*Note: Most standard skills just use `requirements.txt`, which is automatically handled.*
