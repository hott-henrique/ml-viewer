from application.managers.model.definitions.association.Apriori import APRIORI_REGISTRY_INSTANCE
from application.managers.model.definitions.association.Eclat import ECLAT_REGISTRY_INSTANCE

ASSOCIATION_REGISTRY = {
  "Apriori": APRIORI_REGISTRY_INSTANCE,
  "Eclat": ECLAT_REGISTRY_INSTANCE,
}

__all__ = [
  "ASSOCIATION_REGISTRY",
]
