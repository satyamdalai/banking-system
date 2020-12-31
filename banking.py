import os
import random
import sqlite3
from builtins import input

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()


cur.execute('CREATE TABLE IF NOT EXISTS card( id INTEGER NOT NULL PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)')
conn.commit()


def checkLuhnAlgo(cardNo):
    last_digit = int(cardNo[-1])
    if last_digit == 0:
        return False
    cardNo = cardNo[:-1]
    sum = 0
    for i, num in enumerate(cardNo, start=1):
        n = int(num)
        if i % 2 != 0:
            n = n*2
        if n > 9:
            n = n - 9
        sum += n

    if (sum+last_digit) % 10 == 0:
        return True

    return False


def checkAccount(cardNo):
    list_ = cur.execute("SELECT * FROM card")

    for account in list_.fetchall():
        if account[1] == cardNo:
            return False
    return True


def moneyTransfer(cardNo, pin):
    print("Transfer")
    print("Enter card number:")
    beneficiary = input()

    if not checkLuhnAlgo(beneficiary):
        return "Probably you made a mistake in the card number. Please try again!"

    beneficiary_Details = cur.execute(
        f"SELECT balance FROM card WHERE number = {beneficiary}").fetchall()

    if len(beneficiary_Details) == 0:
        return "Such a card does not exist."

    user_Details = cur.execute(
        f"SELECT balance FROM card WHERE number = {cardNo} AND pin = {pin}").fetchall()

    beneficiary_Balance = beneficiary_Details[0][0]
    user_Balance = user_Details[0][0]

    print("Enter how much money you want to transfer:")
    amt = int(input())
    if amt > user_Balance:
        return "Not enough money!"
    else:
        user_Balance = user_Balance - amt
        beneficiary_Balance = beneficiary_Balance + amt
        cur.execute(
            f"UPDATE card SET balance = {user_Balance} WHERE number = {cardNo} AND pin = {pin}")
        cur.execute(
            f"UPDATE card SET balance = {beneficiary_Balance} WHERE number = {beneficiary}")
        conn.commit()

    return "Success!"


def createAccount():
    accNo = random.randint(1000000000, 9999999999)
    cardNo = "400000" + str(accNo)

    while not (checkLuhnAlgo(cardNo) and checkAccount(cardNo)):
        accNo = random.randint(1000000000, 9999999999)
        cardNo = "400000" + str(accNo)

    pin = random.randint(1000, 9999)

    print("Your card has been created")
    print("Your card number:")
    print(cardNo)
    print("Your card PIN:")
    print(pin)

    cur.execute(f"INSERT INTO card (number, pin) VALUES ({cardNo}, {pin})")
    conn.commit()


def logIn():
    print("Enter your card number:")
    cardNo = input()
    print("Enter your PIN:")
    pin = int(input())
    values = cur.execute(
        f"SELECT * FROM card WHERE number = {cardNo} AND pin = {pin}").fetchall()

    if len(values) == 0:
        print("Wrong card number or PIN!")
    else:
        print("You have successfully logged in!")
        while True:
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")

            ch = int(input())

            if ch == 1:
                values = cur.execute(
                    f"SELECT * FROM card WHERE number = {cardNo} AND pin = {pin}").fetchall()
                print("Balance:", values[0][3])

            if ch == 2:
                values = cur.execute(
                    f"SELECT * FROM card WHERE number = {cardNo} AND pin = {pin}").fetchall()
                balance = values[0][3]
                print("Enter income:")
                balance = balance + int(input())
                cur.execute(
                    f"UPDATE card SET balance = {balance} WHERE number = {cardNo} AND pin = {pin}")
                conn.commit()
                print("Income was added!")

            if ch == 3:
                print(moneyTransfer(cardNo, pin))
            if ch == 4:
                cur.execute(
                    f"DELETE FROM card WHERE number = {cardNo} AND pin = {pin}")
                conn.commit()
                print("The account has been closed!")
                break
            if ch == 5:
                print("You have successfully logged out!")
                break
            if ch == 0:
                print("Bye!")
                exit()


if __name__ == '__main__':
    while True:
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")

        ch = int(input())

        if ch == 1:
            createAccount()
        if ch == 2:
            logIn()
        if ch == 0:
            print("Bye!")
            exit()
