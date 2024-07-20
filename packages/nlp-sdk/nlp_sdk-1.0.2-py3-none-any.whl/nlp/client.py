"""
/*******************************************************************************
 * Copyright (c) cortical.io GmbH. All rights reserved.
 *
 * This software is confidential and proprietary information.
 * You shall use it only in accordance with the terms of the
 * license agreement you entered into with cortical.io GmbH.
 ******************************************************************************/
"""

import httpx
import logging
from typing import Any, Dict

from nlp.models import SupportedLanguagesResponse, KeywordsRequest, KeywordsResponse, CompareRequest, \
    CompareResponse, LanguageDetectRequest, LanguageDetectResponse, LabelsRequest, LabelsResponse, SegmentationRequest, \
    SegmentationResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NLPClient:
    def __init__(self, api_key: str, base_url: str = "https://gw.cortical.io/nlp"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _get(self, endpoint: str) -> Any:
        try:
            response = httpx.get(f"{self.base_url}{endpoint}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTPStatusError: {e}")
            if e.response:
                logger.error(f"Response body: {e.response.text}")
            raise

    def _post(self, endpoint: str, data: Dict) -> Any:
        try:
            response = httpx.post(f"{self.base_url}{endpoint}", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTPStatusError: {e}")
            if e.response:
                logger.error(f"Response body: {e.response.text}")
            raise

    def get_supported_languages(self) -> SupportedLanguagesResponse:
        response = self._get("/supported-languages")
        return SupportedLanguagesResponse(**response)

    def extract_keywords(self, request: KeywordsRequest) -> KeywordsResponse:
        response = self._post("/keywords", request.model_dump())
        return KeywordsResponse(**response)

    def compare_texts(self, request: CompareRequest) -> CompareResponse:
        response = self._post("/compare", request.model_dump())
        return CompareResponse(**response)

    def detect_language(self, request: LanguageDetectRequest) -> LanguageDetectResponse:
        response = self._post("/language", request.model_dump())
        return LanguageDetectResponse(**response)

    def get_similar_terms(self, request: LabelsRequest) -> LabelsResponse:
        response = self._post("/labels", request.model_dump())
        return LabelsResponse(**response)

    def segment_text(self, request: SegmentationRequest) -> SegmentationResponse:
        response = self._post("/segmentation", request.model_dump())
        return SegmentationResponse(**response)
