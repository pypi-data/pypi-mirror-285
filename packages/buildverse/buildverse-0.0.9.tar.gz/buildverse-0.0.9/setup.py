import setuptools

setuptools.setup(
    packages=["buildverse"],
    package_dir={
        "buildverse": ".",
    },
    include_package_data=True,
    package_data={"buildverse": ["./ci/**", "./cmake/**", "./templates/**", "./include/**"]},
)
