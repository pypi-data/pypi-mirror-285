from setuptools import setup, find_packages


setup(
    name="ctuFaultDetector",
    version="1.1.1",
    author="Ales Trna",
    author_email="altrna@fel.cvut.cz",
    description="Anomaly detection in time series model",
    long_description="Long Description",
    packages=find_packages(),
    url="https://github.com/altrna/Anomaly-detection-in-timeseries",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=[
        'matplotlib',
        'numpy',
        'pandas',
        'tslearn',
        'scipy',
        'scikit-learn',
        'h5py',
        'pandas',
        'torch',
        'pytorch-lightning',
        'scikit-learn',
        'tslearn',
        'matplotlib',
        'requests',
        'lightning_fabric'
    ],
)