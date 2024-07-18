from setuptools import setup, find_packages
setup(
    name='upstream_code',
    version='0.3',
    packages=find_packages(),
    install_requires=[
        #Add dependencies here.
        #e.g 'numpy>=1.11.1'
    ],
    entry_points={
        "console_scripts": [
            "upstream_code = upstream_code:hello",
        ],
    },
)