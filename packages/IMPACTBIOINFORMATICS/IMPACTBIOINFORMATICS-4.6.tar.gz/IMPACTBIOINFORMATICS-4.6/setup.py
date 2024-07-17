from setuptools import setup, find_packages

setup(
    name='IMPACTBIOINFORMATICS',
    version='4.6',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'torch',
        'torchvision',
        'scikit-learn',
        'umap',
        'grad-cam',
        'torchcam'
    ],
    entry_points={
        'console_scripts': [],
    },
    author='USYD precision medicine center',
    author_email='wenze.ding@sydney.edu.au',
    description='IMPACT: Interpretable Microbial Phenotype Analysis via microbial Characteristic Traits',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Wenze18/IMPACT.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
