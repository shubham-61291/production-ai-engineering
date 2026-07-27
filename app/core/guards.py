import logging
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from app.core.config import settings

logger = logging.getLogger(__name__)

class InputGuard:
    def __init__(self):
        self.model_path = settings.INPUT_GUARD_MODEL_PATH
        if os.path.exists(self.model_path):
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.eval()
        else:
            logger.warning(f"InputGuard model not found at {self.model_path}. Guard will pass by default.")
            self.model = None
            self.tokenizer = None
        self.threshold = 0.85

    def analyze(self, text: str):
        if not self.model or not self.tokenizer:
            return True, 0.0
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
            score = probs[0][1].item()
            is_safe = score <= self.threshold
        return is_safe, score

class OutputGuard:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.operators = {
            "EMAIL": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
            "SSN": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
            "IP_ADDRESS": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
            "CREDIT_CARD": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
        }

    def redact(self, text: str) -> str:
        results = self.analyzer.analyze(text=text, language="en")
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=self.operators
        )
        return anonymized.text

_input_guard = None
_output_guard = None

def get_input_guard():
    global _input_guard
    if _input_guard is None:
        _input_guard = InputGuard()
    return _input_guard

def get_output_guard():
    global _output_guard
    if _output_guard is None:
        _output_guard = OutputGuard()
    return _output_guard
