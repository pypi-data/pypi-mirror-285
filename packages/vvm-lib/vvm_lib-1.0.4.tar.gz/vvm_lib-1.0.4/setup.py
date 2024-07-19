from setuptools import setup


setup(name='vvm_lib',
      version='1.0.4',
      description='my frequently used functions',
      packages=[
          'vvm_lib',
          "vvm_lib.db",
          ],
      package_dir={
        "vvm_lib": "vvm_lib",
        "vvm_lib.db": "vvm_lib/db",
    },
      author_email='v.vazhinskiy@yandex.ru',
      author="vvazhinskiy",
      url="https://github.com/VazhikVM/vvm_lib",
      zip_safe=False,
      install_requires=[
          "pandas",
          "numpy",
          "psycopg2-binary",
          "hvac",
          "openpyxl",
          "requests-ntlm",
          "oauth2client",
          "gspread",
          "pymssql",
          "urllib3",
          "clickhouse-connect",
          "tzlocal",
          "mysql-connector-python",
          ],
      
      )