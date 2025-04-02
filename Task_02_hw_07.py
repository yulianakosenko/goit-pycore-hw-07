import re
from collections import UserDict
from datetime import datetime, timedelta

from Task_01_hw_07 import add_contact, change_contact, show_all, show_phone

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


class Birthday(Field):  # Class for storing birthday
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
        self.birthday = None  # Optional birthday field

    def __str__(self):  # String representation of the record
        phones = '; '.join(p.value for p in self.phones)
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
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

    def add_birthday(self, birthday):  # Add birthday to the contact
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

    def get_upcoming_birthdays(self):  # нова функція для перевірки наступних днів народження
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


# нові функції для обробки команд:
@input_error
def add_birthday(args, book: AddressBook):  # нова функція для додавання дня народження
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
def show_birthday(args, book: AddressBook):  # нова функція для показу дня народження
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is on {record.birthday}"
    return "Contact or birthday not found."

@input_error
def birthdays(args, book: AddressBook):  # нова функція для показу майбутніх днів народження
    today = datetime.now()
    upcoming_birthdays = []
    for record in book.values():
        if record.birthday:
            next_birthday = record.birthday.value.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            if today <= next_birthday <= today + timedelta(days=7):
                upcoming_birthdays.append(f"{record.name.value}: {next_birthday.strftime('%d.%m.%Y')}")
    
    if upcoming_birthdays:
        return "\n".join(upcoming_birthdays)
    return "No upcoming birthdays this week."


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

        if command in ["close", "exit"]: # Exit the program using close or exit
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))  # Викликаємо команду для додавання контакту add [ім'я] [телефон]

        elif command == "change":
            print(change_contact(args, book))  # Викликаємо команду для зміни телефону change [ім'я] [старий телефон] [новий телефон]

        elif command == "phone":
            print(show_phone(args, book))  # Викликаємо команду для показу телефону hone [ім'я]

        elif command == "all":
            print(show_all(book))  # Викликаємо команду для показу всіх контактів

        elif command == "add-birthday":
            print(add_birthday(args, book))  # нова команда для додавання дня народження add-birthday [ім'я] [дата народження]

        elif command == "show-birthday":
            print(show_birthday(args, book))  # нова команда для показу дня народження show-birthday [ім'я]

        elif command == "birthdays":
            print(birthdays(args, book))  # нова команда для показу майбутніх днів народження

        else:
            print("Invalid command.")

if __name__ == "__main__":  # Run the main function 
    main()
