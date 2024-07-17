from setuptools import setup, find_packages

setup(
    name='locaspy',
    version='1.0.4',
    packages=find_packages(),
    author='Fidal',
    author_email='mrfidal@proton.me',
    url='https://mrfidal.in/basic-pip-package/locaspy',
    description='A tool for fetching location, weather, and map link based on IP address.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'requests',
    ],
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
