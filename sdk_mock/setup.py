from setuptools import setup

setup(
    name="qboard",
    packages=["qboard","qboard.solvers"],
    install_requires=[
        "matplotlib",
        "numpy",
        "pandas",
        "scipy"
    ]
)
