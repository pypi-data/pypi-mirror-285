# multi-modal intergration of real-time patient interactions with tabular embedding alignment (TEA)

from blacktea import TEA 

class InteractionAgent():
    '''The agent that interacts with the patient'''
    def __init__(self, model, external_database, **kwargs):
        self.agent = model
        self.kwargs = kwargs
        self.personalized_agent = {}
        self.external_database = external_database

    def initialize_personalized_agent(self, patient):
        '''Initialize personalized agent re: a particular patient'''
        self.personalized_agent[patient] = self.agent(patient, **self.kwargs)
        return self.personalized_agent[patient]
    
    def get_agent(self, patient):
        '''Get the agent for the patient'''
        return self.personalized_agent[patient]
    
    def interact(self, patient, input):
        '''Interact with the patient'''
        return self.personalized_agent[patient].interact(input)
    
    def tea_augment(self, patient, input):
        '''Augment the input with TEA'''
        context = TEA(self.external_database)
        self.personalized_agent[patient].augment(context)

    def get_all_agents(self):
        '''Get all agents'''
        return self.personalized_agent
    
    def augment(self):
        '''Augment the agent with external data'''
        #TODO set a default case
        pass
    
    def __str__(self):
        return "InteractionAgent"
    
    def __repr__(self):

    
