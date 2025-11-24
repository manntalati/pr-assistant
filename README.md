# PR Assistant CLI

[![Version](https://img.shields.io/pypi/v/pr-assistant-cli?color=red&label=version)](https://pypi.org/project/pr-assistant-cli/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Language](https://img.shields.io/badge/language-Python-brightgreen.svg)](#) 
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/pr-assistant-cli?period=total&units=NONE&left_color=grey&right_color=BLUE&left_text=downloads)](https://pepy.tech/projects/pr-assistant-cli)


PR Assistant is an AI-powered CLI tool designed to help developers streamline their workflow. It understands your codebase and automatically generates Pull Requests based on high-level instructions.

## Features

- **AI-Powered PR Creation**: Generate PRs with code changes, titles, and descriptions from simple prompts.
- **Codebase Understanding**: Analyzes your project structure to provide context-aware suggestions.
- **GitHub Integration**: Automatically creates branches and opens PRs in your repository.
- **Rate Limiting**: Built-in client-side rate limiter to prevent API abuse.
- **Gemini Integration**: Uses Google's Gemini models for intelligent code generation.

## Installation

You can install the package directly from the source:

```bash
git clone https://github.com/yourusername/pr-assistant.git
cd pr-assistant
pip install -e .
```

## Configuration

Before using the tool, you need to initialize the configuration with your API keys.

1.  **GitHub Token**: A Personal Access Token (PAT) with `repo` scope.
2.  **Gemini API Key**: Your Google Gemini API key.
3.  **Bot Token (Optional)**: A separate GitHub PAT for a bot account to post reviews.

Run the init command:

```bash
pr-assistant init
```

Follow the interactive prompts to save your credentials.

### Project-Level Configuration

You can configure the tool for specific projects to avoid re-entering the repository name.

1.  Run `pr-assistant init` inside your project directory.
2.  When prompted "Do you want to configure this directory as a project?", answer `y`.
3.  The repository name will be saved to a local `.pr-assistant.json` file.

**Note**: Your API keys are always stored securely in your global configuration (home directory) and are never saved to the local project file.

## Usage

### Global Options

- `--verbose`: Enable detailed debug logging.

```bash
pr-assistant --verbose create 1
```

### Create a PR

To create a PR, use the `create` command. You can specify the number of PRs to generate and a specific instruction.

```bash
pr-assistant create 1 --instruction "Add a hello world function to main.py"
```

### List PRs

To list active PRs in your repository:

```bash
pr-assistant list-prs
```

### Review a PR

To review a PR using AI:

```bash
pr-assistant review-pr <pr_number> --persona "Senior Software Engineer"
```

The AI will analyze the diff and post a comment on the PR with its findings.

## Development & Testing

This project includes a comprehensive test suite using `pytest`.

### Running Tests

To run the tests, ensure you have the dev dependencies installed:

```bash
pip install -e ".[dev]"
python3 -m pytest tests/
```

### Test Coverage

- **Unit Tests**: Config, Rate Limiter, Codebase Reader.
- **Mocked Tests**: GitHub Client, Agent (LLM).
- **Integration Tests**: CLI Commands.
- **Security Tests**: Key handling.

## License

MIT