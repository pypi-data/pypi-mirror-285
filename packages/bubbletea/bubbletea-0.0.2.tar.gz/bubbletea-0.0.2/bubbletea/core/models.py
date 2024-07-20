
# Python library for creating history-augmented interactive medical chatbots with tabular embedding alignment (TEA).

import torch

class TeaChatbotModel():
    '''A chatbot model that can be used to chat with the user.
    Example shown is a 2-layer neural net with LSTM in PyTorch'''
    def __init__(self):
        '''Initialize the chatbot model.
        '''
        model = torch.nn.Sequential(
            torch.nn.LSTM(300, 128, 2, batch_first=True),
            torch.nn.Linear(128, 300)
        )
        self.model = model
        self.optimizer = torch.optim.Adam(self.model.parameters())
        self.loss = torch.nn.CrossEntropyLoss()

    def get_context(self, history, tea):
        '''Get the context from the history.
        '''
        tea_context = tea.get_context(history)
        context = self.model.forward(tea_context,history)
        return context
    
    def get_response(self, context):
        '''Get the response from the context.
        '''
        # TODO correct this to a genearation engine
        response = model.forward(context)
        return response
    
    def train(self, history, tea):
        '''Train the model with the history.
        '''
        context = self.get_context(history, tea)
        response = self.get_response(context)
        loss = self.loss(response, context)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss
    
    def forward(tea_context, history):
        '''Forward pass of the model.
        '''
        tea_context = torch.tensor(tea_context)
        history = torch.tensor(history)
        context = torch.cat((tea_context, history), 1)
        context = self.model(context)
        return context
    


