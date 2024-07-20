from setuptools import setup, find_packages

setup(
    name='yfunc',
    version='1.0.2',
    description='a collection of some productive functions # b68be4fb5d6c08f5c2a34384481318996d8c76b5',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='yzjsswk',
    author_email='yzjsswk@gmail.com',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    install_requires=[
        'clipboard',
        'pillow',
        'loguru',
    ],
)
