from setuptools import setup, find_packages

setup(
    name="aily-cli",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click"
    ],
    entry_points={
        'console_scripts': [
            'aily-cli = aily_cli.cli:cli'
        ]
    },
    author="stao",
    author_email="werewolf_st@hotmail.com",
    description="Aily CLI",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://aily.pro",
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
