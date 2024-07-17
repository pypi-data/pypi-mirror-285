# setup.py
from setuptools import setup, find_packages

setup(
    name='draxutils',
    version='0.1.12',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'pillow',
        'datasets',
        'IPython'
    ],
    author='dddraxxx',
    author_email='dongqh078@gmail.com',
    description='Utility functions for image handling',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # url='https://github.com/dddraxxx/',  # Update with your GitHub URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
# rm -rf build/ dist/ draxutils.egg-info/
# python setup.py sdist bdist_wheel
# twine upload dist/* --verbose
# one liner: rm -rf build/ dist/ draxutils.egg-info/ && python setup.py sdist bdist_wheel && twine upload dist/* --verbose