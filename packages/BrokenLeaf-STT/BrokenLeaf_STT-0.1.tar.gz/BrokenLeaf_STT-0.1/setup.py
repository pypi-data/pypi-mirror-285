from setuptools import setup, find_packages

setup(
    name="BrokenLeaf_STT",
    version='0.1',
    author='Broken Leaf',
    author_email='brokenleaf2010@gmail.com',
    description='This is a very well developed Speech-to-Text program created by me, Broken Leaf....',
)
packages = find_packages(),
install_requirement = ['selenium', 'webdriver-manager', 'pyttsx3']

