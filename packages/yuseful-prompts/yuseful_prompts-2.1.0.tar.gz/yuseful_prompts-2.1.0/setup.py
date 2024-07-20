from setuptools import setup, find_packages

setup(
    name='yuseful_prompts',
    version='2.1.0',
    packages=find_packages(),
    install_requires=[
        'langchain-core',
        'langchain-community'
    ],
    author='yactouat',
    author_email='yacine.touati.pro@gmail.com',
    description='tested prompts for common use-cases using open LLMs with ollama and Langchain',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yactouat/yuseful_prompts',
    license='MIT',
)
