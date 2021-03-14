USE master
GO

IF NOT EXISTS (
    SELECT name
        FROM sys.databases
        WHERE name = N'ECC_AES'
)
CREATE DATABASE ECC_AES
GO

USE ECC_AES
GO

IF OBJECT_ID('PeopleEncColumnName', 'U') IS NOT NULL
DROP TABLE PeopleEncColumnName
GO
IF OBJECT_ID('PeopleEncColumnSurname', 'U') IS NOT NULL
DROP TABLE PeopleEncColumnSurname
GO
IF OBJECT_ID('PeopleEncColumnAge', 'U') IS NOT NULL
DROP TABLE PeopleEncColumnAge
GO
IF OBJECT_ID('PeopleEncColumnBinkey', 'U') IS NOT NULL
DROP TABLE PeopleEncColumnBinkey
GO

IF OBJECT_ID('PeopleEncRow', 'U') IS NOT NULL
DROP TABLE PeopleEncRow
GO
IF OBJECT_ID('PeopleEncElement', 'U') IS NOT NULL
DROP TABLE PeopleEncElement
GO
IF OBJECT_ID('People', 'U') IS NOT NULL
DROP TABLE People
GO

CREATE TABLE People
(
    Id INT NOT NULL,
    Name VARCHAR(32),
    Surname VARCHAR(32),
    Age INT,
    BinKey Binary(32),
    PRIMARY KEY (Id)
)
GO

CREATE TABLE PeopleEncRow
(
    Id INT NOT NULL,
    EncRow Binary(256),
    PRIMARY KEY (Id)
)
GO

CREATE TABLE PeopleEncElement
(
    Id INT NOT NULL,
    ColName VARCHAR(32),
    EncElement Binary(256),
    PRIMARY KEY (Id, ColName)
)
GO

CREATE TABLE PeopleEncColumnName
(
    Id INT NOT NULL,
    EncName Binary(256),
    PRIMARY KEY (Id)
)
GO

CREATE TABLE PeopleEncColumnSurname
(
    Id INT NOT NULL,
    EncSurname Binary(256),
    PRIMARY KEY (Id)
)
GO


CREATE TABLE PeopleEncColumnAge
(
    Id INT NOT NULL,
    EncAge Binary(256),
    PRIMARY KEY (Id)
)
GO

CREATE TABLE PeopleEncColumnBinkey
(
    Id INT NOT NULL,
    EncBinkey Binary(256),
    PRIMARY KEY (Id)
)
GO



