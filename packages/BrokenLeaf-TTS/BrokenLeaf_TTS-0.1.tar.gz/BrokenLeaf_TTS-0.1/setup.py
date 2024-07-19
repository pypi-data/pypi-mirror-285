from setuptools import setup, find_packages

setup(
    name="BrokenLeaf_TTS",
    version='0.1',
    author='Broken Leaf',
    author_email='brokenleaf2010@gmail.com',
    description='This is a very well developed Text-To-Speech program created by me, Broken Leaf....',
)
packages = find_packages(),
install_requirement = ['requests', 'playsound', 'os', 'typing']

