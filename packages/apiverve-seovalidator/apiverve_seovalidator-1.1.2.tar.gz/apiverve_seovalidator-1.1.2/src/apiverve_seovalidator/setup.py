from setuptools import setup, find_packages

setup(
    name='apiverve_seovalidator',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools'
    ],
    description='SEO Validator is a simple tool for validating SEO metrics. It returns a list of issues that need to be fixed to improve the SEO metrics of a web page.',
    author='APIVerve',
    author_email='hello@apiverve.com',
    url='https://apiverve.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
