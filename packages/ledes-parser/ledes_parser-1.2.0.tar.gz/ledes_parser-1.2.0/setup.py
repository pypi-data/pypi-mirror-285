from setuptools import find_packages, setup


def main() -> None:
    import ledes_parser as app

    setup(
        name="ledes-parser",
        description="A package for parsing LEDES format files",
        url="https://github.com/travisbashor/ledes-parser",
        author="Travis Bashor",
        author_email="travis.bashor@gmail.com",
        version=app.__version__,
        packages=find_packages(exclude=["tests*"]),
        include_package_data=True,
        package_data={"ledes_parser": ["grammars/**/*.lark"]},
        install_requires=["lark-parser==0.12.0"],
    )


if __name__ == "__main__":
    main()
