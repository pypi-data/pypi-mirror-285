from setuptools import setup, find_packages

setup(
    name='Easebuzz',  
    version='1.0.4',
    packages=find_packages(),
    author='Easebuzz Payments',
    author_email='root@easebuzz.in',
    description='Wrapper to integrate functionalities of Easebuzz Payment Gateway',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',
    license='MIT',  
    
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=['requests'],
    extras_require={
        "dev": ["twine>=4.0.2"],
    },
    python_requires=">=3.10",
)
