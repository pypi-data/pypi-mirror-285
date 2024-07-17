from setuptools import setup, find_packages

setup(
    name='tse_motion',  
    version='0.2.8.2',
    packages=find_packages(), 
    install_requires=[
        'torch',
        'monai',
        'nibabel',
        'torchvision'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'rate-motion=tse_motion.rate:main',  # Ensure the main function exists in rate.py
            'gen-motion=tse_motion.motion2d:main',  # Ensure the main function exists in motion2d.py
        ],
    },
    author='Jinghang Li',
    author_email='jinghang.li@pitt.edu',
    description='A package to rate motion artifacts in medical images.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jinghangli98/tse-rating',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
