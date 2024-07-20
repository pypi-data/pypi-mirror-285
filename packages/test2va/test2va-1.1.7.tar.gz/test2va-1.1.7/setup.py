from setuptools import setup, find_packages

setup(
    name='test2va',
    version='1.1.7',
    packages=find_packages(),
    install_requires=['appium-python-client', 'pillow', 'customtkinter'],
    license='MIT',
    author='Anon',
    include_package_data=True,
    description='Test2VA',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[],
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'test2va = test2va.mod:main'
        ]
    },
)
