from setuptools import setup, find_packages

setup(
    name="srtseg",
    version="0.4.0",
    author="Jianshuo Wang",
    author_email="jianshuo@hotmail.com",
    description="""The simplest file format is .srt, and it can be handled pretty well with srt lib.
srtseg provides the additional feature on top of srt:
* Get duration of each video (cut in the middle of the space between two subtitle)
* Segment selection
* M3U8 export
* WebVTT export""",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jianshuo/srtseg",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
