# Interactive spoken language tools for communication

class CommunicationAgent():
    '''Base communication agent class that involves two
    parties for communication. It will take in one party's
    message, translate it into understandable information 
    for the other party, and give to the other party. And 
    vice versa, in a loop.'''
    def __init__(self, party1, party2):
        self.party1 = party1
        self.party2 = party2
        self.message = None
        self.translated_message = None
    
    def take_message(self, message):
        '''Take in one party's message'''
        self.message = message

    def translate_message(self):
        '''Translate the message into understandable information'''
        pass

    def give_message(self):
        '''Give the translated message to the other party'''
        pass

    def loop(self):
        '''The loop of communication'''
        while True:
            self.take_message(self.party1)
            self.translate_message()
            self.give_message()
            self.take_message(self.party2)
            self.translate_message()
            self.give_message()

        