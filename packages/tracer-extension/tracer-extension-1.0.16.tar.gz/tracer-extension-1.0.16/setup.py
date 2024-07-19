from setuptools import find_packages, setup
setup(
    name='tracer-extension',
    version='1.0.16',
    author='Gordon',
    author_email='gordon.hamilton@datadoghq.com',
    description='Python Worker Extension for starting Datadog Tracer and a top level span to enable auto-instrumenting of Azure Function Apps',
    include_package_data=True,
    long_description=open('readme.md').read(),
    install_requires=[
        'azure-functions >= 1.7.0, < 2.0.0',
        'ddtrace==2.9.1',
    ],
    license='',
    packages=find_packages(where='.'),
    zip_safe=False,
)