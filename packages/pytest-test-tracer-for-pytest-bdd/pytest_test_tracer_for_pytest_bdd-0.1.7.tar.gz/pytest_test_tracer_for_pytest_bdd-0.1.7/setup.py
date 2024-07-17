from setuptools import setup

setup(
    name="pytest_test_tracer_for_pytest_bdd",
    packages=["pytest_test_tracer_for_pytest_bdd"],
    install_requires=["pytest>=7.4.2"],
    # the following makes a plugin available to pytest
    entry_points={
        "pytest11": ["name_of_plugin = pytest_test_tracer_for_pytest_bdd.plugin"]
    },
    # custom PyPI classifier for pytest plugins
    classifiers=["Framework :: Pytest"],
)
