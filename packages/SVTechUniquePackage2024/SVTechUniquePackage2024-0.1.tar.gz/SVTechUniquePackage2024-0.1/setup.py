from setuptools import setup, find_packages

setup(
    name='SVTechUniquePackage2024',
    version='0.1',
    author='Sairaj Vichare',
    author_email='sairajvichare876@gmail.com',
    description='This is a speech to text package created by Sairaj Vichare',
    packages=find_packages(),
    install_requires=[
        'selenium',
        'webdriver_manager'
    ]
)
