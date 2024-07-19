from setuptools import setup

setup(
    # Needed to silence warnings
    name='pyhelpme',
    url='https://github.com/ankurk017/pyhelpme',
    author='Ankur Kumar',
    author_email='ankurk017@gmail.com',
    # Needed to actually package something
    packages=['pyhelpme'],
    # Needed for dependencies
    install_requires=["cartopy", "matplotlib", "numpy", "xarray"],
    # *strongly* suggested for sharing
    version='0.1',
    license='MIT',
    description='An example of a python package from pre-existing code',
    # We will also need a readme eventually (there will be a warning)
    long_description=open('README.rst').read(),
)
