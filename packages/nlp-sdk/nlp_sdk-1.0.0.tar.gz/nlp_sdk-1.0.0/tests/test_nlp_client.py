"""
/*******************************************************************************
 * Copyright (c) cortical.io GmbH. All rights reserved.
 *
 * This software is confidential and proprietary information.
 * You shall use it only in accordance with the terms of the
 * license agreement you entered into with cortical.io GmbH.
 ******************************************************************************/
"""

import unittest
from unittest.mock import patch, Mock
import httpx
from nlp import NLPClient
from nlp import (
    KeywordsRequest,
    KeywordsResponse,
    InputText,
    CompareRequest,
    CompareResponse,
    LanguageDetectRequest,
    LanguageDetectResponse,
    LabelsRequest,
    LabelsResponse,
    SegmentationRequest,
    SegmentationResponse,
    SupportedLanguagesResponse,
)
from nlp import TEXT, SEGMENTATION_TEXT


def mock_response(status_code=200, json_data=None):
    response = Mock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_data
    response.raise_for_status = Mock()
    response.is_error = False
    return response


class TestNLPClient(unittest.TestCase):

    def setUp(self):
        self.api_key = "fake_api_key"
        self.client = NLPClient(api_key=self.api_key)

        self.expected_responses = {
            "get_supported_languages": {
                "supported_languages": ["de", "en", "es", "fr"],
            },
            "extract_keywords": {
                "keywords": [
                    {
                        "word": "challenges",
                        "document_frequency": 0.0024654430301205,
                        "pos_tags": ["VERB", "NOUN"],
                        "score": 1.0
                    },
                    {
                        "word": "verticals",
                        "document_frequency": 1.8935955564849904e-05,
                        "pos_tags": ["NOUN"],
                        "score": 0.9053916009399887
                    },
                    {
                        "word": "based solutions",
                        "document_frequency": 2.0866319967091884e-05,
                        "pos_tags": ["VERB", "NOUN"],
                        "score": 0.8973093656839998
                    },
                    {
                        "word": "use cases",
                        "document_frequency": 3.796383324409229e-05,
                        "pos_tags": ["VERB", "NOUN"],
                        "score": 0.8474792799260732
                    },
                    {
                        "word": "major companies",
                        "document_frequency": 4.7983343712872086e-05,
                        "pos_tags": ["ADJECTIVE", "NOUN"],
                        "score": 0.8279784449831554
                    },
                    {
                        "word": "based approach",
                        "document_frequency": 9.274941342200751e-05,
                        "pos_tags": ["VERB", "NOUN"],
                        "score": 0.7731070613317652
                    },
                    {
                        "word": "natural language",
                        "document_frequency": 0.0001058942757801,
                        "pos_tags": ["ADJECTIVE", "NOUN"],
                        "score": 0.7620719779622283
                    },
                    {
                        "word": "streamline",
                        "document_frequency": 0.0001390781590758,
                        "pos_tags": ["VERB", "NOUN"],
                        "score": 0.7393761034391105
                    },
                    {
                        "word": "variability",
                        "document_frequency": 0.0003257719734069,
                        "pos_tags": ["NOUN"],
                        "score": 0.6685095583490221
                    }
                ],
                "language": "en"
            },
            "compare_texts": {
                "similarity": 0.8155339805825242,
                "languages": ["en", "en"]
            },
            "get_similar_terms": {
                "labels": [
                    {
                        "word": "need",
                        "document_frequency": 0.0112579771159896,
                        "pos_tags": [
                            "VERB",
                            "NOUN"
                        ]
                    },
                    {
                        "word": "ways",
                        "document_frequency": 0.0059745697470533,
                        "pos_tags": [
                            "NOUN"
                        ]
                    },
                    {
                        "word": "means",
                        "document_frequency": 0.0111743279918924,
                        "pos_tags": [
                            "VERB",
                            "NOUN"
                        ]
                    },
                    {
                        "word": "challenges",
                        "document_frequency": 0.0024654430301205,
                        "pos_tags": [
                            "VERB",
                            "NOUN"
                        ]
                    },
                    {
                        "word": "instance",
                        "document_frequency": 0.0040576259735126,
                        "pos_tags": [
                            "NOUN"
                        ]
                    },
                    {
                        "word": "change",
                        "document_frequency": 0.0147294157660214,
                        "pos_tags": [
                            "VERB",
                            "NOUN"
                        ]
                    },
                    {
                        "word": "others",
                        "document_frequency": 0.0205217039602344,
                        "pos_tags": [
                            "NOUN"
                        ]
                    },
                    {
                        "word": "context",
                        "document_frequency": 0.0039387706796031,
                        "pos_tags": [
                            "NOUN"
                        ]
                    },
                    {
                        "word": "fact",
                        "document_frequency": 0.0119330531240879,
                        "pos_tags": [
                            "NOUN"
                        ]
                    },
                    {
                        "word": "approach",
                        "document_frequency": 0.0076479199174539,
                        "pos_tags": [
                            "NOUN"
                        ]
                    }
                ],
                "language": "en"
            },
            "detect_language": {
                "language": "en"
            },
            "segment_text": {
                "segments": [
                    "Tigers mostly feed on large and medium-sized mammals, particularly ungulates weighing 60–250 kg (130–550 lb). Range-wide, the most selected prey are sambar deer, Manchurian wapiti, barasingha and wild boar. Tigers are capable of taking down larger prey like adult gaur and wild water buffalo, but opportunistically eat much smaller prey, such as monkeys, peafowl and other ground-based birds, hares, porcupines and fish. They also prey on other predators, including dogs, leopards, bears, snakes and crocodiles. Tiger attacks on adult Asian elephants and Indian rhinoceros have also been reported.",
                    "The Middle English tigre and Old English tigras derive from Old French tigre, from Latin tigris. This was a borrowing of Classical Greek 'tigris', a foreign borrowing of unknown origin meaning 'tiger' and the river Tigris. The origin may have been the Persian word tigra ('pointed or sharp') and the Avestan word tigrhi ('arrow'), perhaps referring to the speed of the tiger's leap, although these words are not known to have any meanings associated with tigers.",
                    "There are three other colour variants – white, golden and nearly stripeless snow white – that are now virtually non-existent in the wild due to the reduction of wild tiger populations, but continue in captive populations. The white tiger has white fur and sepia-brown stripes. The golden tiger has a pale golden pelage with a blond tone and reddish-brown stripes. The snow white tiger is a morph with extremely faint stripes and a pale reddish-brown ringed tail. Both snow white and golden tigers are homozygous for CORIN gene mutations."
                ],
                "language": "en"
            }
        }

        self.requests = {
            "extract_keywords": KeywordsRequest(
                text=TEXT,
                language="en"
            ),
            "compare_texts": CompareRequest(root=[
                InputText(text="organ", language="en"),
                InputText(text="piano", language="en")
            ]),
            "get_similar_terms": LabelsRequest(
                text=TEXT,
                language="en"
            ),
            "detect_language": LanguageDetectRequest(text="What language is this?"),
            "segment_text": SegmentationRequest(
                text=SEGMENTATION_TEXT,
                language="en"
            )
        }

    @patch('httpx.get')
    def test_get_supported_languages(self, mock_get):
        mock_get.return_value = mock_response(json_data=self.expected_responses["get_supported_languages"])

        response = self.client.get_supported_languages()

        mock_get.assert_called_once_with(
            f"{self.client.base_url}/supported-languages", headers=self.client.headers
        )
        self.assertIsInstance(response, SupportedLanguagesResponse)
        self.assertEqual(response.supported_languages,
                         self.expected_responses["get_supported_languages"]["supported_languages"])

    @patch('httpx.post')
    def test_extract_keywords(self, mock_post):
        mock_post.return_value = mock_response(json_data=self.expected_responses["extract_keywords"])

        response = self.client.extract_keywords(self.requests["extract_keywords"])

        mock_post.assert_called_once_with(
            f"{self.client.base_url}/keywords", headers=self.client.headers,
            json=self.requests["extract_keywords"].model_dump()
        )
        self.assertIsInstance(response, KeywordsResponse)
        self.assertEqual(response.language, self.expected_responses["extract_keywords"]["language"])
        self.assertEqual(len(response.keywords), len(self.expected_responses["extract_keywords"]["keywords"]))

        for i, keyword in enumerate(self.expected_responses["extract_keywords"]["keywords"]):
            self.assertEqual(response.keywords[i].word, keyword["word"])
            self.assertAlmostEqual(response.keywords[i].document_frequency, keyword["document_frequency"], places=7)
            self.assertEqual(response.keywords[i].pos_tags, keyword["pos_tags"])
            self.assertAlmostEqual(response.keywords[i].score, keyword["score"], places=7)

    @patch('httpx.post')
    def test_compare_texts(self, mock_post):
        mock_post.return_value = mock_response(json_data=self.expected_responses["compare_texts"])

        response = self.client.compare_texts(self.requests["compare_texts"])

        mock_post.assert_called_once_with(
            f"{self.client.base_url}/compare", headers=self.client.headers,
            json=[input_text.model_dump() for input_text in self.requests["compare_texts"].root]
        )
        self.assertIsInstance(response, CompareResponse)
        self.assertAlmostEqual(response.similarity, self.expected_responses["compare_texts"]["similarity"], places=7)
        self.assertEqual(response.languages, self.expected_responses["compare_texts"]["languages"])

    @patch('httpx.post')
    def test_get_similar_terms(self, mock_post):
        mock_post.return_value = mock_response(json_data=self.expected_responses["get_similar_terms"])

        response = self.client.get_similar_terms(self.requests["get_similar_terms"])

        mock_post.assert_called_once_with(
            f"{self.client.base_url}/labels", headers=self.client.headers,
            json=self.requests["get_similar_terms"].model_dump()
        )
        self.assertIsInstance(response, LabelsResponse)
        self.assertEqual(response.language, self.expected_responses["get_similar_terms"]["language"])
        self.assertEqual(len(response.labels), len(self.expected_responses["get_similar_terms"]["labels"]))

        for i, label in enumerate(self.expected_responses["get_similar_terms"]["labels"]):
            self.assertEqual(response.labels[i].word, label["word"])
            self.assertEqual(response.labels[i].document_frequency, label["document_frequency"])
            self.assertEqual(response.labels[i].pos_tags, label["pos_tags"])

    @patch('httpx.post')
    def test_detect_language(self, mock_post):
        mock_post.return_value = mock_response(json_data=self.expected_responses["detect_language"])

        response = self.client.detect_language(self.requests["detect_language"])

        mock_post.assert_called_once_with(
            f"{self.client.base_url}/language", headers=self.client.headers,
            json=self.requests["detect_language"].model_dump()
        )
        self.assertIsInstance(response, LanguageDetectResponse)
        self.assertEqual(response.language, self.expected_responses["detect_language"]["language"])

    @patch('httpx.post')
    def test_segment_text(self, mock_post):
        mock_post.return_value = mock_response(json_data=self.expected_responses["segment_text"])

        response = self.client.segment_text(self.requests["segment_text"])

        mock_post.assert_called_once_with(
            f"{self.client.base_url}/segmentation", headers=self.client.headers,
            json=self.requests["segment_text"].model_dump()
        )
        self.assertIsInstance(response, SegmentationResponse)
        self.assertEqual(response.language, self.expected_responses["segment_text"]["language"])
        self.assertEqual(len(response.segments), len(self.expected_responses["segment_text"]["segments"]))

        for i, segment in enumerate(self.expected_responses["segment_text"]["segments"]):
            self.assertEqual(response.segments[i], segment)


if __name__ == '__main__':
    unittest.main()
