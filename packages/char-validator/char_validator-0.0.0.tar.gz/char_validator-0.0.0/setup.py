from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='char_validator',
    version='0.0.0',
    packages=find_packages(exclude=['tests', "debug_inputs", 'debug_outputs']),
    author="Crimson Tech",
    description="Character validation using morphological operations",
    requires=['numpy', 'skimage', 'cv2'],
)