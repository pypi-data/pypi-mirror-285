from setuptools import find_packages, setup
setup(
    name='tracer-extension',
    version='1.0.15',
    author='Gordon',
    author_email='gordon.hamilton@datadoghq.com',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description='Python Worker Extension for starting Datadog Tracer in order to trace Azure functions',
    include_package_data=True,
    long_description=open('readme.md').read(),
    install_requires=[
        'azure-functions >= 1.7.0, < 2.0.0',
        # Any additional packages that will be used in your extension
        'ddtrace',
        'datadog-sma~=0.5.0',
    ],
    extras_require={},
    license='MIT',
    packages=find_packages(where='.'),
    zip_safe=False,
)