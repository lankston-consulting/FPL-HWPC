from setuptools import setup


setup(
    name="hwpccalc",
    version="0.0.4",
    install_requires=[
        "bokeh<3.0.0",
        "boto3[crt]",
        "cloudpickle",
        "dask[dataframe,diagnostics,distributed]==2022.10.0",
        "dask-cloudprovider[aws]==2022.10.0",
        "distributed==2022.10.0",
        "lz4~=4.0.2",
        "numpy",
        "pandas",
        "plotly",
        "python-dotenv",
        "pytz",
        "scipy",
        "six",
        "xarray"
    ],
)
