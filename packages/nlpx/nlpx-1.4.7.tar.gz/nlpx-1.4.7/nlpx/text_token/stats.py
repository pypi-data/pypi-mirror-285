import math
import operator
from functools import reduce
from typing import Union, Iterable

from .utils import batch_cut, cut


# --------------------------------------------------Token counter------------------------------------------------------
def token_counter(cut_corpus: Union[map, Iterable[str], Iterable[Iterable[str]]]):
    """
    统计词频
    :param cut_corpus: 分词后的语料
    :return: collections.Counter, 可以用items()方法取出[tuple(word, count)]
    """
    from collections import Counter
    if isinstance(cut_corpus, map) or (isinstance(cut_corpus, Iterable) and isinstance(cut_corpus[0], Iterable)):
        # return Counter([token for line in batch_cut for token in line])
        return Counter(reduce(operator.iconcat, cut_corpus, []))
    elif isinstance(cut_corpus, Iterable) and isinstance(cut_corpus[0], str):
        return Counter(cut_corpus)
    raise TypeError("'cut_corpus'参数类型不对")


# -----------------------------------------------------Text analysis----------------------------------------------
def show_label_category_count(labels):
    """
    :param corpus: 语料，可以是Iterable[str], Iterable[Iterable[str]], pandas的Series[str]
    :return: labels, label_count
    """
    import sys
    import pandas as pd
    import matplotlib.pyplot as plt
    if isinstance(labels, pd.Series):
        label_count = labels.value_counts(sort=False)
        label_count.plot(kind='bar')
        labels = labels.unique()
        min_count, max_count = label_count.min(), label_count.max()
    else:
        from collections import Counter
        label_count = Counter(labels)

        labels, counts = [], []
        min_count, max_count = sys.maxsize, 0
        for label, count in label_count.items():
            labels.append(label)
            counts.append(count)
            min_count = count if min_count > count else min_count
            max_count = count if max_count < count else max_count

        plt.bar(labels, counts, width=0.5)
        plt.xticks(ticks=labels, rotation=60)

    print(f'最大值: {max_count}，最小值: {min_count}，相差{max_count / min_count:.0f}倍')
    plt.show()
    return labels, label_count


def show_sentence_len_hist(corpus, language='cn', cut_type='word', bins=50, scope: tuple = (0, 30), cut_fn=None):
    """
    :param corpus: 语料，可以是Iterable[str], Iterable[Iterable[str]], pandas的Series[str]
    :param language:
    :param cut_type:
    :param bins:
    :param scope:
    :param cut_fn:
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    if cut_fn is None and language == 'cn' and cut_type == 'word':
        import jieba
        import logging
        jieba.setLogLevel(logging.INFO)
        cut_fn = jieba.lcut

    plt.figure(figsize=(12, 6))
    if isinstance(corpus, pd.Series):
        sent_length = corpus.map(lambda x: len(cut(x, language, cut_type, cut_fn=cut_fn)))
        sent_length.hist(bins=bins)
    else:
        batch_cuts = batch_cut(corpus, language, cut_type, cut_fn=cut_fn)
        length = list(map(lambda s: len(s), batch_cuts))
        if scope:
            length = [x for x in length if scope[0] <= x <= scope[1]]
        print(f'最短的句子是{min(length)}，最长为{max(length)}')
        plt.hist(length, bins=bins)
    plt.xlabel('sentence length')
    plt.ylabel('sentence (count)')
    plt.grid()
    plt.show()


def show_token_freq_plot(corpus, language='cn', cut_type='word', scope: tuple = None, cut_fn=None):
    """
    :param corpus: 语料，可以是Iterable[str], Iterable[Iterable[str]], pandas的Series[str]
    :param language:
    :param cut_type:
    :param scope:
    :param cut_fn:
    """
    import matplotlib.pyplot as plt
    if cut_fn is None and language == 'cn' and cut_type == 'word':
        import jieba
        import logging
        jieba.setLogLevel(logging.INFO)
        cut_fn = jieba.lcut

    show_num = 10
    batch_cuts = batch_cut(corpus, language, cut_type, cut_fn=cut_fn)
    counter = token_counter(batch_cuts)
    sorted_token_count = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)
    print(f'出现频率最大的{show_num}个token:\n {sorted_token_count[:show_num]}')
    print(f'出现频率最小的{show_num}个token:\n {sorted_token_count[-show_num:]}')
    if scope is not None:
        sorted_token_count = sorted_token_count[scope[0]:scope[1]]

    sorted_count = list(map(lambda kv: kv[1], sorted_token_count))

    # sorted_count = sorted(counter.values(), reverse=True)
    # if scope is not None:
    #     token_count = sorted_count[scope[0]:scope[1]]
    plt.figure(figsize=(10, 6))
    plt.plot(list(map(lambda n: math.log(n), sorted_count)))
    # plt.plot(sorted_count, scalex='log', scaley='log')
    plt.xlabel('token:x')
    plt.ylabel('frequency:log(x)')
    plt.show()
