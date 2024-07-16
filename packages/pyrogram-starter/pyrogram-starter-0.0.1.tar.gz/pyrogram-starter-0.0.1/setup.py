from setuptools import setup, find_packages

setup(
    name="pyrogram-starter",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "gitpython",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "pyrogram-starter=pyrogram_starter.__init__:main",
        ],
    },
    author="Nuhman PK",
    author_email="nuhmanpk7@gmail.com",
    description="A package to clone a pyrogram bot boilerplate from GitHub.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nuhmanpk/pyrogram-starter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
