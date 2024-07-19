from setuptools import setup, find_packages

setup(
    name='docusearch',
    version='0.3.7',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4==4.12.3',
        'EbookLib==0.18',
        'faiss-cpu==1.8.0',
        'numpy==1.26.0',
        'odfpy==1.4.1',
        'openai==0.28.0',
        'pdfplumber==0.11.1',
        'python-docx==1.1.2',
        'tiktoken==0.7.0',
        'packaging==24.1',
        'diskcache==5.6.3'
    ],
    entry_points={
        'console_scripts': [
            'docusearch=docusearch.app:main',  # Assuming you have a main function in app.py
        ],
    },
    author='Arshaan Sayed',
    author_email='as1429@duke.edu',
    description='Query documents quickly and efficiently',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://arc30.com/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
