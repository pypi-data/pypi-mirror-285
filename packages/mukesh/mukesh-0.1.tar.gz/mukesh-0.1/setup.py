from setuptools import setup, find_packages

setup(
    name='mukesh',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pyodm',
    ],
    entry_points={
        'console_scripts': [
            'process-images=mukesh.main:process_images',
        ],
    },
    author='Mukesh Anand G',
    author_email='ai.mukeshanandg@gmail.com',
    description='A simple package to process aerial images and generate orthophotos.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
