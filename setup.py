from distutils.core import setup

setup(
    name='Korail',
    packages=['korail'],
    version='0.0.3',
    description='An unoffical API for Korail.',
    long_description=open('README.rst').read(),
    license='BSD License',
    author='Su Yeol Jeon',
    author_email='devxoul@gmail.com',
    url='https://github.com/devxoul/korail',
    keywords=['Korail'],
    classifiers=[],
    install_requires=[
        'requests',
        'BeautifulSoup4'
    ]
)
