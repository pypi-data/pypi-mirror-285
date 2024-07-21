from setuptools import setup, find_packages

setup(
    name='nonpseudorandom',
    version='0.3.0',
    packages=find_packages(),
    install_requires=[
        'psutil',
        'numpy',
        'sounddevice',
        'opencv-python'
    ],
    author='Sven Steinert',
    author_email='sven.julius.steinert@outlook.com',
    description='A true random number generator using system sensor noise',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Sven-J-Steinert/nonpseudorandom',
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
