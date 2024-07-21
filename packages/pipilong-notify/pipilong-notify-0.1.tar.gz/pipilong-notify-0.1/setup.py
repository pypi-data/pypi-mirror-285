from setuptools import setup, find_packages

setup(
    name="pipilong-notify",
    version="0.1",
    author="PiPiLONG256",
    author_email="66461682@qq.com",
    description="一个钉钉webhook包",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)