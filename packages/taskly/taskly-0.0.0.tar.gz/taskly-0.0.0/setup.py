from setuptools import setup, find_packages

if __name__ == "__main__":
    try:
        setup(
            use_scm_version={"version_scheme": "no-guess-dev"},
            # packages=find_packages(where='src'),
            # package_dir={'': 'src'},
        )
    except Exception as e:
        print(
            "\n\nAn error occurred while building the project:\n",
            str(e),
            "\n\nPlease ensure you have the most updated version of setuptools, "
            "setuptools_scm, and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise
