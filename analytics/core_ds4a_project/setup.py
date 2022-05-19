import setuptools


if __name__ == "__main__":
    setuptools.setup(
        name='core_ds4a_project',
        package_dir={'': '.'},
        packages=setuptools.find_packages(where='.'),
        install_requires=['pandas'],
    )
