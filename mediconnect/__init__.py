import pymysql

pymysql.install_as_MySQLdb()

# Django 6 checks MySQLdb version metadata; map PyMySQL to a compatible value.
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.__version__ = "2.2.1"
