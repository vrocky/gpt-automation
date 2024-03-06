from setuptools import setup, find_packages

setup(
    name="gpt_automation",
    version="0.1.7",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "autogpt = gpt_automation.main:main",
        ],
    },
)