from setuptools import setup, find_packages

setup(
    name="indian-repair",
    version="1.1",
    packages=find_packages(),
    install_requires=[
        'click',  
    ],
    entry_points={
        'console_scripts': [
            'indian-repair=indian_repair.cli:cli',
        ],
    },
    author="Pradeep Kumar N",
    author_email="prajeet67@gmail.com",
    description="Crazy Tool that can fix your network, storage, lag or any effin issue that you have no idea about. Just run indian-repair and see the magic.",
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
