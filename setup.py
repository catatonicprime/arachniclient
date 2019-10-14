import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name='arachniclient',
        version='0.3',
        scripts=['arachni-client'],
        install_requires=[
            'requests'
        ],
        author='catatonicprime',
        author_email='catatonicprime@gmail.com',
        description='REST API client for arachni.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/catatonicprime/arachniclient',
        packages=setuptools.find_packages(),
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            ],
        )
