
from .constants import INCOME_TYPES, RECORD_STATUSES


def income_book_constants(request):
    """
    Контекстний процесор для констант книги доходів

    Додає в контекст шаблонів списки типів доходів та статусів записів
    """
    return {
        'income_types': INCOME_TYPES,
        'record_statuses': RECORD_STATUSES
    }