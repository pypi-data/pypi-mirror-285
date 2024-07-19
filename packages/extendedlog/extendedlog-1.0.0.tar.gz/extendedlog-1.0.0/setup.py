from setuptools import setup, find_packages

setup(
    name='extendedlog',
    version='1.0.0',
    packages=find_packages(),
    description='A simple error and operation logger that allows also to reproduce logs in real time',
    author='Elxes',
    author_email='contact@elxes.mozmail.com',
    url='https://github.com/Elxes04/extendedlog',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
