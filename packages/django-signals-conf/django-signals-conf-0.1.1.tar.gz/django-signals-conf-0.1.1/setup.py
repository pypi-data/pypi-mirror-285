import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='django-signals-conf',
    version='0.1.1',
    packages=find_packages(exclude=["tests", "tests.*", "licenses", "requirements"]),
    description='The library helps configure signals for django projects faster and easier',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Tinh Pham Ba',
    author_email='tinhpb9x@gmail.com',
    url='https://github.com/tinhpb9x/django-signals-conf/',
    license='MIT',
    python_requires='>3.0',
    install_requires=[
        'Django<5.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
