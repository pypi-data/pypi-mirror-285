from setuptools import setup, find_packages

setup(
    name='first-project-ivaaaandmitriev',
    version='0.2.0',
    packages=find_packages(include=['brain_games', 'brain_games.*']),
    entry_points={
        'console_scripts': [
                       
        ],
    },
    install_requires=[
        
    ],
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
