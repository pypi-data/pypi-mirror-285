from setuptools import setup, find_packages

setup(
    name='nonpseudorandom',
    version='0.1.1',
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
    url='https://github.com/Sven-J-Steinert/truerandom',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
