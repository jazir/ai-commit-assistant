# AI Commit Assistant

🤖 AI-powered Git commit message generator with smart hook integration.

Never struggle with commit messages again! AI Commit Assistant uses OpenAI's GPT models to analyze your code changes and generate meaningful, conventional commit messages automatically.

## ✨ Features

- **Smart Commit Messages**: AI analyzes your git diff and generates contextual commit messages
- **Multiple Suggestions**: Get several commit message options to choose from
- **Detailed Mode**: Generate detailed commit messages with body and breaking changes
- **Git Hook Integration**: Automatically suggest commit messages during `git commit`
- **Conventional Commits**: Follows conventional commit format (feat, fix, docs, etc.)
- **Customizable**: Configure AI model, temperature, and message style
- **Easy Setup**: Simple CLI setup and configuration

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

3. **Start using it**:

   ```bash
   # Make some changes to your code
   git add .

   # Get AI-generated commit suggestions
   ai-commit-assistant suggest
   ```

## 🎯 Usage

### Basic Commands

```bash
# Get commit message suggestions
ai-commit-assistant suggest

# Get detailed commit messages with body
ai-commit-assistant suggest --detailed

# Get multiple suggestions to choose from
ai-commit-assistant suggest --count 3

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

🤖 AI Commit Suggestions:
1. feat: add user authentication system
2. feat: implement login and signup functionality
3. feat: add JWT-based authentication

Choose a suggestion (1-3) or press Enter to copy #1: 1
✅ Copied to clipboard: feat: add user authentication system
```

### Detailed Mode

```bash
$ ai-commit-assistant suggest --detailed

🤖 Detailed Commit Suggestion:

feat: add user authentication system

- Implement JWT-based authentication
- Add login and signup endpoints
- Create user model and database schema
- Add password hashing and validation
- Include authentication middleware

BREAKING CHANGE: Authentication now required for protected routes
```

### Multiple Options

```bash
$ ai-commit-assistant suggest --count 5

🤖 AI Commit Suggestions:
1. feat: add user authentication system
2. feat: implement JWT-based login functionality
3. feat: create user authentication and authorization
4. feat: add secure user login and registration
5. feat: implement authentication with JWT tokens

Choose a suggestion (1-5) or press Enter to copy #1:
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
