import os
import sys
import shutil
import subprocess
import tempfile
import json
import argparse
from pathlib import Path
import locale

# --- Localization Support ---
TEXTS = {
    "en": {
        "config_not_found": "Error: skills.json not found.",
        "select_install_loc": "\nSelect installation location:",
        "loc_global": "1. [Global] VS Code User Folder (~/.vscode/skills)",
        "loc_project": "2. [Project] Current Workspace (./skills)",
        "loc_claude": "3. [Claude] Claude Desktop (APPDATA/Claude/skills)",
        "loc_custom": "4. [Custom] Enter custom path",
        "enter_choice": "Enter choice (1/2/3/4) [Default: 2]: ",
        "enter_path": "Enter absolute path: ",
        "err_run_cmd": "Error running command: {0}",
        "installed": "✓ {0} is already installed.",
        "not_installed": "✗ {0} is NOT installed.",
        "installing_pkg": "Installing {0}...",
        "check_deps": "  Checking dependencies for {0}...",
        "found_reqs": "  Found requirements.txt. Installing...",
        "installing_dbt": "  Installing dbt-core...",
        "installing_sqlfluff": "  Installing sqlfluff (SQL linter)...",
        "created_dir": "Created directory: {0}",
        "err_create_dir": "Error creating directory {0}: {1}",
        "fetching_repo": "\nFetching latest skills from repository...",
        "failed_clone": "Failed to clone repository. Check internet connection or git installation.",
        "warn_skill_not_found": "Warning: Skill '{0}' not found in configuration.",
        "err_source_not_found": "Error: Could not find '{0}' source at {1}",
        "found_existing": "Found existing installation for {0}",
        "updating": "Updating",
        "installing": "Installing",
        "processed_success": "✓ Successfully processed {0}.",
        "failed_copy": "Failed to copy {0}: {1}",
        "interactive_help": """
=== Interactive Command Help ===
Options:
  <Numbers> : Select specific skills by index (separated by space).
              Example: '1 3' installs the first and third listed skills.
  A         : Install All skills (Default).
  H         : Show this help message.
===============================
""",
        "avail_skills": "\nAvailable Skills:",
        "install_all": "A. Install All",
        "help_opt": "H. Help",
        "enter_selection": "\nEnter numbers separated by space (e.g., '1 2') or 'A' for all [Default: A]: ",
        "warn_out_of_range": "Warning: Number '{0}' is out of range.",
        "warn_not_number": "Warning: '{0}' is not a number.",
        "selected": "Selected: {0}",
        "no_valid_selection": "No valid skills selected.",
        "invalid_input": "Invalid input format.",
        "remote_cats": "\n=== Remote Categories ===",
        "quit_opt": "q. Quit",
        "select_cat": "\nSelect Category (Number): ",
        "invalid_num": "Invalid number.",
        "invalid_input_short": "Invalid input.",
        "skills_in_cat": "\n=== Skills in '{0}' ===",
        "already_in_config": "\n(* = Already in configuration)",
        "enter_install_nums": "Enter numbers to install (e.g. '1 3') or 'b' to back.",
        "selection_prompt": "Selection: ",
        "fetching_list": "Fetching remote skill list...",
        "no_skills_remote": "No skills found in the remote repository structure (plugins/*/skills/*).",
        "no_skills_sel": "No skills selected.",
        "choose_action": "\nChoose Action:",
        "act_install_only": "1. Install Only (Do not update skills.json)",
        "act_install_config": "2. Install and Add to Configuration (Update skills.json)",
        "enter_choice_short": "Enter choice (1/2) [Default: 1]: ",
        "loc_display": "\nLocation: {0}", 
        "processing": "\nProcessing {0}...",
        "removing_existing": "  Removing existing installation...",
        "installed_to": "  ✓ Installed to {0}",
        "added_to_config": "  Added '{0}' to configuration.",
        "err_installing": "  Error installing {0}: {1}",
        "config_saved": "\nConfiguration saved to skills.json.",
        "warn_save_config": "Warning: Could not save configuration: {0}",
        "browse_header": "=== Browse Remote Skills ===",
        "manager_header": "=== Skills Manager ===",
        "checking_updates": "Checking for updates on installed skills...",
        "no_skills_update": "No known skills found in this location to update.",
        "found_skills": "Found skills: {0}",
        "done": "\n---------------------------------------------------------\nDone."
    },
    "zh": {
        "config_not_found": "错误：未找到 skills.json。",
        "select_install_loc": "\n请选择安装位置：",
        "loc_global": "1. [全局] VS Code 用户文件夹 (~/.vscode/skills)",
        "loc_project": "2. [项目] 当前工作区 (./skills)",
        "loc_claude": "3. [Claude] Claude Desktop (APPDATA/Claude/skills)",
        "loc_custom": "4. [自定义] 输入自定义路径",
        "enter_choice": "输入选择 (1/2/3/4) [默认: 2]: ",
        "enter_path": "输入绝对路径：",
        "err_run_cmd": "执行命令出错：{0}",
        "installed": "✓ {0} 已安装。",
        "not_installed": "✗ {0} 未安装。",
        "installing_pkg": "正在安装 {0}...",
        "check_deps": "  正在检查 {0} 的依赖...",
        "found_reqs": "  发现 requirements.txt。正在安装...",
        "installing_dbt": "  正在安装 dbt-core...",
        "installing_sqlfluff": "  正在安装 sqlfluff (SQL 代码检查)...",
        "created_dir": "已创建目录：{0}",
        "err_create_dir": "创建目录 {0} 失败：{1}",
        "fetching_repo": "\n正在从仓库获取最新 Skills...",
        "failed_clone": "克隆仓库失败。请检查网络连接或 Git 安装。",
        "warn_skill_not_found": "警告：配置中未找到 Skill '{0}'。",
        "err_source_not_found": "错误：在 {1} 找不到 '{0}' 源文件",
        "found_existing": "发现 {0} 的现有安装",
        "updating": "正在更新",
        "installing": "正在安装",
        "processed_success": "✓ 成功处理 {0}。",
        "failed_copy": "复制 {0} 失败：{1}",
        "interactive_help": """
=== 交互式命令帮助 ===
选项:
  <数字> : 通过索引选择特定 Skills（用空格分隔）。
           例如：'1 3' 安装列表中的第1和第3个 Skill。
  A      : 安装所有 Skills（默认）。
  H      : 显示此帮助信息。
===============================
""",
        "avail_skills": "\n可用 Skills：",
        "install_all": "A. 安装所有",
        "help_opt": "H. 帮助",
        "enter_selection": "\n输入数字（用空格分隔，如 '1 2'）或 'A' 代表所有 [默认: A]: ",
        "warn_out_of_range": "警告：数字 '{0}' 超出范围。",
        "warn_not_number": "警告：'{0}' 不是数字。",
        "selected": "已选择：{0}",
        "no_valid_selection": "未选择有效 Skill。",
        "invalid_input": "输入格式无效。",
        "remote_cats": "\n=== 远程分类 ===",
        "quit_opt": "q. 退出",
        "select_cat": "\n选择分类 (数字): ",
        "invalid_num": "无效数字。",
        "invalid_input_short": "无效输入。",
        "skills_in_cat": "\n=== '{0}' 分类下的 Skills ===",
        "already_in_config": "\n(* = 已在配置中)",
        "enter_install_nums": "输入要安装的数字（如 '1 3'）或 'b' 返回。",
        "selection_prompt": "选择: ",
        "fetching_list": "正在获取远程 Skill 列表...",
        "no_skills_remote": "在远程仓库结构 (plugins/*/skills/*) 中未找到 Skills。",
        "no_skills_sel": "未选择 Skills。",
        "choose_action": "\n选择操作：",
        "act_install_only": "1. 仅安装 (不更新 skills.json)",
        "act_install_config": "2. 安装并添加到配置 (更新 skills.json)",
        "enter_choice_short": "输入选择 (1/2) [默认: 1]: ",
        "loc_display": "\n位置：{0}", 
        "processing": "\n正在处理 {0}...",
        "removing_existing": "  正在移除现有安装...",
        "installed_to": "  ✓ 已安装至 {0}",
        "added_to_config": "  已将 '{0}' 添加到配置。",
        "err_installing": "  安装 {0} 出错：{1}",
        "config_saved": "\n配置已保存至 skills.json。",
        "warn_save_config": "警告：无法保存配置：{0}",
        "browse_header": "=== 浏览远程 Skills ===",
        "manager_header": "=== Skills 管理器 ===",
        "checking_updates": "正在检查已安装 Skills 的更新...",
        "no_skills_update": "此处未找到已知的 Skills 可供更新。",
        "found_skills": "发现 Skills：{0}",
        "done": "\n---------------------------------------------------------\n完成。"
    }
}

