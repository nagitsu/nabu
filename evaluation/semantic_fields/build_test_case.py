import os
import random


def main():
    test_categories = {}

    for file_name in os.listdir(os.getcwd()):
        if file_name.endswith('.txt'):  # txt files contain test data
            with open(file_name, 'r') as f:
                category_name = file_name.split('.')[0]
                test_categories[category_name] = [
                    noun.strip() for noun in f.readlines()
                ]

    categories_list = test_categories.keys()
    with open('semantic_fields.test', 'w') as f:
        for cat_name, cat_items in test_categories.iteritems():
            f.write(': {}\n'.format(cat_name))

            for word in cat_items:
                odd_category = random.choice([
                    c for c in categories_list if c != cat_name
                ])
                odds = random.sample(test_categories[odd_category], 3)

                f.write('{} {}\n'.format(word, ' '.join(odds)))

if __name__ == '__main__':
    main()
