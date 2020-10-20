import pytest
from sciwing.datasets.summarization.abstractive_text_summarization_dataset import (
    AbstractiveSummarizationDataset
)
from sciwing.tokenizers.word_tokenizer import WordTokenizer


@pytest.fixture(scope="session")
def test_file(tmpdir_factory):
    p = tmpdir_factory.mktemp("data").join("test.txt")
    p.write("line1###label1\nline2###label2")
    return p


class TestAbstractSummarizationDataset:
    def test_get_lines_labels(self, test_file):
        classification_dataset = AbstractiveSummarizationDataset(
            filename=str(test_file), tokenizers={"tokens": WordTokenizer()}
        )
        lines = classification_dataset.lines
        assert len(lines) == 2

    def test_len_dataset(self, test_file):
        classification_dataset = AbstractiveSummarizationDataset(
            filename=str(test_file), tokenizers={"tokens": WordTokenizer()}
        )
        assert len(classification_dataset) == 2

    def test_get_item(self, test_file):
        classification_dataset = AbstractiveSummarizationDataset(
            filename=str(test_file), tokenizers={"tokens": WordTokenizer()}
        )
        num_instances = len(classification_dataset)
        defined_line_tokens = ["line1", "line2"]
        defined_label_tokens = ["label1", "label2"]
        line_tokens = []
        label_tokens = []
        for idx in range(num_instances):
            line, label = classification_dataset[idx]
            line_tokens.extend(line.tokens["tokens"])
            label_tokens.extend(label.tokens["tokens"])

        line_tokens = list(map(lambda token: token.text, line_tokens))
        label_tokens = list(map(lambda token: token.text, label_tokens))

        assert set(defined_line_tokens) == set(line_tokens)
        assert set(defined_label_tokens) == set(label_tokens)