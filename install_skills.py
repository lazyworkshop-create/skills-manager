import os
import shutil
import subprocess
import sys
import tempfile
import json
import argparse
from pathlib import Path

# Load Configuration
def load_config():
    config_path = Path(__file__).parent / "skills.json"
    if not config_path.exists():
        print("Error: skills.json not found.")
        sys.exit(1)
    with open(config_path, "r") as f:
        return json.load(f)

CONFIG = load_config()
SKILLS_REPO = CONFIG["repo_url"]
SKILLS_MAPPING = CONFIG["skills"]

def get_target_directory():
    """Ask user for installation directory."""
    print("\nSelect installation location:")
    print("1. [Global] VS Code User Folder (~/.vscode/skills)")
    print("2. [Project] Current Workspace (./skills)")
    print("3. [Custom] Enter custom path")
    
    choice = input("Enter choice (1/2/3) [Default: 2]: ").strip()
    
    if choice == "1":
        # Windows: %USERPROFILE%\.vscode\skills, Linux/Mac: ~/.vscode/skills
        return Path.home() / ".vscode" / "skills"
    elif choice == "3":
        custom_path = input("Enter absolute path: ").strip()
        return Path(custom_path)
    else:
        # Default to project skills folder
        return Path(os.getcwd()) / "skills"

def run_command(command, cwd=None, check=True, capture_output=False):
    """Run a shell command."""
    try:
        result = subprocess.run(
            command, 
            cwd=cwd, 
            check=check, 
            shell=True, 
            text=True, 
            capture_output=capture_output
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        if capture_output:
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
        raise

def check_installed(tool_name, check_command):
    """Check if a tool is installed."""
    try:
        subprocess.run(check_command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✓ {tool_name} is already installed.")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ {tool_name} is NOT installed.")
        return False

def install_python_package(package_name):
    """Install a Python package using pip."""
    print(f"Installing {package_name}...")
    run_command(f"{sys.executable} -m pip install {package_name}")

def manage_dependencies(skill_name, skill_path):
    """Check and install dependencies for a skill."""
    print(f"  Checking dependencies for {skill_name}...")
    
    # Generic requirements.txt check
    req_file = skill_path / "requirements.txt"
    if req_file.exists():
        print(f"  Found requirements.txt. Installing...")
        run_command(f"{sys.executable} -m pip install -r requirements.txt", cwd=skill_path)
    
    # Specific tool checks based on skill name mapping or config
    # Ideally this should also be in skills.json, but keeping hardcoded logic for now as per previous known logic
    if "dbt-transformation-patterns" in skill_name:
        if not check_installed("dbt", "dbt --version"):
            print("  Installing dbt-core...")
            install_python_package("dbt-core")
    
    elif "sql-optimization-patterns" in skill_name:
        if not check_installed("sqlfluff", "sqlfluff --version"):
            print("  Installing sqlfluff (SQL linter)...")
            install_python_package("sqlfluff")

def update_or_install_skills(target_dir, specific_skills=None, auto_update=False):
    """
    Install or update skills.
    
    Args:
        target_dir (Path): Destination base directory.
        specific_skills (list): Optional list of skill keys to install/update.
        auto_update (bool): If True, defaults to updating without prompting per skill (though we overwrite anyway).
    """
    if not target_dir.exists():
        try:
            target_dir.mkdir(parents=True)
            print(f"Created directory: {target_dir}")
        except Exception as e:
            print(f"Error creating directory {target_dir}: {e}")
            return

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"\nFetching latest skills from repository...")
        print(f"Repository: {SKILLS_REPO}")
        
        # Git clone (shallow) to get latest version
        try:
            run_command(f"git clone --depth 1 {SKILLS_REPO} .", cwd=temp_path, capture_output=True)
        except Exception:
            print("Failed to clone repository. Check internet connection or git installation.")
            return

        skills_to_process = specific_skills if specific_skills else SKILLS_MAPPING.keys()

        for skill_name in skills_to_process:
            if skill_name not in SKILLS_MAPPING:
                print(f"Warning: Skill '{skill_name}' not found in configuration.")
                continue

            repo_path = SKILLS_MAPPING[skill_name]
            source_path = temp_path / repo_path
            dest_path = target_dir / skill_name
            
            if not source_path.exists():
                print(f"Error: Could not find '{skill_name}' source at {source_path}")
                continue
                
            action = "Installing"
            if dest_path.exists():
                # Simple update check: We just overwrite for now as 'Updating'
                # A more complex check would compare hash or timestamp, but overwrite ensures latest state.
                action = "Updating"
                print(f"Found existing installation for {skill_name}")
                shutil.rmtree(dest_path)
            
            print(f"{action} {skill_name}...")
            try:
                shutil.copytree(source_path, dest_path)
                print(f"✓ Successfully processed {skill_name}.")
                manage_dependencies(skill_name, dest_path)
            except Exception as e:
                print(f"Failed to copy {skill_name}: {e}")

