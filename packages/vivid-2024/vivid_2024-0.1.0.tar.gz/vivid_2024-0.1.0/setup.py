from setuptools import setup, find_packages

setup(
    name='vivid-2024',  # Updated to the new unique name
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A comprehensive platform for HR professionals.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/vivid',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
