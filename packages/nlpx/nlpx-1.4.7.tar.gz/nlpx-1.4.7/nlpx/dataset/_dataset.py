import torch
import numpy as np
import pandas as pd
from typing import Union, List
from torch.utils.data import Dataset

from nlpx.llm import TokenizeVec
from nlpx.text_token import BaseTokenizer, TokenEmbedding
from nlpx.text_token.utils import get_texts_max_length


class TokenDataset(Dataset):
	""" Token的长度不一样
	返回的是(token, label) 不是Tensor, 必须经过PaddingTokenCollator
	"""

	def __init__(self, tokens: Union[List[int], np.ndarray],
				 labels: Union[List, np.ndarray, pd.Series]):
		super().__init__()
		self.tokens = tokens
		self.labels = labels.values if isinstance(labels, pd.Series) else labels

	def __getitem__(self, index: int):
		return self.tokens[index], self.labels[index]

	def __len__(self):
		return len(self.labels)


class SameLengthTokenDataset(Dataset):
	""" Token已经truncate和padding, 长度一样
	返回的是Tensor, 不需要经过collate_fn
	"""

	def __init__(self, tokens: Union[List[int], np.ndarray, torch.LongTensor],
				 labels: Union[List, np.ndarray, pd.Series, torch.LongTensor]):
		super().__init__()
		self.tokens = tokens if isinstance(tokens, torch.LongTensor) else torch.tensor(tokens, dtype=torch.long)
		labels = labels.values if isinstance(labels, pd.Series) else labels
		self.labels = labels if isinstance(labels, torch.LongTensor) else torch.tensor(labels, dtype=torch.long)

	def __getitem__(self, index: int):
		return self.tokens[index], self.labels[index]

	def __len__(self):
		return len(self.labels)


class TextDataset(Dataset):
	""" 返回的是(text, label) 不是Tensor, 必须经过TextVecCollator """

	def __init__(self, texts: Union[List[str], np.ndarray, pd.Series], labels: Union[List, np.ndarray, pd.Series]):
		super().__init__()
		self.texts = texts.values if isinstance(texts, pd.Series) else texts
		self.labels = labels.values if isinstance(labels, pd.Series) else labels

	def __getitem__(self, index: int):
		return self.texts[index], self.labels[index]

	def __len__(self):
		return len(self.labels)


class TextDFDataset(Dataset):
	""" 返回的是(text, label) 不是Tensor, 必须经过TextVecCollator """

	def __init__(self, data_df: pd.DataFrame):
		"""
		:param data_df: 只有两列 ['text', 'label'], 注意顺序，第一列是text, 第二列是label
		"""
		super().__init__()
		self.data = data_df.values

	def __getitem__(self, index: int):
		return self.data[index]

	def __len__(self):
		return len(self.data)


class TextVecCollator:

	def __init__(self, tokenize_vec: Union[TokenizeVec, TokenEmbedding], max_length: int = None, **kwargs):
		self.tokenize_vec = tokenize_vec
		self.max_length = max_length
		self.kwargs = kwargs

	def __call__(self, examples):
		texts, labels = zip(*examples)
		labels = torch.tensor(np.array(labels), dtype=torch.long)

		if isinstance(self.tokenize_vec, TokenizeVec):
			max_length = get_texts_max_length(texts, cut_type='char') + 2
			max_length = min(max_length, self.max_length) if self.max_length and self.max_length > 0 else max_length
			return self.tokenize_vec.encode_plus(texts, max_length=max_length, padding='max_length',
												truncation=True, add_special_tokens=True,
												return_token_type_ids=True,return_attention_mask=True,
												return_tensors='pt', **self.kwargs), labels
		elif isinstance(self.tokenize_vec, TokenEmbedding):
			max_length = get_texts_max_length(texts, cut_type=self.tokenize_vec.cut_type,
											  language=self.tokenize_vec.language, cut_fn=self.tokenize_vec.cut_fn)
			max_length = min(max_length, self.max_length) if self.max_length and self.max_length > 0 else max_length
			return self.tokenize_vec(texts, max_length, **self.kwargs), labels

		raise ValueError("Invalid tokenize_vec, it must be a TokenizeVec or TokenEmbedding.")


class TokenizeCollator:

	def __init__(self, tokenizer, max_length: int = None, **kwargs):
		self.tokenizer = tokenizer
		self.max_length = max_length
		self.kwargs = kwargs

	def __call__(self, examples):
		texts, labels = zip(*examples)
		labels = torch.tensor(np.array(labels), dtype=torch.long)

		if isinstance(self.tokenizer, BaseTokenizer):
			max_length = get_texts_max_length(texts, cut_type=self.tokenizer.cut_type, language=self.tokenizer.language,
											  cut_fn=self.tokenizer.cut_fn)
			max_length = min(max_length, self.max_length) if self.max_length and self.max_length > 0 else max_length
			return torch.tensor(self.tokenizer.batch_encode(texts, max_length, **self.kwargs), dtype=torch.long), labels

		max_length = get_texts_max_length(texts, cut_type='char') + 2
		max_length = min(max_length, self.max_length) if self.max_length and self.max_length > 0 else max_length
		result = self.tokenizer.batch_encode_plus(texts, max_length=max_length, padding='max_length',
												  return_token_type_ids=True, return_attention_mask=True,
											  	  truncation=True, add_special_tokens=True, return_tensors='pt', **self.kwargs)
		result['labels'] = labels
		return result


class PaddingTokenCollator:
	"""
	与TokenDataset配合使用
	"""

	def __init__(self, padding_func, max_length: int = None, return_sequence_length=False):
		self.padding_func = padding_func
		self.max_length = max_length
		self.return_sequence_length = return_sequence_length

	def __call__(self, examples):
		tokens, labels = zip(*examples)
		labels = torch.tensor(np.array(labels), dtype=torch.long)

		max_length = max(map(lambda x: len(x), tokens))
		max_length = min(max_length, self.max_length) if self.max_length and self.max_length > 0 else max_length
		ids, sequence_lengths = self.padding_func(tokens, max_length)
		if self.return_sequence_length:
			return torch.tensor(ids, dtype=torch.long), labels, torch.tensor(sequence_lengths, dtype=torch.int)
		return torch.tensor(ids, dtype=torch.long), labels
