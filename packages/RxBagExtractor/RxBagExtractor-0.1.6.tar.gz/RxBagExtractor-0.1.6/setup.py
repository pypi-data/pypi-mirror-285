from setuptools import setup, find_packages

setup(
    name='RxBagExtractor',
    version='0.1.6',
    packages=find_packages(),
    description='Filter OCR text from prescriptions to extract drug-related texts',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='sanakang',
    author_email='sanakang0615@kaist.ac.kr',
    url='https://github.com/sanakang0615/RxBagExtractor',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    
    python_requires='>=3.7',
    install_requires=[
        'pandas>=1.0.0'
    ]
)
