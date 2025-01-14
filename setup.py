from setuptools import setup, find_packages


install_requires = [
    "numpy",
    "scipy",
    "brian2",
    "neo==0.8.0",
    "pynn",
    "h5py",
    "matplotlib",
    "argparse",
    "elephant==0.8.0",
    "colorama",
    "pandas==1.2.2",
    "hilbertcurve"
]

setup(
    name='spinncer',
    version='1.0.0',
    packages=find_packages(),
    url='https://github.com/pabogdan/spinncer',
    license="GNU GPLv3.0",
    author='Petrut Antoniu Bogdan',
    author_email='petrut.bogdan@manchester.ac.uk',
    description='Simulating a large scale Cerebellum model on SpiNNaker',
    # Requirements
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",

        "Intended Audience :: Science/Research",

        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",

        "Programming Language :: Python :: 3"
        "Programming Language :: Python :: 3.7"
        
        "Topic :: Scientific/Engineering",
    ]
)
