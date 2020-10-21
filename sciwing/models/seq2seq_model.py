import torch.nn as nn
from typing import Dict, List
import torch
from sciwing.modules.lstm2seqdecoder import Lstm2SeqDecoder
from sciwing.data.datasets_manager import DatasetsManager
from torch.nn import CrossEntropyLoss
from torch.nn.functional import softmax
from sciwing.data.seq_label import SeqLabel
from sciwing.data.line import Line
from sciwing.utils.class_nursery import ClassNursery


class Seq2SeqModel(nn.Module, ClassNursery):
    """PyTorch module for sequence to sequence module"""

    def __init__(
        self,
        rnn2seqencoder: nn.Module,
        rnn2seqdecoder: nn.Module,
        datasets_manager: DatasetsManager,
        enc_hidden_dim: int,
        bidirectional: bool,
        # vocab_size: int,
        device: torch.device = torch.device("cpu"),
        label_namespace: str = "tokens",
        vocab_namespace: str = "shared_tokens",
    ):
        """

        Parameters
        ----------
        rnn2seqencoder : nn.Module
            Encoder module to convert the input embedding to a set of hidden state or a vector
        rnn2seqdecoder : nn.Module
            Decoder module with or without attention
        encoding_dim : int
            Hidden dimension of the lstm2seq encoder
        vocab_size : int
            The size of the output label space
        """
        super(Seq2SeqModel, self).__init__()
        self.rnn2seqencoder = rnn2seqencoder
        self.rnn2seqdecoder = rnn2seqdecoder
        self.enc_hidden_dim = enc_hidden_dim
        self.device = device
        self.label_namespace = label_namespace
        self.vocab_namespace = vocab_namespace
        self.datasets_manager = datasets_manager

        self.vocabulary = self.datasets_manager.namespace_to_vocab[self.vocab_namespace]
        self.vocab_size = self.vocabulary.get_vocab_len()
        self.dec_hidden_dim = self.enc_hidden_dim * 2 if bidirectional else self.enc_hidden_dim

        self._loss = CrossEntropyLoss()
        self.linear_proj = nn.Linear(self.dec_hidden_dim, self.vocab_size)

    def forward(
        self,
        lines: List[Line],
        labels: List[Line] = None,
        is_training: bool = False,
        is_validation: bool = False,
        is_test: bool = False,
    ):
        """
        Parameters
        ----------
        lines : List[lines]
            A list of lines
        labels: List[Line]
            A list of sequence labels
        is_training : bool
            running forward on training dataset?
        is_validation : bool
            running forward on validation dataset ?
        is_test : bool
            running forward on test dataset?

        Returns
        -------
        Dict[str, Any]
            logits: torch.FloatTensor
                Un-normalized probabilities over all the classes
                of the shape ``[batch_size, num_classes]``
            predicted_tags: List[List[int]]
                Set of predicted tags for the batch
            loss: float
                Loss value if this is a training forward pass
                or validation loss. There will be no loss
                if this is the test dataset
        """

        # batch size, max_num_word_tokens, hidden_dim
        encoding = self.rnn2seqencoder(lines=lines)
        dec_output = self.rnn2seqdecoder(lines=labels)
        max_time_steps = dec_output.size(1)
        print(dec_output.size()) # 2, 2, 200

        output_dict = {}

        # batch size, time steps, num_classes
        namespace_logits = self.linear_proj(dec_output)
        print(namespace_logits.size()) # 2, 2, 28
        normalized_probs = softmax(namespace_logits, dim=2)
        print(normalized_probs.size())

        batch_size, time_steps, _ = namespace_logits.size()
        print(batch_size, time_steps)
        output_dict[f"logits_{self.vocab_namespace}"] = namespace_logits
        output_dict["normalized_probs"] = normalized_probs
        predicted_tags = torch.topk(namespace_logits, k=1, dim=2)
        print(len(predicted_tags))

        # gets the max element indices and flattens it to get List[List[int]]
        predicted_tags = predicted_tags.indices.flatten(start_dim=1).tolist()
        output_dict[f"predicted_tags_{self.vocab_namespace}"] = predicted_tags

        print("labels: ", len(labels))

        labels_indices = []
        if is_training or is_validation:
            for label in labels:

                numericalizer = self.datasets_manager.namespace_to_numericalizer[
                    self.vocab_namespace
                ]
                label_ = label.tokens[self.label_namespace]
                print(self.label_namespace)
                label_ = [tok.text for tok in label_]
                print(label_)
                print(self.vocab_size)
                label_instances = numericalizer.numericalize_instance(instance=label_)
                print(label_instances)
                label_instances = numericalizer.pad_instance(
                    numericalized_text=label_instances,
                    max_length=max_time_steps,
                    add_start_end_token=False,
                )
                print(label_instances)
                label_instances = torch.tensor(
                    label_instances, dtype=torch.long, device=self.device
                )
                labels_indices.append(label_instances)
                print(labels_indices)

            # batch_size, num_steps
            labels_tensor = torch.stack(labels_indices)
            print(labels_tensor.size())
            print(batch_size * max_time_steps)
            loss = self._loss(
                input=normalized_probs.view(batch_size * max_time_steps, -1),
                target=labels_tensor.view(-1)
            )

            output_dict["loss"] = loss

        return output_dict
