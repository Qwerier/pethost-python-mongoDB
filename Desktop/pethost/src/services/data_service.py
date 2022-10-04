import datetime
from typing import List

from data.bookings import Booking
from data.rooms import Room
from data.owners import Owner
from data.pets import Pet


def create_account(name: str, email: str, password: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email
    owner.password = password

    owner.save()

    return owner


def find_account(email: str, password: str) -> Owner:
    owner = Owner.objects().filter(email=email).filter(password=password).first()

    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects().filter(email=email).first()

    return owner


def register_room(active_account: Owner,
                  name, surface, height, price) -> Room:
    room = Room()

    room.name = name
    room.surface = surface
    room.height = height
    room.price = price

    room.save()

    account = find_account_by_email(active_account.email)
    account.room_ids.append(room.id)

    account.save()

    return room


def find_rooms_for_user(account: Owner) -> List:
    query = Room.objects(id__in=account.room_ids)
    rooms = list(query)

    return rooms


def add_available_date(room: Room, start_date: datetime.datetime, days: int):
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    room = Room.objects(id=room.id).first()
    room.bookings.append(booking)
    room.save()

    return room


def add_pet(account, species, name, height, need_desc) -> Pet:
    owner = find_account_by_email(account.email)

    pet = Pet()
    pet.species = species
    pet.name = name
    pet.height = height
    pet.need_desc = need_desc

    pet.save()

    owner.pet_ids.append(pet.id)
    owner.save()

    return pet


def get_pets_for_user(account: Owner) -> List[Pet]:
    owner = Owner.objects(id=account.id).first()
    pets = Pet.objects(id__in=owner.pet_ids).all()
    return list(pets)


def get_available_rooms(checkin: datetime.datetime, checkout: datetime.datetime,
                        pet: Pet) -> List[Room]:
    query = Room.objects() \
        .filter(height__gt=pet.height + 0.1) \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    rooms = query

    final_rooms = []
    for r in rooms:
        for b in r.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and not b.guest_pet_id:
                final_rooms.append(r)

    return final_rooms


def book_room(account, pet, room, checkin, checkout):
    booking = None

    for b in room.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_pet_id:
            booking = b
            break

    booking.guest_owner_id = account.id
    booking.guest_pet_id = pet.id
    booking.booked_date = datetime.datetime.now()

    room.save()


def get_bookings_for_user(email: str) -> List[Booking]:
    account = find_account_by_email(email)
    booked_rooms = Room.objects() \
        .filter(bookings__guest_owner_id=account.id) \
        .only("bookings", 'name')

    def map_room_to_booking(room, booking):
        booking.room = room
        return booking

    bookings = [
        map_room_to_booking(room, booking)
        for room in booked_rooms
        for booking in room.bookings
        if booking.guest_owner_id == account.id
    ]

    return bookings
