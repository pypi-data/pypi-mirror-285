from setuptools import setup, find_packages

setup(
    name='canadapostwrapper1',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='shibakek',
    author_email='wilhemnorman732@gmail.com',
    description='A wrapper for tracking packages with Canada Post',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/shibakek2/canada-post',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)