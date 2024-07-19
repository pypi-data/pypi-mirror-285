from setuptools import setup, find_packages

setup(
    name='heytextual',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'heytextual=heytextual:main',
        ],
    },
    author="Daniel Fernandez Gutierrez",
    author_email="dfernandez@heytextual.com",
    description="A Python SDK for the HeyTextual API",
    license="MIT",
    keywords="API SDK HEYTEXTUAL",
    url="https://github.com/danielfergu/heytextual-python",
)
