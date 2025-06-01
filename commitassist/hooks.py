"""
Git Hooks Management for Commit Assistant

This module handles the installation, removal, and status checking of Git hooks
for the Commit Assistant tool. It supports both local repository hooks and
global hooks that work across all repositories.
"""

import os
import platform
import subprocess
import git


def install_git_hook():
    """
    Install Commit Assistant as a Git hook.
    
    Creates a prepare-commit-msg hook that automatically suggests commit messages.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Check if we're in a Git repository
        repo = git.Repo(".")
        
        # Path to Git hooks directory
        hooks_dir = os.path.join(repo.git_dir, 'hooks')
        
        # Make sure hooks directory exists
        os.makedirs(hooks_dir, exist_ok=True)
        
        # Path to prepare-commit-msg hook
        hook_path = os.path.join(hooks_dir, 'prepare-commit-msg')
        
        # Check if hook already exists
        if os.path.exists(hook_path):
            return False, f"Git hook already exists at: {hook_path}"
        
        # Determine if we're in development mode or installed mode
        commit_command = _get_commit_command()
        
        # Create the hook script content
        hook_content = _create_hook_script(commit_command, is_global=False)
        
        # Write the hook file
        _write_hook_file(hook_path, hook_content)
        
        return True, f"Git hook installed successfully at: {hook_path}"
        
    except git.exc.InvalidGitRepositoryError:
        return False, "Current directory is not a Git repository."
    except Exception as e:
        return False, f"Error installing Git hook: {str(e)}"


def uninstall_git_hook():
    """
    Remove the Commit Assistant Git hook.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Check if we're in a Git repository
        repo = git.Repo(".")
        
        # Path to prepare-commit-msg hook
        hook_path = os.path.join(repo.git_dir, 'hooks', 'prepare-commit-msg')
        
        if not os.path.exists(hook_path):
            return False, "No commit-assistant hook found to remove."
        
        # Check if it's our hook by looking for our signature
        if not _is_our_hook(hook_path):
            return False, "Hook exists but was not created by commit-assistant. Won't remove it."
        
        # Remove the hook
        os.remove(hook_path)
        
        return True, f"Git hook removed successfully from: {hook_path}"
        
    except git.exc.InvalidGitRepositoryError:
        return False, "Current directory is not a Git repository."
    except Exception as e:
        return False, f"Error removing Git hook: {str(e)}"


def check_git_hook_status():
    """
    Check if the Commit Assistant Git hook is installed and working.
    
    Returns:
        dict: Status information about the hook
    """
    try:
        # Check if we're in a Git repository
        repo = git.Repo(".")
        
        # Path to prepare-commit-msg hook
        hook_path = os.path.join(repo.git_dir, 'hooks', 'prepare-commit-msg')
        
        status = {
            'hook_exists': os.path.exists(hook_path),
            'hook_path': hook_path,
            'is_our_hook': False,
            'is_executable': False,
            'git_repo': True
        }
        
        if status['hook_exists']:
            status['is_our_hook'] = _is_our_hook(hook_path)
            
            # Check if it's executable
            try:
                status['is_executable'] = os.access(hook_path, os.X_OK)
            except:
                status['is_executable'] = False
        
        return status
        
    except git.exc.InvalidGitRepositoryError:
        return {
            'hook_exists': False,
            'hook_path': None,
            'is_our_hook': False,
            'is_executable': False,
            'git_repo': False
        }
    except Exception as e:
        return {
            'hook_exists': False,
            'hook_path': None,
            'is_our_hook': False,
            'is_executable': False,
            'git_repo': False,
            'error': str(e)
        }


