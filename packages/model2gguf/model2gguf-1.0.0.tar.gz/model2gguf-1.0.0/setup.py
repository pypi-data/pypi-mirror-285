from setuptools import setup, find_packages

setup(
    name='model2gguf',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'huggingface_hub',
    ],
    entry_points={
        'console_scripts': [
            'model2gguf=model2gguf.converter:main',
        ],
    },
    author='Rahul Patnaik, Krishna Dvaipayan',
    author_email='rpatnaik2005@gmail.com, krishnadvaipayan.ei21@rvce.edu.in',
    description='A tool to convert Hugging Face models to GGUF format and manage Ollama models.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/RahulPatnaik/model2gguf',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Specify Python version requirement
)
