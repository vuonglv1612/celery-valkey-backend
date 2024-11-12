# Publishing to PyPI

This guide explains how to publish your package to PyPI using GitHub Actions.

## One-time Setup

1. Create a PyPI account
    - Go to https://pypi.org/account/register/
    - Create your account

2. Create a PyPI API token
    - Log in to PyPI
    - Go to Account Settings → API tokens
    - Click "Create API token"
    - Give it a name (e.g., "GitHub Actions")
    - Save the token safely (you won't see it again)

3. Add PyPI token to GitHub Secrets
    - Go to your GitHub repository
    - Click Settings → Secrets and variables → Actions
    - Click "New repository secret"
    - Name: `PYPI_API_TOKEN`
    - Value: Your PyPI token
    - Click "Add secret"

## Publishing a New Release

1. Update version in setup.py
```python
setup(
    name="celery-valkey-backend",
    version="X.Y.Z",  # Update this
    ...
)
```

2. Create a new release on GitHub
    - Go to your repository on GitHub
    - Click "Releases" on the right
    - Click "Create a new release"
    - Choose a tag (e.g., v1.0.0)
    - Write release notes
    - Click "Publish release"

3. The GitHub Action will automatically:
    - Build your package
    - Upload it to PyPI

## Verification

After publishing:
1. Check your package on PyPI: https://pypi.org/project/celery-valkey-backend/
2. Try installing it:
```bash
pip install celery-valkey-backend==X.Y.Z
```

## Troubleshooting

If the publish fails:
1. Check the GitHub Actions logs
2. Verify the PyPI token is correctly set
3. Ensure version number is unique
4. Check package build is successful locally:
```bash
python -m build
twine check dist/*
```

## Development Workflow

1. Make changes to code
2. Update tests
3. Update version in setup.py
4. Commit changes
5. Create GitHub release
6. GitHub Actions will handle PyPI publishing