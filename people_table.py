from typing import Generator
import pyodbc
import asn1
import ecc

DB_CONNECTION = pyodbc.connect('''
            Driver={SQL Server};
            Server=LOCALHOST\\SQLEXPRESS;
            Database=ECC_AES;
            Trusted_Connection=yes;''')
DB_CONNECTION.autocommit = True

class People():
    def __init__(self):
        self.columns = ['id', 'name', 'surname', 'age', 'binKey']
        self.cursor = DB_CONNECTION.cursor()

    def encryptRow(self, ecc_key, id):
        sql = 'SELECT ' + ', '.join(self.columns) + ' FROM People WHERE id = (?)'
        res = self.cursor.execute(sql, id).fetchall()
        if len(res) != 1:
            return None
        res = tuple(res[0])

        encoded_res = asn1.encode(res)
        encrypted_res = ecc_key.encrypt(encoded_res)
        encrypted_res = asn1.encode(encrypted_res)

        try:
            sql = 'INSERT INTO PeopleEncRow(id, EncRow) VALUES (?, ?)'
            self.cursor.execute(sql, (id, encrypted_res))
        except Exception as e:
            pass

        print("Encrypted row:")
        print(encrypted_res)
        print()

        return encrypted_res

    def decryptRow(self, ecc_key, id):
        sql = 'SELECT EncRow FROM PeopleEncRow WHERE id = (?)'
        encrypted_res = self.cursor.execute(sql, id).fetchone()
        if len(encrypted_res) != 1:
            return None

        encrypted_res = encrypted_res[0]
        
        encrypted_res, tail = asn1.decode(encrypted_res)
        print(encrypted_res)
        encoded_res = ecc_key.decrypt(encrypted_res) #TODO: расшифровать
        res, tail = asn1.decode(encoded_res)

        print("Decrypted row:")
        print("%2d | %12s | %12s | %2d | %s" % tuple(res) )
        print()

        return res

    def encryptColumn(self, ecc_key, column):
        sql = 'SELECT id, ' + column + ' FROM People'
        col = self.cursor.execute(sql).fetchall()

        enc_col = [
            (
                id, 
                asn1.encode(ecc_key.encrypt(asn1.encode(val)))
            ) 
            for id, val in col
        ]

        try:
            sql = 'INSERT INTO PeopleEncColumn' + column + ' VALUES (?, ?)'
            for enc_val in enc_col:
                self.cursor.execute(sql, enc_val)
        except Exception as e:
            pass


        print("Encrypted column "+ column +":")
        for id, enc_val in enc_col:
            print("%2d |"%id, enc_val)
        print()


        return enc_col


    def decryptColumn(self, ecc_key, column):
        sql = 'SELECT id, Enc' + column + ' FROM PeopleEncColumn' + column
        enc_col = self.cursor.execute(sql).fetchall()

        col = [
            (
                id, 
                asn1.decode(ecc_key.decrypt(asn1.decode(val)[0]))[0]
            ) 
            for id, val in enc_col
        ]

        print("Decrypted column "+ column +":")
        for id, val in col:
            print("%2d |"%id, val)
        print()

        return col

    def encryptElement(self, ecc_key, id, column):
        sql = 'SELECT ' + column + ' FROM People WHERE id = (?)'
        elem = self.cursor.execute(sql, id).fetchone()

        elem = elem[0]

        enc_elem = asn1.encode(ecc_key.encrypt(asn1.encode(elem)))

        try:
            sql = 'INSERT INTO PeopleEncElement VALUES (?, ?, ?)'
            self.cursor.execute(sql, (id, column, enc_elem))
        except Exception as e:
            pass

        print('Encrypted Element ' + column)
        print('%2d |'%id, enc_elem)
        print()

        return enc_elem

    def decryptElement(self, ecc_key, id, column):
        sql = 'SELECT EncElement FROM PeopleEncElement WHERE id = (?) AND colName = (?)'
        enc_elem = self.cursor.execute(sql, (id, column)).fetchone()

        enc_elem = enc_elem[0]

        elem, tail = asn1.decode(ecc_key.decrypt(asn1.decode(enc_elem)[0]))

        print('Decrypted Element ' + column)
        print('%2d |'%id, elem)
        print()

        return elem

    def selectAll(self):
        sql = 'SELECT * FROM People'
        res = self.cursor.execute(sql).fetchall()

        sql = 'SELECT id, EncRow FROM PeopleEncRow'
        enc_res = self.cursor.execute(sql).fetchall()

        for row in res:
            print("%2d | %12s | %12s | %2d | %s" % tuple(row))

        for row in enc_res:
            print("%2d | %s" % tuple(row))
        


people = People()

ecc_key = ecc.generate()

people.encryptRow(ecc_key, 5)
people.encryptRow(ecc_key, 7)

people.decryptRow(ecc_key, 5)
people.decryptRow(ecc_key, 7)

people.encryptColumn(ecc_key, 'name')
people.decryptColumn(ecc_key, 'name')

people.encryptColumn(ecc_key, 'age')
people.decryptColumn(ecc_key, 'age')


people.encryptElement(ecc_key, 3, 'surname')
people.decryptElement(ecc_key, 3, 'surname')

people.encryptElement(ecc_key, 8, 'age')
people.decryptElement(ecc_key, 8, 'age')