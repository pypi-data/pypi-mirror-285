from setuptools import setup, find_packages

setup(
    name='fshredder',
    version='0.1.0',
    description='Advanced file shredding tool that deletes files with no data left using encryption techniques',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Babar Ali Jamali',
    author_email='babar995@gmail.com',
    url='https://github.com/babaralijamali/fshredder',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'fshredder=fshredder.fshredder:main',
        ],
    },
)
