from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-cythonizer',
    version='0.0.10',  # Updated to match the version in settings.yaml
    author='Salah Aldain Alhajj',
    author_email='contact@salahaldain.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
        'djangorestframework>=3.15.2',
        'Cython>=3.0.10',
        'PyYAML>=6.0.1',
    ],
    python_requires='>=3.6',
    description='Supercharge your Django project with the power of Cython',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/salah-alhajj/django-cythonizer',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
    ],
    keywords='django, cython, optimization, performance, compilation',
    project_urls={
        'Bug Reports': 'https://github.com/salah-alhajj/django-cythonizer/issues',
        'Source': 'https://github.com/salah-alhajj/django-cythonizer',
    },
)