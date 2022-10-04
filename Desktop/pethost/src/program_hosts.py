import pwinput
from colorama import Fore
from dateutil import parser
import datetime
from infrastructure.switchlang import switch
import infrastructure.state as state
import services.data_service as svc


def run():
    print(' ****************** Welcome host **************** ')
    print()

    show_commands()

    while True:
        action = get_action()

        with switch(action) as s:
            s.case('c', create_account)
            s.case('a', log_into_account)
            s.case('l', list_rooms)
            s.case('r', register_room)
            s.case('u', update_availability)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.default(unknown_command)

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('Login to your [a]ccount')
    print('[L]ist your rooms')
    print('[R]egister a room')
    print('[U]pdate room availability')
    print('[V]iew your bookings')
    print('Change [M]ode (guest or host)')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def create_account():
    print(' ------------ REGISTER ------------')

    name = input("Name: ")
    email = input("Email: ").strip().lower()
    old_account = svc.find_account_by_email(email=email)

    if old_account:
        error_msg(f"ERROR: Account with email {email} already exists")
        return

    password = pwinput.pwinput(prompt="Password: ")
    state.active_account = svc.create_account(name, email, password)
    success_msg(f"Created new account with id {state.active_account.id}")


def log_into_account():
    print(' ****************** LOGIN **************** ')

    email = input("Email : ").strip().lower()

    account = svc.find_account_by_email(email)

    if not account:
        error_msg("Couldn't find the account")
        return

    password = pwinput.pwinput(prompt="Password: ")
    account = svc.find_account(email, password)

    if not account:
        error_msg("Password is incorrect")
        return

    state.active_account = account
    success_msg("Logged in successfully")


def register_room():
    print(' ****************** REGISTER room **************** ')

    if not state.active_account:
        error_msg("You must login first to register a room.")
        return

    try:
        surface = float(input("How many square meters is the property? "))
        price = int(input("What's the daily price? "))
        height = float(input("What's the height of the room? "))
    except ValueError:
        error_msg("Please enter the right type for each field!")
        return

    name = input("Give your property a name: ")

    room = svc.register_room(
        state.active_account, name, surface,height, price,
    )
    state.reload_account()
    success_msg(f"Register new room with id {room.id}")


def list_rooms(suppress_header=False):
    if not suppress_header:
        print(' ******************     Your rooms     **************** ')

    if not state.active_account:
        error_msg("You must login first to register a room")
        return

    rooms = svc.find_rooms_for_user(state.active_account)
    print(f"You have {len(rooms)} rooms")
    for idx, room in enumerate(rooms):
        print(f" {idx+1}. Property '{room.name}' is {room.square_meters} m\N{SUPERSCRIPT TWO}")
        for booking in room.bookings:
            print(f"Booking {booking.check_in_date}, "
                  f"{(booking.check_out_date - booking.check_in_date).days} days, booked "
                  f"{'YES' if booking.booked_date is not None else 'no'} ")


def update_availability():
    print(' ****************** Add available date **************** ')
    if not state.active_account:
        error_msg("You must login first to register a property")
        return

    list_rooms(suppress_header=True)

    try:
        room_number = int(input("Enter room number: "))
    except ValueError:
        print("Please enter a valid property number")
        update_availability()

    rooms = svc.find_rooms_for_user(state.active_account)
    selected_room = rooms[room_number-1]

    success_msg(f"Selected room {selected_room.name}")

    start_date = parser.parse(
        input("Enter starting date [yyyy-mm-dd]:")
    )

    days = int(input("How many days is this block of time?"))

    svc.add_available_date(
        selected_room,
        start_date,
        days
    )

    state.reload_account()

    success_msg(f"Date added to room {selected_room.name}")


def view_bookings():
    print(' ****************** Your bookings **************** ')
    if not state.active_account:
        error_msg("You must log in first to register a room")
        return

    rooms = svc.find_rooms_for_user(state.active_account)

    bookings = [
        (c, b)
        for c in rooms
        for b in c.bookings
    ]

    print(f"You have {len(bookings)} bookings.")
    for c, b in bookings:
        print(f" room: {c.name}, "
              f"booked date: {datetime.date(b.booked_date.year,b.booked_date.month, b.booked_date.day)}, "
              f"from {datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day)} "
              f"for {b.duration_in_days} days.")


def exit_app():
    print()
    print('bye')
    raise KeyboardInterrupt()


def get_action():
    text = '> '
    if state.active_account:
        text = f'{state.active_account.name}> '

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def unknown_command():
    print("Sorry we didn't understand that command.")


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
