from setuptools import setup, find_packages

setup(
    name='DecimalCalcul',
    version='2.3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Liste des dépendances
    ],
    tests_require=['pytest'],
    author='Bouquet Cédric',
    author_email='cedric-bouquet-7@outlook.fr',
    description='Fournit une classe dédiée aux calculs sur des nombres décimaux',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/votre_utilisateur/mon_projet',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.0',
)
