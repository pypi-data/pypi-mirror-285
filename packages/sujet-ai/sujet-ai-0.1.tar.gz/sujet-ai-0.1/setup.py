from setuptools import setup, find_packages

setup(
    name='sujet-ai',
    version='0.1',
    author='Sujet AI',
    author_email='<hamed@sujet.ai',
    description='AI tools for ALL',
    url='https://github.com/sujet-ai/E2D-Privacy-Enhanced-RAG',
    packages=find_packages(),
    install_requires=["spacy"],
    
    project_urls={
        'Bug Tracker': 'https://github.com/sujet-ai/E2D-Privacy-Enhanced-RAG/issues'
    },
    readme = "README.md",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X ",
        "Operating System :: Unix ",
        "Operating System :: Microsoft :: Windows ",
    ],

)