def install_global_git_hook():
    """
    Install Commit Assistant as a global Git hook for all repositories.
    
    This sets up a global hooks directory that Git will use for all repos.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Create a global hooks directory
        global_hooks_dir = _get_global_hooks_dir()
        os.makedirs(global_hooks_dir, exist_ok=True)
        
        # Path to global prepare-commit-msg hook
        hook_path = os.path.join(global_hooks_dir, 'prepare-commit-msg')
        
        # Determine the correct command to use
        commit_command = _get_commit_command()
        
        # Create the global hook script
        hook_content = _create_hook_script(commit_command, is_global=True)
        
        # Write the hook file
        _write_hook_file(hook_path, hook_content)
        
        # Configure Git to use the global hooks directory
        result = subprocess.run([
            'git', 'config', '--global', 'core.hooksPath', global_hooks_dir
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            return False, f"Failed to configure global hooks: {result.stderr}"
        
        return True, f"Global Git hook installed at: {hook_path}"
        
    except Exception as e:
        return False, f"Error installing global Git hook: {str(e)}"


def uninstall_global_git_hook():
    """
    Remove the global Git hook configuration.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Remove the global hooks configuration
        subprocess.run([
            'git', 'config', '--global', '--unset', 'core.hooksPath'
        ], capture_output=True, text=True)
        
        # Try to remove the hooks directory
        global_hooks_dir = _get_global_hooks_dir()
        hook_path = os.path.join(global_hooks_dir, 'prepare-commit-msg')
        
        removed_hook = False
        if os.path.exists(hook_path) and _is_our_hook(hook_path):
            os.remove(hook_path)
            removed_hook = True
        
        # Remove directory if empty
        try:
            if os.path.exists(global_hooks_dir) and not os.listdir(global_hooks_dir):
                os.rmdir(global_hooks_dir)
        except:
            pass
        
        if removed_hook:
            return True, "Global Git hook removed successfully"
        else:
            return True, "Global Git hooks configuration reset"
            
    except Exception as e:
        return False, f"Error removing global Git hook: {str(e)}"


def check_global_hook_status():
    """
    Check if global Git hooks are configured.
    
    Returns:
        dict: Status information about global hooks
    """
    try:
        # Check if global hooks path is configured
        result = subprocess.run([
            'git', 'config', '--global', 'core.hooksPath'
        ], capture_output=True, text=True)
        
        global_hooks_configured = result.returncode == 0
        global_hooks_path = result.stdout.strip() if global_hooks_configured else None
        
        # Check if our hook exists
        expected_hooks_dir = _get_global_hooks_dir()
        hook_path = os.path.join(expected_hooks_dir, 'prepare-commit-msg')
        
        hook_exists = os.path.exists(hook_path)
        is_our_hook = hook_exists and _is_our_hook(hook_path)
        
        return {
            'global_hooks_configured': global_hooks_configured,
            'global_hooks_path': global_hooks_path,
            'expected_path': expected_hooks_dir,
            'hook_exists': hook_exists,
            'is_our_hook': is_our_hook,
            'hook_path': hook_path
        }
        
    except Exception as e:
        return {
            'global_hooks_configured': False,
            'global_hooks_path': None,
            'expected_path': None,
            'hook_exists': False,
            'is_our_hook': False,
            'hook_path': None,
            'error': str(e)
        }


# Private helper functions

