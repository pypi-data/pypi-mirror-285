from setuptools import setup, find_packages

setup(
    name='ajax_requester',
    version='0.5',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='Fyah',
    author_email='727475183@qq.com',
    description='A simple library to handle AJAX requests with cookies',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/ajax_requester',  # 将此URL替换为你的库的实际URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
