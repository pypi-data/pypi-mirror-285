import setuptools

# PRODUCTION setup.py: name, version, install_requires, packages only
with open('requirements.txt', encoding="utf-8") as file:
    install_requires = file.read().splitlines()
setuptools.setup(
    name='django-aiohttp-rq',
    version='0.0.3',
    install_requires=install_requires,
    packages=setuptools.find_packages()
)
