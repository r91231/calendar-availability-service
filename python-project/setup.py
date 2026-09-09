from setuptools import setup, find_packages

setup(
    name="comp-takehome-exercise",
    version="1.0.0",
    description="Comp In-Office Coding Evaluation - Python Implementation",
    url="https://comp.io",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "comp-calendar=io_comp.app:main",
        ],
    },
)