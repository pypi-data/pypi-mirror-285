from setuptools import setup, find_packages

setup(
    name='rmrag',
    version='0.3.0',
    packages=find_packages(exclude=["tests*"]),
    install_requires=[],
    author='Lasse Tranekjær Leed',
    author_email='lasseleed@gmail.com',
    description='RAG functions',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha', 
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.9']
)

#0.2 = added tests for all function + get_response into class 
#0.3 = Fixed tests and added Chatbot_OpenSource