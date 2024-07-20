"""
/*******************************************************************************
 * Copyright (c) cortical.io GmbH. All rights reserved.
 *
 * This software is confidential and proprietary information.
 * You shall use it only in accordance with the terms of the
 * license agreement you entered into with cortical.io GmbH.
 ******************************************************************************/
"""

from pydantic import RootModel, BaseModel, Field
from typing import List, Optional


class InputText(BaseModel):
    text: str = Field(..., description="The input text. Cannot be empty.", min_length=1)
    language: Optional[str] = Field(None, description="Language of the text, e.g. 'en' (ISO 639-1). If not provided, "
                                                      "the service will try to infer it from the text.")


# NLP API Request Models


class CompareRequest(RootModel[List[InputText]]):
    pass


class LabelsRequest(InputText):
    pass


class SegmentationRequest(InputText):
    pass


class LanguageDetectRequest(BaseModel):
    text: str = Field(..., description="The input text.", min_length=1)


class KeywordsRequest(InputText):
    pass


# NLP API Response Models


class ScoredRetinaTermLabel(BaseModel):
    word: str
    document_frequency: float
    pos_tags: List[str]
    score: float


class RetinaTermLabel(BaseModel):
    word: str
    document_frequency: float
    pos_tags: List[str]


class CompareResponse(BaseModel):
    similarity: Optional[float]
    languages: List[str]


class KeywordsResponse(BaseModel):
    keywords: List[ScoredRetinaTermLabel]
    language: str


class LabelsResponse(BaseModel):
    labels: List[RetinaTermLabel]
    language: str


class LanguageDetectResponse(BaseModel):
    language: str


class SegmentationResponse(BaseModel):
    segments: List[str]
    language: str


class SupportedLanguagesResponse(BaseModel):
    supported_languages: List[str]


# NLP API Error Response Models


class HTTPValidationError(BaseModel):
    loc: List[str]
    msg: str
    type: str


class ErrorResponse(BaseModel):
    message: str
