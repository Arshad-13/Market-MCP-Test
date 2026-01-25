# Contributing to Market Intelligence MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Market-MCP-Test.git
   cd Market-MCP-Test
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest  # For testing
   ```

## Code Guidelines

### Python Style
- Follow PEP 8
- Use type hints where possible
- Document all public functions with docstrings
- Keep functions focused and under 50 lines when possible

### Naming Conventions
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Testing
- Write tests for new features
- Run test suite before committing:
  ```bash
  pytest tests/ -v
  ```
- Maintain > 80% code coverage

## Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   pytest tests/ -v
   python -m tools.exchange_tools  # Manual testing
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "feat: Add your feature description"
   ```
   
   Use conventional commits:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation
   - `refactor:` Code refactoring
   - `test:` Testing changes

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

## What We're Looking For

### Priority Areas
- ✅ Additional exchange integrations (Bybit, OKX, etc.)
- ✅ More ML models (LSTM, Transformers)
- ✅ Enhanced backtesting capabilities
- ✅ Additional anomaly detection patterns
- ✅ Performance optimizations

### Feature Ideas
- Redis caching layer
- PostgreSQL support
- REST API wrapper
- Mobile app integration
- Advanced portfolio analytics

## Code Review Criteria

Your PR will be reviewed for:
- **Functionality**: Does it work as intended?
- **Tests**: Are changes covered by tests?
- **Documentation**: Is it well-documented?
- **Style**: Does it follow project conventions?
- **Performance**: Are there any bottlenecks?

## Questions?

- Open an [Issue](https://github.com/Arshad-13/Market-MCP-Test/issues)
- Join [Discussions](https://github.com/Arshad-13/Market-MCP-Test/discussions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping improve the Market Intelligence MCP Server! 🚀
