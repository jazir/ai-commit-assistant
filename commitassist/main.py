import os
import sys
import git
import platform
import subprocess
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import click
import time
import random
import re
import string

# Import hook functions from the hooks module
from . import hooks

# Load environment variables from a .env file if present
# This allows users to store their API keys securely
load_dotenv()

# Initialize the OpenAI client with the API key from environment variables
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_openai_client():
    """
    Get OpenAI client with lazy initialization and API key validation.
    
    Returns:
        OpenAI: Configured OpenAI client
        
    Raises:
        SystemExit: If API key is not found
    """
    # Try to load environment variables again in case they were set after import
    home_env_path = os.path.join(os.path.expanduser("~"), '.commit-assistant', '.env')
    if os.path.exists(home_env_path):
        load_dotenv(home_env_path, override=True)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not api_key.strip():
        click.echo("OpenAI API key not found.", err=True)
        click.echo("Please run: ai-commit-assistant setup", err=True)
        click.echo("Or set environment variable: OPENAI_API_KEY=your_key", err=True)
        click.echo("Get your API key from: https://platform.openai.com/api-keys", err=True)
        sys.exit(1)
    
    return OpenAI(api_key=api_key.strip())


def get_git_diff():
    """
    Get the current git diff for staged files.
    
    Returns:
        tuple: (diff_text, list_of_files) if successful, or (None, error_message) if failed
    """
    try:
        # Open the current directory as a Git repository
        repo = git.Repo(".")
        
        # Check if there are any staged changes (files added to index)
        staged_files = repo.index.diff("HEAD")
        
        if not staged_files:
            # No changes are staged, return an error message
            return None, "No staged changes found. Use 'git add <files>' to stage changes."
        
        # Get diff for staged changes (--cached shows only staged changes)
        diff = repo.git.diff("--cached")
        
        # If diff is empty but we have staged files, there might be new files
        if not diff.strip():
            # Try to get diff including new files
            diff = repo.git.diff("--cached", "--no-prefix")
        
        # Get the list of changed file paths
        changed_files = []
        
        # Get staged files (modified existing files)
        for item in staged_files:
            changed_files.append(item.a_path or item.b_path)
            # DEBUG: Print what files we detected
            # print(f"DEBUG: Staged files detected: {changed_files}")
            # print(f"DEBUG: Diff length: {len(diff)} characters")
            # print(f"DEBUG: First 200 chars of diff: {diff[:200]}")
            
        # Also check for new files that are staged
        try:
            # Get files that are staged but not in HEAD (new files)
            new_files = repo.git.diff("--cached", "--name-only", "--diff-filter=A").splitlines()
            for new_file in new_files:
                if new_file not in changed_files:
                    changed_files.append(new_file)
        except:
            pass
                
        # If we still don't have a diff, try a different approach
        if not diff.strip() and changed_files:
            # For new files, git diff --cached might be empty
            # Let's try to get the content of new files
            try:
                diff = repo.git.diff("--cached", "--", *changed_files)
            except:
                # Fallback: just indicate that files were added
                diff = f"New files added: {', '.join(changed_files)}"
        
        return diff, changed_files
        
    except git.exc.InvalidGitRepositoryError:
        # Not a git repository
        return None, "Current directory is not a Git repository."
    except git.exc.GitCommandError as e:
        # Git command failed
        return None, f"Git error: {str(e)}"
    except Exception as e:
        # Catch any other errors
        return None, f"Error: {str(e)}"


def detect_file_types(files):
    """
    Analyze the file types to provide language-specific context.
    
    Args:
        files (list): List of file paths
        
    Returns:
        tuple: (list of languages, dict of extensions counts)
    """
    extensions = {}
    
    # Count file extensions
    for file in files:
        # Get the file extension (lowercase for consistency)
        ext = os.path.splitext(file)[1].lower()
        if ext:
            # Count occurrences of each extension
            extensions[ext] = extensions.get(ext, 0) + 1
    
    # Map extensions to common programming languages
    languages = []
    if '.py' in extensions:
        languages.append('Python')
    if '.js' in extensions:
        languages.append('JavaScript')
    if '.ts' in extensions:
        languages.append('TypeScript')
    if '.jsx' in extensions or '.tsx' in extensions:
        languages.append('React')
    if '.html' in extensions or '.css' in extensions:
        languages.append('Web')
    if '.json' in extensions or '.yml' in extensions or '.yaml' in extensions:
        languages.append('Config')
    if '.md' in extensions or '.txt' in extensions:
        languages.append('Documentation')
    
    return languages, extensions


def get_repo_context(files, max_commits=5):
    """
    Get contextual information about the repository to improve AI suggestions.
    
    Args:
        files (list): List of file paths
        max_commits (int): Maximum number of recent commits to analyze
        
    Returns:
        dict: Repository context information
    """
    try:
        repo = git.Repo(".")
        
        # Try to get repository name from remote URL
        try:
            remote_url = repo.remotes.origin.url
            # Extract repo name from URL (e.g., 'user/repo.git' -> 'repo')
            repo_name = os.path.basename(remote_url)
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]  # Remove .git suffix
        except:
            # Fallback to directory name if remote not available
            repo_name = os.path.basename(os.path.abspath("."))
        
        # Get recent commits for the changed files
        recent_commits = []
        
        # For each file, get recent commits
        for file_path in files:
            try:
                # Get up to 'max_commits' recent commits for this file
                file_commits = list(repo.iter_commits(paths=file_path, max_count=max_commits))
                
                for commit in file_commits:
                    # Add commit information to our list
                    recent_commits.append({
                        'file': file_path,
                        'message': commit.message.strip(),
                        'hash': commit.hexsha[:7]  # Short hash
                    })
            except:
                # Skip if we can't get commits for this file
                continue
        
        # Get repository branches
        try:
            current_branch = repo.active_branch.name
        except:
            current_branch = "Unknown"
            
        return {
            'name': repo_name,
            'branch': current_branch,
            'recent_commits': recent_commits
        }
        
    except Exception as e:
        # Return minimal context if we encounter any errors
        return {
            'name': os.path.basename(os.path.abspath(".")),
            'branch': "Unknown",
            'recent_commits': []
        }


