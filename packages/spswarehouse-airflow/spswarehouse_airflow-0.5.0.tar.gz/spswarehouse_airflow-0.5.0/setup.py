import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spswarehouse_airflow",
    version="0.5.0",
    author="Summit Public Schools; Harry Li Consulting, LLC",
    author_email="warehouse@summitps.org",
    description="Summit Public Schools Snowflake warehouse for use in Airflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SummitPublicSchools/spswarehouse_airflow",
    packages=setuptools.find_packages(),
    # This needs to be set so you get the files included by MANIFEST.in
    # when you run "pip install"
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        'pandas==1.5.2',
        'SQLAlchemy==1.4.44',
        'snowflake-sqlalchemy==1.4.4',
        'google-api-python-client==1.12.11',
        'google-auth-httplib2==0.1.0',
        'google-auth-oauthlib==0.7.1',
        'gspread==5.7.2',
        'PyDrive2==1.15.0',
        'spswarehouse>=0.7.3',
        'duct-tape>=0.26.0',
        'apache-airflow<=2.5.0',
    ]
)
