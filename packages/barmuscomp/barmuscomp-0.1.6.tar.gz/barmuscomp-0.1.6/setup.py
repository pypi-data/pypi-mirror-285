import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="barmuscomp",
    version="0.1.6",
    author="Marmoret Axel",
    author_email="axel.marmoret@imt-atlantique.fr",
    description="Package for barwise compression applied on musical segmentation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.imt-atlantique.fr/a23marmo/barmuscomp",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Programming Language :: Python :: 3.8"
    ],
    license='BSD',
    install_requires=[
        'as_seg',
        'base_audio',
        'librosa >= 0.10',
        #'madmom @ git+https://github.com/CPJKU/madmom',
        'madmom >= 0.16.1',
        'matplotlib',
        'mir_eval >= 0.6',
        'mirdata >= 0.3.3',
        'smart_open', # For mirdata, not installed by default, may be fixed in future release
        'nn-fac >= 0.3.2',
        'numpy >= 1.18.2',
        'pandas',
        'scipy >= 1.4.1',
        'scikit-learn',
        'tensorly >= 0.5.1',
        'torch >= 1.8.0'
    ],
)
