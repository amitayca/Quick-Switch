from setuptools import setup, find_packages

setup(
    name="quick_translate",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'PyQt6',
        'keyboard',
        'googletrans==3.1.0a0',
        'pywin32',
    ],
    entry_points={
        'console_scripts': [
            'quick_translate=src.main:main',
        ],
    },
)