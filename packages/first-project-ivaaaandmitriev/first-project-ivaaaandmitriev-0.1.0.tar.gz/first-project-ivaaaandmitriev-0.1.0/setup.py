from setuptools import setup, find_packages

setup(
    name='first-project-ivaaaandmitriev',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'brain_games=brain_games.scripts.brain_games:main',
            'brain_even=brain_games.scripts.brain_even:main',
            'brain_calc=brain_games.scripts.brain_calc:main',
            'brain_gcd=brain_games.scripts.brain_gcd:main',
            'brain_prime=brain_games.scripts.brain_prime:main',
            'brain_progression=brain_games.scripts.brain_progression:main'
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
