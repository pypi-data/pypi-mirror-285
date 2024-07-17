from setuptools import setup, find_packages

setup(
    name='kssm-searcher',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'textract',
        'PyPDF2'
    ],
    entry_points={
        'console_scripts': [
            'kssm-searcher = searcher.searcher:main',
        ],
    },
    author='Kssm',
    author_email='your.email@example.com',
    description='Herramienta para extraer informacion de documentos localizados en un directorio en base a keywords.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitlab.com/Karlossam/searcher',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
    ],
    python_requires='>=3.6',
)
