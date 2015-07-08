import sys
import locale
import urllib2
import cStringIO
from datetime import datetime

import dataset

# Database.
DB_NAME = 'questions-words.db'
TRANSLATIONS_TABLE = 'translations'

# Files.
IN_FILE = 'mod-questions-words.txt'
OUT_FILE = 'questions-words-ES.txt'

# Marks.
DELETE_MARK = 'DELETE_MARK'


def create_db():
    f = open(IN_FILE, 'r')
    lines = f.readlines()

    total_words = set([])
    db = dataset.connect('sqlite:///%s' % DB_NAME)
    translations_table = db[TRANSLATIONS_TABLE]

    for line in lines:
        line = line.strip()
        if line.startswith(':'):
            # Comment line.
            continue

        # Add words to set.
        total_words.update(line.split())

    print 'Total words in file:', len(total_words)

    rows = [
        dict(
            word=w, translation='', updated=datetime.now()
        ) for w in total_words
    ]
    translations_table.insert_many(rows)
    translations_table.create_index(['word'])


def google_translate(to_translate, to_language="auto", language="auto"):
    '''
    Return the translation using google translate you must shortcut the
    language you define (French = fr, English = en, Spanish = es, etc...) if
    you don't define anything it will detect it or use english by default.

    Example:
        > print(translate("salut tu vas bien?", "en"))
        > hello you alright?

    Taken from:
        https://github.com/mouuff/Google-Translate-API/blob/master/python/GoogleTranslate.py
    '''
    agents = {
        'User-Agent': "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)"
    }
    before_trans = 'class="t0">'
    link = "http://translate.google.com/m?hl=%s&sl=%s&q=%s" % (
        to_language, language, to_translate.replace(" ", "+")
    )
    request = urllib2.Request(link, headers=agents)
    page = urllib2.urlopen(request).read()
    result = page[page.find(before_trans) + len(before_trans):]
    result = result.split("<")[0]
    return result


def translate():
    db = dataset.connect('sqlite:///%s' % DB_NAME)
    table = db[TRANSLATIONS_TABLE]

    while True:
        try:
            remaining = table.count(translation='')
            if not remaining:
                print '\n[INFO] All words translated.'
                break
            print '\n[INFO] Remaining items: %d' % table.count(translation='')

            rows = table.find(translation='', _limit=10)
            for row in rows:
                google_help = google_translate(
                    row['word'], to_language='es', language='en'
                ).decode('utf8')

                question = "\nPlease translate '%s' (Google: '%s'): " % (
                    row['word'], google_help
                )
                trans = raw_input(
                    question.encode('utf8')
                ).decode(
                    sys.stdin.encoding or locale.getpreferredencoding(True)
                ).strip()

                if trans == '=':
                    # No need for translation, it is the same in Spanish.
                    trans = row['word']
                elif trans in (',', '.'):
                    # Troublesome word, mark for removal.
                    trans = DELETE_MARK
                elif not trans:
                    # No input, we will use Google's suggestion.
                    trans = google_help

                print u'You wrote:', trans

                # Update db.
                table.update(
                    dict(
                        word=row['word'], translation=trans,
                        updated=datetime.now()
                    ),
                    ['word']
                )
        except (KeyboardInterrupt, SystemExit):
            print '\nInterrupt received... Closing.'
            sys.exit()


def translate_file():
    db = dataset.connect('sqlite:///%s' % DB_NAME)
    trans = {}
    for row in db[TRANSLATIONS_TABLE]:
        if row['translation'] != DELETE_MARK:
            trans[row['word']] = row['translation']

    with open(IN_FILE, 'r') as f:
        lines = f.readlines()

    buff = cStringIO.StringIO()
    for line in lines:
        try:
            new_line = u' '.join([trans[w] for w in line.split()])
        except KeyError:
            # This line has a word for which we have no translation, skip it.
            continue
        buff.write('%s\n' % new_line.encode('utf8'))

    with open(OUT_FILE, 'w') as f:
        lines = f.write(buff.getvalue())
    buff.close()

if __name__ == '__main__':
    # create_db()
    # translate()
    translate_file()
