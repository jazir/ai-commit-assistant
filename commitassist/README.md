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

### Method 2: Install from Source

```bash
git clone https://github.com/jazir/commit-assistant.git
cd commit-assistant
pip install -e .
```

### Method 3: Development Setup (Current)

```bash
git clone https://github.com/jazir/commit-assistant.git
cd commit-assistant
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

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

### Basic Commands

All examples show both installed and development versions:

| Installed Version          | Development Version                   |
| -------------------------- | ------------------------------------- |
| `commit-assistant suggest` | `python -m commitassist.main suggest` |
| `commit-assistant quick`   | `python -m commitassist.main quick`   |

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

# More creative
commit-assistant suggest --temp 0.9
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

## 🔧 Advanced Features

### Git Hook Integration

Install as a Git hook for automatic suggestions during commits:

```bash
commit-assistant install-hook
# or: python -m commitassist.main install-hook
```

After installation, when you run `git commit`, you'll see suggested messages in your commit editor.

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
│   └── main.py          # Main application code
├── requirements.txt     # Dependencies
├── setup.py            # Package configuration
├── README.md           # This file
└── .env               # API key (create this)
```

### Contributing

1. Fork the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```
3. Install dependencies: `pip install -r requirements.txt`
4. Make your changes
5. Test thoroughly
6. Submit a pull request

### Running Tests

```bash
# Test basic functionality
git add .
python -m commitassist.main suggest

# Test interactive mode
python -m commitassist.main suggest --interactive

# Test detailed messages
python -m commitassist.main suggest --detailed
```

## 🔍 Troubleshooting

### Common Issues

**"No staged changes found"**

- Run `git add .` or `git add <specific-files>` first
- Check `git status` to see staged changes

**"OpenAI API key not found"**

- Run `commit-assistant setup` or `python -m commitassist.main setup`
- Ensure your `.env` file contains `OPENAI_API_KEY=your_key_here`
- Check that the `.env` file is in the correct location

**"Not a Git repository"**

- Ensure you're in a Git repository (`git init` if needed)
- Check that `.git` folder exists in your project

**"Git command failed"**

- Ensure Git is installed and in your PATH
- Try running `git status` manually to check Git setup

**Import errors during development**

- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check that you're in the correct directory

### Windows-Specific Notes

- Use `venv\Scripts\activate` to activate virtual environment
- Git hooks work with Git Bash
- PowerShell multi-line strings: Use `@"..."@` syntax

### API Usage and Costs

- Typical cost: $0.001-0.005 per commit message (very affordable)
- API calls are made only when generating suggestions
- No API calls during Git operations or setup

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
