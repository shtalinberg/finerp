


TRANTYPE_DEBIT = 'D' # платіж від нас
TRANTYPE_CREDIT = 'C' # платіж до нас
TRANTYPE_CASH = 'CASH'

STATEMENT_TYPE_REAL = 'r'  # - реальний,
STATEMENT_TYPE_INFO = 'i'  # - інформаційний

STATEMENT_TYPES = ((STATEMENT_TYPE_REAL, 'real'), (STATEMENT_TYPE_INFO, 'information'))

STATEMENT_STATE_R = 'r'  # проведено
STATEMENT_STATE_T = 't'  # сторнований

STATEMENT_STATES = (
    (STATEMENT_STATE_R, 'проведено'),  # - проведено,
    (STATEMENT_STATE_T, 'сторнований'),  # - сторнований
)

STATEMENT_DOC_TYPE_P = 'p'  # доручення
STATEMENT_DOC_TYPE_T = 't'  # вимога
STATEMENT_DOC_TYPE_M = 'm'  # меморіальний ордер
STATEMENT_DOC_TYPE_X = 'x'  # сторнований
STATEMENT_DOC_TYPE_R = 'r'  # сторнований

STATEMENT_DOC_TYPES = (
    (STATEMENT_DOC_TYPE_P, 'доручення'),
    (STATEMENT_DOC_TYPE_T, 'вимога'),
    (STATEMENT_DOC_TYPE_M, 'меморіальний ордер'),
    (STATEMENT_DOC_TYPE_X, 'прибутковий ордер'),
    (STATEMENT_DOC_TYPE_R, 'видатковий ордер'),
)
