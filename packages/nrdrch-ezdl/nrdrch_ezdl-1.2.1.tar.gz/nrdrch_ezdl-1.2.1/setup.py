from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nrdrch-ezdl",
    version="1.2.1",
    author="Lukas H",
    author_email="nrdrch@proton.com",
    description="yt-dlp wrapper for ultimate simplicity",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nrdrch/nrdrch-ezdl",
    project_urls={
        "Bug Tracker": "https://github.com/nrdrch/nrdrch-ezdl/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11"
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "rich>=13.7.1",
        "toml>=0.10.2",
        "yt-dlp>=2024.5.27",
        "spotipy>=2.24.0"
    ],
    entry_points={
        "console_scripts": [
            "ezdl=nrdrch_ezdl.__main__:main",
        ],
    },
)
