from setuptools import find_packages, setup

setup(
    name='earthos',
    packages=find_packages(),
    version='0.1.1',
    description='Ecosophy EarthOS API bindings',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='Ecosophy',
    author_email='info@ecosophy.is',
    license='Apache',
    url='https://ecosophy.is/',
    install_requires=[
        'requests',
        'Pillow',
        'numpy',
    ],
    tests_require=[
        'pytest',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: Oceanography",
    ],
)
