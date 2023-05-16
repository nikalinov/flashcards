from random import randrange
import sys
from io import StringIO
import argparse


class Flashcard:
    """
    The Flashcard class. Methods: initializer, simple getters,
    and increment/reset the number of errors made by a user.
    """
    def __init__(self, term, definition, errors=0):
        """
        Initialize a Flashcard instance.

        parameters:
        term -- the term of a card
        definition -- the definition of a card
        errors -- the number of errors made by a user
        """
        self.term = term
        self.definition = definition
        self.errors = errors

    def add_error(self):
        self.errors += 1

    def get_term(self):
        return self.term

    def get_definition(self):
        return self.definition

    def get_errors(self):
        return self.errors

    def reset_errors(self):
        self.errors = 0


class FlashcardManager:
    """
    The FlashcardManager class, used for flashcards practicing.
    """
    def __init__(self):
        self.final_export = False
        self.flashcards = []
        self.commands = {
            "add": self.add_flashcard,
            "remove": self.remove_card,
            "import": self.import_cards,
            "export": self.export_cards,
            "ask": self.test_knowledge,
            "exit": self.exit,
            "log": self.log,
            "hardest card": self.print_hardest,
            "reset stats": self.reset_stats
        }
        # initialize I/O logging
        self.file_log = StringIO()
        sys.stdout = LoggerOut(self.file_log)
        sys.stdin = LoggerIn(self.file_log)

    def add_flashcard(self):
        print(f"The card:")
        while True:
            term = input()
            if term not in [card.get_term() for card in self.flashcards]:
                break
            print(f"The term \"{term}\" already exists. Try again:")

        print(f"The definition of {term}:")
        while True:
            definition = input()
            if definition not in [card.get_definition() for card in self.flashcards]:
                print(f"The pair (\"{term}\":\"{definition}\") has been added")
                break
            print(f"The definition \"{definition}\" already exists. Try again:")
        self.flashcards.append(Flashcard(term, definition))

    def remove_card(self):
        term = input("Which card?\n")
        terms = [card.get_term() for card in self.flashcards]
        if term in terms:
            self.flashcards.pop(terms.index(term))
            print("The card has been removed.")
        else:
            print(f"Can't remove \"{term}\": there is no such card.")

    def import_cards(self, import_from=None):
        if not import_from:
            file_name = input("File name:\n")
        else:
            file_name = import_from
        try:
            with open(file_name) as f:
                n = 0
                for line in f:
                    term, definition, errors = line.rstrip('\n').split(',')
                    terms = [card.get_term() for card in self.flashcards]
                    new_card = Flashcard(term, definition, int(errors))
                    if term in terms:
                        self.flashcards[terms.index(term)] = new_card
                    else:
                        self.flashcards.append(new_card)
                    n += 1
                print(f"{n} cards have been loaded.")
        except FileNotFoundError:
            print("File not found.")

    def export_cards(self, export_to=None):
        if not export_to:
            file_name = input("File name:\n")
        else:
            file_name = export_to
        try:
            with open(file_name, 'w') as f:
                n = 0
                for card in self.flashcards:
                    f.write(card.get_term() + ',' + card.get_definition() +
                                              ',' + str(card.get_errors()) + '\n')
                    n += 1
                print(f"{n} cards have been saved.")
        except FileNotFoundError:
            print("File not found.")

    def test_knowledge(self):
        for i in range(int(input("How many times to ask?"))):
            # get a random index and the corresponding card
            rand_i = randrange(len(self.flashcards))
            card = self.flashcards[rand_i]
            answer = input(f"Print the definition of \"{card.get_term()}\":\n")
            definitions = [card.get_definition() for card in self.flashcards]
            # if answer is not the definition but consists in the list of definitions,
            # get such a definition's index and find the corresponding term
            if answer != card.get_definition() and answer in definitions:
                ans_index = definitions.index(answer)
                another_term = self.flashcards[ans_index].get_term()
                print(f"Wrong. The right answer is \"{card.get_definition()}\", "
                      f"but your definition is correct for \"{another_term}\".")
                self.flashcards[rand_i].add_error()
            elif answer != card.get_definition():
                print(f"Wrong. The right answer is \"{card.get_definition()}\".")
                self.flashcards[rand_i].add_error()
            else:
                print("Correct!")

    def exit(self):
        if self.final_export:
            self.export_cards(self.final_export)
        print("Bye bye!")

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--import_from")
        parser.add_argument("--export_to")
        args = parser.parse_args()
        if args.import_from:
            self.import_cards(args.import_from)
        if args.export_to:
            self.final_export = args.export_to

    def log(self):
        file_name = input("File name:")
        with open(file_name, 'w') as file:
            file.write(self.file_log.getvalue())
        print("The log has been saved.")

    def print_hardest(self):
        max_error = max([card.get_errors() for card in self.flashcards], default=0)
        if not max_error:
            print("There are no cards with errors.")
            return
        hardest_cards = [card for card in self.flashcards
                         if card.get_errors() == max_error]
        if len(hardest_cards) == 1:
            card = hardest_cards[0]
            print(f"The hardest card is \"{card.get_term()}\". You have "
                  f"{card.get_errors()} errors answering it")
        else:
            print(f"The hardest cards are "
                  f"{', '.join([card.get_term() for card in hardest_cards])}."
                  f" You have {max_error} errors answering them")

    def reset_stats(self):
        self.flashcards.clear()
        print("Card statistics have been reset.")


class LoggerOut:
    def __init__(self, file_log):
        self.terminal = sys.stdout
        self.file_log = file_log

    def flush(self):
        pass

    def write(self, message):
        self.terminal.write(message)
        print(message, file=self.file_log, flush=True)


class LoggerIn:
    def __init__(self, file_log):
        self.terminal = sys.stdin
        self.file_log = file_log

    def flush(self):
        pass

    def readline(self):
        entry = self.terminal.readline()
        print(entry.rstrip(), file=self.file_log, flush=True)
        return entry


def main():
    flashcard_manager = FlashcardManager()
    flashcard_manager.parse_args()
    cmd = ""
    while cmd != "exit":
        cmd = input("Input the action (add, remove, import, export, ask, "
                    "exit, log, hardest card, reset stats):\n")
        if cmd in flashcard_manager.commands:
            flashcard_manager.commands[cmd]()


if __name__ == "__main__":
    main()
