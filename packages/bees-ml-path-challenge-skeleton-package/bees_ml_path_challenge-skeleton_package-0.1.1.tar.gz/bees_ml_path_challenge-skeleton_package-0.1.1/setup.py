from setuptools import setup, find_packages

setup(
    name='bees_ml_path_challenge-skeleton_package',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'pytest',
        'pytest-cov'
    ],
    author='Yuri Crotti',
    author_email='yuricrotti@gmail.com',
    description='bees_ml_path_challenge-skeleton test package',
    url='https://github.com/yuricrotti/bees_ml_path_challenge-skeleton/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10.4',
)
