# Contributing to PyScrum

Thank you for your interest in contributing to **PyScrum**!  
We welcome improvements, bug fixes, ideas, and feature suggestions.

---

## 🔧 Setting up the project locally

1. Clone the repository:

```bash
git clone https://github.com/dospalko/pyscrum.git
cd pyscrum
```
Set up a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
pip install -r requirements-dev.txt
```

## 🧪 Running tests
All code must pass unit tests. To run the test suite:

```bash
pytest --cov=pyscrum
```
You’ll get a test report with coverage statistics.

## ✍️ Creating a pull request
1. Fork the repository  
2. Create a feature branch:

```bash
git checkout -b feature/your-feature-name
```
3. Make your changes and commit them:

```bash
git commit -m "feat: short description of your feature"
```
4. Push to your fork:

```bash
git push origin feature/your-feature-name
```
5. Open a pull request on GitHub

## 🧹 Code style
- Follow [PEP8](https://peps.python.org/pep-0008/)  
- Use meaningful commit messages  
- Keep functions and methods short and clear  
- Add docstrings where appropriate

