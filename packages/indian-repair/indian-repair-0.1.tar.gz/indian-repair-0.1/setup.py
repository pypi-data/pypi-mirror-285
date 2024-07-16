from setuptools import setup, find_packages

setup(
    name="indian-repair",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'click',  # Add click as a dependency
    ],
    entry_points={
        'console_scripts': [
            'indian-repair=indian_repair.cli:cli',
        ],
    },
    author="Pradeep Kumar N",
    author_email="prajeet67@gmail.com",
    description="A simple package to restart the computer based on the operating system.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/sickuritywizard/indian-repair",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
