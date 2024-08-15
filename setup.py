from setuptools import setup, find_packages

setup(
    packages=find_packages(),
    package_data={
        'gpt_automation': [
            '**/*.json',  # Include all JSON files in gpt_automation and its subdirectories
            'resources/*',  # Include all files in the resources directory
        ]
    }
)