def get_language():
    """Detect system language."""
    # Check env var first
    env_lang = os.environ.get("SKILL_LANG")
    if env_lang:
        if env_lang.startswith("zh"): return "zh"
        return "en"
    
    # Check system locale
    try:
        sys_lang = locale.getdefaultlocale()[0]
        if sys_lang and sys_lang.startswith("zh"):
            return "zh"
    except:
        pass
    return "en"

CURRENT_LANG = get_language()

def t(key, *args):
    """Get localized text."""
    lang_dict = TEXTS.get(CURRENT_LANG, TEXTS["en"])
    text = lang_dict.get(key, TEXTS["en"].get(key, key))
    if args:
        return text.format(*args)
    return text

# Load Configuration
def load_config():
    config_path = Path(__file__).parent / "skills.json"
    if not config_path.exists():
        print(t("config_not_found"))
        sys.exit(1)
    with open(config_path, "r") as f:
        return json.load(f)

CONFIG = load_config()
SKILLS_REPO = CONFIG["repo_url"]
SKILLS_MAPPING = CONFIG["skills"]

def get_target_directory():
    """Ask user for installation directory."""
    print(t("select_install_loc"))
    print(t("loc_global"))
    print(t("loc_project"))
    print(t("loc_claude"))
    print(t("loc_custom"))
    print(t("quit_opt"))
    
    choice = input(t("enter_choice")).strip()
    if choice.lower() == 'q':
        sys.exit(0)
    
    if choice == "1":
        # Windows: %USERPROFILE%\.vscode\skills, Linux/Mac: ~/.vscode/skills
        return Path.home() / ".vscode" / "skills"
    elif choice == "3":
        # Claude Desktop location
        if sys.platform == "win32":
            app_data = os.environ.get("APPDATA")
            base = Path(app_data) if app_data else Path.home() / "AppData" / "Roaming"
            return base / "Claude" / "skills"
        elif sys.platform == "darwin":
            return Path.home() / "Library" / "Application Support" / "Claude" / "skills"
        else:
             return Path.home() / ".config" / "Claude" / "skills"
    elif choice == "4":
        custom_path = input(t("enter_path")).strip()
        if custom_path.lower() == 'q':
            sys.exit(0)
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
        print(t("err_run_cmd", command))
        if capture_output:
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
        raise

