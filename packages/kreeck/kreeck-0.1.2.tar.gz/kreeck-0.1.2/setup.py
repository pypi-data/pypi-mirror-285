from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("CHANGELOG.md", "r", encoding="utf-8") as fh:
    changelog = fh.read()


setup(
    name="kreeck",
    version="0.1.2",

    packages=find_packages(),

    install_requires=[
        "GitPython",
        "pandas",
        "matplotlib",
        "python-dotenv",
        "tqdm",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "kreeck=kreeck.cli:main",
        ],
    },
    author="Kreeck",
    author_email="dave@kreeck.com",
    description="A tool to track Git contributions, generate detailed reports, and motivate contributors.",
    long_description=f"{long_description}\n\n{changelog}",
    long_description_content_type="text/markdown",
    url="https://github.com/kreeckacademy/kreeeckAnalyser",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
