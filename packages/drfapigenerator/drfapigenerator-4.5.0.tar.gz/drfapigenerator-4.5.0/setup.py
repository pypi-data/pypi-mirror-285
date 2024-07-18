from setuptools import setup, find_packages
import os

# Read the content of your README file
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='drfapigenerator',
    version='4.5.0',
    include_package_data=True,
    
    install_requires=[
        'django',
        'djangorestframework',
        'djangorestframework-simplejwt'
    ],
    entry_points={
        'console_scripts': [
            # Define any command line scripts here
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'Framework :: Django :: 3.2',  # Specify the appropriate Django version
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',

    description="A Django app for automating RESTful API development using Django Rest Framework (DRF), simplifying CRUD operations for Django models.",
    long_description = long_description,
    long_description_content_type='text/markdown',
    author='Manoj Kumar Das',
    author_email='manojdas.py@gmail.com',
    url='https://github.com/mddas2/drfapigenerator',
    # packages=['drfapigenerator'],

    package_data={
        'drfapigenerator.management.commands.data.routers': ['*.txt'],
        'drfapigenerator.management.commands.data.serializers': ['*.txt'],
        'drfapigenerator.management.commands.data.utilities': ['*.txt'],
        'drfapigenerator.management.commands.data.viewsets': ['*.txt'],
    },
    
)


