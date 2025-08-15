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
    MEMORY_SUMMARY = "memory_summary"
    # Grammar
    GRAMMAR_USAGE = "grammar_usage"
    GRAMMAR_NAME = "grammar_name"
    # Vocabulary
    VOCAB_USAGE = "vocab_usage"
    VOCAB_NAME = "vocab_name"

    # Mistake
    MISTAKE_QUESTION = "mistake_question"
    MISTAKE_ANSWER = "mistake_answer"
    MISTAKE_CORRECT_ANSWER = "mistake_correct_answer"
    MISTAKE_ERROR_REASON = "mistake_error_reason"

    # Story
    STORY_CONTENT = "story_content"
    STORY_SUMMARY = "story_summary"
    STORY_CATEGORY = "story_category"


# Collection config mapping
COLLECTIONS_CONFIG: Dict[VectorCollection, VectorParams] = {
    collection: VectorParams(size=EMBEDDING_DIMENSION, distance=Distance.COSINE)
    for collection in VectorCollection
}

# A key is (model_class.__name__, field_name)
MODEL_FIELD_TO_COLLECTION: Dict[Tuple[str, str], VectorCollection] = {
    # Memory
    ("Memory", "content"): VectorCollection.MEMORY_CONTENT,
    ("Memory", "summary"): VectorCollection.MEMORY_SUMMARY,
    # Grammar
    ("Grammar", "usage"): VectorCollection.GRAMMAR_USAGE,
    ("Grammar", "name"): VectorCollection.GRAMMAR_NAME,
    # Vocab
    ("Vocab", "usage"): VectorCollection.VOCAB_USAGE,
    ("Vocab", "name"): VectorCollection.VOCAB_NAME,
    
    # Mistake
    ("Mistake", "question"): VectorCollection.MISTAKE_QUESTION,
    ("Mistake", "answer"): VectorCollection.MISTAKE_ANSWER,
    ("Mistake", "correct_answer"): VectorCollection.MISTAKE_CORRECT_ANSWER,
    ("Mistake", "error_reason"): VectorCollection.MISTAKE_ERROR_REASON,

    # Story
    ("Story", "content"): VectorCollection.STORY_CONTENT,
    ("Story", "summary"): VectorCollection.STORY_SUMMARY,
    ("Story", "category"): VectorCollection.STORY_CATEGORY,

} 