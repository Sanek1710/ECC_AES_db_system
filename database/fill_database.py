import pyodbc as odbc
from faker import Faker
from random import randint, getrandbits


fake = Faker()

DB_CONNECTION = odbc.connect('''
            Driver={SQL Server};
            Server=LOCALHOST\\SQLEXPRESS;
            Database=ECC_AES;
            Trusted_Connection=yes;''')
DB_CONNECTION.autocommit = True

for i in range(10):
    fullname = fake.name().split()
    name = fullname[0]
    surname = fullname[1]
    age = randint(16, 60)
    binkey = getrandbits(256).to_bytes(32, 'big')
    row = (i, name, surname, age, binkey)
    print('%2d | %10s | %10s | %2d | %s '%row)
    DB_CONNECTION.execute('''insert into People values (?,?,?,?,?)''', row)







sql = '''
select * from People
'''

data = DB_CONNECTION.execute(sql).fetchall()
print(data)
