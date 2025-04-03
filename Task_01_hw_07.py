# Virtual Assistant Bot for managing a contact list with features like adding, editing, and deleting contacts,
#  as well as managing phone numbers and birthdays.

import re
from collections import UserDict
from datetime import datetime, timedelta

class Field:  # Base class for fields in the contact list
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):  # Class for storing names
    def __init__(self, value):
        if not value:
            raise ValueError("Name is required!")
        super().__init__(value)

class Phone(Field):  # Class for storing phone numbers
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Phone number must be 10 digits!")
        super().__init__(value)

    @staticmethod  # Validate phone number format
    def validate_phone(value):
        return bool(re.match(r"^\d{10}$", value))


class Birthday(Field):  #NEW Class for storing birthday
    def __init__(self, value):
        try:
            # Try to convert the string to a datetime object
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:  # Class for storing a contact record
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None  # NEW Optional birthday field

    def __str__(self):  # String representation of the record
        phones = '; '.join(p.value for p in self.phones)
        birthday = f", birthday: {self.birthday}" if self.birthday else ""  #Adited
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"

    def add_phone(self, phone_number):  # Add a new phone number
        if self.find_phone(phone_number):
            raise ValueError("Phone number already exists.")
        if not Phone.validate_phone(phone_number):
            raise ValueError("Phone number must be 10 digits!")
        if not phone_number:
            raise ValueError("Phone number is required!")
        if len(self.phones) >= 3:
            raise ValueError("Cannot add more than 3 phone numbers.")
        if len(phone_number) != 10:
            raise ValueError("Phone number must be 10 digits!")
        if not self.phones:  # If no phones exist, add the first one
            self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):  # Remove a phone number
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
            return f"Phone {phone_number} removed."
        return "Phone number not found."

    def edit_phone(self, old_phone_number, new_phone_number):  # Change a phone number
        self.remove_phone(old_phone_number)
        self.add_phone(new_phone_number)

    def find_phone(self, phone_number):  # Find a phone number in the record
        return next((p for p in self.phones if p.value == phone_number), None)

    def add_birthday(self, birthday):  # new Add birthday to a contact
        if self.birthday:
            raise ValueError("Birthday already exists.")
        self.birthday = Birthday(birthday)


class AddressBook(UserDict):  # Class for managing the address book
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name, phone=None):
        record = self.find(name)
        if not record:
            return "Contact not found."
        if phone:
            record.remove_phone(phone)
            return f"Phone {phone} removed from {name}."
        del self.data[name]
        return f"Contact {name} deleted."

    def get_upcoming_birthdays(self):     # new function to check upcoming birthdays
        today = datetime.now()
        upcoming_birthdays = []
        for record in self.values():
            if record.birthday:
                # Check if the birthday is within the next 7 days
                next_birthday = record.birthday.value.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)
                if today <= next_birthday <= today + timedelta(days=7):
                    upcoming_birthdays.append(record.name.value)
        return upcoming_birthdays


def input_error(func):  # Using Decorator for handling errors from previous task
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Enter a name."
        except KeyError:
            return "Enter a phone."

    return inner

def parse_input(user_input):
    cmd, *args = user_input.strip().split()
    return cmd.lower(), args

@input_error
def add_contact(args, book):  # Add a new contact to the address book
    if len(args) != 2:
        return "Provide a name and a phone number."
    name, phone = args
    record = book.find(name) or Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return f"Contact {name} added."

@input_error
def add_birthday_contact(args, book):  # new Add birthday to a contact
    if len(args) != 2:
        return "Provide a name and a birthday (DD.MM.YYYY)."
    name, birthday = args
    record = book.find(name)
    if record:
        try:
            record.add_birthday(birthday)
            return f"Birthday for {name} added."
        except ValueError as e:
            return str(e)
    return f"Contact {name} not found."

@input_error
def change_contact(args, book):  # Change an existing contact's phone number
    if len(args) != 3:
        return "Please provide the name, OLD phone number, and a NEW phone number"
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        try:
            record.edit_phone(old_phone, new_phone)
            return f"Phone number for {name} updated from {old_phone} to {new_phone}."
        except ValueError as e:
            return str(e)
    return f"Contact {name} not found."

@input_error
def show_phone(args, book):  # Show the phone number of a contact
    name = args[0]
    record = book.find(name)
    if record:
        return ', '.join(p.value for p in record.phones)
    return "Contact not found."

@input_error
def show_all(book):  # Show all contacts in the address book
    if not book.data:
        return "No contacts found."
    return '\n'.join(str(record) for record in book.values())

@input_error
def delete_contact(args, book):  # Delete a contact from the address book
    name = args[0]
    return book.delete(name)

@input_error
def remove_phone(args, book):  # Remove a phone number from a contact
    name, phone = args
    record = book.find(name)
    if record:
        record.remove_phone(phone)
        return f"Phone {phone} removed from {name}."
    return "Contact not found."

@input_error
def find_phone(args, book):  # Find a contact by phone number
    phone = args[0]
    for record in book.values():
        if any(p.value == phone for p in record.phones):
            return f"Phone {phone} belongs to {record.name.value}."
    return "Phone not found."

def main():  # Main function to run the assistant bot
    book = AddressBook()  # Create an instance of AddressBook

    # Створення запису для John (для тестування)
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")
    john_record.add_birthday("01.05.1990")
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane (для тестування)
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    book.add_record(jane_record)

    # Creating bot instance
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["exit", "close"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "add_birthday":  # new command to add birthday
            print(add_birthday_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "delete":
            print(delete_contact(args, book))
        elif command == "remove_phone":
            print(remove_phone(args, book))
        elif command == "find_phone":
            print(find_phone(args, book))
        elif command == "upcoming_birthdays":  #new command to show upcoming birthdays
            print(book.get_upcoming_birthdays())
        else:
            print("Invalid command.")

if __name__ == "__main__":  # Entry point of the program
    main()