def check_installed(tool_name, check_command):
    """Check if a tool is installed."""
    try:
        subprocess.run(check_command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(t("installed", tool_name))
        return True
    except subprocess.CalledProcessError:
        print(t("not_installed", tool_name))
        return False

def install_python_package(package_name):
    """Install a Python package using pip."""
    print(t("installing_pkg", package_name))
    # Use quotes around sys.executable to handle paths with spaces
    run_command(f'"{sys.executable}" -m pip install {package_name}')

def manage_dependencies(skill_name, skill_path):
    """Check and install dependencies for a skill."""
    print(t("check_deps", skill_name))
    
    # Generic requirements.txt check
    req_file = skill_path / "requirements.txt"
    if req_file.exists():
        print(t("found_reqs"))
        run_command(f'"{sys.executable}" -m pip install -r requirements.txt', cwd=skill_path)
    
    # Specific tool checks based on skill name mapping or config
    # Ideally this should also be in skills.json, but keeping hardcoded logic for now as per previous known logic
    if "dbt-transformation-patterns" in skill_name:
        if not check_installed("dbt", "dbt --version"):
            print(t("installing_dbt"))
            install_python_package("dbt-core")
    
    elif "sql-optimization-patterns" in skill_name:
        if not check_installed("sqlfluff", "sqlfluff --version"):
            print(t("installing_sqlfluff"))
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
            print(t("created_dir", target_dir))
        except Exception as e:
            print(t("err_create_dir", target_dir, e))
            return

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(t("fetching_repo"))
        print(f"Repository: {SKILLS_REPO}")
        
        # Git clone (shallow) to get latest version
        try:
            run_command(f"git clone --depth 1 {SKILLS_REPO} .", cwd=temp_path, capture_output=True)
        except Exception:
            print(t("failed_clone"))
            return

        skills_to_process = specific_skills if specific_skills else SKILLS_MAPPING.keys()

        for skill_name in skills_to_process:
            if skill_name not in SKILLS_MAPPING:
                print(t("warn_skill_not_found", skill_name))
                continue

            repo_path = SKILLS_MAPPING[skill_name]
            source_path = temp_path / repo_path
            dest_path = target_dir / skill_name
            
            if not source_path.exists():
                print(t("err_source_not_found", skill_name, source_path))
                continue
                
            action = t("installing")
            if dest_path.exists():
                # Simple update check: We just overwrite for now as 'Updating'
                # A more complex check would compare hash or timestamp, but overwrite ensures latest state.
                action = t("updating")
                print(t("found_existing", skill_name))
                shutil.rmtree(dest_path)
            
            print(f"{action} {skill_name}...")
            try:
                shutil.copytree(source_path, dest_path)
                print(t("processed_success", skill_name))
                manage_dependencies(skill_name, dest_path)
            except Exception as e:
                print(t("failed_copy", skill_name, e))

def show_interactive_help():
    print(t("interactive_help"))

def select_skills(skills_mapping):
    """Interactive skill selection."""
    skills_list = list(skills_mapping.keys())
    while True:
        print(t("avail_skills"))
        for idx, name in enumerate(skills_list, 1):
            print(f"{idx}. {name}")
        print(t("install_all"))
        print(t("help_opt"))
        print(t("quit_opt"))
        
        selection = input(t("enter_selection")).strip()
        
        if selection.upper() == 'Q':
            sys.exit(0)

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
                        print(t("warn_out_of_range", part))
                except ValueError:
                    print(t("warn_not_number", part))
            
            if selected_keys:
                print(t("selected", ', '.join(selected_keys)))
                return selected_keys
            else:
                print(t("no_valid_selection"))
        except ValueError:
            print(t("invalid_input"))

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

def browse_categories_and_skills(skills):
    """
    Interactive selection of category and then skills.
    
    Args:
        skills (list): List of skill dictionaries.

    Returns:
        list: Selected skill dictionaries.
    """
    categories = sorted(list(set(s['category'] for s in skills)))
    
    while True:
        print(t("remote_cats"))
        for idx, cat in enumerate(categories, 1):
            print(f"{idx}. {cat}")
        print(t("quit_opt"))

        cat_selection = input(t("select_cat")).strip()
        if cat_selection.lower() == 'q':
            return []

        try:
            cat_idx = int(cat_selection) - 1
            if not (0 <= cat_idx < len(categories)):
                print(t("invalid_num"))
                continue
        except ValueError:
            print(t("invalid_input_short"))
            continue
        
        selected_category = categories[cat_idx]
        category_skills = sorted([s for s in skills if s['category'] == selected_category], key=lambda x: x['name'])
        
        print(t("skills_in_cat", selected_category))
        for idx, skill in enumerate(category_skills, 1):
            installed_mark = "* " if skill['name'] in SKILLS_MAPPING else "  "
            print(f"{idx}. {installed_mark}{skill['name']}")
        
        print(t("already_in_config"))
        print(t("enter_install_nums"))
        
        skill_selection = input(t("selection_prompt")).strip()
        if skill_selection.lower() == 'q':
            sys.exit(0)
        if skill_selection.lower() == 'b':
            continue
            
        selected_skills_to_return = []
        try:
            parts = skill_selection.split()
            valid = True
            for part in parts:
                idx = int(part) - 1
                if 0 <= idx < len(category_skills):
                    selected_skills_to_return.append(category_skills[idx])
                else:
                    print(t("warn_out_of_range", part))
                    valid = False
            
            if valid and selected_skills_to_return:
                return selected_skills_to_return
        except ValueError:
             print(t("invalid_input_short"))

def browse_and_install_remote_skills(target_dir):
    """List remote skills and allow interactive installation."""
    print(t("fetching_list"))
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        try:
             run_command(f"git clone --depth 1 {SKILLS_REPO} .", cwd=temp_path, capture_output=True)
        except Exception:
            print(t("failed_clone"))
            return

        skills = discover_skills(temp_path)
        if not skills:
            print(t("no_skills_remote"))
            return
        
        selected_skills = browse_categories_and_skills(skills)
        if not selected_skills:
            print(t("no_skills_sel"))
            return

        # Ask user next action
        print(t("choose_action"))
        print(t("act_install_only"))
        print(t("act_install_config"))
        print(t("quit_opt"))
        
        action_choice = input(t("enter_choice_short")).strip()
        if action_choice.lower() == 'q':
            sys.exit(0)
        
        save_to_config = (action_choice == '2')

        # If target_dir was not provided initially, ask for it now
        if target_dir is None:
             target_dir = get_target_directory()
             print(t("loc_display", target_dir))

        # Create target dir if not exists
        if not target_dir.exists():
             target_dir.mkdir(parents=True)

        config_changed = False
        for skill in selected_skills:
            print(t("processing", skill['name']))
            
            dest_path = target_dir / skill['name']
            source_path = temp_path / skill['path']
            
            if dest_path.exists():
                print(t("removing_existing"))
                shutil.rmtree(dest_path)
            
            try:
                shutil.copytree(source_path, dest_path)
                print(t("installed_to", dest_path))
                manage_dependencies(skill['name'], dest_path)
                
                # Update mapping
                if save_to_config and skill['name'] not in SKILLS_MAPPING:
                    SKILLS_MAPPING[skill['name']] = skill['path']
                    config_changed = True
                    print(t("added_to_config", skill['name']))
            except Exception as e:
                print(t("err_installing", skill['name'], e))

        if config_changed:
            config_path = Path(__file__).parent / "skills.json"
            try:
                CONFIG["skills"] = SKILLS_MAPPING
                with open(config_path, "w") as f:
                    json.dump(CONFIG, f, indent=4)
                print(t("config_saved")) 
            except Exception as e:
                print(t("warn_save_config", e))

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
  python install_skills.py --upgrade                   # Update currently installed skills
  python install_skills.py --ls                        # Browse and install new skills from remote
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--global-install", action="store_true", help="Install to global VS Code folder (~/.vscode/skills)")
    parser.add_argument("--project-install", action="store_true", help="Install to current project folder (./skills)")
    parser.add_argument("--claude-install", action="store_true", help="Install to Claude Desktop folder")
    parser.add_argument("--upgrade", action="store_true", help="Check and update all installed skills")
    parser.add_argument("--ls", action="store_true", help="Browse available remote skills interactively")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip interactive confirmation (installs all)")
    parser.add_argument("--lang", help="Specify language (en/zh)", choices=["en", "zh"])
    args = parser.parse_args()

    # Override Language if specified
    if args.lang:
        global CURRENT_LANG
        CURRENT_LANG = args.lang

    # Determine Target Directory
    target_dir = None
    if args.global_install:
        target_dir = Path.home() / ".vscode" / "skills"
    elif args.project_install:
        target_dir = Path(os.getcwd()) / "skills"
    elif args.claude_install:
        if sys.platform == "win32":
            app_data = os.environ.get("APPDATA")
            base = Path(app_data) if app_data else Path.home() / "AppData" / "Roaming"
            target_dir = base / "Claude" / "skills"
        elif sys.platform == "darwin":
            target_dir = Path.home() / "Library" / "Application Support" / "Claude" / "skills"
        else:
            target_dir = Path.home() / ".config" / "Claude" / "skills"
    else:
        # Check context
        if args.ls:
             print(t("browse_header"))
             # We do NOT ask for target_dir yet for ls command, unless it was passed as arg
             pass
        elif not args.upgrade:
             # Default install mode
             print(t("manager_header"))
             target_dir = get_target_directory()
        # If upgrade is true, we fall through to below default

    # Only enforce target_dir if we are NOT in ls mode or upgrade mode with no dir logic
    # Actually, upgrade needs a target dir.
    # ls mode will ask for it inside if needed.
    if target_dir is None and not args.ls: 
        target_dir = get_target_directory()

    if target_dir:
        print(t("loc_display", target_dir))

    # Operations
    if args.ls:
        browse_and_install_remote_skills(target_dir)
    elif args.upgrade:
        print(t("checking_updates"))
        # Identify which skills are currently installed in the target dir
        installed_skills = []
        if target_dir.exists():
            for item in target_dir.iterdir():
                if item.is_dir() and item.name in SKILLS_MAPPING:
                    installed_skills.append(item.name)
        
        if not installed_skills:
            print(t("no_skills_update"))
        else:
            print(t("found_skills", ", ".join(installed_skills)))
            update_or_install_skills(target_dir, specific_skills=installed_skills, auto_update=True)
    else:
        # Selection logic
        selected_skills = None
        if not args.yes:
            selected_skills = select_skills(SKILLS_MAPPING)
        
        update_or_install_skills(target_dir, specific_skills=selected_skills, auto_update=True)

    print(t("done"))

if __name__ == "__main__":
    main()