def show_interactive_help():
    print("\n=== Interactive Command Help ===")
    print("Options:")
    print("  <Numbers> : Select specific skills by index (separated by space).")
    print("              Example: '1 3' installs the first and third listed skills.")
    print("  A         : Install All skills (Default).")
    print("  H         : Show this help message.")
    print("================================")

def select_skills(skills_mapping):
    """Interactive skill selection."""
    skills_list = list(skills_mapping.keys())
    while True:
        print("\nAvailable Skills:")
        for idx, name in enumerate(skills_list, 1):
            print(f"{idx}. {name}")
        print("A. Install All")
        print("H. Help")
        
        selection = input("\nEnter numbers separated by space (e.g., '1 2') or 'A' for all [Default: A]: ").strip()
        
        if selection.upper() == 'H':
            show_interactive_help()
            continue
            
        if not selection or selection.upper() == 'A':
            return None  # None implies all in the current logic
        
        selected_keys = []
        try:
            parts = selection.split()
            valid = True
            for part in parts:
                try:
                    idx = int(part) - 1
                    if 0 <= idx < len(skills_list):
                        key = skills_list[idx]
                        if key not in selected_keys:
                            selected_keys.append(key)
                    else:
                        print(f"Warning: Number '{part}' is out of range.")
                except ValueError:
                    print(f"Warning: '{part}' is not a number.")
            
            if selected_keys:
                print(f"Selected: {', '.join(selected_keys)}")
                return selected_keys
            else:
                print("No valid skills selected.")
        except ValueError:
            print("Invalid input format.")

def discover_skills(repo_root):
    """Scan the downloaded repository for available skills."""
    discovered = []
    plugins_dir = repo_root / "plugins"
    if not plugins_dir.exists():
        return discovered
    
    # Iterate over category folders
    for category_path in plugins_dir.iterdir():
        if category_path.is_dir():
            skills_dir = category_path / "skills"
            if skills_dir.exists() and skills_dir.is_dir():
                for skill_path in skills_dir.iterdir():
                    if skill_path.is_dir():
                         rel_path = skill_path.relative_to(repo_root).as_posix()
                         discovered.append({
                             "name": skill_path.name,
                             "path": rel_path,
                             "category": category_path.name
                         })
    return discovered

