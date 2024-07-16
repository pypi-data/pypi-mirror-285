from setuptools import setup, find_packages

setup(
    name="nanosense",
    version="0.5.17",  # Make sure this matches the version in pyproject.toml
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'nanosense=nanosense.nanosense:main',
        ],
    },
)