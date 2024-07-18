from setuptools import setup, find_packages
setup(
    name='upstream_code',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        #Add dependencies here.
        #e.g 'numpy>=1.11.1'
    ],
    entry_points={
        "console_script": [
            "upstream_code = upstream_code:hello",
        ],
    },
)