def browse_and_install_remote_skills(target_dir):
    """List remote skills and allow interactive installation."""
    print("Fetching remote skill list...")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        try:
             run_command(f"git clone --depth 1 {SKILLS_REPO} .", cwd=temp_path, capture_output=True)
        except Exception:
            print("Failed to clone repository.")
            return

        skills = discover_skills(temp_path)
        if not skills:
            print("No skills found in the remote repository structure (plugins/*/skills/*).")
            return

        # Sort by category then name
        skills.sort(key=lambda x: (x['category'], x['name']))

        print("\n=== Available Remote Skills ===")
        print(f"{'No.':<4} {'Category':<25} {'Skill Name':<30}")
        print("-" * 60)
        
        for idx, skill in enumerate(skills, 1):
            installed_mark = "*" if skill['name'] in SKILLS_MAPPING else " "
            print(f"{str(idx) + '.':<4} {skill['category']:<25} {skill['name']:<30} {installed_mark}")
        
        print(f"\n(* = Already in configuration)")
        print("Enter numbers to install/update (e.g. '1 3 5') or 'q' to quit.")
        selection = input("Selection: ").strip()
        
        if selection.lower() == 'q':
            return

        selected_indices = []
        try:
            parts = selection.split()
            for part in parts:
                idx = int(part) - 1
                if 0 <= idx < len(skills):
                    selected_indices.append(idx)
        except ValueError:
            print("Invalid input.")
            return

        if not selected_indices:
            print("No valid selection.")
            return

        # Create target dir if not exists
        if not target_dir.exists():
             target_dir.mkdir(parents=True)

        config_changed = False
        for idx in selected_indices:
            skill = skills[idx]
            print(f"\nProcessing {skill['name']}...")
            
            dest_path = target_dir / skill['name']
            source_path = temp_path / skill['path']
            
            if dest_path.exists():
                print(f"  Removing existing installation...")
                shutil.rmtree(dest_path)
            
            try:
                shutil.copytree(source_path, dest_path)
                print(f"  ✓ Installed to {dest_path}")
                manage_dependencies(skill['name'], dest_path)
                
                # Update mapping
                if skill['name'] not in SKILLS_MAPPING:
                    SKILLS_MAPPING[skill['name']] = skill['path']
                    config_changed = True
                    print(f"  Added '{skill['name']}' to configuration.")
            except Exception as e:
                print(f"  Error installing {skill['name']}: {e}")

        if config_changed:
            config_path = Path(__file__).parent / "skills.json"
            try:
                CONFIG["skills"] = SKILLS_MAPPING
                with open(config_path, "w") as f:
                    json.dump(CONFIG, f, indent=4)
                print("\nConfiguration saved to skills.json.") 
            except Exception as e:
                print(f"Warning: Could not save configuration: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Manage VS Code Skills - Install, update, and manage agent skills.",
        epilog="""
Interactive Mode:
  Run without arguments to enter interactive mode.
  You will be prompted to select an installation location and specific skills.

Examples:
  python install_skills.py --global-install --yes      # Install all skills to global folder silently
  python install_skills.py --project-install           # Install to current folder (interactive selection)
  python install_skills.py --check-updates             # Update currently installed skills
  python install_skills.py --ls                        # Browse and install new skills from remote
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--global-install", action="store_true", help="Install to global VS Code folder (~/.vscode/skills)")
    parser.add_argument("--project-install", action="store_true", help="Install to current project folder (./skills)")
    parser.add_argument("--check-updates", action="store_true", help="Check and update all installed skills")
    parser.add_argument("--ls", action="store_true", help="Browse available remote skills interactively")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip interactive confirmation (installs all)")
    args = parser.parse_args()

    # Determine Target Directory
    target_dir = None
    if args.global_install:
        target_dir = Path.home() / ".vscode" / "skills"
    elif args.project_install:
        target_dir = Path(os.getcwd()) / "skills"
    else:
        # Check context
        if args.ls:
             print("=== Browse Remote Skills ===")
             target_dir = get_target_directory()
        elif not args.check_updates:
             # Default install mode
             print("=== Skills Manager ===")
             target_dir = get_target_directory()
        # If check_updates is true, we fall through to below default

    if target_dir is None:
        target_dir = get_target_directory()

    print(f"\nLocation: {target_dir}")

    # Operations
    if args.ls:
        browse_and_install_remote_skills(target_dir)
    elif args.check_updates:
        print("Checking for updates on installed skills...")
        # Identify which skills are currently installed in the target dir
        installed_skills = []
        if target_dir.exists():
            for item in target_dir.iterdir():
                if item.is_dir() and item.name in SKILLS_MAPPING:
                    installed_skills.append(item.name)
        
        if not installed_skills:
            print("No known skills found in this location to update.")
        else:
            print(f"Found skills: {', '.join(installed_skills)}")
            update_or_install_skills(target_dir, specific_skills=installed_skills, auto_update=True)
    else:
        # Selection logic
        selected_skills = None
        if not args.yes:
            selected_skills = select_skills(SKILLS_MAPPING)
        
        update_or_install_skills(target_dir, specific_skills=selected_skills, auto_update=True)

    print("\n---------------------------------------------------------")
    print("Done.")

if __name__ == "__main__":
    main()
