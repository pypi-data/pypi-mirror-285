from setuptools import setup, find_packages

VERSION = '0.0.7'
DESCRIPTION = 'Props AI Python API Library'

setup(
    name='props-ai',
    version=VERSION,
    author='Props AI',
    author_email='contact@getprops.ai',
    description=DESCRIPTION,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/PropsAI/propsai-python',
    packages=find_packages(),
    install_requires=[
        'requests>=2.0.0',
    ],
    keywords=["openai",
    "open",
    "ai",
    "gpt-3",
    "gpt3",
    "gpt4",
    "propsai",
    "observability",
    "evaluation",
    "analytics",
    "experimentation"],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
