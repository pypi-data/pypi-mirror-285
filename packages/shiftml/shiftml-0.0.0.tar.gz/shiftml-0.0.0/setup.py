import sys

from setuptools import setup
from wheel.bdist_wheel import bdist_wheel


class no_wheel(bdist_wheel):
    def run(self):
        sys.exit(
            "This project is not yet fully released on PyPI, please install it from "
            "source for now: https://github.com/lab-cosmo/ShiftML"
        )


if __name__ == "__main__":
    setup(
        cmdclass={"bdist_wheel": no_wheel},
    )
