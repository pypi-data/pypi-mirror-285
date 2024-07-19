"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="asyncs",
    version="1.0.0",
    description="A simple asynchronous web library based on aiohttp.",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/sscefalix/asyncs",  # Optional
    author="sscefalix",  # Optional
    author_email="sscefalix@gmail.com",  # Optional
    # classifiers=[  # Optional
    #     # How mature is this project? Common values are
    #     #   3 - Alpha
    #     #   4 - Beta
    #     #   5 - Production/Stable
    #     "Development Status :: 3 - Alpha",
    #     # Indicate who your project is intended for
    #     "Intended Audience :: Developers",
    #     "Topic :: Software Development :: Build Tools",
    #     # Pick your license as you wish
    #     "License :: OSI Approved :: MIT License",
    #     # Specify the Python versions you support here. In particular, ensure
    #     # that you indicate you support Python 3. These classifiers are *not*
    #     # checked by 'pip install'. See instead 'python_requires' below.
    #     "Programming Language :: Python :: 3",
    #     "Programming Language :: Python :: 3.7",
    #     "Programming Language :: Python :: 3.8",
    #     "Programming Language :: Python :: 3.9",
    #     "Programming Language :: Python :: 3.10",
    #     "Programming Language :: Python :: 3 :: Only",
    # ],
    keywords="web, aiohttp, asyncs, fastapi, web server",  # Optional
    packages=["asyncs", "asyncs.response"],  # Required
    # Specify which Python versions you support. In contrast to the
    # 'Programming Language' classifiers above, 'pip install' will check this
    # and refuse to install the project if the version does not match. See
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires=">=3.10, <4",
    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/discussions/install-requires-vs-requirements/
    install_requires=["jinja2", "aiohttp"],  # Optional
    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    # extras_require={  # Optional
    #     "dev": ["check-manifest"],
    #     "test": ["coverage"],
    # },
    # If there are data files included in your packages that need to be
    # installed, specify them here.
    # package_data={  # Optional
    #     "sample": ["package_data.dat"],
    # },
    # Entry points. The following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    # entry_points={  # Optional
    #     "console_scripts": [
    #         "sample=sample:main",
    #     ],
    # },
    project_urls={  # Optional
        "Bug Reports": "https://github.com/sscefalix/asyncs/issues",
        # "Funding": "https://donate.pypi.org",
        # "Say Thanks!": "http://saythanks.io/to/example",
        "Source": "https://github.com/sscefalix/asyncs/",
    },
)
