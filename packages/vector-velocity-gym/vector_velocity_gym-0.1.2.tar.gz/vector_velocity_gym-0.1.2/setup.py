from setuptools import setup, find_packages
import os

CI_VERSION = os.getenv('CI_VERSION')
CI_LICENSE = os.getenv('CI_LICENSE')

if not CI_VERSION:
    raise ValueError("CI_VERSION environment variable is not set")
if not CI_LICENSE:
    raise ValueError("CI_LICENSE environment variable is not set")

long_description = ''
if os.path.exists('README.md'):
    with open('README.md', 'r', encoding='utf-8') as fh:
        long_description = fh.read()

setup(
    name='vector-velocity-gym',
    version=CI_VERSION,
    description="A space-themed OpenAI Gym environment for reinforcement learning",
    maintainer="MrChriwo",
    url="https://github.com/MrChriwo/VectorVelocity",
    author='MrChriwo & Stevenschneider',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=('tests', 'tests.*')),
    license=CI_LICENSE,
    install_requires=[
        'gymnasium',
        'pygame',
        'numpy',
    ],
    include_package_data=True
)
