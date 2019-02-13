import train_app_utils as utils
import argparse
import logging
import datetime
import time
import os
import keras

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

def setup_logger(name, log_file=None, level=logging.INFO):
    """Function to setup as many loggers as you want"""

    if log_file is not None:
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def main(epochs, sentences, generate, temperature, verbose=False):
    #Create log directory for job run
    job_start_time = time.strftime("%Y%m%d_%H%M%S")
    data_directory = "output_data_" + job_start_time
    utils.nice_mk_dir(data_directory)

    #Define the loggers
    config_logger = setup_logger('config_logger', data_directory + '/config.log')
    training_logger = setup_logger('training_logger', data_directory + '/training.log')
    testing_logger = setup_logger('testing_logger', data_directory + '/testing.log')
    console_logger = setup_logger('console_logger')

    #Set the command line arguments 
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    num_epochs = epochs
    create_str_len = generate
    my_data = utils.Nietzche_Data()
    mdl = utils.sl_lstm_model(my_data.chars, my_data.maxlen)

    if sentences is not None:
        if sentences > my_data.len_sentences:
            config_logger.error('Optional argument {} was set to {}. However this is outside '\
                    'of the range 0 - {}.'.format('Sentences', sentences, my_data.len_sentences))
            data_size = my_data.len_sentences
            config_logger.info('Optional argument {} was set to {}'.format('Sentences',sentences))
        else:
            config_logger.info('Optional argument {} has been set. '\
                    'The value is: {}'.format('Sentences', sentences))
            data_size = sentences
    else:
        data_size = my_data.len_sentences

#    temperature = [0.2, 0.5, 1.0, 1.2]

    config_logger.info('Number of Epochs: {}'.format(str(epochs)))
    console_logger.info('Number of Epochs: {}'.format(str(epochs)))
    config_logger.info('Data Size: {}'.format(str(data_size)))
    console_logger.info('Data Size: {}'.format(str(data_size)))
    config_logger.info('String Length to create: {}'.format(str(create_str_len)))
    console_logger.info('String Length to create: {}'.format(str(create_str_len)))

    training_logger.info(['Job_Start_Time', 'Create_String_Len', 'Data_Size', 'Epoch_Num',\
        'Epoch_tm', 'Model_tm','SeedGen_tm', 'temp0.2_tm','temp0.5_tm','temp1.0_tm', 'temp1.2_tm'])

    #Setup the number of 'tests' to generate text
    gen_after_epoch_num = 5
    epoch_num_list = range(0, num_epochs - 1)
    epochs_to_test = list(filter(lambda x: x % (gen_after_epoch_num - 1) == 0, epoch_num_list))
    config_logger.info('Will genereate text after each of the following epochs: {}'.format(epochs_to_test))
    console_logger.info('Will genereate text after each of the following epochs: {}'.format(epochs_to_test))

    for epoch in range(num_epochs):
        training_logger.info('Training Epoch number: {}'.format(str(epoch)))
        console_logger.info('--------Training Epoch number: {}------'.format(str(epoch)))
        callbacks_list = [
            keras.callbacks.ModelCheckpoint(
                filepath=data_directory + '/my_model_{epoch}.h5'.format(epoch=epoch)
            )
        ]
        mdl.fit(my_data.x[0:data_size], my_data.y[0:data_size],
            batch_size=128,
            epochs=1,
            callbacks=callbacks_list,
            verbose=0
        )
        if epoch in epochs_to_test:
            #Generate Seed Text
            seed_text = utils.get_seed_text(my_data.text, my_data.maxlen)
            testing_logger.info('Seed Text: {}'.format(seed_text))
            console_logger.info('Seed Text: {}'.format(seed_text))
            #Generate Text
            for temp in temperature:
                generated_text = utils.generate_text(mdl, my_data.maxlen, my_data.chars,
                        my_data.char_indices, seed_text, temp, create_str_len)
                testing_logger.info('Generated Text: [Temp: {0}] {1}'.format(temp, generated_text))
                console_logger.info('Generated Text: [Temp: {0}] {1}'.format(temp, generated_text))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=\
            'Create a text generator based on the corpus of Fredriche Nietzsche writings')

    #Define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e","--epochs", help="number of epochs to train",default=60, type=int)
    parser.add_argument("-s", "--sentences", help="number of sentences to train; default is all", type=int)
    parser.add_argument("-g", "--generate", help="length of text to generate",default=400, type=int)
    parser.add_argument("-t", "--temperature", help="temperature is a measure of the output variability ",\
                    default=[0.2, 0.5, 0.8, 1.0])
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    
    args = parser.parse_args()
    
    main(args.epochs, args.sentences, args.generate, args.temperature)
