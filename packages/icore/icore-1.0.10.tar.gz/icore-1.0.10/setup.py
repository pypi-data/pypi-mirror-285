from setuptools import setup, find_packages

setup(
    name="icore",
    version="1.0.10",
    author="Hermílio Alves",
    author_email="hermilio@illimitar.com.br",
    description="Modulo de icore.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/illimitar/icore.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "dash",
        "pandas",
        "dash-mantine-components",
        "elastic-apm",
        "dash_iconify",
        "dash_ag_grid",
        "sqlalchemy",
        "pymssql",
        "mysql-connector-python",
        "blinker",
        "gunicorn",
    ],
    python_requires=">=3.10",
)
