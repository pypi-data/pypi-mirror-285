from setuptools import setup, find_packages

setup(
    name='cocheck',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'requests',
        'simple_colors',
    ],

    author='Oliver Sthana',
    author_email='oliver@string.sk',
    description='A simple site connectivity checker',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/onilooo/cocheck',  # Replace with your GitHub repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)