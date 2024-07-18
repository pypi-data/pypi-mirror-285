from setuptools import setup

setup(
    name="dotsinspace_debugger",
    version="1.0.6",
    description="Debugger for colorful logging.",
    long_description="README.md",
    author="dotsinspace",
    author_email="dotsinspace@gmail.com",
    maintainer="dotsinspace",
    maintainer_email="dotsinspace@gmail.com",
    license="MIT License",
    classifiers=[
        "Development Status :: 5 - Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
    ],
    python_requires=">=3.8",
    keywords=["utility", "debugger"],
    install_requires=["ujson", "aiofiles", "sentry_sdk", "colorama"],
    extras_require={},
    url="https://github.com/dotsinspace/Debugger",
    project_urls={
        "Homepage": "https://github.com/dotsinspace/Debugger",
        "Bug Reports": "https://github.com/dotsinspace/Debugger/issues",
        "Funding": "https://donate.pypi.org",
        "Say Thanks!": "http://saythanks.io/dotsinspace",
        "Source": "https://github.com/dotsinspace/Debugger",
    }
)
