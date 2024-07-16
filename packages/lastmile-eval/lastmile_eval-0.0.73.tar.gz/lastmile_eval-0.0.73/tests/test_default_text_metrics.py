from typing import Any

import numpy as np
from phoenix.evals import OpenAIModel

import lastmile_eval.text as text_metrics
from lastmile_eval.text.metrics import (
    _calculate_human_vs_ai_score_helper,  # type:ignore[private import ok for test]
)
from lastmile_eval.text.metrics import (
    _calculate_qa_score_helper,  # type:ignore[private import ok for test]
)
from lastmile_eval.text.metrics import (
    _calculate_relevance_score_helper,  # type:ignore[private import ok for test]
)
from lastmile_eval.text.metrics import (
    _calculate_summarization_score_helper,  # type:ignore[private import ok for test]
)
from lastmile_eval.text.metrics import (
    _calculate_toxicity_score_helper,  # type:ignore[private import ok for test]
)


def test_calculate_bleu_score_with_similar_sentences():
    # Example data
    predictions = [
        "The quick brown fox jumps over the lazy dog.",
    ]

    references = ["The swift brown fox leaps over the lazy dog."]

    response = text_metrics.calculate_bleu_score(predictions, references)

    assert response == [0.4671379777282001]


def test_calculate_rouge_score_with_similar_sentences():
    # Example data
    predictions = [
        "The quick brown fox jumps over the lazy dog.",
    ]

    references = [
        [
            "The swift brown fox leaps over the lazy dog."
        ],  # Slightly different wording
    ]

    response = text_metrics.calculate_rouge1_score(predictions, references)

    np.isclose(response, np.array([0.777777]))


def test_calculate_bleu_score_with_exact_and_no_match_sentences():
    # Example data
    predictions = [
        "the quick brown fox jumps over the lazy dog",
        "the quick brown fox jumps over the lazy dog",
        "foo baz",
    ]
    references = [
        "the swift brown fox jumps over the lazy dog",
        "the quick brown fox jumps over the lazy dog",
        "foo bar",
    ]

    response = text_metrics.calculate_bleu_score(predictions, references)

    assert np.isclose(response, np.array([0.75062, 1.0, 0.0])).all()


def test_calculate_exact_match_score():
    # Example data
    predictions = [
        "hello there general kenobi",
        "foo bar foobar",
        "foo bar foobar",
    ]
    references = [
        "hello there general kenobi",
        "foo bar foobar",
        "foo bar foobar!",
    ]

    response = text_metrics.calculate_exact_match_score(
        predictions, references
    )

    assert response == [1.0, 1.0, 0.0]


def _make_mock_phoenix_openai_model(fn_async_gen):  # type:ignore[fixme]
    class _MockPhoenixOpenaiModel(OpenAIModel):
        def __init__(self):
            super().__init__(api_key="mock")

        async def _async_generate(self, prompt: str, **kwargs: Any) -> str:
            return await fn_async_gen(prompt, **kwargs)  # type:ignore[fixme]

    return _MockPhoenixOpenaiModel()


