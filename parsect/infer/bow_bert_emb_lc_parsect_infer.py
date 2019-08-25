import json
import os
import parsect.constants as constants
from parsect.modules.embedders.bert_embedder import BertEmbedder
from parsect.modules.bow_encoder import BOW_Encoder
from parsect.models.simpleclassifier import SimpleClassifier
from parsect.datasets.classification.parsect_dataset import ParsectDataset
from parsect.infer.classification.classification_inference import (
    ClassificationInference,
)
import torch

PATHS = constants.PATHS
FILES = constants.FILES
OUTPUT_DIR = PATHS["OUTPUT_DIR"]
SECT_LABEL_FILE = FILES["SECT_LABEL_FILE"]


def get_bow_bert_emb_lc_parsect_infer(dirname: str):
    hyperparam_config_filepath = os.path.join(dirname, "config.json")
    with open(hyperparam_config_filepath, "r") as fp:
        config = json.load(fp)

    EMBEDDING_DIM = config["EMBEDDING_DIMENSION"]
    NUM_CLASSES = config["NUM_CLASSES"]
    BERT_TYPE = config["BERT_TYPE"]

    DEVICE = config["DEVICE"]
    EMBEDDING_TYPE = config.get("EMBEDDING_TYPE", "random")
    EMBEDDING_DIMENSION = config["EMBEDDING_DIMENSION"]
    MODEL_SAVE_DIR = config["MODEL_SAVE_DIR"]
    VOCAB_SIZE = config["VOCAB_SIZE"]
    MAX_NUM_WORDS = config["MAX_NUM_WORDS"]
    MAX_LENGTH = config["MAX_LENGTH"]
    vocab_store_location = config["VOCAB_STORE_LOCATION"]
    DEBUG = config["DEBUG"]
    DEBUG_DATASET_PROPORTION = config["DEBUG_DATASET_PROPORTION"]

    model_filepath = os.path.join(MODEL_SAVE_DIR, "best_model.pt")

    embedder = BertEmbedder(
        emb_dim=EMBEDDING_DIM,
        dropout_value=0.0,
        aggregation_type="average",
        bert_type=BERT_TYPE,
        device=torch.device(DEVICE),
    )

    encoder = BOW_Encoder(
        embedder=embedder, emb_dim=EMBEDDING_DIM, aggregation_type="average"
    )
    model = SimpleClassifier(
        encoder=encoder,
        encoding_dim=EMBEDDING_DIM,
        num_classes=NUM_CLASSES,
        classification_layer_bias=True,
    )

    dataset = ParsectDataset(
        filename=SECT_LABEL_FILE,
        dataset_type="test",
        max_num_words=MAX_NUM_WORDS,
        max_instance_length=MAX_LENGTH,
        word_vocab_store_location=vocab_store_location,
        debug=DEBUG,
        debug_dataset_proportion=DEBUG_DATASET_PROPORTION,
        word_embedding_type=EMBEDDING_TYPE,
        word_embedding_dimension=EMBEDDING_DIMENSION,
    )

    parsect_inference = ClassificationInference(
        model=model,
        model_filepath=model_filepath,
        hyperparam_config_filepath=hyperparam_config_filepath,
        dataset=dataset,
        dataset_class=ParsectDataset,
    )

    return parsect_inference


if __name__ == "__main__":
    experiment_dirname = os.path.join(
        OUTPUT_DIR, "debug_bow_bert_base_cased_emb_lc_10e_1e-2lr"
    )
    inference_client = get_bow_bert_emb_lc_parsect_infer(experiment_dirname)
