from setuptools import setup, find_packages

setup(
    name="Dsave",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'pyodbc',
        "sqlite3"
    ],
    author="Mahendra Sai Phaneeswar Yerramsetti",
    author_email="mhendrayerramsetti@gmail.com",
    description="Data Save",
    long_description="""Data Save Module is a eay to use module for saving data in database in python
    It is simpler and faster than other modules.
    its easy to learn and use because it uses simple syntax.""",
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
