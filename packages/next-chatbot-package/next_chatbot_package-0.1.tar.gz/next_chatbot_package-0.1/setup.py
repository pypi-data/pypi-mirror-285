from setuptools import setup, find_packages

setup(
    name='next_chatbot_package',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here, e.g., 'requests', 'numpy'
    ],
    entry_points={
        'console_scripts': [
            # Define command-line scripts here if any
        ],
    },
    author='Omkar Singh',
    author_email='singhomkar20.1995@gmail.com',
    description='In one command we are ready with chatbot',
    keywords='example package',
    url='http://example.com/YourPackage',  # Placeholder for project home page
    project_urls={
        'Bug Tracker': 'http://example.com/YourPackage/issues',  # Placeholder for bug tracker
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)

