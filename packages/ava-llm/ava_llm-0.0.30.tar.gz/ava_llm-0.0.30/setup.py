from setuptools import setup, find_packages

VERSION = "0.0.30"
DESCRIPTION = "A simple llm package."

# Setting up
setup(
    name="ava_llm",
    version=VERSION,
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=["openai", "groq", "python-dotenv"],
    keywords=["python"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
