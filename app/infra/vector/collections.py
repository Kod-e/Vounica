from enum import Enum
from typing import Dict, Tuple

from qdrant_client.http.models import VectorParams, Distance

from app.core.vector.embeddings import EMBEDDING_DIMENSION


# Collection name definitions
class VectorCollection(str, Enum):
    """
    Enumerate all Qdrant collection names used in the project.
    """

    # Memory
    MEMORY_CONTENT = "memory_content"
    # Grammar
    GRAMMER_USAGE = "grammer_usage"
    # Vocabulary
    VOCAB_USAGE = "vocab_usage"

    # Mistake
    MISTAKE_QUESTION = "mistake_question"
    MISTAKE_ANSWER = "mistake_answer"
    MISTAKE_CORRECT_ANSWER = "mistake_correct_answer"
    MISTAKE_ERROR_REASON = "mistake_error_reason"

    # Story
    STORY_CONTENT = "story_content"
    STORY_SUMMARY = "story_summary"



# Collection config mapping
COLLECTIONS_CONFIG: Dict[VectorCollection, VectorParams] = {
    collection: VectorParams(size=EMBEDDING_DIMENSION, distance=Distance.COSINE)
    for collection in VectorCollection
}

# A key is (model_class.__name__, field_name)
MODEL_FIELD_TO_COLLECTION: Dict[Tuple[str, str], VectorCollection] = {
    # Memory
    ("Memory", "content"): VectorCollection.MEMORY_CONTENT,

    # Grammer
    ("Grammer", "usage"): VectorCollection.GRAMMER_USAGE,

    # Vocab
    ("Vocab", "usage"): VectorCollection.VOCAB_USAGE,
    # Mistake
    ("Mistake", "question"): VectorCollection.MISTAKE_QUESTION,
    ("Mistake", "answer"): VectorCollection.MISTAKE_ANSWER,
    ("Mistake", "correct_answer"): VectorCollection.MISTAKE_CORRECT_ANSWER,
    ("Mistake", "error_reason"): VectorCollection.MISTAKE_ERROR_REASON,

    # Story
    ("Story", "content"): VectorCollection.STORY_CONTENT,
    ("Story", "summary"): VectorCollection.STORY_SUMMARY,

} 