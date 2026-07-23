from enum import StrEnum

class LearningParadigm(StrEnum):
  SUPERVISED = "Supervised"
  UNSUPERVISED = "Unsupervised"

class ProblemType(StrEnum):
  CLASSIFICATION = "Classification"
  REGRESSION = "Regression"
  CLUSTERING = "Clustering"
  DIMENSIONALITY_REDUCTION = "Dimensionality Reduction"

class ParamType(StrEnum):
  INT = "int"
  FLOAT = "float"
  BOOL = "bool"
  CATEGORICAL = "categorical"
  STRING = "string"

class ExperimentStatus(StrEnum):
  PENDING = "Pending"
  OK = "OK"
  NOK = "NOK"