from setuptools import setup, find_packages
from spacedork import VERSION

setup(
    name='spacedork',
    version=VERSION,
    url='',
    description='',
    long_description='',
    keywords='dork search',
    author='',
    author_email='tongchengbin@outlook.com',
    maintainer='',
    platforms=['any'],
    license='',
    zip_safe=False,
    include_package_data=True,
    python_requires='>=3.6',
    packages=find_packages(exclude=['spacedork.tests'], ),
    entry_points={
        "console_scripts": [
            "dork = spacedork.cli:main"
        ]
    },
    install_requires=[
        "PyYAML",
    ],
)
