import setuptools

from endstech_shared import __version__


with open("README.md", "r", encoding="utf-8") as file_handle:
    long_description = file_handle.read()

setuptools.setup(
    name="endstech_shared",
    version=__version__,
    author="Joseph Waggy",
    author_email="jwaggy@gmail.com",
    description="Shared code used by endstech",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jwaggy/endstech_shared",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development"
    ],
    install_requires=[
        "pyside6>=6.7.2",
        "SQLAlchemy>=2.0.31",
        "alembic>=1.13.2",
        "python-dateutil>=2.9.0",
        "pytz>=2024.1"
    ]
)