def _get_commit_command():
    """
    Determine the correct command to use for calling commit-assistant.
    
    Returns:
        str: The command to use (either 'commit-assistant' or 'python -m commitassist.main')
    """
    try:
        # Test if commit-assistant command is available (installed mode)
        result = subprocess.run(['commit-assistant', '--help'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return "commit-assistant"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # Fall back to development mode
    return "python -m commitassist.main"


def _get_global_hooks_dir():
    """
    Get the path to the global hooks directory.
    
    Returns:
        str: Path to the global hooks directory
    """
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, '.git-hooks')


def _create_hook_script(commit_command, is_global=False):
    """
    Create the hook script content with intelligent suggestion selection.
    
    Args:
        commit_command (str): The command to use for calling commit-assistant
        is_global (bool): Whether this is a global hook
        
    Returns:
        str: The hook script content
    """
    hook_type = "Global Git hook" if is_global else "Git hook"
    global_indicator = " global hook" if is_global else ""
    
    hook_content = f"""#!/bin/sh
# {hook_type} to suggest commit messages
# Generated by commit-assistant (Smart Hook)

# Only run if no commit message is provided (not from merge, template, etc.)
if [ -z "$2" ]; then
    # Check if commit-assistant is available
    if command -v {commit_command.split()[0]} >/dev/null 2>&1; then
        
        # Smart detection: Analyze the size and complexity of changes
        LINES_CHANGED=$(git diff --cached --stat | tail -n 1 | grep -o '[0-9]\\+ insertion\\|[0-9]\\+ deletion' | grep -o '[0-9]\\+' | awk '{{sum += $1}} END {{print sum + 0}}')
        FILES_CHANGED=$(git diff --cached --name-only | wc -l)
        
        # Default to simple suggestions
        SUGGESTION_TYPE=""
        
        # Use detailed suggestions for:
        # - More than 50 lines changed OR
        # - More than 3 files changed OR  
        # - New files being added OR
        # - Significant file types (py, js, ts, etc.)
        if [ "$LINES_CHANGED" -gt 50 ] || [ "$FILES_CHANGED" -gt 3 ]; then
            SUGGESTION_TYPE="--detailed"
        else
            # Check for new files
            NEW_FILES=$(git diff --cached --name-status | grep "^A" | wc -l)
            if [ "$NEW_FILES" -gt 0 ]; then
                SUGGESTION_TYPE="--detailed"
            else
                # Check for important file types
                IMPORTANT_FILES=$(git diff --cached --name-only | grep -E "\\.(py|js|ts|jsx|tsx|java|cpp|c|h|php|rb|go|rs|swift)$" | wc -l)
                if [ "$IMPORTANT_FILES" -gt 0 ] && [ "$LINES_CHANGED" -gt 20 ]; then
                    SUGGESTION_TYPE="--detailed"
                fi
            fi
        fi
        
        # Get the appropriate suggestion
        SUGGESTED=$({commit_command} suggest $SUGGESTION_TYPE --count 1 2>/dev/null)
        
        # Check if we got a valid suggestion
        if [ $? -eq 0 ] && [ -n "$SUGGESTED" ]; then
            # Extract the message (handle both simple and detailed formats)
            if echo "$SUGGESTED" | grep -q "====="; then
                # Detailed format - extract everything between === lines
                MESSAGE=$(echo "$SUGGESTED" | sed -n '/=====/,/=====/{{/=====/d; p;}}' | sed '/^$/d')
                echo "# Smart AI Suggested commit message (detailed):" >> "$1"
                echo "#" >> "$1"
                # Add each line of the detailed message as comments
                echo "$MESSAGE" | while IFS= read -r line; do
                    if [ -n "$line" ]; then
                        echo "# $line" >> "$1"
                    else
                        echo "#" >> "$1"
                    fi
                done
                echo "#" >> "$1"
                echo "# Remove the '#' from the lines above to use this suggestion" >> "$1"
            else
                # Simple format
                MESSAGE=$(echo "$SUGGESTED" | grep -A 1 "\\[1\\]" | tail -n 1 | sed 's/^[[:space:]]*//')
                if [ -n "$MESSAGE" ] && [ "$MESSAGE" != "Analyzing staged changes..." ]; then
                    echo "# Smart AI Suggested commit message (simple):" >> "$1"
                    echo "# $MESSAGE" >> "$1"
                    echo "#" >> "$1"
                    echo "# Remove the '#' above to use this suggestion" >> "$1"
                fi
            fi
            echo "# Generated by commit-assistant{global_indicator}" >> "$1"
            echo "#" >> "$1"
        else
            echo "# commit-assistant suggestion unavailable" >> "$1"
            echo "#" >> "$1"
        fi
    else
        echo "# commit-assistant not found - install for AI suggestions" >> "$1"
        echo "#" >> "$1"
    fi
fi
"""
    
    return hook_content


def _write_hook_file(hook_path, hook_content):
    """
    Write the hook content to a file and make it executable.
    """
    # Convert Windows line endings to Unix for compatibility
    hook_content = hook_content.replace('\r\n', '\n')
    
    # Write with UTF-8 encoding
    with open(hook_path, 'w', newline='\n', encoding='utf-8') as f:
        f.write(hook_content)
    
    # Make executable
    try:
        os.chmod(hook_path, 0o755)
    except:
        pass


def _is_our_hook(hook_path):
    """
    Check if a hook file was created by commit-assistant.
    
    Args:
        hook_path (str): Path to the hook file
        
    Returns:
        bool: True if the hook was created by commit-assistant
    """
    try:
        with open(hook_path, 'r') as f:
            content = f.read()
        return "Generated by commit-assistant" in content
    except:
        return False