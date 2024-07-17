from setuptools import setup

PACKAGES = ["chiklisp_stdlib", "chiklisp_stdlib.nightly", "chiklisp_stdlib.stable"]

setup(
    packages=PACKAGES,
    package_data={"": ["stable/*.clib", "nightly/*.clib"]},
)
