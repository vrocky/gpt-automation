from setuptools import setup, find_packages

setup(
    name="gpt_automation_tests",
    version="0.1.11",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "autogpt = gpt_automation_tests.main:main",
        ],
    },
)