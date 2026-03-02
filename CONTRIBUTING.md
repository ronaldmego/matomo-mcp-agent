# Contributing to Matomo MCP

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

1. Fork and clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your credentials
4. Run the app: `streamlit run app.py`

## How to Contribute

### Reporting Bugs

Open an [issue](https://github.com/ronaldmego/matomo-mcp/issues) with:
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS

### Suggesting Features

Open an issue with the `enhancement` label describing:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives you considered

### Submitting Code

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Test with `python test_api.py`
4. Commit with a descriptive message: `git commit -m "feat: add new tool"`
5. Push and open a Pull Request

## Code Style

- Python code follows standard conventions
- All code, variables, and comments in English
- Commit messages use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, etc.)

## Adding New Matomo Tools

To add a new analytics tool:

1. Add the function in `server.py` with the `@mcp.tool` decorator
2. Add a LangChain `Tool` wrapper in `app.py`
3. Update the tools table in `README.md`

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
