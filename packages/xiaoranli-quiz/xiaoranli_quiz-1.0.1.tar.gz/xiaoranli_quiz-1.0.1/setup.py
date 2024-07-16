from setuptools import setup, find_packages

setup(
    name="xiaoranli_quiz",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        "torch",
        "prompt_toolkit",
        "colorama",
        "rich",
        "RestrictedPython",
    ],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.txt", "*.rst"],
        # And include any files found in the 'data' folder within the 'xiaoranli_quiz' package, also:
        "xiaoranli_quiz": ["data/*", "*.py"],
    },
    entry_points={
        "console_scripts": [
            "quizz=xiaoranli_quiz.main:main",
        ],
    },
    author="xiaoranli",
    author_email="1240897116@qq.com",
    description="A quiz application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/graceleeis/xiaoran-quiz",  # Replace with your GitHub repository URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