def generate_commit_message(diff, files, temperature=0.7, max_retries=3):
    """
    Generate a commit message using OpenAI's API with retry logic.
    
    Args:
        diff (str): The git diff text
        files (list): List of changed files
        temperature (float): Controls randomness in AI response (0.0-1.0)
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        str: Generated commit message or error message
    """
    if not diff:
        return "No changes to analyze."
    
    # Get file types to provide context about programming languages
    languages, extensions = detect_file_types(files)
    
    # Get repository context for better suggestions
    repo_context = get_repo_context(files)
    
    # Format context information for the prompt
    context = f"""
    Repository: {repo_context['name']}
    Branch: {repo_context['branch']}
    
    Languages detected: {', '.join(languages) if languages else 'None specifically identified'}
    """
    
    # Add recent commit history if available (but clean it up)
    if repo_context['recent_commits']:
        context += "\nRecent commit message patterns:\n"
        # List up to 3 recent commits for style reference, but remove hashes
        for i, commit in enumerate(repo_context['recent_commits'][:3]):
            # Clean the commit message - remove any hash patterns
            clean_message = commit['message'].split('(')[0].strip()  # Remove anything in parentheses
            context += f"- {clean_message}\n"
    
    # Prepare a system message that instructs the AI how to generate commit messages
    system_message = """
    You are a git commit message generator that follows best practices. Generate concise, meaningful commit messages that:
    
    1. Use the conventional commits format when appropriate (type: description)
    2. Start with a verb in imperative mood (e.g., "Add", "Fix", "Update", "Refactor")
    3. Are concise but descriptive (under 72 characters for the first line)
    4. Focus on the "why" and "what" rather than the "how"
    5. Match the project's existing commit style if examples are provided
    6. NEVER include commit hashes, issue numbers, or any parenthetical references unless specifically mentioned in the changes
    7. Write in present tense as if the commit is being applied now
    
    Respond ONLY with the suggested commit message text, nothing else. Do not include any metadata, hashes, or additional formatting.
    """
    
    # Create the user prompt with the diff and context
    # Smart diff handling for large changes
    if len(diff) > 5000:
        # For large diffs, show a summary of changes rather than raw diff
        diff_summary = f"Large changeset with {len(files)} files:\n"
        for file in files:
            diff_summary += f"- {file}\n"
        diff_summary += f"\nFirst 2000 chars of diff:\n{diff[:2000]}"
        diff_summary += f"\n\nLast 1000 chars of diff:\n{diff[-1000:]}"
    else:
        diff_summary = diff

    user_prompt = f"""
    Please suggest a commit message for the following changes:

    {context}

    Files changed: {', '.join(files)}

    Diff summary:
    {diff_summary}

    Generate a clean commit message without any commit hashes, issue numbers, or metadata.
    """
    
    # Retry loop for API calls
    for attempt in range(max_retries):
        try:
            # Get client with lazy initialization
            client = get_openai_client()
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Can be changed to gpt-4 for better results
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,  # Controls randomness (0.0 = deterministic, 1.0 = creative)
                max_tokens=100,  # Limit response length
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract the message from the response
            commit_message = response.choices[0].message.content.strip()
            
            # Clean up the message - remove any remaining hashes or unwanted patterns
            # Remove patterns like (abc1234) or [abc1234] or #abc1234
            import re
            commit_message = re.sub(r'\s*[\(\[]?[a-f0-9]{6,8}[\)\]]?\s*$', '', commit_message)
            commit_message = re.sub(r'\s*#[a-f0-9]{6,8}\s*', '', commit_message)
            
            return commit_message.strip()
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check for specific error types
            if "rate limit" in error_str or "too many requests" in error_str:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                    click.echo(f"Rate limit hit. Waiting {wait_time:.1f} seconds before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    return "Error: Rate limit exceeded. Please try again in a few minutes."
            
            elif "500 internal server error" in error_str or "502 bad gateway" in error_str or "503 service unavailable" in error_str:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    click.echo(f"Server error (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    return "Error: OpenAI service is currently experiencing issues. Please try again later."
            
            elif "authentication" in error_str or "api key" in error_str or "unauthorized" in error_str:
                return "Error: Invalid API key. Please check your OpenAI API key and run 'ai-commit-assistant setup' if needed."
            
            elif "quota" in error_str or "billing" in error_str:
                return "Error: OpenAI API quota exceeded. Please check your billing and usage limits."
            
            elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
                if attempt < max_retries - 1:
                    wait_time = 2 + random.uniform(0, 1)
                    click.echo(f"Network error (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    return "Error: Network connection issues. Please check your internet connection."
            
            else:
                # For unknown errors, try once more if we have retries left
                if attempt < max_retries - 1:
                    click.echo(f"Unexpected error (attempt {attempt + 1}/{max_retries}). Retrying...")
                    time.sleep(1)
                    continue
                else:
                    return f"Error generating commit message: {str(e)}"
    
    return "Error: All retry attempts failed."

def generate_detailed_commit_message(diff, files, temperature=0.7, max_retries=3):
    """
    Generate a detailed commit message with header and body using OpenAI's API with retry logic.
    
    Args:
        diff (str): The git diff text
        files (list): List of changed files
        temperature (float): Controls randomness in AI response (0.0-1.0)
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        str: Generated detailed commit message with header and body
    """
    if not diff:
        return "No changes to analyze."
    
    # Get file types to provide context about programming languages
    languages, extensions = detect_file_types(files)
    
    # Get repository context for better suggestions
    repo_context = get_repo_context(files)
    
    # Format context information for the prompt
    context = f"""
    Repository: {repo_context['name']}
    Branch: {repo_context['branch']}
    
    Languages detected: {', '.join(languages) if languages else 'None specifically identified'}
    """
    
    # Add recent commit history if available (but clean it up)
    if repo_context['recent_commits']:
        context += "\nRecent commit message patterns:\n"
        # List up to 3 recent commits for style reference, but remove hashes
        for i, commit in enumerate(repo_context['recent_commits'][:3]):
            # Clean the commit message - remove any hash patterns
            clean_message = commit['message'].split('(')[0].strip()
            context += f"- {clean_message}\n"
    
    # Prepare a system message for detailed commit messages
    system_message = """
    You are a git commit message generator that creates detailed, professional commit messages. Generate a commit message with both header and body that follows this format:

    HEADER: Brief description (under 72 characters)
    
    BODY: Detailed explanation including what was changed and why

    Guidelines:
    1. Header should use conventional commits format (type: description)
    2. Header should start with a verb in imperative mood (Add, Fix, Update, Refactor, etc.)
    3. Body should explain the changes in detail with bullet points if multiple changes
    4. Body should explain WHY the changes were made, not just what
    5. Keep lines under 72 characters wide
    6. NEVER include commit hashes, issue numbers, or metadata
    7. Use present tense as if the commit is being applied now
    8. Separate header and body with a blank line

    Example format:
    feat: Add user authentication system
    
    Implement JWT-based authentication to secure API endpoints.
    
    - Add login/logout functionality with token generation
    - Create middleware for request validation
    - Implement secure password hashing
    - Set up session management for user state
    
    This addresses security requirements and improves user experience
    by providing seamless authentication flow.

    Respond with the complete commit message in this format.
    """
    
    # Create the user prompt with the diff and context
    # Smart diff handling for large changes
    if len(diff) > 5000:
        # For large diffs, show a summary of changes rather than raw diff
        diff_summary = f"Large changeset with {len(files)} files:\n"
        for file in files:
            diff_summary += f"- {file}\n"
        diff_summary += f"\nFirst 2000 chars of diff:\n{diff[:2000]}"
        diff_summary += f"\n\nLast 1000 chars of diff:\n{diff[-1000:]}"
    else:
        diff_summary = diff

    user_prompt = f"""
    Please suggest a commit message for the following changes:

    {context}

    Files changed: {', '.join(files)}

    Diff summary:
    {diff_summary}

    Generate a clean commit message without any commit hashes, issue numbers, or metadata.
    """
    
    # Retry loop for API calls
    for attempt in range(max_retries):
        try:
            # Get client with lazy initialization
            client = get_openai_client()
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=300,  # Increased for detailed messages
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract the message from the response
            commit_message = response.choices[0].message.content.strip()
            
            # Clean up the message - remove any remaining hashes or unwanted patterns
            import re
            commit_message = re.sub(r'\s*[\(\[]?[a-f0-9]{6,8}[\)\]]?\s*$', '', commit_message)
            commit_message = re.sub(r'\s*#[a-f0-9]{6,8}\s*', '', commit_message)
            
            return commit_message.strip()
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check for specific error types (same logic as above)
            if "rate limit" in error_str or "too many requests" in error_str:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    click.echo(f"Rate limit hit. Waiting {wait_time:.1f} seconds before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    return "Error: Rate limit exceeded. Please try again in a few minutes."
            
            elif "500 internal server error" in error_str or "502 bad gateway" in error_str or "503 service unavailable" in error_str:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    click.echo(f"Server error (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    return "Error: OpenAI service is currently experiencing issues. Please try again later."
            
            elif "authentication" in error_str or "api key" in error_str or "unauthorized" in error_str:
                return "Error: Invalid API key. Please check your OpenAI API key and run 'ai-commit-assistant setup' if needed."
            
            elif "quota" in error_str or "billing" in error_str:
                return "Error: OpenAI API quota exceeded. Please check your billing and usage limits."
            
            elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
                if attempt < max_retries - 1:
                    wait_time = 2 + random.uniform(0, 1)
                    click.echo(f"Network error (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    return "Error: Network connection issues. Please check your internet connection."
            
            else:
                if attempt < max_retries - 1:
                    click.echo(f"Unexpected error (attempt {attempt + 1}/{max_retries}). Retrying...")
                    time.sleep(1)
                    continue
                else:
                    return f"Error generating detailed commit message: {str(e)}"
    
    return "Error: All retry attempts failed."



def suggest_commit_message(count=1, temperature=0.7):
    """
    Main function to suggest a commit message.
    
    Args:
        count (int): Number of suggestions to generate
        temperature (float): Controls randomness in AI response
        
    Returns:
        list: List of suggested messages or list with single error message
    """
    # Get the git diff
    diff, files_or_error = get_git_diff()
    
    # If no diff is available, files_or_error will be an error message string
    if not diff:
        return [files_or_error]  # Return error message as single item in list
    
    # If we reach here, files_or_error contains the list of files
    file_list = files_or_error
    
    # Generate the requested number of suggestions
    suggestions = []
    for i in range(count):
        # Vary temperature slightly for more diverse suggestions
        temp = temperature + (i * 0.05)
        message = generate_commit_message(diff, file_list, temperature=min(temp, 1.0))
        suggestions.append(message)  # message should be a string
        
    return suggestions


def suggest_detailed_commit_message(count=1, temperature=0.7):
    """
    Generate detailed commit messages with header and body.
    
    Args:
        count (int): Number of suggestions to generate
        temperature (float): Controls randomness in AI response
        
    Returns:
        list: List of suggested detailed messages
    """
    # Get the git diff
    diff, files_or_error = get_git_diff()
    
    # If no diff is available, files_or_error will be an error message string
    if not diff:
        return [files_or_error]
    
    # If we reach here, files_or_error contains the list of files
    file_list = files_or_error
    
    # Generate the requested number of detailed suggestions
    suggestions = []
    for i in range(count):
        # Vary temperature slightly for more diverse suggestions
        temp = temperature + (i * 0.05)
        message = generate_detailed_commit_message(diff, file_list, temperature=min(temp, 1.0))
        suggestions.append(message)
        
    return suggestions


def execute_git_commit(message, is_detailed=False):
    """
    Execute git commit with the selected message.
    
    Args:
        message (str): The commit message to use
        is_detailed (bool): Whether the message has header and body
        
    Returns:
        bool: True if commit was successful, False otherwise
    """
    try:
        if is_detailed and '\n\n' in message:
            # Split detailed message into header and body
            parts = message.split('\n\n', 1)
            header = parts[0]
            body = parts[1] if len(parts) > 1 else ""
            
            # Use multiple -m flags for header and body
            if body:
                result = subprocess.run([
                    'git', 'commit', '-m', header, '-m', body
                ], capture_output=True, text=True)
            else:
                result = subprocess.run([
                    'git', 'commit', '-m', header
                ], capture_output=True, text=True)
        else:
            # Simple single-line message
            result = subprocess.run([
                'git', 'commit', '-m', message
            ], capture_output=True, text=True)
        
        if result.returncode == 0:
            click.secho("+ Commit successful!", fg='green')
            click.echo(result.stdout)
            return True
        else:
            click.secho("X Commit failed:", fg='red')
            click.echo(result.stderr)
            return False
            
    except Exception as e:
        click.secho(f"X Error executing commit: {str(e)}", fg='red')
        return False


def get_user_selection(suggestions, message_type="commit message"):
    """
    Display suggestions and get user selection.
    
    Args:
        suggestions (list): List of suggested messages
        message_type (str): Type of message for display
        
    Returns:
        tuple: (selected_message, user_choice) or (None, None) if cancelled
    """
    if not suggestions:
        return None, None
    
    # Display all suggestions
    click.echo(f"\nGenerated {len(suggestions)} {message_type} suggestion(s):\n")
    
    for i, message in enumerate(suggestions):
        click.secho(f"[{i+1}] ", fg='blue', nl=False)
        click.echo("=" * 60)
        click.echo(message)
        click.echo("=" * 60)
        click.echo("")
    
    # Get user choice
    while True:
        click.echo("Options:")
        click.echo("  1-{}: Select a suggestion to commit".format(len(suggestions)))
        click.echo("  c: Copy a suggestion to clipboard (if available)")
        click.echo("  r: Regenerate suggestions")
        click.echo("  q: Quit without committing")
        
        choice = click.prompt("\nWhat would you like to do?", type=str).strip().lower()
        
        # Handle quit
        if choice in ['q', 'quit', 'exit']:
            return None, 'quit'
        
        # Handle regenerate
        if choice in ['r', 'regenerate', 'regen']:
            return None, 'regenerate'
        
        # Handle copy (basic implementation)
        if choice in ['c', 'copy']:
            copy_choice = click.prompt(f"Which suggestion to copy? (1-{len(suggestions)})", type=int)
            if 1 <= copy_choice <= len(suggestions):
                selected_message = suggestions[copy_choice - 1]
                click.echo(f"\nSelected message:\n{selected_message}")
                click.echo("\nCopy the message above and use: git commit")
                return None, 'copy'
            else:
                click.secho("Invalid selection. Please try again.", fg='yellow')
                continue
        
        # Handle number selection
        try:
            selection = int(choice)
            if 1 <= selection <= len(suggestions):
                return suggestions[selection - 1], selection
            else:
                click.secho(f"Invalid selection. Please choose 1-{len(suggestions)}.", fg='yellow')
        except ValueError:
            click.secho("Invalid input. Please enter a number, 'c', 'r', or 'q'.", fg='yellow')


# CLI Commands

@click.group()
def cli():
    """
    Commit Assistant - AI-powered Git commit message generator.
    
    This tool analyzes your staged changes and suggests meaningful commit messages.
    """
    # Try to load from multiple locations
    if not os.getenv("OPENAI_API_KEY"):
        # Path to .env file in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(script_dir, '.env')
        
        # Also check user's home directory
        home_env_path = os.path.join(os.path.expanduser("~"), '.commit-assistant', '.env')
        
        # Try loading from both locations
        if os.path.exists(home_env_path):
            load_dotenv(home_env_path, override=True)
        elif os.path.exists(env_path):
            load_dotenv(env_path, override=True)

def sanitize_api_key(raw_input):
    """
    Sanitize API key input by removing control characters and normalizing whitespace.
    
    Args:
        raw_input (str): Raw input from user
        
    Returns:
        str: Sanitized API key or None if invalid
    """
    if not raw_input:
        return None
    
    # Convert to string if not already
    raw_input = str(raw_input)
    
    # Remove all control characters (ASCII 0-31 except tab, newline, carriage return)
    # This includes SYN (ASCII 22) and other problematic characters
    sanitized = ''.join(char for char in raw_input 
                       if ord(char) >= 32 or char in '\t\n\r')
    
    # Normalize whitespace - strip leading/trailing and collapse internal whitespace
    sanitized = ' '.join(sanitized.split())
    
    # Remove any quotes that might have been added
    sanitized = sanitized.strip('\'"')
    
    # Additional cleanup for common copy-paste issues
    # Remove zero-width characters
    zero_width_chars = ['\u200b', '\u200c', '\u200d', '\ufeff']  # Zero-width space, ZWNJ, ZWJ, BOM
    for char in zero_width_chars:
        sanitized = sanitized.replace(char, '')
    
    # Remove any non-printable characters that might remain
    sanitized = ''.join(char for char in sanitized if char in string.printable).strip()
    
    return sanitized if sanitized else None


def validate_api_key(api_key):
    """
    Validate API key format and content.
    
    Args:
        api_key (str): API key to validate
        
    Returns:
        dict: Validation result with 'valid' boolean and 'error' message if invalid
    """
    if not api_key:
        return {'valid': False, 'error': 'API key is empty'}
    
    # Check for obvious placeholders
    placeholders = [
        'key', 'your_api_key', 'your_api_key_here', 'your_actual_api_key_here',
        'sk-example', 'sk-placeholder', 'sk-your_key_here', 'insert_key_here'
    ]
    
    if api_key.lower() in placeholders:
        return {'valid': False, 'error': 'API key appears to be a placeholder'}
    
    # Check basic format
    if not api_key.startswith('sk-'):
        return {'valid': False, 'error': "API key should start with 'sk-'"}
    
    # Check length (OpenAI keys are typically around 51 characters)
    if len(api_key) < 40:
        return {'valid': False, 'error': f'API key too short ({len(api_key)} chars). Expected ~51 characters'}
    
    if len(api_key) > 80:
        return {'valid': False, 'error': f'API key too long ({len(api_key)} chars). Expected ~51 characters'}
    
    # Check for valid characters (OpenAI keys use alphanumeric + some symbols)
    if not re.match(r'^sk-[a-zA-Z0-9\-_]+$', api_key):
        return {'valid': False, 'error': 'API key contains invalid characters'}
    
    # Check for suspicious patterns
    if api_key.count('-') > 5:  # Too many dashes
        return {'valid': False, 'error': 'API key has suspicious format (too many dashes)'}
    
    # Check for repeated characters (likely corrupted)
    if len(set(api_key)) < 10:  # Too few unique characters
        return {'valid': False, 'error': 'API key has too few unique characters'}
    
    return {'valid': True, 'error': None}


def test_saved_configuration(env_path, expected_key):
    """
    Test that the saved configuration can be loaded correctly.
    
    Args:
        env_path (str): Path to the .env file
        expected_key (str): Expected API key value
        
    Returns:
        dict: Test result with 'success' boolean and 'error' message if failed
    """
    try:
        # Clear any existing environment variable
        if 'OPENAI_API_KEY' in os.environ:
            original_key = os.environ['OPENAI_API_KEY']
            del os.environ['OPENAI_API_KEY']
        else:
            original_key = None
        
        # Try to load the saved file
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)
        
        # Get the loaded key
        loaded_key = os.getenv('OPENAI_API_KEY')
        
        # Restore original environment
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # Check if loading worked
        if not loaded_key:
            return {'success': False, 'error': 'Could not load API key from saved file'}
        
        if loaded_key != expected_key:
            return {'success': False, 'error': f'Loaded key differs from saved key'}
        
        return {'success': True, 'error': None}
        
    except Exception as e:
        return {'success': False, 'error': f'Exception during test: {str(e)}'}


# Also add a command to clean existing configuration
@cli.command()
def clean_config():
    """
    Remove saved configuration file.
    Windows-safe version.
    """
    config_dir = os.path.join(os.path.expanduser("~"), '.commit-assistant')
    env_path = os.path.join(config_dir, '.env')
    
    if os.path.exists(env_path):
        click.echo(f"Found configuration file: {env_path}")
        if click.confirm("Remove this configuration file?", default=False):
            try:
                os.remove(env_path)
                click.secho("Configuration file removed.", fg='green')
                
                # Remove directory if empty
                try:
                    if os.path.exists(config_dir) and not os.listdir(config_dir):
                        os.rmdir(config_dir)
                        click.echo("Configuration directory removed.")
                except OSError:
                    # Directory not empty or permission issue
                    pass
                    
            except Exception as e:
                click.secho(f"Error removing file: {e}", fg='red')
        else:
            click.echo("Configuration file kept.")
    else:
        click.echo("No configuration file found to remove.")
        click.echo(f"Checked: {env_path}")


# Add a debug command to inspect configuration
@cli.command()
def debug_config():
    """
    Show configuration file locations and status.
    Windows-safe version.
    """
    click.echo("Configuration Debug")
    click.echo("=" * 40)
    
    # Home config file
    home_config = os.path.join(os.path.expanduser("~"), '.commit-assistant', '.env')
    click.echo(f"\nHome config: {home_config}")
    click.echo(f"Exists: {os.path.exists(home_config)}")
    
    if os.path.exists(home_config):
        try:
            # Try UTF-8 first, fallback to other encodings
            content = None
            for encoding in ['utf-8', 'utf-8-sig', 'ascii', 'cp1252']:
                try:
                    with open(home_config, 'r', encoding=encoding) as f:
                        content = f.read().strip()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content and 'OPENAI_API_KEY=' in content:
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('OPENAI_API_KEY='):
                        key_value = line.split('=', 1)[1]
                        click.echo(f"Contains API key: {key_value[:15]}... (length: {len(key_value)})")
                        break
            else:
                click.echo("No OPENAI_API_KEY found or couldn't read file")
                
        except Exception as e:
            click.echo(f"Error reading file: {e}")
    
    # Current directory .env
    current_env = os.path.abspath('.env')
    click.echo(f"\nCurrent dir .env: {current_env}")
    click.echo(f"Exists: {os.path.exists(current_env)}")
    
    if os.path.exists(current_env):
        try:
            # Try UTF-8 first, fallback to other encodings
            content = None
            for encoding in ['utf-8', 'utf-8-sig', 'ascii', 'cp1252']:
                try:
                    with open(current_env, 'r', encoding=encoding) as f:
                        content = f.read().strip()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content and 'OPENAI_API_KEY=' in content:
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('OPENAI_API_KEY='):
                        key_value = line.split('=', 1)[1]
                        click.echo(f"Contains API key: {key_value[:15]}... (length: {len(key_value)})")
                        break
            else:
                click.echo("No OPENAI_API_KEY found or couldn't read file")
                
        except Exception as e:
            click.echo(f"Error reading file: {e}")
    
    # Environment variable
    env_key = os.getenv('OPENAI_API_KEY')
    click.echo(f"\nEnvironment variable: {'Set' if env_key else 'Not set'}")
    if env_key:
        click.echo(f"Value: {env_key[:15]}... (length: {len(env_key)})")
    
    click.echo("\n" + "=" * 40)



@cli.command()
@click.option('--count', '-c', default=1, help='Number of suggestions to generate')
@click.option('--temp', '-t', default=0.7, help='Temperature (creativity) of suggestions, 0.0-1.0')
@click.option('--detailed', '-d', is_flag=True, help='Generate detailed commit with header and body')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode: select and commit directly')
@click.option('--auto-commit', '-a', is_flag=True, help='Auto-commit the first suggestion without prompting')
def suggest(count, temp, detailed, interactive, auto_commit):
    """
    Suggest commit messages based on staged changes.
    
    Analyzes your git diff and generates commit message suggestions.
    Use --detailed for messages with both header and body.
    Use --interactive to select and commit directly.
    Use --auto-commit to automatically commit the first suggestion.
    """
    # Validate inputs
    count = max(1, min(5, count))
    temp = max(0.0, min(1.0, temp))
    
    # For auto-commit, we only need one suggestion
    if auto_commit:
        count = 1
    
    # For interactive mode, default to more suggestions if not specified
    if interactive and count == 1:
        count = 3
    
    click.echo("Analyzing staged changes...")
    
    # Generate suggestions
    while True:  # Loop for regeneration
        if detailed:
            suggestions = suggest_detailed_commit_message(count=count, temperature=temp)
            message_type = "detailed commit message"
        else:
            suggestions = suggest_commit_message(count=count, temperature=temp)
            message_type = "commit message"
        
        # Check if we got an error or warning message
        if len(suggestions) == 1 and isinstance(suggestions[0], str) and (suggestions[0].startswith("Error") or suggestions[0].startswith("No ")):
            click.secho(suggestions[0], fg='yellow')
            return
        
        # Auto-commit mode
        if auto_commit:
            click.echo(f"\nAuto-committing with suggestion:")
            click.echo("=" * 60)
            click.echo(suggestions[0])
            click.echo("=" * 60)
            
            if click.confirm("\nProceed with this commit?", default=True):
                success = execute_git_commit(suggestions[0], detailed)
                if success:
                    return
                else:
                    click.echo("Commit failed. Try manual commit or fix the issues.")
                    return
            else:
                click.echo("Auto-commit cancelled.")
                return
        
        # Interactive mode
        elif interactive:
            selected_message, choice = get_user_selection(suggestions, message_type)
            
            if choice == 'quit':
                click.echo("Exiting without committing.")
                return
            elif choice == 'regenerate':
                click.echo("Regenerating suggestions...")
                # Vary temperature slightly for different results
                temp = min(1.0, temp + 0.1)
                continue
            elif choice == 'copy':
                return
            elif selected_message:
                # Confirm and commit
                click.echo(f"\nSelected message:")
                click.echo("=" * 60)
                click.echo(selected_message)
                click.echo("=" * 60)
                
                if click.confirm("\nCommit with this message?", default=True):
                    success = execute_git_commit(selected_message, detailed)
                    if success:
                        return
                    else:
                        # Ask if they want to try again or exit
                        if click.confirm("Would you like to try a different message?"):
                            continue
                        else:
                            return
                else:
                    # Ask if they want to select again or exit
                    if click.confirm("Would you like to select a different message?"):
                        continue
                    else:
                        click.echo("Exiting without committing.")
                        return
        
        # Non-interactive mode (original behavior)
        else:
            click.echo(f"\nGenerated {len(suggestions)} {message_type} suggestion(s):\n")
            
            for i, message in enumerate(suggestions):
                click.secho(f"[{i+1}] ", fg='blue', nl=False)
                click.echo("=" * 60)
                click.echo(message)
                click.echo("=" * 60)
                click.echo("")
            
            # Provide usage instructions
            if detailed:
                click.echo("To use a detailed suggestion:")
                click.echo('git commit -m "Header from above" -m "Body from above"')
                click.echo("Or simply: git commit (then paste the full message in your editor)")
            else:
                click.echo("To use a suggestion: git commit -m \"suggested message\"")
            
            click.echo("\nTip: Use --interactive (-i) to select and commit directly!")
            return


@cli.command()
@click.option('--temp', '-t', default=0.7, help='Temperature (creativity) of suggestions, 0.0-1.0')
@click.option('--detailed', '-d', is_flag=True, help='Generate detailed commit with header and body')
def quick(temp, detailed):
    """
    Quick commit: Generate one suggestion and commit immediately if approved.
    
    This is equivalent to: commit-assistant suggest --auto-commit
    """
    # Validate input
    temp = max(0.0, min(1.0, temp))
    
    click.echo("Generating commit suggestion...")
    
    # Generate one suggestion
    if detailed:
        suggestions = suggest_detailed_commit_message(count=1, temperature=temp)
    else:
        suggestions = suggest_commit_message(count=1, temperature=temp)
    
    # Check for errors
    if len(suggestions) == 1 and isinstance(suggestions[0], str) and (suggestions[0].startswith("Error") or suggestions[0].startswith("No ")):
        click.secho(suggestions[0], fg='yellow')
        return
    
    message = suggestions[0]
    
    # Display the suggestion
    click.echo(f"\nSuggested commit message:")
    click.echo("=" * 60)
    click.echo(message)
    click.echo("=" * 60)
    
    # Confirm and commit
    if click.confirm("\nCommit with this message?", default=True):
        success = execute_git_commit(message, detailed)
        if not success:
            click.echo("\nYou can manually commit with:")
            if detailed and '\n\n' in message:
                parts = message.split('\n\n', 1)
                click.echo(f'git commit -m "{parts[0]}" -m "{parts[1]}"')
            else:
                click.echo(f'git commit -m "{message}"')
    else:
        click.echo("Commit cancelled.")
        click.echo("\nTry: python -m commitassist.main suggest --interactive")


@cli.command()
def setup():
    """
    Set up Commit Assistant configuration.
    
    Creates necessary configuration files and directories.
    Simple, cross-platform setup that supports copy-paste.
    Windows-safe version.
    """
    # Create config directory in user's home
    config_dir = os.path.join(os.path.expanduser("~"), '.commit-assistant')
    os.makedirs(config_dir, exist_ok=True)
    
    # Path to .env file
    env_path = os.path.join(config_dir, '.env')
    
    # Check if .env already exists
    if os.path.exists(env_path):
        click.echo(f"\nConfiguration file already exists at: {env_path}")
        overwrite = click.confirm("Do you want to update it with a new API key?", default=True)
        if not overwrite:
            click.echo("Setup canceled.")
            return
    
    # Simple, clear instructions
    click.echo("\n" + "=" * 60)
    click.echo("OpenAI API Key Setup")
    click.echo("=" * 60)
    click.echo("Get your API key from: https://platform.openai.com/api-keys")
    click.echo("")
    click.echo("Your API key should:")
    click.echo("  - Start with 'sk-'")
    click.echo("  - Be a long string (can be 50-200+ characters)")
    click.echo("  - You can copy-paste it here")
    click.echo("")
    click.echo("The input will be visible for easy copy-paste verification.")
    click.echo("=" * 60)
    
    # Get API key with simple, visible input
    api_key = None
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            click.echo(f"\nAttempt {attempt + 1} of {max_attempts}")
            
            # Simple prompt - no hiding, works everywhere
            raw_input = click.prompt("Paste your OpenAI API key here", type=str, default="")
            
            if not raw_input or not raw_input.strip():
                click.secho("No input provided. Please paste your API key.", fg='yellow')
                continue
            
            # Basic sanitization - just remove obvious problematic characters
            api_key = sanitize_api_key_simple(raw_input)
            
            if not api_key:
                click.secho("Could not process the input. Please try again.", fg='red')
                continue
            
            # Show what we got
            click.echo(f"\nReceived API key:")
            click.echo(f"  Length: {len(api_key)} characters")
            click.echo(f"  Starts with: {api_key[:10]}...")
            click.echo(f"  Ends with: ...{api_key[-10:]}")
            
            # Basic validation
            validation_result = validate_api_key_simple(api_key)
            if not validation_result['valid']:
                click.secho(f"Warning: {validation_result['warning']}", fg='yellow')
                if not click.confirm("Continue anyway?", default=True):
                    continue
            else:
                click.secho("API key format looks good!", fg='green')
            
            # Confirm before saving
            if click.confirm("Save this API key?", default=True):
                break
            else:
                api_key = None
                continue
                
        except KeyboardInterrupt:
            click.echo("\nSetup canceled by user.")
            return
        except Exception as e:
            click.secho(f"Error: {str(e)}", fg='red')
            if attempt < max_attempts - 1:
                click.echo("Please try again.")
                continue
    
    if not api_key:
        click.secho("\nCould not get a valid API key.", fg='red')
        show_manual_setup_instructions(env_path)
        return
    
    # Save the API key
    try:
        save_api_key_to_file(env_path, api_key)
        
        # Test the saved configuration
        click.echo("\nTesting the saved configuration...")
        if test_api_key_loading(env_path):
            click.secho("Setup completed successfully!", fg='green')
            click.echo(f"Configuration saved to: {env_path}")
            click.echo("\nYou can now use:")
            click.echo("  ai-commit-assistant suggest")
            click.echo("  ai-commit-assistant quick")
        else:
            click.secho("API key saved but there was an issue loading it.", fg='yellow')
            click.echo("Try running: ai-commit-assistant test-api")
            
    except Exception as e:
        click.secho(f"Error saving configuration: {str(e)}", fg='red')
        show_manual_setup_instructions(env_path)


def sanitize_api_key_simple(raw_input):
    """
    Simple API key sanitization that preserves the key while removing obvious problems.
    Windows-safe version.
    
    Args:
        raw_input (str): Raw input from user
        
    Returns:
        str: Cleaned API key or None if invalid
    """
    if not raw_input:
        return None
    
    # Convert to string and strip whitespace
    cleaned = str(raw_input).strip()
    
    # Remove common problematic characters but preserve the key content
    # Remove control characters (0-31) except tab/newline/carriage return
    cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\t\n\r')
    
    # Remove zero-width characters that can come from copy-paste
    # Using basic string replacement instead of Unicode escapes
    zero_width_chars = [
        '\u200b',  # Zero width space
        '\u200c',  # Zero width non-joiner
        '\u200d',  # Zero width joiner
        '\ufeff',  # Byte order mark
        '\u2060'   # Word joiner
    ]
    for char in zero_width_chars:
        cleaned = cleaned.replace(char, '')
    
    # Remove quotes if the entire thing is wrapped in quotes
    if (cleaned.startswith('"') and cleaned.endswith('"')) or \
       (cleaned.startswith("'") and cleaned.endswith("'")):
        cleaned = cleaned[1:-1]
    
    # Final strip
    cleaned = cleaned.strip()
    
    # Remove any internal newlines/tabs (keep it as one line)
    cleaned = ' '.join(cleaned.split())
    
    return cleaned if cleaned else None


def validate_api_key_simple(api_key):
    """
    Simple validation that doesn't restrict length but checks basic format.
    Windows-safe version.
    
    Args:
        api_key (str): API key to validate
        
    Returns:
        dict: Validation result with 'valid' boolean and 'warning' message
    """
    if not api_key:
        return {'valid': False, 'warning': 'API key is empty'}
    
    # Check for obvious placeholders
    placeholders = [
        'key', 'your_api_key', 'your_api_key_here', 'your_actual_api_key_here',
        'sk-example', 'sk-placeholder', 'sk-your_key_here', 'insert_key_here',
        'paste_your_key_here', 'replace_with_your_key'
    ]
    
    if api_key.lower() in placeholders:
        return {'valid': False, 'warning': 'This looks like a placeholder, not a real API key'}
    
    # Check if it starts with sk-
    if not api_key.startswith('sk-'):
        return {'valid': False, 'warning': "OpenAI API keys should start with 'sk-'"}
    
    # Check minimum length (very basic check)
    if len(api_key) < 20:
        return {'valid': False, 'warning': f'API key seems too short ({len(api_key)} chars)'}
    
    # Check for reasonable character set (allow more flexibility)
    # Using basic character checking instead of regex
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_./+=')
    suspicious_chars = [c for c in api_key if c not in allowed_chars]
    
    if suspicious_chars:
        return {'valid': False, 'warning': f'API key contains unusual characters: {suspicious_chars[:5]}'}
    
    # All checks passed
    return {'valid': True, 'warning': None}


def save_api_key_to_file(env_path, api_key):
    """
    Save API key to .env file with proper formatting.
    Windows-safe version with explicit line ending handling.
    
    Args:
        env_path (str): Path to .env file
        api_key (str): API key to save
    """
    # Create the content with Windows-safe line ending
    content = f"OPENAI_API_KEY={api_key}\n"
    
    # Save with UTF-8 encoding
    # Use 'w' mode which will use the system's default line endings
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except UnicodeEncodeError:
        # Fallback to ASCII if UTF-8 fails
        with open(env_path, 'w', encoding='ascii', errors='ignore') as f:
            f.write(content)
    
    # Verify the file was written correctly
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            saved_content = f.read().strip()
    except UnicodeDecodeError:
        with open(env_path, 'r', encoding='ascii', errors='ignore') as f:
            saved_content = f.read().strip()
    
    # Basic verification
    if not saved_content.startswith('OPENAI_API_KEY='):
        raise Exception("File verification failed - content doesn't match expected format")
    
    saved_key = saved_content.split('=', 1)[1]
    if saved_key != api_key:
        raise Exception("File verification failed - saved key doesn't match input key")


def test_api_key_loading(env_path):
    """
    Test that the API key can be loaded from the saved file.
    Windows-safe version.
    
    Args:
        env_path (str): Path to .env file
        
    Returns:
        bool: True if loading works, False otherwise
    """
    try:
        # Save current environment
        original_key = os.environ.get('OPENAI_API_KEY')
        
        # Clear environment variable
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # Try to load from file
        from dotenv import load_dotenv
        load_dotenv(env_path, override=True)
        
        # Check if it loaded
        loaded_key = os.getenv('OPENAI_API_KEY')
        success = loaded_key is not None and len(loaded_key.strip()) > 0
        
        # Restore original environment
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        return success
        
    except Exception as e:
        click.echo(f"Loading test failed: {e}")
        return False


def show_manual_setup_instructions(env_path):
    """
    Show manual setup instructions as fallback.
    Windows-safe version.
    
    Args:
        env_path (str): Path where .env file should be created
    """
    click.echo("\nManual Setup Instructions:")
    click.echo("=" * 50)
    click.echo(f"1. Create this file: {env_path}")
    click.echo("2. Add this line to the file:")
    click.echo("   OPENAI_API_KEY=your_actual_api_key_here")
    click.echo("3. Replace 'your_actual_api_key_here' with your real API key")
    click.echo("")
    click.echo("Alternative - Set environment variable:")
    
    if platform.system() == "Windows":
        click.echo("Windows Command Prompt:")
        click.echo("   set OPENAI_API_KEY=your_api_key")
        click.echo("")
        click.echo("Windows PowerShell:")
        click.echo("   $env:OPENAI_API_KEY='your_api_key'")
    else:
        click.echo("Unix/Linux/Mac:")
        click.echo("   export OPENAI_API_KEY=your_api_key")
    
    click.echo("")
    click.echo("Then test with: ai-commit-assistant test-api")


# Hook-related CLI commands using the hooks module

@cli.command()
def install_hook():
    """
    Install Commit Assistant as a Git hook.
    
    Sets up a prepare-commit-msg hook to suggest messages automatically
    when you run 'git commit' (without -m flag).
    """
    click.echo("Installing Git hook...")
    
    success, message = hooks.install_git_hook()
    
    if success:
        click.secho("+ " + message, fg='green')
        click.echo("\nThe hook is now installed! Here's how it works:")
        click.echo("1. Stage your changes: git add .")
        click.echo("2. Start a commit: git commit")
        click.echo("3. Your editor will open with an AI-suggested message")
        click.echo("4. Edit or accept the suggestion and save")
        
        # Check for Windows-specific notes
        if platform.system() == "Windows":
            click.echo("\n" + "="*50)
            click.secho("Windows Users Note:", fg='yellow', bold=True)
            click.echo("Make sure Git is configured to use the correct shell:")
            click.echo("  git config --global core.autocrlf true")
            click.echo("The hook will work with Git Bash, Git for Windows, and most Git clients.")
            click.echo("="*50)
            
    else:
        if "already exists" in message:
            click.secho("! " + message, fg='yellow')
            click.echo("\nTo reinstall, first remove the existing hook:")
            click.echo("  ai-commit-assistant uninstall-hook")
            click.echo("Then install again:")
            click.echo("  ai-commit-assistant install-hook")
        else:
            click.secho("X " + message, fg='red')


@cli.command()
def uninstall_hook():
    """
    Remove the Commit Assistant Git hook.
    
    Removes the prepare-commit-msg hook installed by this tool.
    """
    click.echo("Removing Git hook...")
    
    success, message = hooks.uninstall_git_hook()
    
    if success:
        click.secho("✓ " + message, fg='green')
        click.echo("Git hook has been removed. You can reinstall it anytime with:")
        click.echo("  python -m commitassist.main install-hook")
    else:
        if "not found" in message:
            click.secho("ℹ " + message, fg='blue')
        else:
            click.secho("✗ " + message, fg='red')


@cli.command()
def install_global_hook():
    """
    Install Commit Assistant as a global Git hook for ALL repositories.
    
    This sets up the hook to work in every Git repository on your system.
    You only need to run this once, not per repository.
    """
    click.echo("Installing global Git hook...")
    
    success, message = hooks.install_global_git_hook()
    
    if success:
        click.secho("+ " + message, fg='green')
        click.echo("\nGlobal hook installed successfully!")
        click.echo("\nThis hook will now work in ALL your Git repositories!")
        click.echo("\nHow it works:")
        click.echo("1. Go to any Git repository")
        click.echo("2. Stage changes: git add .")
        click.echo("3. Start commit: git commit")
        click.echo("4. See AI suggestions in your editor")
        
        click.echo(f"\nHook location: {message.split(': ')[1]}")
        
        if platform.system() == "Windows":
            click.echo("\n" + "="*50)
            click.secho("Windows Users:", fg='yellow', bold=True)
            click.echo("Global hooks work with Git for Windows and most Git clients.")
            click.echo("="*50)
            
    else:
        click.secho("X " + message, fg='red')


@cli.command()
def uninstall_global_hook():
    """
    Remove the global Git hook configuration.
    
    This removes the global hook setup, but won't affect individual
    repository hooks that were installed separately.
    """
    click.echo("Removing global Git hook...")
    
    success, message = hooks.uninstall_global_git_hook()
    
    if success:
        click.secho("✓ " + message, fg='green')
        click.echo("\nGlobal hook removed. You can:")
        click.echo("1. Reinstall globally: python -m commitassist.main install-global-hook")
        click.echo("2. Install per-repo: python -m commitassist.main install-hook")
    else:
        click.secho("✗ " + message, fg='red')


def hook_status():
    """
    Check the status of Git hook installation (both local and global).
    """
    click.echo("Git Hook Status Report:")
    click.echo("=" * 60)
    
    # Check local hook status
    click.secho("LOCAL REPOSITORY HOOK:", fg='blue', bold=True)
    local_status = hooks.check_git_hook_status()
    
    if not local_status['git_repo']:
        click.secho("X Not in a Git repository", fg='red')
    elif local_status['hook_exists'] and local_status['is_our_hook']:
        click.secho("+ Local hook installed", fg='green')
        click.echo(f"Location: {local_status['hook_path']}")
    else:
        click.secho("- No local hook", fg='red')
    
    click.echo()
    
    # Check global hook status
    click.secho("GLOBAL HOOK (works in all repos):", fg='blue', bold=True)
    global_status = hooks.check_global_hook_status()
    
    if global_status['global_hooks_configured'] and global_status['is_our_hook']:
        click.secho("+ Global hook installed and active", fg='green')
        click.echo("Works in ALL Git repositories!")
        click.echo(f"Location: {global_status['hook_path']}")
    else:
        click.secho("- No global hook", fg='red')
    
    click.echo("=" * 60)
    
    # Recommendations
    click.secho("RECOMMENDATIONS:", fg='yellow', bold=True)
    
    if global_status['global_hooks_configured'] and global_status['is_our_hook']:
        click.echo("You're all set! Global hook works everywhere.")
    else:
        click.echo("Install global hook for convenience:")
        click.echo("   ai-commit-assistant install-global-hook")
        click.echo("   (Works in all repositories, setup once)")
    
    click.echo()
    click.echo("Alternative commands:")
    click.echo("• Local hook:  ai-commit-assistant install-hook")
    click.echo("• Global hook: ai-commit-assistant install-global-hook")


@cli.command()
def global_hook_status():
    """
    Check the status of global Git hook installation.
    """
    status = hooks.check_global_hook_status()
    
    click.echo("Global Git Hook Status:")
    click.echo("=" * 50)
    
    if status.get('error'):
        click.secho(f"✗ Error checking status: {status['error']}", fg='red')
        return
    
    if status['global_hooks_configured']:
        click.secho("✓ Global Git hooks are configured", fg='green')
        click.echo(f"Hooks path: {status['global_hooks_path']}")
        
        if status['hook_exists'] and status['is_our_hook']:
            click.secho("✓ Commit Assistant global hook is active", fg='green')
            click.echo(f"Hook file: {status['hook_path']}")
            click.echo("\n✨ The hook will work in ALL your Git repositories!")
        elif status['hook_exists']:
            click.secho("⚠ A global hook exists but wasn't created by commit-assistant", fg='yellow')
        else:
            click.secho("✗ Global hook file missing", fg='red')
            click.echo("Try reinstalling: python -m commitassist.main install-global-hook")
    else:
        click.secho("✗ Global Git hooks not configured", fg='red')
        click.echo("Install with: python -m commitassist.main install-global-hook")
    
    click.echo("=" * 50)

# Debug command to test API connectivity
@cli.command()
def test_api():
    """
    Test OpenAI API connectivity and authentication.
    Windows-safe version.
    """
    click.echo("Testing OpenAI API...")
    click.echo("=" * 40)
    
    try:
        # Show what key we're using
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Try loading from config files
            from dotenv import load_dotenv
            
            # Try current directory first
            if os.path.exists('.env'):
                load_dotenv('.env', override=True)
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    click.echo("Loaded API key from current directory .env")
            
            # Try home directory if not found
            if not api_key:
                home_env = os.path.join(os.path.expanduser("~"), '.commit-assistant', '.env')
                if os.path.exists(home_env):
                    load_dotenv(home_env, override=True)
                    api_key = os.getenv("OPENAI_API_KEY")
                    if api_key:
                        click.echo(f"Loaded API key from home config: {home_env}")
        
        if not api_key:
            click.secho("No API key found!", fg='red')
            click.echo("Run: ai-commit-assistant setup")
            return
        
        click.echo(f"Using API key: {api_key[:15]}... (length: {len(api_key)})")
        
        # Test the API
        client = OpenAI(api_key=api_key.strip())
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'API test successful' if you can read this."}
            ],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        click.secho("API test successful!", fg='green')
        click.echo(f"Response: {result}")
        click.echo("\nYou can now use: ai-commit-assistant suggest")
        
    except Exception as e:
        click.secho(f"API test failed: {str(e)}", fg='red')
        
        error_str = str(e).lower()
        if "authentication" in error_str or "api key" in error_str:
            click.echo("Check your API key with: ai-commit-assistant setup")
        elif "quota" in error_str or "billing" in error_str:
            click.echo("Check your OpenAI billing and usage limits")
        elif "network" in error_str or "connection" in error_str:
            click.echo("Check your internet connection")
        else:
            click.echo("Try: ai-commit-assistant setup")

@cli.command()
def commit():
    """
    Generate a detailed commit message and format it for easy copying.
    
    This command generates a single detailed commit message optimized for copy-paste.
    """
    temp = 0.7
    
    click.echo("Generating detailed commit message...")
    
    suggestions = suggest_detailed_commit_message(count=1, temperature=temp)
    
    if len(suggestions) == 1 and isinstance(suggestions[0], str) and (suggestions[0].startswith("Error") or suggestions[0].startswith("No ")):
        click.secho(suggestions[0], fg='yellow')
        return
    
    message = suggestions[0]
    
    # Split into header and body for formatted output
    lines = message.split('\n')
    header = lines[0] if lines else ""
    body = '\n'.join(lines[2:]) if len(lines) > 2 else ""  # Skip header and blank line
    
    click.echo("\n" + "=" * 70)
    click.secho("COMMIT MESSAGE", fg='green', bold=True)
    click.echo("=" * 70)
    click.echo(message)
    click.echo("=" * 70)
    
    click.echo("\n" + "=" * 70)
    click.secho("COPY-PASTE COMMANDS", fg='blue', bold=True)
    click.echo("=" * 70)
    
    if body:
        click.echo("Option 1 - Using multiple -m flags:")
        click.echo(f'git commit -m "{header}" -m "{body.replace(chr(10), chr(10))}"')
        
        click.echo("\nOption 2 - Using editor (recommended):")
        click.echo("git commit")
        click.echo("(Then paste the full message above in your editor)")
        
        click.echo("\nOption 3 - PowerShell multi-line:")
        click.echo('git commit -m @"')
        click.echo(message)
        click.echo('"@')
    else:
        click.echo("Single line commit:")
        click.echo(f'git commit -m "{header}"')
    
    click.echo("=" * 70)


# Entry point for the command-line interface
if __name__ == "__main__":
    cli()