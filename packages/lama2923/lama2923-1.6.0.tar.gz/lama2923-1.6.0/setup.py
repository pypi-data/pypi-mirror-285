from setuptools import setup, find_packages

# Komutlar.txt dosyasından komutlar ile terminalde setup dosyasını çalıştırım upload edebilirsin.

with open("long_description.md", "r", encoding="utf-8") as file:
    long_description = file.read()


setup(
    name='lama2923',
    version='1.6.0',
    description='Sikimsonik bir kütüphane',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='lama2923',
    author_email='lama2923.v2@gmail.com',
    project_urls={
        'Author GitHub': 'https://github.com/lama2923'
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    keywords='example project evelopment discord lama2923 api design custom custominput customprint',
    packages=find_packages(),
    install_requires=[
        'colorama',
        'requests'
    ],
    python_requires='>=3.7',
)

