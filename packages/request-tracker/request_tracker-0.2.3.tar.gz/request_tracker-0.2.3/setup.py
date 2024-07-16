from setuptools import setup, find_packages

setup(
    name='request_tracker',
    version='0.2.3',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'SQLAlchemy',
        'psycopg2-binary'
    ],
    entry_points={
        'console_scripts': [
            'request_tracker=request_tracker.tracker:main',
        ],
    },
    author='vishal kumar',
    author_email='vishal.k@simplify3x.com',
    description='A package for tracking requests, code coverage, and data changes.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vishalksimplify/request_tracker',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
