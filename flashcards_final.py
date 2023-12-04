import argparse
import random
import os
import json
import logging
import io


class FlashCards:
    def __init__(self, import_filename=None, export_filename=None):
        logging.basicConfig(filename='flashcard_log.log', level=logging.INFO, format='%(message)s')
        self.flashcards = dict()
        self.term_definition_dict = dict()
        self.error_count = dict()
        self.log_string = io.StringIO()
        self.errors = []
        self.import_filename = import_filename
        self.export_filename = export_filename

        if self.import_filename:
            self.import_flashcards(self.import_filename)

    def flashcard_operations(self):
        while True:
            action = input('Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats): \n')
            logging.info('Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats): ')
            logging.info(action)

            if action == 'exit':
                message = 'Bye bye!'
                print(message)
                logging.info(message)
                if self.export_filename:
                    self.export_flashcards(self.export_filename)
                break

            elif action == 'add':
                self.add_flashcard()
            elif action == 'remove':
                self.remove_flashcard()
            elif action == 'import':
                filename = input('File name: \n')
                logging.info(filename)
                self.import_flashcards(filename)
            elif action == 'export':
                filename = input('File name: \n')
                logging.info(filename)
                self.export_flashcards(filename)
            elif action == 'ask':
                self.ask_flashcards()
            elif action == 'log':
                self.logs()
            elif action == 'hardest card':
                self.hardest_card()
            elif action == 'reset stats':
                self.reset_stats()

    def add_flashcard(self):
        a = 0
        d = 0
        term = ""
        definition = ""
        while True:
            if a == 0:
                term = input('The card: \n')
                logging.info('The card: ')
            else:
                term = input()
                a -= 1
            logging.info(term)
            self.log_string.write(term + '\n')
            if term not in self.flashcards:
                break
            else:
                print(f'The card "{term}" already exists. Try again:')
                logging.info(f'The card "{term}" already exists. Try again:')
                a += 1
                continue
        while True:
            if d == 0:
                definition = input('The definition of the card: \n')
                logging.info('The definition of the card: ')
            else:
                definition = input()
                d -= 1
            logging.info(definition)
            self.log_string.write(definition + '\n')
            if definition not in self.term_definition_dict:
                break
            else:
                print(f'The definition "{definition}" already exists. Try again:')
                logging.info(f'The definition "{definition}" already exists. Try again:')
                d += 1
                continue
        self.flashcards[term] = definition
        self.term_definition_dict[definition] = term
        self.error_count[term] = 0
        print(f'The pair ("{term}":"{definition}") has been added.')

    def remove_flashcard(self):
        term = input('Which card? \n')
        logging.info('Which card? ')
        logging.info(term)
        if term in self.flashcards:
            self.flashcards.pop(term)
            self.error_count.pop(term)
            message = 'The card has been removed.'
            print(message)
            logging.info(message)
        else:
            message = f'Can\'t remove "{term}": there is no such card.'
            print(message)
            logging.info(message)

    def import_flashcards(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                data = file.read()
            try:
                flashcards = json.loads(data[:data.index('}') + 1])
                error_count = json.loads(data[data.index('}') + 1:])
                self.flashcards.update(flashcards)
                self.term_definition_dict = {v: k for k, v in self.flashcards.items()}
                self.error_count.update(error_count)
                message = f'{len(flashcards)} cards have been loaded.'
                print(message)
                logging.info(message)
            except json.JSONDecodeError as e:
                message = 'Invalid JSON data.'
                print(message)
                logging.info(message)
        else:
            message = 'File not found.'
            print(message)
            logging.info(message)

    def export_flashcards(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.flashcards, file)
            json.dump(self.error_count, file)
        message = f'{len(self.flashcards)} cards have been saved.'
        print(message)
        logging.info(message)

    def ask_flashcards(self):
        if not self.flashcards:
            message = 'No cards to ask.'
            print(message)
            logging.info(message)
            return

        times = int(input('How many times to ask? \n'))
        logging.info(str(times))
        for _ in range(times):
            term, definition = random.choice(list(self.flashcards.items()))
            user_input = input(f'Print the definition of "{term}": \n')
            logging.info(user_input)

            if user_input == definition:
                message = 'Correct!'
                print(message)
                logging.info(message)
            elif user_input in self.term_definition_dict:
                correct_term = self.term_definition_dict[user_input]
                message = f'Wrong. The right answer is "{definition}", but your definition is correct for "{correct_term}".'
                print(message)
                logging.info(message)

                if term in self.error_count:
                    self.error_count[term] += 1
                else:
                    self.error_count[term] = 1
            else:
                message = f'Wrong. The right answer is "{definition}".'
                print(message)
                logging.info(message)

                if term in self.error_count:
                    self.error_count[term] += 1
                else:
                    self.error_count[term] = 1

            self.errors.append(term)

    def logs(self):
        filename = input('File name: \n')
        logging.info(filename)
        with open("flashcard_log.log", "r") as f:
            a = []
            for i in f:
                a.append(i)
            with open(filename, 'w') as file:
                for i in a:
                    file.write(i)
        message = 'The log has been saved.'
        print(message)
        logging.info(message)

    def hardest_card(self):
        if not self.error_count or all(value == 0 for value in self.error_count.values()):
            message = 'There are no cards with errors.'
            print(message)
            logging.info(message)
        else:
            max_error = max(self.error_count.values())
            hardest_cards = [term for term, count in self.error_count.items() if count == max_error]

            if len(hardest_cards) == 1:
                message = f'The hardest card is "{hardest_cards[0]}". You have {max_error} errors answering it.'
            else:
                terms = ', '.join([f'"{term}"' for term in hardest_cards])
                message = f'The hardest cards are {terms}. You have {max_error} errors answering them.'

            print(message)
            logging.info(message)

    def reset_stats(self):
        for key in self.error_count.keys():
            self.error_count[key] = 0
        message = 'Card statistics have been reset.'
        print(message)
        logging.info(message)


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--import_from')
        parser.add_argument('--export_to')
        args = parser.parse_args()
        flashcard_game = FlashCards(args.import_from, args.export_to)
        flashcard_game.flashcard_operations()
    except IndexError:
        flashcard_game = FlashCards()
        flashcard_game.flashcard_operations()
        