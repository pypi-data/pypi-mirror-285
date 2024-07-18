from setuptools import setup, find_packages

setup(
    name='init_checks',
    version='0.1.6',
    packages=find_packages(),
    install_requires=[
        'pyyaml',
        'pre-commit',
        'tabulate'
    ],
    entry_points={
        'console_scripts': [
            'install-precommit-hook=init_checks.install_hook:install_pre_commit_hook',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
