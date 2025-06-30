# AI Commit Assistant

🤖 AI-powered Git commit message generator with smart hook integration.

Never struggle with commit messages again! AI Commit Assistant uses OpenAI's GPT models to analyze your code changes and generate meaningful, conventional commit messages automatically.

[![PyPI version](https://badge.fury.io/py/ai-commit-assistant.svg)](https://badge.fury.io/py/ai-commit-assistant)
[![Python Support](https://img.shields.io/pypi/pyversions/ai-commit-assistant.svg)](https://pypi.org/project/ai-commit-assistant/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **Smart Commit Messages**: AI analyzes your git diff and generates contextual commit messages
- **Interactive Mode**: Select from multiple suggestions and commit directly with confirmation
- **Multiple Suggestions**: Get several commit message options to choose from (1-10 suggestions)
- **Flexible Workflow**: Copy to clipboard, regenerate suggestions, or commit directly
- **Detailed Mode**: Generate detailed commit messages with body and breaking changes
- **Git Hook Integration**: Automatically suggest commit messages during `git commit`
- **Smart Hook System**: Intelligently chooses between simple and detailed suggestions based on change complexity
- **Conventional Commits**: Follows conventional commit format (feat, fix, docs, etc.)
- **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux
- **Easy Setup**: Simple CLI setup and configuration with robust API key handling
- **Flexible API Key Support**: Supports API keys of any length (50-200+ characters)

## 🚀 Installation

```bash
pip install ai-commit-assistant
```

## 📋 Prerequisites

- Python 3.7+
- Git repository
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## ⚙️ Quick Setup

1. **Install the package**:

   ```bash
   pip install ai-commit-assistant
   ```

2. **Configure your OpenAI API key**:

   ```bash
   ai-commit-assistant setup
   ```

   This will prompt you to enter your OpenAI API key. The input is visible for easy copy-paste verification, and supports API keys of any length.

3. **Start using it with interactive mode** (recommended):

   ```bash
   # Make some changes to your code
   git add .

   # Get AI-generated commit suggestions with interactive selection
   ai-commit-assistant suggest --count 3 --interactive
   ```

## 🎯 Usage

### Basic Commands

```bash
# Get a single commit message suggestion
ai-commit-assistant suggest

# Get detailed commit messages with body
ai-commit-assistant suggest --detailed

# Get multiple suggestions to choose from
ai-commit-assistant suggest --count 3

# Interactive mode - select and commit directly
ai-commit-assistant suggest --count 3 --interactive

# Quick commit with auto-generated message
ai-commit-assistant quick

# Install smart Git hook (auto-suggests during git commit)
ai-commit-assistant install-hook

# Install global Git hook (works in all repositories)
ai-commit-assistant install-global-hook

# Remove Git hooks
ai-commit-assistant uninstall-hook

# Test API connectivity
ai-commit-assistant test-api

# Show help
ai-commit-assistant --help
```

### Smart Git Hook

Install the smart hook to get automatic suggestions during `git commit`:

```bash
ai-commit-assistant install-hook
```

The smart hook intelligently analyzes your changes and provides:

- **Simple suggestions** for small changes (< 50 lines, < 3 files)
- **Detailed suggestions** for larger changes (> 50 lines, > 3 files, or new files)

Now when you run `git commit` (without `-m`), you'll automatically get AI-generated suggestions:

```bash
git add .
git commit
# AI will suggest commit messages in your editor
```

### Global Hook (Recommended)

Install a global hook that works across all your repositories:

```bash
ai-commit-assistant install-global-hook
```

This sets up the hook once and it works everywhere!

### Configuration Management

```bash
# Setup or reconfigure API key
ai-commit-assistant setup

# Clean configuration (remove saved API key)
ai-commit-assistant clean-config

# Debug configuration files
ai-commit-assistant debug-config

# Test API connectivity
ai-commit-assistant test-api
```

## 📖 Examples

### Simple Suggestions

```bash
$ ai-commit-assistant suggest

Generated commit message: feat: add user authentication system
```

### Multiple Suggestions

```bash
$ ai-commit-assistant suggest --count 3

Generated 3 commit message suggestion(s):

[1] ============================================================
feat: add user authentication system
============================================================

[2] ============================================================
feat: implement JWT-based login functionality
============================================================

[3] ============================================================
feat: create secure user authentication flow
============================================================

To use a suggestion: git commit -m "suggested message"
Tip: Use --interactive (-i) to select and commit directly!
```

### Interactive Mode (Recommended)

```bash
$ ai-commit-assistant suggest --count 3 --interactive

Generated 3 commit message suggestion(s):

[1] ============================================================
feat: add user authentication system
============================================================

[2] ============================================================
feat: implement JWT-based login functionality
============================================================

[3] ============================================================
feat: create secure user authentication flow
============================================================

Options:
  1-3: Select a suggestion to commit
  c: Copy a suggestion to clipboard (if available)
  r: Regenerate suggestions
  q: Quit without committing

What would you like to do?: 2

Selected message:
============================================================
feat: implement JWT-based login functionality
============================================================

Commit with this message? [Y/n]: y

+ Commit successful!
[main a1b2c3d] feat: implement JWT-based login functionality
 5 files changed, 127 insertions(+), 23 deletions(-)
```

### Detailed Mode

```bash
$ ai-commit-assistant suggest --detailed

Generated detailed commit message:

feat: implement user authentication system

Add comprehensive JWT-based authentication to secure API endpoints.

- Create login/logout functionality with token generation
- Implement middleware for request validation
- Add secure password hashing with bcrypt
- Set up session management for user state
- Create user registration and profile management

This addresses security requirements and improves user experience
by providing seamless authentication flow across the application.
```

### Quick Commit

```bash
$ ai-commit-assistant quick

Generating commit suggestion...

Suggested commit message:
============================================================
feat: add user authentication system
============================================================

Commit with this message? [Y/n]: y

+ Commit successful!
```

## 🔧 Advanced Configuration

### API Key Management

The tool supports multiple ways to provide your API key:

1. **Interactive setup** (recommended):

   ```bash
   ai-commit-assistant setup
   ```

2. **Environment variable**:

   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Project-specific .env file**:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

The tool supports API keys of any length and handles various formats automatically.

### Hook Configuration

Check hook status:

```bash
# Check local repository hook
ai-commit-assistant hook-status

# Check global hook status
ai-commit-assistant global-hook-status
```

### Model and Temperature Settings

You can customize the AI behavior by modifying the code:

- **Model**: Change from `gpt-3.5-turbo` to `gpt-4` for better results (higher cost)
- **Temperature**: Adjust creativity (0.0 = deterministic, 1.0 = creative)

## 🛠️ Development

### Installing from Source

```bash
git clone https://github.com/jazir/ai-commit-assistant.git
cd ai-commit-assistant
pip install -e .
```

### Project Structure

```
ai-commit-assistant/
├── commitassist/
│   ├── __init__.py
│   ├── main.py          # Main CLI application
│   └── hooks.py         # Git hook management
├── setup.py             # Package configuration
├── README.md
├── requirements.txt
└── .env.example
```

### Running Tests

```bash
# Test API connectivity
ai-commit-assistant test-api

# Debug configuration
ai-commit-assistant debug-config

# Test hooks
ai-commit-assistant install-hook
git commit  # Test the hook
ai-commit-assistant uninstall-hook
```

## 📝 Conventional Commits

AI Commit Assistant follows the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks
- `perf:` - Performance improvements
- `ci:` - CI/CD changes
- `build:` - Build system changes

## 🔒 Security & Privacy

- API keys are stored locally in `~/.commit-assistant/.env`
- No commit data is stored or logged by this tool
- All communication is directly with OpenAI's API
- Your code diffs are sent to OpenAI for analysis (standard API usage)

## 🚨 Troubleshooting

### Common Issues

**API Key Issues**:

```bash
# Clean and reconfigure
ai-commit-assistant clean-config
ai-commit-assistant setup
ai-commit-assistant test-api
```

**Hook Not Working**:

```bash
# Check hook status
ai-commit-assistant debug-config

# Reinstall hooks
ai-commit-assistant uninstall-hook
ai-commit-assistant install-hook
```

**Windows Users**:

- Use Git Bash, PowerShell, or Command Prompt
- The tool is fully Windows-compatible
- Long API keys (150+ characters) are supported

**No Staged Changes**:

```bash
git add .  # Stage your changes first
ai-commit-assistant suggest
```

### Debug Commands

```bash
# Check configuration
ai-commit-assistant debug-config

# Test API connectivity
ai-commit-assistant test-api

# Check hook status
ai-commit-assistant hook-status
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- The Git community for the amazing version control system
- All contributors who help improve this tool

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/jazir/ai-commit-assistant/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/jazir/ai-commit-assistant/discussions)
- 📧 **Email**: jazirsha@gmail.com

## 📈 Changelog

### v1.0.1 (Latest)

- ✅ Enhanced cross-platform compatibility (Windows, macOS, Linux)
- ✅ Support for API keys of any length (50-200+ characters)
- ✅ Improved input sanitization and error handling
- ✅ Smart Git hook with intelligent suggestion selection
- ✅ Global Git hook support
- ✅ Better debugging and configuration management
- ✅ Robust API key validation and setup process
- ✅ Enhanced Unicode and encoding support for Windows

### v1.0.0

- 🎉 Initial release
- ✅ Basic commit message generation
- ✅ Interactive mode
- ✅ Git hook integration
- ✅ Conventional commits support

## 🔗 Links

- **PyPI**: https://pypi.org/project/ai-commit-assistant/
- **GitHub**: https://github.com/jazir/ai-commit-assistant
- **Documentation**: https://github.com/jazir/ai-commit-assistant/wiki

---

Made with ❤️ by [Jazir Hameed](https://github.com/jazir)
