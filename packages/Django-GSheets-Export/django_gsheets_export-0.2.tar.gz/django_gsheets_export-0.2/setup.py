from setuptools import setup, find_packages

setup(
    name='Django-GSheets-Export',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Export data from Django tp Google Sheets',
    long_description=open('README.md').read(),
    url='http://your-package-url.com/',
    author='Nicolas Candela',
    author_email='nico.candela@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
    install_requires=[
        'Django>=4.1',
        'django-environ==0.11.2',
        'google-api-python-client',
        'google-auth'
    ],
)