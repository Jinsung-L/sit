from setuptools import setup

setup(
    name='sitmango',
    version='0.1.3',
    description='Simple deployment for Flask micro web service',
    url='https://github.com/Jinsung-L/sit/',
    author='Jinsung Lim',
    author_email='js99028@gmail.com',
    license='MIT',
    packages=[
        'sitmango',
        'sitmango.scripts',
    ],
    entry_points = {
        'console_scripts': ['sit=sitmango.scripts.sit:cli'],
    },
    install_requires = [
        'flask',
        'python-dotenv',
        'Click',
        'colorama',
        'paramiko',
    ],
    include_package_data=True,
    zip_safe=False
)
