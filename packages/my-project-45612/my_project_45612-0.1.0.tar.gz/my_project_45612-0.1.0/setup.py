from setuptools import setup, find_packages

setup(
    name="my_project-45612",
    version="0.1.0",
    author="Your Name",
    author_email="sashaperevozniuk01@gmail.com",
    description="A brief description of the package",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/perevozniuk13/my_project-45612",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)