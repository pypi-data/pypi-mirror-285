from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="rocket-welder-sdk",
    version="0.0.1",
    author="Rafal Maciag",
    author_email="rafal.maciag@modelingevolution.com",
    description="Supporting sdk for RocketWelder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rocket-welder-sdk/rocket-welder-sdk",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'opencv-python',
        'requests',  # Add any other dependencies here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    package_data={
        'rocket_welder_camera': ['*.py'],  # Include only Python files
    },
    exclude_package_data={
        '': ['tests/*'],  # Exclude test files
    },
)