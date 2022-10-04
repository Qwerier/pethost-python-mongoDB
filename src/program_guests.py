from dateutil import parser

from infrastructure.switchlang import switch
import program_hosts as hosts
import infrastructure.state as state
import services.data_service as svc
import datetime


def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_pet)
            s.case('y', view_your_pets)
            s.case('b', book_a_room)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a room')
    print('[A]dd a pet')
    print('View [y]our pets')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_pet():
    print(' ****************** Add a pet **************** ')

    if not state.active_account:
        hosts.error_msg("You must log in first to add a pet")
        return

    species = input("What's the species of your pet?")
    name = input(f"What's the name of your {species}?")
    height = float(input(f"How long is your {species} (in meters)?"))
    needs_desc = input(f"What special needs does your {species} have?")

    pet = svc.add_pet(state.active_account,species, name, height, needs_desc)
    state.reload_account()

    hosts.success_msg(f"Created {pet.name} with id {pet.id}")


def view_your_pets():
    print(' ****************** Your pets **************** ')
    if not state.active_account:
        hosts.error_msg("You need to be logged in")
        return

    pets = svc.get_pets_for_user(state.active_account)
    print(f"You have {len(pets)} pets")

    for idx,p in enumerate(pets):
        print(f"{p.name} is a {p.species} that is {p.height}m "
              f"long and {'has no needs' if p.any_need=='' else 'has this/these needs:'}"
              f"{p.any_need if not p.any_need==''else''}")


def book_a_room():
    print(' ****************** Book a room **************** ')
    if not state.active_account:
        print("You need to have an account before logging in")
        return
    pets = svc.get_pets_for_user(state.active_account)
    if not pets:
        hosts.error_msg("You must first add a pet before booking a room")
        return

    print("Let's start by finding available rooms.")
    start_text = input("Check-in date [yyyy-mm-dd]: ")
    if not start_text:
        hosts.error_msg("Cancelled")
        return

    checkin = parser.parse(
        start_text
    )

    checkout = parser.parse(
        input("Check-out date [yyyy-mm-ddd]: ")
    )

    if checkin >= checkout:
        hosts.error_msg("Check in must be before check out")
        return

    for idx, p in enumerate(pets):
        print(f"{idx+1}.{p.name}(height:{p.length}"
              f"species:{p.species})"
              )

    pet = pets[int(input('Which pet do you want to book (number)'))-1]

    rooms = svc.get_available_rooms(checkin, checkout, pet)

    print(f"There are {len(rooms)} rooms available in that time")

    for idx, r in enumerate(rooms):
        print(f"{idx+1}. {r.name} with "
              f"and {r.square_meters}m "
              f"height: {r.height}"
              f"and price{r.price}.")

    if not rooms:
        hosts.error_msg("Sorry no rooms are available for that date.")
        return
    room = rooms[int(input("Which room do you want to book (number"))-1]
    svc.book_room(pet, room, checkin, checkout)

    hosts.success_msg("You just booked the room")


def view_bookings():
    print(' ****************** Your bookings **************** ')
    if not state.active_account:
        hosts.error_msg("You must log in first to register a room")
        return

    pets = {p.id: p for p in svc.get_pets_for_user(state.active_account)}
    bookings = svc.get_bookings_for_user(state.active_account)

    print(f"You have {len(bookings)} bookings.")

    for b in bookings:
        print(f"pet: {pets.get(b.guest_pet_id).name} is booked at "
              f"{b.room.name} from {datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day)} for "
              f"{(b.check_out_date - b.check_in_date).days} days")

