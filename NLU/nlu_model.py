from rasa_nlu.training_data import load_data
from rasa_nlu import config
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter


def train_nlu(data, configs, model_dir):
    training_data = load_data(data)
    trainer = Trainer(config.load(configs))
    trainer.train(training_data)
    model_directory = trainer.persist(model_dir, fixed_model_name='Lambton')
    print(model_directory)

def run_nlu():
    interpreter = Interpreter.load('./models/default/Lambton')
    print(interpreter.parse("I am planning to visit Lambton College to check MADT classes."))


if __name__ == '__main__':
    #train_nlu('./data/data.json', 'config_spacy.json', './models/')
    run_nlu()
