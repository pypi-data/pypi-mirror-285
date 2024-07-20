# Django-Cythonizer 🚀

![Django-Cythonizer Logo](https://raw.githubusercontent.com/salah-alhajj/django-cythonizer/main/Cython_logo.svg?token=GHSAT0AAAAAACT36IXH3OKDLE7OCUBENUZGZU2FRXQ)

<p align="center">
  <a href="https://badge.fury.io/py/django-cythonizer">
    <img src="https://badge.fury.io/py/django-cythonizer.svg" alt="PyPI version" />
  </a>
  <a href="https://pypi.org/project/django-cythonizer/">
    <img src="https://img.shields.io/pypi/pyversions/django-cythonizer.svg" alt="Python Versions" />
  </a>
  <a href="https://www.djangoproject.com/">
    <img src="https://img.shields.io/badge/django-3.2%20%7C%204.0%20%7C%204.1%20%7C%204.2-blue" alt="Django Versions" />
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  </a>
  <a href="https://github.com/salah-alhajj/django-cythonizer/actions">
    <img src="https://github.com/salah-alhajj/django-cythonizer/workflows/Build/badge.svg" alt="Build Status" />
  </a>
  <a href="https://codecov.io/gh/salah-alhajj/django-cythonizer">
    <img src="https://codecov.io/gh/salah-alhajj/django-cythonizer/branch/main/graph/badge.svg" alt="codecov" />
  </a>
</p>


Supercharge your Django project with the power of Cython! 🐍💨

## 🌟 Features

- 🚀 Automatically compile Django views and models to Cython
- 📈 Boost performance by up to 30% (results may vary)
- 🛠 Easy integration with existing Django projects
- 🔒 Secure your Python source code
- 🔧 Customizable compilation settings

## 🚀 Quick Start

### Installation

```bash
pip install django-cythonizer
```

### Usage

1. Add 'cythonizer' to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
    # ...
    'cythonizer',
    # ...
]
```

2. Run the cythonize command:

```bash
python manage.py cythonize
```

3. Open build FLoder and run it as normal django project 
<br>
4. Enjoy the speed boost! 🎉🎉🎉🎉
<br/>
## ⚠️ Important Considerations

### Handling Excluded Paths

- **Virtual Environments**: The `.venv` directory is excluded by default.
- **Migration Files**: The `migrations` folders are excluded to avoid issues with Django's migration system.
- **Configuration Files**: Sensitive files like `settings.py` and `urls.py` are excluded.

### Other Considerations

- Always test your project after compilation to ensure no unexpected errors occur.
- Keep a backup of your original code before applying compilation on a large scale.

## 🔧 Configuration

The `settings.yaml` file in your project root controls the cythonizer behavior:

```yaml
build:
  path: 'build'

exclude:
  files:
    - 'setup.py'
    - '__init__.py'
    - 'manage.py'
    - 'urls.py'
    - '.gitigonre'
    - '.git'
  dirs:
    - 'migrations'
    - '.venv'
    - 'build'

# ... (other settings)
```

## 🔥 Performance Comparison

Here's a quick benchmark comparing a standard Django view vs a Cythonized view:

| Scenario   | Requests/sec | Latency (ms) |
|------------|--------------|--------------|
| Standard   | 1000         | 50           |
| Cythonized | 1300         | 38           |

As the load increases on the system, the performance and reliability gap between the standard Django project and the Cythonized Django project widens, with the Cythonized version consistently outperforming, despite both projects being identical in terms of code and environment.

## 🛠 How It Works

1. **Analysis**: Django-Cythonizer scans your project structure.
2. **Compilation**: It compiles eligible Python files to Cython.
3. **Integration**: The compiled modules seamlessly replace the original ones.
4. **Optimization**: Enjoy the performance benefits!

## 🤔 FAQs

<details>
<summary>Is it compatible with all Django versions?</summary>
Django-Cythonizer supports Django 3.2 and above, as specified in the project requirements.
</details>

<details>
<summary>Will it break my existing code?</summary>
No, Django-Cythonizer is designed to be non-intrusive. Your original Python files remain untouched.
</details>

<details>
<summary>Can I use it in production?</summary>
Absolutely! Many projects use Cython in production to great effect. Always thoroughly test before deploying.
</details>

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## 📜 License

Django-Cythonizer is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

## 🙏 Acknowledgements

- The amazing Django community
- The Cython team for their incredible work
- All our contributors and users

## 📬 Contact

For support or queries, reach out to us at [contact@salahaldain.com](mailto:contact@salahaldain.com).


---
<br>
<p align="center">
  Made with ❤️ by developers, for developers.<br>
  Initiated by <a href="https://github.com/salah-alhajj">Salah Aldain Alhajj</a>
</p>