def test_phoenix_arize_eval_relevance():
    # Retrieved from wiki_qa-train dataset
    predictions = [
        "what year lord of rings made?",
        "how an outdoor wood boiler works?",
    ]
    references = [
        """The Lord of the Rings is an epic high fantasy novel written by English philologist and University of Oxford professor J. R. R. Tolkien . The story began as a sequel to Tolkien's 1937 children's fantasy novel The Hobbit , but eventually developed into a much larger work. It was written in stages between 1937 and 1949, much of it during World War II . It is the second best-selling novel ever written , with over 150 million copies sold. The title of the novel refers to the story's main antagonist , the Dark Lord Sauron , who had in an earlier age created the One Ring to rule the other Rings of Power as the ultimate weapon in his campaign to conquer and rule all of Middle-earth . From quiet beginnings in the Shire , a Hobbit land not unlike the English countryside, the story ranges across north-west Middle-earth, following the course of the War of the Ring through the eyes of its characters, notably the hobbits Frodo Baggins , Samwise "Sam" Gamgee , Meriadoc "Merry" Brandybuck and Peregrin "Pippin" Took , but also the hobbits' chief allies and travelling companions: Aragorn , a Human Ranger ; Boromir , a man from Gondor ; Gimli , a Dwarf warrior; Legolas , an Elven prince; and Gandalf , a Wizard. The work was initially intended by Tolkien to be one volume of a two-volume set, with the other being The Silmarillion , but this idea was dismissed by his publisher. It was decided for economic reasons to publish The Lord of the Rings as three volumes over the course of a year from 29 July 1954 to 20 October 1955, thus creating the now familiar Lord of the Rings trilogy. The three volumes were entitled The Fellowship of the Ring , The Two Towers , and The Return of the King . Structurally, the novel is divided internally into six books, two per volume, with several appendices of background material included at the end of the third volume. The Lord of the Rings has since been reprinted numerous times and translated into many languages . Tolkien's work has been the subject of extensive analysis of its themes and origins. Although a major work in itself, the story was only the last movement of a larger epic Tolkien had worked on since 1917, in a process he described as mythopoeia . Influences on this earlier work, and on the story of The Lord of the Rings, include philology, mythology, religion and the author's distaste for the effects of industrialization, as well as earlier fantasy works and Tolkien's experiences in World War I . The Lord of the Rings in its turn is considered to have had a great effect on modern fantasy; the impact of Tolkien's works is such that the use of the words "Tolkienian" and "Tolkienesque" have been recorded in the Oxford English Dictionary . The enduring popularity of The Lord of the Rings has led to numerous references in popular culture, the founding of many societies by fans of Tolkien's works , and the publication of many books about Tolkien and his works. The Lord of the Rings has inspired, and continues to inspire , artwork, music, films and television, video games , and subsequent literature. Award-winning adaptations of The Lord of the Rings have been made for radio , theatre , and film . """,
        "The outdoor wood boiler is a variant of the classic wood stove adapted for set-up outdoors while still transferring the heat to interior buildings.",
    ]

    async def _fn_async_gen(prompt: str, **kwargs: Any) -> str:
        return "Relevant" if "lord of rings" in prompt.lower() else "0"

    mock_openai_model = _make_mock_phoenix_openai_model(_fn_async_gen)

    response = _calculate_relevance_score_helper(
        predictions,
        references,
        "gpt-4",
        mock_openai_model,  # type:ignore[fixme]
    )

    assert response == [1.0, 0.0]


def test_phoenix_arize_eval_toxicity():
    # Retrieved from wiki_qa-train dataset
    texts = ["i love you", "i hate you"]

    async def _fn_async_gen(prompt: str, **kwargs: Any) -> str:
        return "toxic" if "i hate you" in prompt.lower() else "non-toxic"

    mock_openai_model = _make_mock_phoenix_openai_model(_fn_async_gen)

    response = _calculate_toxicity_score_helper(
        texts,
        "gpt-4",
        mock_openai_model,  # type:ignore[fixme]
    )

    assert response == [0.0, 1.0]


def test_phoenix_arize_eval_qa():
    # Retrieved from wiki_qa-train dataset
    answers = ["blue"]
    questions = ["what color is the sky?"]
    references = ["the sky is blue"]

    async def _fn_async_gen(prompt: str, **kwargs: Any) -> str:
        return "correct"

    mock_openai_model = _make_mock_phoenix_openai_model(_fn_async_gen)

    response = _calculate_qa_score_helper(
        answers,
        references,
        questions,
        "gpt-4",
        mock_openai_model,  # type:ignore[fixme]
    )

    assert response == [1.0]


def test_phoenix_arize_eval_summarization():
    # Retrieved from wiki_qa-train dataset
    texts = ["the quick brown fox jumps over the lazy dog"]
    references = ["animal moves"]

    async def _fn_async_gen(prompt: str, **kwargs: Any) -> str:
        return "good"

    mock_openai_model = _make_mock_phoenix_openai_model(_fn_async_gen)

    response = _calculate_summarization_score_helper(
        texts,
        references,
        "gpt-4",
        mock_openai_model,  # type:ignore[fixme]
    )

    assert response == [1.0]


def test_phoenix_arize_eval_human_vs_ai():
    # Retrieved from wiki_qa-train dataset
    answers = ["blue"]
    questions = ["what color is the sky?"]
    references = ["the sky is blue"]

    async def _fn_async_gen(prompt: str, **kwargs: Any) -> str:
        return "correct"

    mock_openai_model = _make_mock_phoenix_openai_model(_fn_async_gen)

    response = _calculate_human_vs_ai_score_helper(
        answers,
        references,
        questions,
        "gpt-4",
        mock_openai_model,  # type:ignore[fixme]
    )

    assert response == [1.0]
