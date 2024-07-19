from setuptools import setup, find_packages

#import glob

# Listando todos os arquivos .ipynb na pasta notebooks
#notebooks_files = glob.glob('notebooks/*.ipynb')

setup(
    name='socialdataanalysis',
    version='0.0.55',
    packages=find_packages(),
    #include_package_data=True,
    #package_data={
    #    'socialdataanalysis': ['notebooks/*.ipynb'],
    #},
    #data_files=[
    #    ('share/socialdataanalysis', notebooks_files),
    #],
    install_requires=[
        'pandas',
        'numpy',
        'statsmodels',
        'scipy',
        'matplotlib',
        'sympy',
        'prince',
        'altair',
        'requests',
        #'tempfile', # é um módulo da biblioteca padrão do Python e não deve ser listado como uma dependência instalável 
        #'os', # é um módulo da biblioteca padrão do Python e não deve ser listado como uma dependência instalável 
        'pyreadstat',
        'pingouin',
        'tabulate',
        'ipython',
        'warnings', 
        'itertools',
        'plotly'

    ],
    author='Ricardo Mergulhao',
    author_email='ricardomergulhao@gmail.com',
    description='Funções personalizadas para análise de dados nas ciências sociais, complementando o uso do SPSS.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/rcmergulhao/socialdataanalysis',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
