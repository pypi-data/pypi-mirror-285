from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as readme_file:
    long_description = readme_file.read()


setup(
    name="murnitur",
    version="1.1.1",
    description="Murnitur empowers AI teams to seamlessly test, evaluate, deploy, monitor, and safeguard GenAI applications continuously.",
    url="https://murnitur.ai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Caleb Okpara",
    author_email="support@murnitur.com",
    packages=find_packages(),
    install_requires=[
        "requests",
        "openlit==1.16.0",
        "transformers>=4.39.3",
        "pandas",
        "vaderSentiment",
        "openai",
        "groq",
        "anthropic",
        "tqdm",
        "pytest",
        "tabulate",
        "typer",
        "rich",
        "protobuf==4.25.1",
        "pydantic",
        "portalocker",
        "langchain",
        "langchain-core",
        "langchain_openai",
        "ragas",
        "docx2txt~=0.8",
        "importlib-metadata>=6.0.2",
        "tenacity~=8.2.3",
    ],
    python_requires=">=3.7.1",
)
