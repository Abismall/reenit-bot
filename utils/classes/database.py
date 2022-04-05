from dotenv import load_dotenv
import mysql.connector
import os
from botconfig import requiredEnv


class Database:
    def __init__(self):

        self.host = os.getenv(requiredEnv["csgoscrimbot"]["db_host"])
        self.user = os.getenv(requiredEnv["csgoscrimbot"]["db_user"])
        self.password = os.getenv(requiredEnv["csgoscrimbot"]["db_password"])
        self.current_database = os.getenv(requiredEnv["csgoscrimbot"]["db"])

    def connect(self):
        try:
            mydb = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.current_database)
            return mydb
        except mysql.connector.Error as err:
            print("Database error: {}".format(err))

    def fetch_user(self, user):
        try:
            with self.connect() as db:
                mycursor = db.cursor()
                query = "SELECT * FROM users WHERE discord = '{user}'".format(
                    user=user)
                mycursor.execute(query)
                user = mycursor.fetchone()
            return user
        except mysql.connector.Error as err:
            print("Database error: {}".format(err))

    def register_user(self, steam_id, discord_name):
        try:
            with self.connect() as db:
                mycursor = db.cursor()
                mycursor.execute(
                    "INSERT INTO users (id, discord) VALUES (%s,%s)", (steam_id, discord_name))
                db.commit()
                return discord_name
        except mysql.connector.Error as err:
            print("Database error: {}".format(err))
