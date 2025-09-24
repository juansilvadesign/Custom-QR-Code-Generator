# 🤝 Contributing to Custom QR Code Generator

Thank you for your interest in contributing to the Custom QR Code Generator! We welcome contributions from developers of all skill levels. This document provides guidelines and information on how to contribute effectively to this project.

## 🌟 Ways to Contribute

There are many ways you can contribute to this project:

- 🐛 **Bug Reports**: Help us identify and fix issues
- 💡 **Feature Requests**: Suggest new features or improvements
- 🔧 **Code Contributions**: Submit bug fixes, new features, or improvements
- 📚 **Documentation**: Improve README, add examples, or write tutorials
- 🎨 **Design**: Contribute logos, icons, or UI improvements
- 🧪 **Testing**: Help test the application on different platforms

## 🚀 Getting Started

### Prerequisites

Before contributing, make sure you have:

- Python 3.7 or higher installed
- Git installed and configured
- A GitHub account
- Basic knowledge of Python programming

### Setting Up Your Development Environment

1. **Fork the repository**
   ```bash
   # Click the "Fork" button on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/Custom-QR-Code-Generator.git
   cd Custom-QR-Code-Generator
   ```

2. **Add the upstream remote**
   ```bash
   git remote add upstream https://github.com/juansilvadesign/Custom-QR-Code-Generator.git
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv .env
   ```

4. **Activate the virtual environment**
   - **Windows**: `.env\Scripts\activate`
   - **macOS/Linux**: `source .env/bin/activate`

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Test the installation**
   ```bash
   python main.py
   ```

## 📋 Contribution Workflow

### For Bug Fixes and Features

1. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   # or for bug fixes:
   git checkout -b bugfix/fix-issue-description
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow the existing code style
   - Add comments where necessary
   - Test your changes thoroughly

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add some amazing feature"
   ```
   
   **Commit Message Guidelines:**
   - Use present tense ("Add feature" not "Added feature")
   - Use imperative mood ("Move cursor to..." not "Moves cursor to...")
   - Limit the first line to 72 characters or less
   - Reference issues and pull requests liberally after the first line

4. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

5. **Open a Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill out the pull request template
   - Link any related issues

## 💡 Feature Ideas and Roadmap

Here are some ideas for contributions. Feel free to pick any of these or suggest your own:

### 🎨 **UI/UX Improvements**
- [ ] **GUI Interface**: Create a graphical user interface using tkinter, PyQt, or web-based interface
- [ ] **Progress Indicators**: Add progress bars for QR code generation
- [ ] **Color Picker**: Visual color selection instead of text input
- [ ] **Live Preview**: Real-time QR code preview as users type

### 🚀 **Core Features**
- [ ] **Multiple Export Formats**: PNG, JPEG, PDF export options
- [ ] **Logo Embedding**: Add logos or images to the center of QR codes
- [ ] **Batch Processing**: Generate multiple QR codes from CSV or text files
- [ ] **QR Code Reading**: Decode existing QR codes
- [ ] **Custom Shapes**: Round corners, circular QR codes
- [ ] **Gradient Colors**: Support for gradient backgrounds/foregrounds

### 🔧 **Technical Improvements**
- [ ] **Configuration Files**: YAML/JSON config for default settings
- [ ] **Plugin System**: Extensible architecture for custom content types
- [ ] **CLI Arguments**: Command-line interface for scripting
- [ ] **API Mode**: REST API for web integration
- [ ] **Caching**: Cache generated QR codes for repeated content

### 📱 **Content Type Extensions**
- [ ] **vCard Support**: Contact information QR codes
- [ ] **Calendar Events**: iCal event QR codes
- [ ] **Cryptocurrency**: Bitcoin/crypto wallet addresses
- [ ] **Social Media**: Instagram, Twitter, LinkedIn profiles
- [ ] **App Store Links**: Direct links to mobile apps

### 🧪 **Testing and Quality**
- [ ] **Unit Tests**: Comprehensive test suite
- [ ] **Integration Tests**: End-to-end testing
- [ ] **Performance Tests**: Benchmark QR code generation speed
- [ ] **Cross-platform Testing**: Ensure compatibility across OS

## 🎯 Code Style Guidelines

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Use type hints where appropriate

**Example:**
```python
def get_color_input(prompt: str, default_color: str) -> str:
    """
    Get color input from user with validation.
    
    Args:
        prompt: The prompt message to display to the user
        default_color: Default color to use if no input provided
        
    Returns:
        A valid color string in hex format
        
    Raises:
        ValueError: If color format is invalid
    """
    # Implementation here
```

### Documentation Style

- Use clear, concise language
- Include examples where helpful
- Keep README sections focused and scannable
- Use consistent emoji and formatting

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear Description**: What happened vs. what you expected
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Environment Info**: 
   - Operating system and version
   - Python version
   - Any relevant error messages
4. **Screenshots**: If applicable, add screenshots to help explain the problem

**Bug Report Template:**
```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Environment**
- OS: [e.g. Windows 10, macOS 12.1, Ubuntu 20.04]
- Python Version: [e.g. 3.9.7]
- Error Message: [paste any error messages]

**Additional context**
Add any other context about the problem here.
```

## 💬 Feature Requests

For feature requests, please include:

1. **Problem Statement**: What problem does this solve?
2. **Proposed Solution**: How would you like it to work?
3. **Alternatives**: What alternatives have you considered?
4. **Use Cases**: When would this feature be useful?

## 📝 Pull Request Guidelines

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] Self-review of your own code
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation updates if needed
- [ ] No merge conflicts with the main branch

### Pull Request Template

```markdown
## Description
Brief description of changes and why they were made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] I have tested this change locally
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
```

## 🏷️ Issue Labels

We use the following labels to categorize issues:

- **🐛 bug**: Something isn't working
- **✨ enhancement**: New feature or request
- **📚 documentation**: Improvements or additions to documentation
- **❓ question**: Further information is requested
- **🆘 help wanted**: Extra attention is needed
- **👍 good first issue**: Good for newcomers
- **🔧 maintenance**: Code maintenance and refactoring

## 🎉 Recognition

Contributors will be recognized in the following ways:

- Listed in the project's contributors section
- Mentioned in release notes for significant contributions
- GitHub's automatic contributor recognition
- Special recognition for first-time contributors

## 📞 Getting Help

If you need help or have questions:

1. **Check Existing Issues**: Search for similar questions or problems
2. **Documentation**: Review the README and code comments
3. **Create an Issue**: Open a new issue with the "question" label
4. **Discussion**: Use GitHub Discussions for broader topics

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same MIT License that covers the project. See [LICENSE](LICENSE) file for details.

---

Thank you for contributing to Custom QR Code Generator! 🎉

*Every contribution, no matter how small, makes a difference and is greatly appreciated.*