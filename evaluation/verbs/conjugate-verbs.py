import json
import requests
from lxml import html


# Files.
IN_FILE = 'verbs-ES.txt'
OUT_FILE = 'conjugate-verbs-ES.txt'


def main():
    with open(IN_FILE, 'r') as f:
        lines = f.readlines()

    visited_verbs = []
    verb_data = {}
    for verb in lines:
        print 'Processing: %s' % verb

        response = requests.get('http://verbos.woxikon.es/es/%s' % verb)
        if response.status_code != 200:
            print 'ERROR with HTTP request for %s' % verb
            continue

        root = html.fromstring(response.content)

        found_verb = root.cssselect('span.hl')[0].text_content()
        if found_verb in visited_verbs:
            # We already have this verb, continue.
            continue

        table_css = 'div.table-responsive table.verbs-table tr td'

        css_extract = lambda index: root.cssselect(
            table_css
        )[index].text_content()

        try:
            current_data = {
                'gerundio': css_extract(0),
                'participio': css_extract(1),
                'presente': {
                    'yo': css_extract(2),
                    'tu': css_extract(3),
                    'el': css_extract(4),
                    'nosotros': css_extract(5),
                    'vosotros': css_extract(6),
                    'ellos': css_extract(7)
                },
                'imperfecto': {
                    'yo': css_extract(8),
                    'tu': css_extract(9),
                    'el': css_extract(10),
                    'nosotros': css_extract(11),
                    'vosotros': css_extract(12),
                    'ellos': css_extract(13)
                },
                'indefinido': {
                    'yo': css_extract(14),
                    'tu': css_extract(15),
                    'el': css_extract(16),
                    'nosotros': css_extract(17),
                    'vosotros': css_extract(18),
                    'ellos': css_extract(19)
                },
                'futuro_1': {
                    'yo': css_extract(20),
                    'tu': css_extract(21),
                    'el': css_extract(22),
                    'nosotros': css_extract(23),
                    'vosotros': css_extract(24),
                    'ellos': css_extract(25)
                },
                'condicional': {
                    'yo': css_extract(26),
                    'tu': css_extract(27),
                    'el': css_extract(28),
                    'nosotros': css_extract(29),
                    'vosotros': css_extract(30),
                    'ellos': css_extract(31)
                },
                'subjuntivo': {
                    'yo': css_extract(32),
                    'tu': css_extract(33),
                    'el': css_extract(34),
                    'nosotros': css_extract(35),
                    'vosotros': css_extract(36),
                    'ellos': css_extract(37)
                },
                'subjuntivo_p_i_1': {
                    'yo': css_extract(38),
                    'tu': css_extract(39),
                    'el': css_extract(40),
                    'nosotros': css_extract(41),
                    'vosotros': css_extract(42),
                    'ellos': css_extract(43)
                },
                'subjuntivo_p_i_2': {
                    'yo': css_extract(44),
                    'tu': css_extract(45),
                    'el': css_extract(46),
                    'nosotros': css_extract(47),
                    'vosotros': css_extract(48),
                    'ellos': css_extract(49)
                },
                'subjuntivo_futuro': {
                    'yo': css_extract(50),
                    'tu': css_extract(51),
                    'el': css_extract(52),
                    'nosotros': css_extract(53),
                    'vosotros': css_extract(54),
                    'ellos': css_extract(55)
                },
                'imperativo_presente': {
                    'tu': css_extract(105),
                    'el': css_extract(106),
                    'nosotros': css_extract(107),
                    'vosotros': css_extract(108),
                    'ellos': css_extract(109)
                },
            }
        except IndexError:
            print 'ERROR processing: %s' % verb
            continue

        verb_data[found_verb] = current_data
        visited_verbs.append(found_verb)

    with open(OUT_FILE, 'w') as f:
        f.write(
            json.dumps(
                verb_data, indent=4, sort_keys=True, ensure_ascii=False
            ).encode('utf8')
        )


if __name__ == '__main__':
    main()
