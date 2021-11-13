"""
Program for predicting similarity of two source code files by 
Bag or Tokens technique

History of traing is pickled to be plotted with other application

The programm processes all files in the given directory
Each file there contains all samples of one class of samples,
i.e. tokenised source code

Number of classes (lables) is defined automatically
"""
import sys
import os
import argparse
import pickle

main_dir = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
sys.path.extend([f"{main_dir}/Dataset",
                 f"{main_dir}/ModelMaker",
                 f"{main_dir}/PostProcessor",
                 f"{main_dir}/CommonFunctions"])

from ProgramArguments   import (makeArgParserCodeML, parseArguments)
from Utilities          import *
from BagTokSimilarityDS import BagTokSimilarityDS
from DsUtilities        import DataRand
from SeqModelMaker      import SeqModelFactory

def main(args):
    """
    Main function of program for predicting similarity of 
    two source code samples

    Parameters:
    - args  -- Parsed command line arguments
               as object returned by ArgumentParser
    """
    resetSeeds()
    DataRand.setDsSeeds(args.seed_ds)
    if args.ckpt_dir:
        _latest_checkpoint = setupCheckpoint(args.ckpt_dir)
        _checkpoint_callback = makeCkptCallback(args.ckpt_dir)
        _callbacks=[_checkpoint_callback]
    else:
        _latest_checkpoint = None
        _callbacks = None
    _ds = BagTokSimilarityDS(args.dataset,
                             min_n_solutions = args.min_solutions,
                             max_n_problems = args.problems,
                             short_code_th = args.short_code,
                             long_code_th = args.long_code,
                             test = args.testpart)

    _val_ds, _train_ds = \
        _ds.trainValidDsSameProblems(
            args.valpart, args.valsize, args.trainsize,
            args.similpart) if args.validation == "same" else \
        _ds.trainValidDsDifferentProblems(
            args.valpart, args.valsize, args.trainsize,
            args.similpart)

    _model_factory = SeqModelFactory(_ds.n_token_types * 2, 1)
    if _latest_checkpoint:
        print("Restoring from", _latest_checkpoint)
        _dnn = tf.keras.models.load_model(_latest_checkpoint)
    else:
        _dnn = _model_factory.denseDNN(args.dense)

    _history = _dnn.fit(_train_ds[0], _train_ds[1],
                        epochs = args.epochs, batch_size = args.batch,
                        validation_data = (_val_ds[0], _val_ds[1]),
                        verbose = args.progress, callbacks = _callbacks)

    with open(args.history, 'wb') as _jar:
        pickle.dump(_history.history, _jar)

################################################################################
# Args are described below
################################################################################
if __name__ == '__main__':
    print("\nCODE SIMILARITY WITH BAG OF TOKENS TECHNIQUE")

    #Handle command-line arguments
    parser = makeArgParserCodeML(
        "Bag of tokens source code similarity analysis",
        task = "similarity")
    args = parseArguments(parser)

    main(args)


