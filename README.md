# Commit Assistant

An AI-powered tool that generates meaningful Git commit messages by analyzing your code changes. Never struggle with writing commit messages again!

## ✨ Features

- 🔍 **Smart Analysis**: Analyzes git diffs to suggest contextual commit messages
- 🧠 **AI-Powered**: Uses OpenAI's GPT models to understand code and generate relevant messages
- 🌐 **Multi-Language Support**: Recognizes multiple programming languages including Python, JavaScript, TypeScript, and more
- 📚 **Repository Awareness**: Learns from your repository's history and commit patterns
- 🎯 **Multiple Formats**: Generate simple one-line messages or detailed header + body format
- ⚡ **Interactive Mode**: Select and commit directly without copy-pasting
- 🚀 **Quick Commit**: One-command commit with AI-generated messages
- 🔄 **Git Integration**: Optional Git hook integration for seamless workflow
- 🎛️ **Customizable**: Adjustable creativity levels and multiple suggestion options

## 📋 Prerequisites

- **Python 3.7 or higher**
- **Git** (installed and configured)
- **OpenAI API Key**: Each user needs their own OpenAI API key
  - Sign up at [OpenAI](https://platform.openai.com/signup)
  - Create an API key at [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
  - Usage will be billed to your OpenAI account (typically very affordable - few cents per commit)

## 🚀 Installation

### Method 1: Install from PyPI (Coming Soon)

```bash
pip install commit-assistant
```

### Method 2: Install from Source (Recommended for Latest Features)

```bash
git clone https://github.com/jazir/commit-assistant.git
cd commit-assistant
pip install -e .
```

### Method 3: Development Setup (Current)

**Step 1: Clone the Repository**

```bash
git clone https://github.com/jazir/commit-assistant.git
cd commit-assistant
```

**Step 2: Create Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

**Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

**Step 4: Verify Installation**

```bash
# Test that the tool works
python -m commitassist.main --help
```

You should see the help menu with all available commands.

### Method 4: Quick Setup Script (Windows)

Create a `setup.bat` file with:

```batch
@echo off
echo Setting up Commit Assistant...
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo.
echo Setup complete! Run 'venv\Scripts\activate' to start using the tool.
pause
```

Run: `setup.bat`

### Method 5: Quick Setup Script (macOS/Linux)

Create a `setup.sh` file with:

```bash
#!/bin/bash
echo "Setting up Commit Assistant..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo ""
echo "Setup complete! Run 'source venv/bin/activate' to start using the tool."
```

Run: `chmod +x setup.sh && ./setup.sh`

## ⚙️ Setup

### Configure Your OpenAI API Key

**Option 1: Using the setup command**

```bash
# If installed:
commit-assistant setup

# If using development setup:
python -m commitassist.main setup
```

**Option 2: Manual setup**
Create a `.env` file in your project directory or in `~/.commit-assistant/` with:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## 📖 Usage

### Command Format

| If Installed                 | Development Mode                        |
| ---------------------------- | --------------------------------------- |
| `commit-assistant <command>` | `python -m commitassist.main <command>` |

_All examples below show both formats_

### Basic Commands

### 1. Simple Commit Messages

Generate a basic one-line commit message:

```bash
# Stage your changes first
git add .

# Generate suggestion
commit-assistant suggest
# or: python -m commitassist.main suggest
```

**Example output:**

```
[1] feat: Add user authentication to API endpoints
```

### 2. Detailed Commit Messages

Generate commit messages with header and body:

```bash
commit-assistant suggest --detailed
# or: python -m commitassist.main suggest --detailed
```

**Example output:**

```
[1] ============================================================
feat: Add user authentication system

Implement JWT-based authentication to secure API endpoints.

- Add login/logout functionality with token generation
- Create middleware for request validation
- Implement secure password hashing
- Set up session management for user state

This addresses security requirements and improves user experience
by providing seamless authentication flow.
============================================================
```

### 3. Interactive Mode (Recommended)

Select and commit directly without copy-pasting:

```bash
commit-assistant suggest --interactive
# or: python -m commitassist.main suggest --interactive
```

**Interactive session:**

```
Generated 3 commit message suggestions:

[1] ============================================================
feat: Add interactive commit selection
============================================================

[2] ============================================================
refactor: Improve user experience with direct commit
============================================================

[3] ============================================================
update: Add interactive mode for commit selection
============================================================

Options:
  1-3: Select a suggestion to commit
  c: Copy a suggestion to clipboard
  r: Regenerate suggestions
  q: Quit without committing

What would you like to do? 1

Selected message:
============================================================
feat: Add interactive commit selection
============================================================

Commit with this message? [Y/n]: y
✓ Commit successful!
```

### 4. Quick Commit (Fastest)

Generate one suggestion and commit immediately:

```bash
commit-assistant quick
# or: python -m commitassist.main quick
```

### 5. Advanced Options

#### Multiple Suggestions

```bash
commit-assistant suggest --count 5
# or: python -m commitassist.main suggest --count 5
```

#### Adjust Creativity Level

```bash
# More predictable (0.0-1.0, default: 0.7)
commit-assistant suggest --temp 0.2
# or: python -m commitassist.main suggest --temp 0.2

# More creative
commit-assistant suggest --temp 0.9
# or: python -m commitassist.main suggest --temp 0.9
```

#### Combine Options

```bash
# Interactive detailed mode with 3 suggestions
commit-assistant suggest --detailed --interactive --count 3
# or: python -m commitassist.main suggest --detailed --interactive --count 3
```

#### Auto-commit First Suggestion

```bash
commit-assistant suggest --auto-commit
# or: python -m commitassist.main suggest --auto-commit
```

## 🔧 Git Hook Integration

### Global Hook Installation (Recommended - Setup Once)

Install the hook globally to work in ALL repositories:

```bash
# Install global hook
commit-assistant install-global-hook
# or: python -m commitassist.main install-global-hook

# Check status
commit-assistant hook-status
# or: python -m commitassist.main hook-status
```

**Benefits:**

- ✅ Works in every Git repository on your system
- ✅ Setup once, use everywhere
- ✅ No need to install per repository
- ✅ Consistent experience across all projects

### Local Hook Installation (Per Repository)

Install the hook only in the current repository:

```bash
# Install local hook
commit-assistant install-hook
# or: python -m commitassist.main install-hook
```

### How Git Hooks Work

After installing a hook, when you run `git commit` (without `-m` flag):

1. **Your editor opens** with an AI-suggested commit message
2. **Use or edit the suggestion** by removing the `#` at the beginning
3. **Save and close** to complete the commit

**Example editor content:**

```
# 🤖 AI Suggested commit message:
# feat: Add user authentication system
#
# Remove the '#' above to use this suggestion
# Generated by commit-assistant global hook
#

# Please enter the commit message for your changes. Lines starting
# with '#' are ignored, and an empty message aborts the commit.
# On branch main
# Changes to be committed:
#       modified:   auth.py
```

### Hook Management Commands

```bash
# Check hook status (both local and global)
commit-assistant hook-status
# or: python -m commitassist.main hook-status

# Install global hook (recommended)
commit-assistant install-global-hook
# or: python -m commitassist.main install-global-hook

# Install local hook (current repo only)
commit-assistant install-hook
# or: python -m commitassist.main install-hook

# Remove global hook
commit-assistant uninstall-global-hook
# or: python -m commitassist.main uninstall-global-hook

# Remove local hook
commit-assistant uninstall-hook
# or: python -m commitassist.main uninstall-hook

# Check only global hook status
commit-assistant global-hook-status
# or: python -m commitassist.main global-hook-status
```

### Hook Workflow Examples

**With Hook Installed:**

```bash
# Normal workflow with automatic suggestions
git add .
git commit          # Opens editor with AI suggestion
# Edit message if needed, save and close
```

**Manual Override:**

```bash
# Skip hook by providing message directly
git commit -m "Manual commit message"
```

**Hook Status Check:**

```bash
commit-assistant hook-status
# or: python -m commitassist.main hook-status
```

Output:

```
Git Hook Status Report:
============================================================
LOCAL REPOSITORY HOOK:
✗ No local hook

GLOBAL HOOK (works in all repos):
✓ Global hook installed and active
✨ Works in ALL Git repositories!
Location: /Users/username/.git-hooks/prepare-commit-msg
============================================================
RECOMMENDATIONS:
✅ You're all set! Global hook works everywhere.
```

### Command Reference

| Command                 | Description                                 | Example                            |
| ----------------------- | ------------------------------------------- | ---------------------------------- |
| `suggest`               | Generate commit message suggestions         | `suggest --count 3`                |
| `suggest --detailed`    | Generate detailed messages with header/body | `suggest --detailed --interactive` |
| `suggest --interactive` | Interactive selection and commit            | `suggest -i -c 5`                  |
| `suggest --auto-commit` | Auto-commit first suggestion                | `suggest -a`                       |
| `quick`                 | Quick commit workflow                       | `quick --detailed`                 |
| `setup`                 | Configure API key                           | `setup`                            |
| `install-hook`          | Install Git hook                            | `install-hook`                     |
| `--help`                | Show help for any command                   | `suggest --help`                   |

### Options Reference

| Option          | Short | Description                   | Default |
| --------------- | ----- | ----------------------------- | ------- |
| `--count`       | `-c`  | Number of suggestions (1-5)   | 1       |
| `--temp`        | `-t`  | Creativity level (0.0-1.0)    | 0.7     |
| `--detailed`    | `-d`  | Generate header + body format | False   |
| `--interactive` | `-i`  | Interactive selection mode    | False   |
| `--auto-commit` | `-a`  | Auto-commit first suggestion  | False   |

## 💡 Tips and Best Practices

### 1. Staging Changes

- Always stage your changes before generating suggestions: `git add .`
- Stage related changes together for better commit messages
- Use `git add -p` for selective staging

### 2. Choosing Message Types

- Use **simple messages** for small, straightforward changes
- Use **detailed messages** for complex features or significant refactoring
- Use **interactive mode** when you want to see multiple options

### 3. Creativity Levels

- **Low temperature (0.1-0.3)**: Consistent, predictable messages
- **Medium temperature (0.5-0.8)**: Balanced creativity and consistency
- **High temperature (0.9-1.0)**: Creative, varied messages

### 4. Workflow Recommendations

**For daily commits:**

```bash
git add .
commit-assistant quick
```

**For important features:**

```bash
git add .
commit-assistant suggest --detailed --interactive --count 3
```

**For code reviews:**

```bash
git add .
commit-assistant suggest --detailed --temp 0.3
```

## 🛠️ Development

### Project Structure

```
commit-assistant/
├── commitassist/
│   ├── __init__.py
│   ├── main.py          # Core functionality & CLI commands
│   └── hooks.py         # Git hooks management
├── requirements.txt     # Project dependencies
├── setup.py            # Package configuration (optional)
├── README.md           # This file
├── .env               # API key (create this)
└── .gitignore         # Git ignore rules
```

### Development Setup

1. **Fork and Clone**

   ```bash
   git clone https://github.com/jazir/commit-assistant.git
   cd commit-assistant
   ```

2. **Set Up Environment**

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Key**

   ```bash
   python -m commitassist.main setup
   ```

5. **Test Your Setup**

   ```bash
   # Test basic functionality
   python -m commitassist.main --help

   # Test with real changes
   echo "test" > test.txt
   git add test.txt
   python -m commitassist.main suggest
   ```

### Development Workflow

**Making Changes:**

```bash
# Make your changes to the code
# Test thoroughly
python -m commitassist.main suggest --interactive

# Use the tool to commit your own changes!
git add .
python -m commitassist.main suggest --interactive
```

**Testing Different Features:**

```bash
# Test interactive mode
python -m commitassist.main suggest --interactive

# Test detailed messages
python -m commitassist.main suggest --detailed

# Test hook functionality
python -m commitassist.main install-hook
git add .
git commit  # Should show AI suggestion

# Test global hooks
python -m commitassist.main install-global-hook
```

### Code Organization

- **`main.py`**: Contains core commit message generation, CLI interface, and user interaction
- **`hooks.py`**: Contains all Git hook management functionality (install, uninstall, status checking)
- **Separation of Concerns**: Hook functionality is modular and can be imported independently

### Contributing Guidelines

1. **Test your changes** thoroughly with various repository types
2. **Update documentation** if you add new features
3. **Follow existing code style** and patterns
4. **Add error handling** for edge cases
5. **Test on multiple platforms** (Windows, macOS, Linux) if possible

### Running Tests

```bash
# Basic functionality tests
python -m commitassist.main --help

# Test with different types of changes
echo "function test() { return true; }" > test.js
git add test.js
python -m commitassist.main suggest

# Test hook installation
python -m commitassist.main hook-status
python -m commitassist.main install-global-hook
python -m commitassist.main hook-status
```

### Development Tips

1. **Use the tool for its own development** - it's great for dogfooding
2. **Test with large diffs** to ensure truncation works properly
3. **Test in different repositories** (Python, JavaScript, mixed projects)
4. **Verify hooks work** in both development and installed modes
5. **Check cross-platform compatibility** especially for hook scripts

## 🔍 Troubleshooting

### Common Issues

**"No staged changes found"**

```bash
# Solution: Stage your changes first
git add .
# or stage specific files:
git add file1.py file2.js

# Check what's staged:
git status
```

**"OpenAI API key not found"**

```bash
# Solution 1: Use setup command
python -m commitassist.main setup

# Solution 2: Set environment variable
# Windows:
set OPENAI_API_KEY=your_key_here
# macOS/Linux:
export OPENAI_API_KEY=your_key_here

# Solution 3: Check if .env file exists and has correct format
# File should contain: OPENAI_API_KEY=your_key_here
```

**"Not a Git repository"**

```bash
# Solution: Ensure you're in a Git repository
git init
# or navigate to an existing Git repository
cd your-git-project
```

**"Git command failed"**

```bash
# Check Git installation
git --version

# Ensure Git is in your PATH
# Windows: Add Git to System PATH
# macOS: Install via Homebrew: brew install git
# Linux: sudo apt install git (Ubuntu) or sudo yum install git (CentOS)
```

**"commit-assistant command not found" (Development Mode)**

```bash
# You're in development mode, use full command:
python -m commitassist.main suggest

# To install properly:
pip install -e .
# Then you can use: commit-assistant suggest
```

**Import errors during development**

```bash
# Ensure virtual environment is activated
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check you're in the correct directory (should contain commitassist/ folder)
ls commitassist/
```

**Hook not working**

```bash
# Check hook status
python -m commitassist.main hook-status

# Reinstall hook
python -m commitassist.main uninstall-global-hook
python -m commitassist.main install-global-hook

# Test hook manually
git add .
git commit  # Should show AI suggestion in editor
```

### Platform-Specific Issues

#### Windows

- **Git Bash vs Command Prompt**: Use Git Bash for better hook compatibility
- **Path Issues**: Ensure Python and Git are in your system PATH
- **Line Endings**: Git handles this automatically with `core.autocrlf=true`

```bash
# Configure Git for Windows
git config --global core.autocrlf true
git config --global core.editor "code --wait"  # If using VS Code
```

#### macOS

- **Python Version**: Use `python3` if `python` points to Python 2
- **Homebrew Installation**: `brew install python git`

```bash
# Check Python version
python3 --version
# Use python3 instead of python if needed
python3 -m commitassist.main suggest
```

#### Linux

- **Permission Issues**: Ensure hook files are executable
- **Package Manager**: Use apt, yum, or dnf to install dependencies

```bash
# Install on Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip git

# Install on CentOS/RHEL
sudo yum install python3 python3-pip git
```

### API Usage and Costs

**Typical Costs:**

- Simple commit message: ~$0.001-0.003 per generation
- Detailed commit message: ~$0.003-0.008 per generation
- Very affordable for regular development work

**Rate Limits:**

- OpenAI has rate limits on API usage
- If you hit limits, wait a few minutes and try again
- Consider upgrading your OpenAI plan if needed

### Debug Mode

Add temporary debugging to understand issues:

```python
# Add to main.py temporarily
print(f"DEBUG: API Key found: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"DEBUG: Current directory: {os.getcwd()}")
print(f"DEBUG: Git repo check: {git.Repo('.').git_dir}")
```

### Getting Help

1. **Check this troubleshooting section** first
2. **Run with verbose output**: `python -m commitassist.main suggest --help`
3. **Check Git status**: `git status` and `git diff --cached`
4. **Verify API key**: Echo (without revealing) that it's set
5. **Test in a fresh repository** to isolate the issue

### Reset Everything

If all else fails, start fresh:

```bash
# Remove all hooks
python -m commitassist.main uninstall-global-hook
python -m commitassist.main uninstall-hook

# Recreate virtual environment
deactivate
rm -rf venv  # or rmdir /s venv on Windows
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall
pip install -r requirements.txt
python -m commitassist.main setup
python -m commitassist.main install-global-hook
```

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for their powerful language models
- GitPython for excellent Git integration
- Click for elegant command-line interfaces
- The open-source community for inspiration and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/jazir/commit-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jazir/commit-assistant/discussions)
- **Email**: jazirsha@gmail.com

---

**Happy committing! 🚀**

_Made with ❤️ for developers who want better commit messages_
