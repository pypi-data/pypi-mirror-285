from setuptools import setup, find_packages

setup(
    name='arkose',
    version='0.1',
    description='A Python package to interact with Funcaptcha (Arkose Labs)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Micxzy/arkose',
    author='Micxzy',
    author_email='no@dont.email.me',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'requests',
        'pycryptodome'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
