from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crewai-tools-cn",
    version="0.4.9",
    author="aithoughts",
    author_email="ai.flyingwheel@gmail.com",
    description="Set of tools for the crewAI framework (Chinese Version)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aithoughts/aipmAI-tools",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10,<3.14",
    install_requires=[
        "pydantic>=2.6.1",
        "langchain>0.2,<0.4",
        "pytest>=8.0.0",
        "lancedb>=0.5.4",
        "openai>=1.12.0",
        "chromadb>=0.4.22",
        "pyright>=1.1.350",
        "pytube>=15.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.3",
        "selenium>=4.18.1",
        "docx2txt>=0.8",
        "docker>=7.1.0",
        "embedchain>=0.1.114"
    ],
)