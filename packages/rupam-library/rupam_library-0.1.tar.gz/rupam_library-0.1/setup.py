from setuptools import setup, find_packages

setup(
    name='rupam-library',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Description of your Django app',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your@email.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'Django>=3.0',  # adjust the version as needed
        # add any other dependencies here
    ],
)
