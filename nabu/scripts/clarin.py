import json
import re
import requests
import sys
import time

from datetime import datetime, date, timedelta
from lxml import html

from nabu.corpus.models import db, Entry, DataSource


BASE_URL = 'http://www.clarin.com/archivo/pager.json?date={}&page={}'
FIRST_DATE = date(2010, 5, 29)


def save_entries(ids, data_source):
    now = datetime.now()
    new_entries = []
    for source_id in ids:
        new_entries.append({
            'outcome': 'pending',
            'source_id': source_id,
            'added': now,
            'number_of_tries': 0,
            'data_source_id': data_source
        })
    db.execute(Entry.__table__.insert(), new_entries)
    db.commit()


def main(first_date=FIRST_DATE):
    clarin = db.query(DataSource).filter_by(domain='clarin.com').first()
    if not clarin:
        clarin = DataSource(domain='clarin.com')
        db.merge(clarin)
        db.commit()

    day_count = (date.today() - first_date).days

    for current_day in range(day_count):
        day = first_date + timedelta(days=current_day)
        print("day: {}".format(day))

        page_number = 1
        day_ids = []
        while True:
            url = BASE_URL.format(str(day).replace('-', ''), page_number)
            response = requests.get(url)

            # Remove beginning and ending parentheses.
            if not response.text:
                print("error; sleeping...")
                time.sleep(60)
                continue

            page = json.loads(response.text[1:-1])
            if not page['news']:
                break

            # Get the IDs for each link on the history page.
            root = html.fromstring(page['news'])
            links = [
                el.get('href')
                for el in root.xpath('//li[@class="item"]/a[@href]')
            ]
            day_ids.extend(
                [re.sub(r'.*_(\d+)\.html', r'\1', l) for l in links]
            )

            if not page.get('moreContents'):
                break
            page_number += 1

        if day_ids:
            save_entries(day_ids, clarin.id)


if __name__ == '__main__':
    if len(sys.argv) > 3:
        year, month, day = map(int, sys.argv[1:4])
        first_date = date(year, month, day)
        main(first_date)
    else:
        main()
