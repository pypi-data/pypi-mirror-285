from setuptools import setup, find_packages

setup(
    name="bus_16",
    version="0.0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # List your package dependencies here
        # "some_package>=1.0.0",
    ],
    entry_points={
        'console_scripts': [
            # Define command-line scripts here
            # 'my_command=my_package.module:function',
        ],
    },
    author="Manjunath Srinivasa",
    author_email="manjevas@outlook.com",
    description="16-bit address bus, ferrying 8-bit data per clock.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/mcsrinivasa/bus-16.git",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

