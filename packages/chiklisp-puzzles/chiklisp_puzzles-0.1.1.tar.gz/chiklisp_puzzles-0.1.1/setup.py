from setuptools import setup, find_packages
from runtime_builder import build_runtime_setuptools


setup(
    packages=["chiklisp_puzzles", "chiklisp_puzzles.puzzles"],
    package_data={"chiklisp_puzzles.puzzles": ["*.hex", "*.clsp", "runtime_build"]},
    cmdclass={
        "build_runtime_builder_artifacts": build_runtime_setuptools("chiklisp_puzzles.puzzles"),
    },
)
