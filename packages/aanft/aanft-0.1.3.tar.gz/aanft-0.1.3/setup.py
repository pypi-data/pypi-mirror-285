from setuptools import setup, find_packages

setup(
    name='aanft',
    version='0.1.3',
    description='Fetching WAX AtomicAssets made easier',
    url='https://github.com/funkaclau',
    author='funkaclau',
    packages=find_packages(),
    install_requires=[
        "aiohttp",
        "asyncio",
        "loguru",
        "typing_extensions",
        "typing"
    ],
    include_package_data=True
)
