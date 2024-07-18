from setuptools import setup, find_packages
from readme_fetch import fetch_github_readme

setup(
    name='ts_arm',
    version='0.0.3',
    description='Guidelines for Augmentation Selection in Contrastive Learning '
                'for Time Series Classification',
    long_description=fetch_github_readme('DL4mHealth', 'TS-Contrastive-Augmentation-Recommendation', 'main'),
    long_description_content_type="text/markdown",
    url='https://github.com/DL4mHealth/TS-Contrastive-Augmentation-Recommendation',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'ts_arm': ['synthetic_F1_array.npy'],
    },
    license='MIT',
    author='Ziyu Liu',
    author_email='ziyu.liu2@student.rmit.edu.au',
    install_requires=[
        'numpy',
        'scikit_learn',
        'scipy',
        'statsmodels',
        'tqdm',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        'Intended Audience :: Science/Research'
    ],
)
