import logging
from dataclasses import dataclass, field
from pathlib import Path

import fitz

from config.settings import Settings

logger = logging.getLogger("pdfforge")

HEURISTIC_RULES: dict[str, list[str]] = {
    "contrato": ["cláusula", "contratante", "contratado", "objeto do contrato", "vigência"],
    "nota_fiscal": ["CNPJ", "valor total", "NF-e", "nota fiscal", "tributos"],
    "procuracao": ["outorgante", "outorgado", "poderes", "instrumento particular"],
    "laudo": ["laudo", "perícia", "parecer técnico", "conclusão", "examinado"],
    "relatorio": ["relatório", "período", "resultados", "conclusões", "recomendações"],
    "ata": ["ata", "reunião", "presentes", "deliberou", "aprovado por unanimidade"],
    "curriculo": ["formação", "experiência profissional", "habilidades", "objetivo profissional"],
}


@dataclass
class ClassificationResult:
    doc_type: str
    confidence: float
    method: str
    scores: dict[str, float] = field(default_factory=dict)


class DocumentClassifier:
    def classify(self, doc: fitz.Document) -> ClassificationResult:
        text = ""
        for i in range(min(3, doc.page_count)):
            text += doc[i].get_text()

        model_path = Settings().CLASSIFIER_MODEL_PATH
        if model_path.exists():
            try:
                import joblib
                model = joblib.load(str(model_path))
                prediction = model.predict([text])[0]
                probabilities = model.predict_proba([text])[0]
                classes = model.classes_
                scores = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
                max_prob = float(max(probabilities))
                logger.info("Classificacao ML: %s (%.2f)", prediction, max_prob)
                return ClassificationResult(
                    doc_type=prediction,
                    confidence=max_prob,
                    method="ml",
                    scores=scores,
                )
            except Exception as exc:
                logger.warning("Falha no modelo ML, usando heuristica: %s", exc)

        return self._classify_heuristic(text)

    def _classify_heuristic(self, text: str) -> ClassificationResult:
        text_lower = text.lower()
        scores: dict[str, float] = {}

        for doc_type, keywords in HEURISTIC_RULES.items():
            matches = sum(1 for kw in keywords if kw.lower() in text_lower)
            scores[doc_type] = matches / len(keywords) if keywords else 0.0

        if not scores or max(scores.values()) == 0.0:
            return ClassificationResult(
                doc_type="indefinido",
                confidence=0.0,
                method="heuristic",
                scores=scores,
            )

        best_type = max(scores, key=lambda k: scores[k])
        confidence = scores[best_type]
        logger.info("Classificacao heuristica: %s (%.2f)", best_type, confidence)
        return ClassificationResult(
            doc_type=best_type,
            confidence=confidence,
            method="heuristic",
            scores=scores,
        )

    def classify_batch(
        self, docs: list[tuple[Path, fitz.Document]]
    ) -> list[tuple[Path, ClassificationResult]]:
        results = []
        total = len(docs)
        for i, (path, doc) in enumerate(docs):
            logger.info("Classificando [%d/%d]: %s", i + 1, total, path.name)
            result = self.classify(doc)
            results.append((path, result))
        return results


# "O conhecimento organizado é poder." — Francis Bacon
