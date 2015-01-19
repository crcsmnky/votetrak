import sunlight.config
from sunlight.pagination import PagingService
from sunlight import congress
from pymongo import MongoClient
from csv import DictReader

sunlight.config.API_KEY="7050db17a1ae4543b6b3adec66da1ef9"
db = MongoClient()['votetrak']

def parse_districts(distfile):
    with open(distfile) as file:
        reader = DictReader(file, fieldnames=['zip', 'state', 'district'])
        for row in reader:
            db.districts.insert(row)


def recent_active_bills():
    paging = PagingService(congress)
    recent_active_bills = paging.bills(
        history={'active':True}, 
        order='last_action_at', 
        limit=50
    )
    db.bills.insert(list(recent_active_bills))


def upcoming_bills():
    upcoming_bills = congress.upcoming_bills()
    db.upcoming.insert(upcoming_bills)


def floor_updates():
    paging = PagingService(congress)
    floor_updates = paging.floor_updates(limit=50)
    db.updates.insert(list(floor_updates))


def legislators():
    legislators = congress.all_legislators_in_office()
    db.legislators.insert(legislators)


def main():
    # parse_districts('districts.csv')
    # recent_active_bills()
    # upcoming_bills()
    # floor_updates()
    # legislators()


if __name__ == '__main__':
    main()

