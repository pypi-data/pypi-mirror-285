import enum


class EmbeddingModel(enum.Enum):
    """
    Enum for supported embedding models. Used to specify the model used to generate embeddings for
    document and text indices.

    Attributes:
        ROBERTA: [RoBERTa](https://arxiv.org/abs/1907.11692) model
        SENTENCE_TRANSFORMER: [Sentence Transformer](https://sbert.net/) model
    """

    ROBERTA = "roberta"
    SENTENCE_TRANSFORMER = "sentence_transformer"
