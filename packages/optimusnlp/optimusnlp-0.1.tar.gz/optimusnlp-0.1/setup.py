from setuptools import setup, find_packages

setup(
    name='optimusnlp',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['data/ner.txt'],
    },
    description='A package that includes a NER dataset.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my_package',
    author='John doe',
    author_email='your.email@example.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
