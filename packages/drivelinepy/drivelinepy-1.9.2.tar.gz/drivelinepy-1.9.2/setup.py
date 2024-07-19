from setuptools import setup, find_packages
import os

# print working directory
print("Current working directory: ", os.getcwd())
print("Contents of current working directory: ", os.listdir())

# Read the contents of your README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='drivelinepy',
    version='1.9.2',
    author='Garrett York',
    author_email='garrett@drivelinebaseball.com',
    description='A Python package for Driveline Baseball API interactions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/drivelineresearch/drivelinepy',
    packages=find_packages(),
    install_requires=[
        'certifi>=2024.2.2,<2025.0.0',
        'charset-normalizer>=3.3.2,<4.0.0',
        'idna>=3.6,<4.0.0',
        'numpy>=1.24.4,<1.26.0',
        'pandas>=1.4.3,<2.0.0',
        'python-dateutil>=2.8.2,<3.0.0',
        'python-dotenv>=1.0.1,<2.0.0',
        'pytz>=2024.1,<2025.0.0',
        'requests>=2.31.0,<3.0.0',
        'six>=1.16.0,<2.0.0',
        'tzdata>=2024.1,<2025.0.0',
        'urllib3>=2.2.0,<3.0.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)