import setuptools

setuptools.setup(
    author='Errucha',
    author_email='masserucha@kontolodon.com',
    description='Tools for facebook.',
    entry_points={"console_scripts": ["scraping=facebook:Facebook"]},
    install_requires=["requests", "bs4"],
    name='fb-errucha',
    packages=setuptools.find_packages(),
    version='1.0.0'
)
