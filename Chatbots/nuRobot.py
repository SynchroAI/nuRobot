from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import warnings

from Chatbots.policy import nuRobotPolicy
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core import utils
from rasa_core.actions import Action
from rasa_core.agent import Agent
from rasa_core.channels.console import ConsoleInputChannel
from rasa_core.events import SlotSet
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.policies.memoization import MemoizationPolicy

logger = logging.getLogger(__name__)


class ActionSuggest(Action):
    def name(self):
        return 'action_suggest'

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message("here's what I found:")
        dispatcher.utter_message(tracker.get_slot("matches"))
        dispatcher.utter_message("is it ok for you? "
                                 "hint: I'm not going to "
                                 "find anything else :)")
        return []


def train_nlu(project='Lambton'):
    from rasa_nlu.training_data import load_data
    from rasa_nlu.config import RasaNLUModelConfig
    from rasa_nlu.model import Trainer
    from rasa_nlu import config

    training_data = load_data('../Chatbots/projects/'+project+'/intents')
    #training_data = load_data('projects/' + project + '/intents')
    #trainer = Trainer(config.load('../Chatbots/projects/' + project + '/config_spacy_tensor.yml'))
    #trainer = Trainer(config.load('../Chatbots/projects/'+project+'/config_spacy.yml'))
    trainer = Trainer(config.load('../Chatbots/projects/' + project + '/config_mitie.yml'))
    #trainer = Trainer(config.load('../Chatbots/projects/' + project + '/config_tensorflow.yml'))
    trainer.train(training_data)
    model_directory = trainer.persist('../Chatbots/projects/'+project+'/models/nlu/', fixed_model_name="current")

    return model_directory


def train_dialogue(project='Lambton'):

    domain_file='../Chatbots/projects/'+project+'/domain.yml'
    training_data_file="../Chatbots/projects/"+project+"/stories/stories.md"
    model_path="../Chatbots/projects/"+project+"/models/dialogue"

    agent = Agent(domain_file, policies=[MemoizationPolicy(max_history=3), nuRobotPolicy()])

    training_data = agent.load_data(training_data_file)
    
    agent.train(
            training_data,
            max_training_samples=300,
            epochs=300,
            batch_size=33,
            validation_split=0.2
    )

    agent.persist(model_path)
    return agent


def train_online(project='Lambton'):
    domain_file="../Chatbots/projects/"+project+"/domain.json",
    model_path="../Chatbots/projects/"+project+"models/dialogue",
    #training_data_file="projects/"+project+"/stories/stories.md"
    training_data_file="../Chatbots/projects/"+project+"/stories/stories.md"
    
    agent = Agent(domain_file, policies=[MemoizationPolicy(), nuRobotPolicy()])

    agent.train_online(training_data_file,
                       input_channel=ConsoleInputChannel(),
                       max_history=3,
                       batch_size=50,
                       epochs=200,
                       max_training_samples=300)

    agent.persist(model_path)
    return agent


def load_model(project='Lambton'):
    interpreter = RasaNLUInterpreter("../Chatbots/projects/"+project+"/models/nlu/default/current")
    agent = Agent.load("../Chatbots/projects/"+project+"/models/dialogue", interpreter=interpreter)
    return agent


def process_input(agent, serve_forever=True, message='Hi'):
    
    if serve_forever:
        output = agent.handle_message(message)
        
    return output, agent


def testbot(project='Lambton', serve_forever=True):
    interpreter = RasaNLUInterpreter("../Chatbots/projects/"+project+"/models/nlu/default/current")
    agent = Agent.load("../Chatbots/projects/"+project+"/models/dialogue", interpreter=interpreter)

    if serve_forever:
        agent.handle_channel(ConsoleInputChannel())

    return agent


def respond(project='Lambton', message=""):
    interpreter = RasaNLUInterpreter("../Chatbots/projects/"+project+"/models/nlu/default/current")
    agent = Agent.load("../Chatbots/projects/"+project+"/models/dialogue", interpreter=interpreter)

    output = agent.handle_message(message)
    
    return output, agent


if __name__ == '__main__':
    utils.configure_colored_logging(loglevel="INFO")

    parser = argparse.ArgumentParser(
            description='starts the bot')

    parser.add_argument(
            'task',
            choices=["train-nlu", "train-dialogue", "train-online", "test-bot", "respond"],
            help="what the bot should do - e.g. run or train?")

    parser.add_argument(
        'project',
        nargs='?',
        help="what the project you want to load")
    
    parser.add_argument(
        'message',
        nargs='?',
        help="input message you want to process")
        
    task = parser.parse_args().task
    project = parser.parse_args().project

    if project is None:
        project = 'Lambton'
        
    print("Selected task ", task)
    print("Selected project ", project)

    task = parser.parse_args().task


    # decide what to do based on first parameter of the script
    if task == "train-nlu":
        train_nlu(project)
    elif task == "train-dialogue":
        train_dialogue(project)
    elif task == "test-bot":
        testbot(project)
    elif task == "train-online":
        train_online(project)
    elif task == "respond":
        message = parser.parse_args().message
        if message:
            response, active_agent = respond(project, message)
            print("Response", response)
        else:
            warnings.warn("No input message to process")
    else:
        warnings.warn("Need to pass either 'train-nlu', 'train-dialogue' or "
                      "'run' to use the script.")
        exit(1)