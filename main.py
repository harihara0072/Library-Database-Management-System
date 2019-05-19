#Team Details:
#Name : Hari Hara Kumar
#Student Id : 1001102740

#Name:Tandra Sohith chandra Naidu
#Student ID: 1001715618

#Importing the libraries that are required
import pymysql
import os

#Establishing the connection with the database

connection = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='kimi1992',
                             db='library')
print("Database connected...")

#Douwnloaded the .CSV files which has the data into the folder "Input Data
data_dir = 'Data'

#Changing the directory to the input data
files = os.listdir(data_dir)

#Iterating through all the files in the input dirctory and loading the data in each file by reading each line.
for file in files:

    #Using the file name withut .csv extension as the table name
    file_name = file[:-4]

    #Opening the CSV file
    data = open(data_dir + "/" + file, encoding='utf-8')

    #Reading each line of the file
    data = data.readlines()
    for i in data:
        cur = connection.cursor()

        #Inserting each line
        command = "INSERT INTO " + file_name + " VALUES(" + str(i).rstrip('/\n') + ");"
        cur.execute(command)

    #Commiting the changes.
    connection.commit()




