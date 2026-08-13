from dataclasses import dataclass, field


@dataclass
class AnalyzerResult:

    name: str

    score: int

    confidence: int = 100

    passed: bool = True

    details: dict = field(default_factory=dict)

    recommendations: list = field(default_factory=list)