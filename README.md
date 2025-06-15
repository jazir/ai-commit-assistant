# AI Commit Assistant

🤖 AI-powered Git commit message generator with smart hook integration.

Never struggle with commit messages again! AI Commit Assistant uses OpenAI's GPT models to analyze your code changes and generate meaningful, conventional commit messages automatically.

## ✨ Features

- **Smart Commit Messages**: AI analyzes your git diff and generates contextual commit messages
- **Interactive Mode**: Select from multiple suggestions and commit directly with confirmation
- **Multiple Suggestions**: Get several commit message options to choose from (1-10 suggestions)
- **Flexible Workflow**: Copy to clipboard, regenerate suggestions, or commit directly
- **Detailed Mode**: Generate detailed commit messages with body and breaking changes
- **Git Hook Integration**: Automatically suggest commit messages during `git commit`
- **Conventional Commits**: Follows conventional commit format (feat, fix, docs, etc.)
- **Easy Setup**: Simple CLI setup and configuration
- **Smart Options**: Copy, regenerate, or quit without committing

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

   This will prompt you to enter your OpenAI API key securely.

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

# Install smart Git hook (auto-suggests during git commit)
ai-commit-assistant install-hook

# Remove the Git hook
ai-commit-assistant uninstall-hook

# Show help
ai-commit-assistant --help
```

### Smart Git Hook

Install the smart hook to get automatic suggestions during `git commit`:

```bash
ai-commit-assistant install-hook
```

Now when you run `git commit` (without `-m`), you'll automatically get AI-generated suggestions:

```bash
git add .
git commit
# AI will suggest commit messages, you can accept or edit them
```

### Configuration

```bash
# Setup or reconfigure API key
ai-commit-assistant setup

# Check current configuration
ai-commit-assistant --help
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
Implement JWT-based authentication with login and signup
============================================================
[2] ============================================================
feat: implement user login functionality
Add secure authentication system with JWT tokens
============================================================
[3] ============================================================
feat: create authentication and authorization
Add user management with secure login system
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
Implement JWT-based authentication with login and signup
============================================================
[2] ============================================================
feat: implement user login functionality
Add secure authentication system with JWT tokens
============================================================
[3] ============================================================
feat: create authentication and authorization
Add user management with secure login system
============================================================

Options:
  1-3: Select a suggestion to commit
  c: Copy a suggestion to clipboard (if available)
  r: Regenerate suggestions
  q: Quit without committing
What would you like to do?: 2

Selected message:
============================================================
feat: implement user login functionality
Add secure authentication system with JWT tokens
============================================================
Commit with this message? [Y/n]: y
✓ Commit successful!
[main a1b2c3d] feat: implement user login functionality
 5 files changed, 127 insertions(+), 23 deletions(-)
```

## 🔧 Advanced Configuration

The tool stores configuration in `~/.ai-commit-assistant/config.json`. You can manually edit:

```json
{
  "openai_api_key": "your-api-key",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 100
}
```

### Environment Variables

You can also set your API key using environment variables:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 🛠️ Development

### Installing from Source

```bash
git clone https://github.com/jazir/ai-commit-assistant.git
cd ai-commit-assistant
pip install -e .
```

### Running Tests

```bash
python -m pytest tests/
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

## 🔗 Links

- **PyPI**: https://pypi.org/project/ai-commit-assistant/
- **GitHub**: https://github.com/jazir/ai-commit-assistant
- **Documentation**: https://github.com/jazir/ai-commit-assistant/wiki

---

Made with ❤️ by [Jazir Hameed](https://github.com/jazir)
