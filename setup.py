from setuptools import setup

setup(
    name="github-label-sync",
    version="0.0.1",
    packages=['cli'],
    description='Github label sync from config file.',
    url='https://github.com/vivitInc/github-label-sync',
    author='vivit,inc.',
    author_email='dev@vivit.co.jp',
    license='MIT',
    scripts=['bin/github-label-sync'],
    install_requires=['fire', 'pygithub', 'pyyaml'],
)
