from setuptools import find_packages, setup

readme = ""
with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="Nueue",
    version="1.0.0",
    packages=find_packages(),
    author="sus2790",
    author_email="ddoaoing@gmail.com",
    description="An easier way to create the queue.",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/sus2790/Nueue",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["queue", "discord.py", "py-cord"],
)
