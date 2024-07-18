from setuptools import setup, find_packages

setup(
    name='prueba-100-django',
    version='0.0.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.0',
    ],
    entry_points={
        'console_scripts': [
            'createcomponente = DjangoComponents.management.commands.createcomponent:Command.handle',
        ],
    },
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    author='Alejandro',
    description='Este paquete se instala en Django para proporcionar componentes HTML y otras funcionalidades.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jose-CR/Django-components',
)



