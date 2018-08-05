from setuptools import setup

setup(
    name='sitmango',
    version='0.1.0',
    description='Simple deployment for Flask micro web service',
    url='https://github.com/Jinsung-L/sit/',
    author='Jinsung Lim',
    author_email='js99028@gmail.com',
    license='MIT',
    packages=[
        'sit',
        'sit.scripts',
    ],
    entry_points = {
        'console_scripts': ['sit=sit.scripts.sit:cli'],
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
