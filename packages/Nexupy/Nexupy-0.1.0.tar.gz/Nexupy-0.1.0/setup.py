from setuptools import setup, find_packages

setup(
    name='Nexupy',
    version='0.1.0',
    description='An interface to work with sonatype Nexus RestApi',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Shayan Ghani',
    author_email='shayanghani1384@gmail.com',
    url='https://github.com/Shayan-Ghani/nexupy',
    packages=find_packages(),
    install_requires=[
        "certifi==2024.7.4",
        "charset-normalizer==3.3.2",
        "idna==3.7",
        "requests==2.32.3",
        "urllib3==2.2.2"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
