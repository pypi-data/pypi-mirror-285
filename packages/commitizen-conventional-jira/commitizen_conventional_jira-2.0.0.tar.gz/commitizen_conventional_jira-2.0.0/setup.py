import setuptools
from setuptools import setup

setup(
    name='commitizen_conventional_jira',
    version='2.0.0',
    py_modules=['cz_conventional_jira'],
    url='https://gitlab.com/kentharold/commitizen-conventional-jira',
    license='MIT',
    author='Kent Harold Mbatchakwe',
    author_email='mbatchakwe.kentharold@gmail.com',
    description='An extension of the conventional commits to include JIRA issues.',
    install_requires=['commitizen'],
    packages=setuptools.find_packages(),
    entry_points={"commitizen.plugin": ["cz_conventional_jira = cz_conventional_jira:ConventionalJiraCz"]}
)
