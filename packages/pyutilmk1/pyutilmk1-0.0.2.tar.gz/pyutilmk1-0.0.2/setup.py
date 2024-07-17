from setuptools import setup

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

exec(open("pyutilmk1/__init__.py").read())

setup(
    name='pyutilmk1',
    version=__version__,
    include_package_data=True,
    python_requires='>=3',
    description='Small utilities for path, strings, fs, dict, .etc manipulation. mark1',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Markus Peitl",
    author_email='office@markuspeitl.com',
    url="https://github.com/markuspeitl/pyutilmk1",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries"

    ],
    install_requires=[
        'tldextract',
        'pyperclip',
        'zstd'
        # 'zlib'
    ],
    entry_points={},
    packages=['pyutilmk1']
)
