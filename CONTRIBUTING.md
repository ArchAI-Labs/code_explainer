# Contributing to code_explainer

Thank you for your interest in contributing to code_explainer! We appreciate your time and effort. This document outlines the guidelines for contributing to this project. By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

There are many ways you can contribute to code_explainer, including:

* **Reporting Bugs:** If you find a bug, please open an issue on GitHub. Be sure to include:
    * A clear and descriptive title.
    * Steps to reproduce the bug.
    * The expected behavior.
    * The actual behavior.
    * Your operating system and version.
    * The code_explainer version (if applicable).
* **Suggesting Enhancements:** Have an idea for a new feature or improvement? Open an issue to discuss it with the maintainers. Explain your suggestion in detail and why you think it would be beneficial.
* **Submitting Pull Requests:** If you've fixed a bug or implemented a new feature, submit a pull request! Please follow these guidelines:
    * Create a new branch for your changes: `git checkout -b feature/your-feature-name` or `git checkout -b bugfix/bug-description`
    * Make your changes.
    * Ensure your code follows the project's coding style (see below).
    * Write clear and concise commit messages. Follow the [Conventional Commits](https://www.conventionalcommits.org/v1.0.0/) specification if possible.
    * Test your changes thoroughly.
    * Submit your pull request to the `develop` branch.
    * Include a clear description of your changes in the pull request.
* **Improving Documentation:** Outdated or unclear documentation? Help us improve it! Submit a pull request with your changes.
* **Spreading the Word:** Share the project with others! Let people know about code_explainer and its features.

## Development Setup

To contribute code, you'll need to set up your development environment. Here's a general guide:

1. **Fork the Repository:** Click the "Fork" button on the GitHub page.
2. **Clone your Fork:** `git clone https://github.com/your-username/code_explainer.git`
3. **Create a Virtual Environment (Recommended):** `python3 -m venv .venv` (or similar, depending on your language)
4. **Activate the Virtual Environment:** `. .venv/bin/activate` (or similar)
5. **Install Dependencies:** `crewai install` (or similar)

## Coding Style

Please adhere to the project's coding style. We use the [Black](https://black.readthedocs.io/en/stable/) formatter for Python code.  Run `black .` to format your code before submitting a pull request.

## Testing

All contributions should be thoroughly tested. Run the project's tests using `pytest`.

## Commit Message Guidelines

We encourage you to use clear and descriptive commit messages. A good commit message should explain *what* changed and *why*. Consider using the [Conventional Commits](https://www.conventionalcommits.org/v1.0.0/) specification.

## Code of Conduct

This project adheres to the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold its principles.

Thank you again for your contribution!