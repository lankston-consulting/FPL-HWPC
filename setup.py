from setuptools import setup


setup(
    name="hwpccalc",
    version="0.0.2",
    install_requires=[
        "awscrt==0.14.0",
        "bokeh==2.4.3",
        "boto3[crt]==1.24.78",
        "botocore==1.27.78; python_version >= '3.7'",
        "click==8.1.3; python_version >= '3.7'",
        "cloudpickle==2.2.0",
        "dask[dataframe,diagnostics,distributed]==2022.9.1",
        "distributed==2022.9.1",
        "fsspec==2022.8.2; python_version >= '3.7'",
        "heapdict==1.0.1",
        "jinja2==3.1.2; python_version >= '3.7'",
        "jmespath==1.0.1; python_version >= '3.7'",
        "locket==1.0.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "lz4==4.0.2",
        "markupsafe==2.1.1; python_version >= '3.7'",
        "msgpack==1.0.4",
        "numpy==1.23.3",
        "packaging==21.3; python_version >= '3.6'",
        "pandas==1.5.0",
        "partd==1.3.0; python_version >= '3.7'",
        "pillow==9.2.0; python_version >= '3.7'",
        "psutil==5.9.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "pyparsing==3.0.9; python_full_version >= '3.6.8'",
        "python-dateutil==2.8.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "python-dotenv==0.21.0",
        "pytz==2022.2.1",
        "pyyaml==6.0; python_version >= '3.6'",
        "s3transfer==0.6.0; python_version >= '3.7'",
        "scipy==1.9.1",
        "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "sortedcontainers==2.4.0",
        "tblib==1.7.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "toolz==0.12.0; python_version >= '3.5'",
        "tornado==6.1; python_version >= '3.5'",
        "typing-extensions==4.3.0; python_version >= '3.7'",
        "urllib3==1.26.12; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5' and python_version < '4'",
        "xarray==2022.6.0",
        "zict==2.2.0; python_version >= '3.7'",
    ],
)
