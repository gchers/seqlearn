from nose.tools import assert_equal, assert_true
from numpy.testing import assert_array_equal

import numpy as np
import re

from seqlearn.evaluation import bio_f_score, SequenceKFold


def test_bio_f_score():
    # Check against putputs from the "conlleval" Perl script from CoNLL 2002.
    examples = [
        ("OBIO", "OBIO", 1.),
        ("BII", "OBI", 0.),
        ("BB", "BI", 0.),
        ("BBII", "BBBB", 1 / 3.),
        ("BOOBIB", "BOBOOB", 2 / 3.),
        ("B-PER I-PER O B-PER I-PER O O B-LOC O".split(),
         "B-LOC I-LOC O B-PER I-PER O O B-LOC I-LOC".split(),
         1 / 3.)
    ]

    for y_true, y_pred, score in examples:
        y_true = list(y_true)
        y_pred = list(y_pred)
        assert_equal(score, bio_f_score(y_true, y_pred))


def test_kfold():
    sequences = [
        "BIIOOOBOO",
        "OOBIOOOBI",
        "OOOOO",
        "BIIOOOOO",
        "OBIOOBIIIII",
        "OOBII",
        "BIBIBIO",
    ]

    y = np.asarray(list(''.join(sequences)))

    for random_state in [75, 82, 91, 57, 291]:
        kfold = SequenceKFold(map(len, sequences), n_folds=3, shuffle=True,
                              random_state=random_state)
        folds = list(iter(kfold))
        for train, test in folds:
            assert_true(np.issubdtype(train.dtype, np.integer))
            assert_true(np.issubdtype(test.dtype, np.integer))

            assert_true(np.all(train < len(y)))
            assert_true(np.all(test < len(y)))

            y_train = ''.join(y[train])
            y_test = ''.join(y[test])
            # consistent BIO labeling preserved
            assert_true(re.match(r'O*(?:BI*)O*', y_train))
            assert_true(re.match(r'O*(?:BI*)O*', y_test))
