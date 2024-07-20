
# Python library for creating history-augmented interactive medical chatbots with tabular embedding alignment (TEA).

from blacktea import TEA
from models import TeaChatbotModel

class TeaChatbot():
    '''A chatbot that can be used to chat with the user.
    It references the dataset powered by the tabular 
    embedding alignment (TEA) model as knowledge bases
    for question answering and personalization.
    '''
    def __init__(self, chat_model, tea: TEA):
        '''Initialize the chatbot with the TEA model.
        '''
        self.tea = tea
        self.model = chat_model
        self.history = []
        self.context = None
        self.response = None
        self.personalization = None

    def chat(self, message: str):
        '''Chat with the user.
        '''
        self.history.append(message)
        self.context = self.chat_model.get_context(self.history, self.tea)
        self.response = self.chat_model.get_response(self.context)
        self.personalization = self.tea.get_personalization(self.context)
        return self.response, self.personalization
    
    def reset(self):
        '''Reset the chatbot.
        '''
        self.history = []
        self.context = None
        self.response = None
        self.personalization = None



