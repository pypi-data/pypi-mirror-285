from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="cda.ai-modular-framework",
    version="0.1.0",
    author="Cdaprod",
    author_email="Cdaprod@Cdaprod.dev",
    description="A modular AI framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Cdaprod/cda.ai-modular-framework",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-dotenv", 
        "openai",
        "kubernetes",
        "pytest",
        "flake8"
    ],
    entry_points={
        'console_scripts': [
            'cda-ai-modular-framework=cda_ai_modular_framework.main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)