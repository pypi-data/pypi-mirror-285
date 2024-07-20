from setuptools import setup, find_packages

setup(
    name='simple_ai_manager',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'openai',
        'google-generativeai',
        'anthropic',
        'setuptools',
        'wheel',    
    ],
    author='555happy',
    author_email='555happy.jp@gmail.com',
    description='A common management module for AI generation services',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/555happy/AI_Manager',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
