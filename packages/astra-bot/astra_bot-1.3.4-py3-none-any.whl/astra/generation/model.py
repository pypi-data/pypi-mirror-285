import markovify

from astra.connections import AstraDBConnection

class AstraMarkovModel:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            AstraDBConnection()
            cls._instance = super().__new__(cls)
            cls._instance.initialize_model()
        return cls._instance
        
    def initialize_model(self):
        all_quotes = AstraDBConnection.query_all()
        quotes = '\n'.join(all_quotes)
        self._model = markovify.NewlineText(quotes).compile()
        
    def make_sentence(self):
        return self._model.make_sentence()