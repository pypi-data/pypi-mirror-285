from setuptools import setup, find_packages

if __name__ == '__main__':
    name = 'taichu-storage'

    with open('requirements.txt', 'r') as f:
        requirements = f.read().splitlines()

    long_description = 'storage sdks aggregation'
    # with open('README.md', 'r') as f:
    #     long_description = f.read()

    setup(
        name=name,
        version='1.0.22',
        description='storage sdks aggregation',
        long_description=long_description,
        author='taichu platform team',
        python_requires=">=3.6.0",
        url='',
        keywords='taichu',
        packages=find_packages(),
        install_requires=requirements,
        include_package_data=True,
        entry_points={
            'console_scripts': ['ts = taichu_storage.command:cli']
        },
        package_data={
            '': ['*.sh'],
        }
    )
