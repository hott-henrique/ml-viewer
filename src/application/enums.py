from enum import StrEnum

class LearningParadigm(StrEnum):
  SUPERVISED = "Supervised"
  UNSUPERVISED = "Unsupervised"
  SEMI_SUPERVISED = "Semi-Supervised"
  REINFORCEMENT = "Reinforcement"

class ProblemType(StrEnum):
  CLASSIFICATION = "Classification"
  REGRESSION = "Regression"
  CLUSTERING = "Clustering"
  DIMENSIONALITY_REDUCTION = "Dimensionality Reduction"
  ASSOCIATION_RULES = "Association Rules"
  SEMI_SUPERVISED_CLASSIFICATION = "Semi-Supervised Classification"
  SEMI_SUPERVISED_REGRESSION = "Semi-Supervised Regression"
  REINFORCEMENT_LEARNING = "Reinforcement Learning"

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

class AnalysisOutputKind(StrEnum):
  SCALAR = "scalar"
  TEXT = "text"
  IMAGE = "image"

class DatasetLayout(StrEnum):
  NO_SPLIT = "NoSplit"
  TRAIN_TEST_SPLIT = "TrainTestSplit"
  LABELED_UNLABELED = "LabeledUnlabeled"

class DatasetFileRole(StrEnum):
  FULL = "Full"
  TRAIN = "Train"
  TEST = "Test"
  LABELED = "Labeled"
  UNLABELED = "Unlabeled"
