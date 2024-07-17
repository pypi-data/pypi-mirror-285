import torch
from torch import nn
from typing import Union, List
from ._text_cnn import TextCNN
from ._attention import RNNAttention, CNNRNNAttention, RNNCNNAttention, ResRNNCNNAttention
from ._embedding import EmbeddingLayer


class EmbeddingClassifier(nn.Module):
	"""
	Examples
	--------
	>>> from nlpx.text_token import TokenEmbedding
	>>> from nlpx.models import TextCNN, RNNAttention, EmbeddingClassifier
	>>> tokenizer = TokenEmbedding(pretrained_path)
	>>> attn = RNNAttention(tokenizer.embed_dim, num_heads=2, out_features=len(classes))
	>>> classifier = EmbeddingClassifier(atten, embedding=tokenizer.embedding)
	>>> classifier = EmbeddingClassifier(atten, vocab_size=tokenizer.vocab_size, embed_dim=tokenizer.embed_dim)
	"""

	def __init__(self, classifier, embedding: Union[nn.Embedding, torch.Tensor, List] = None, vocab_size: int = None,
	             embed_dim: int = None):
		"""
		:param classifier: 分类器
		:param embedding: 输入的embedding，可以是nn.Embedding，torch.Tensor，list
		:param vocab_size: vocab size
		:param embed_dim: word embedding维度
		"""
		super().__init__()
		self.classifier = classifier
		self.embedding = EmbeddingLayer(embed_dim, vocab_size, embedding)

	def forward(self, input_ids: torch.Tensor, labels: torch.LongTensor = None):
		embedding = self.embedding(input_ids)
		return self.classifier(embedding, labels)
	

class MaskEmbeddingClassifier(EmbeddingClassifier):
	"""
	Examples
	--------
	>>> from nlpx.text_token import TokenEmbedding
	>>> from nlpx.models import TextCNN, RNNAttention, EmbeddingClassifier
	>>> tokenizer = TokenEmbedding(pretrained_path)
	>>> attn = RNNAttention(tokenizer.embed_dim, num_heads=2, out_features=len(classes))
	>>> classifier = MaskEmbeddingClassifier(atten, embedding=tokenizer.embedding)
	>>> classifier = MaskEmbeddingClassifier(atten, vocab_size=tokenizer.vocab_size, embed_dim=tokenizer.embed_dim)
	"""
	
	def forward(self, input_ids: torch.Tensor, labels: torch.LongTensor = None, mask=None):
		embedding = self.embedding(input_ids)
		return self.classifier(embedding, labels, mask)


class TextCNNClassifier(EmbeddingClassifier):
	"""
	Examples
	--------
	>>> from nlpx.text_token import Tokenizer
	>>> from nlpx.models import TextCNNClassifier
	>>> tokenizer = Tokenizer(corpus)
	>>> classifier = TextCNNClassifier(embed_dim, len(classes), vocab_size=tokenizer.vocab_size)
	"""

	def __init__(self, embed_dim: int, num_classes: int, embedding: Union[nn.Embedding, torch.Tensor, List] = None,
	             vocab_size: int = None, kernel_sizes=(2, 3, 4), cnn_channels: int = 64, activation=nn.ReLU(inplace=True),
				 num_hidden_layer: int = 0, batch_norm=False, layer_norm=False, residual=False, drop_out: float = 0.0):
		"""
		:param embed_dim: word embedding维度
		:param num_classes: 类别数
		:param embedding: 出入的embedding
		:param vocab_size: vocab size
		:param kernel_sizes: size of each CNN kernel
		:param activation: CNN 激活函数
		:param num_hidden_layer: 隐藏层数
		:param batch_norm：是否批正则化
		:param layer_norm：是否层正则化
		:param residual: 是否残差
		:param drop_out：
		"""
		classifier = TextCNN(embed_dim, kernel_sizes, cnn_channels, num_classes, activation, num_hidden_layer, batch_norm,
						   layer_norm, residual, drop_out)
		super().__init__(classifier, embedding, vocab_size, embed_dim)


class RNNAttentionClassifier(MaskEmbeddingClassifier):
	"""
	如果是英文、分词, 不用residual 效果比较好
	
	Examples
	--------
	>>> from nlpx.text_token import Tokenizer
	>>> from nlpx.models import RNNAttentionClassifier
	>>> tokenizer = Tokenizer(corpus)
	>>> classifier = RNNAttentionClassifier(embed_dim, len(classes), vocab_size=tokenizer.vocab_size)
	"""

	def __init__(self, embed_dim: int, num_classes: int, embedding: Union[nn.Embedding, torch.Tensor, List] = None,
	             vocab_size: int = None, hidden_size: int = 64, num_layers: int = 1, num_heads: int = 1, rnn=nn.GRU,
	             bidirectional=True, layer_norm=False, residual=False, drop_out: float = 0.0):
		"""
		:param embed_dim: word embedding维度
		:param num_classes: 类别数
		:param embedding: 出入的embedding
		:param vocab_size: vocab size
		:param hidden_size: RNN的hidden_size, RNN隐藏层维度
		:param num_layers: RNN的num_layers, RNN层数
		:param num_heads: 抽头数
		:param rnn: 所用的RNN模型：GRU和LSTM，默认是GRU
		:param bidirectional： 是否是双向RNN
		:param layer_norm：是否层正则化
		:param residual: 是否残差
		:param drop_out：
		"""
		classifier = RNNAttention(embed_dim, hidden_size, num_layers, num_heads, num_classes, rnn, bidirectional,
		                          layer_norm, residual, drop_out)
		super().__init__(classifier, embedding, vocab_size, embed_dim)


class CNNRNNAttentionClassifier(EmbeddingClassifier):
	"""
	Examples
	--------
	>>> from nlpx.text_token import Tokenizer
	>>> from nlpx.models import CNNRNNAttentionClassifier
	>>> tokenizer = Tokenizer(corpus)
	>>> classifier = CNNRNNAttentionClassifier(embed_dim, num_classes=len(classes), vocab_size=tokenizer.vocab_size)
	"""

	def __init__(self, embed_dim: int, seq_length: int = 16, cnn_channels: int = None, kernel_sizes=(2, 3, 4),
	             activation=nn.ReLU(inplace=True), num_classes: int = 2,
	             embedding: Union[nn.Embedding, torch.Tensor, List] = None, vocab_size: int = None,
				 hidden_size: int = 64, num_layers: int = 1,num_heads: int = 2, rnn=nn.GRU,
				 bidirectional=True, layer_norm=False, residual=False, drop_out: float = 0.0, bias=False):
		"""
		:param embed_dim: word embedding维度
		:param seq_length: 句子序列长度
		:param cnn_channels: CNN out_channels
		:param kernel_sizes: size of each CNN kernel
		:param activation: CNN 激活函数
		:param num_classes: 类别数
		:param embedding: 出入的embedding
		:param vocab_size: vocab size
		:param hidden_size: RNN的hidden_size, RNN隐藏层维度
		:param num_layers: RNN的num_layers, RNN层数
		:param num_heads: 抽头数
		:param rnn: 所用的RNN模型：GRU和LSTM，默认是GRU
		:param bidirectional： 是否是双向RNN
		:param layer_norm：是否层正则化
		:param residual: 是否残差
		:param drop_out：
		:param bias：
		"""
		cnn_channels = cnn_channels or embed_dim
		classifier = CNNRNNAttention(embed_dim, seq_length, cnn_channels, kernel_sizes, activation, hidden_size,
		                             num_layers, num_heads, num_classes, rnn, bidirectional, layer_norm, residual,
		                             drop_out, bias)
		super().__init__(classifier, embedding, vocab_size, embed_dim)


class RNNCNNAttentionClassifier(MaskEmbeddingClassifier):
	"""
	Examples
	--------
	>>> from nlpx.text_token import Tokenizer
	>>> from nlpx.models import CNNRNNAttentionClassifier
	>>> tokenizer = Tokenizer(corpus)
	>>> classifier = RNNCNNAttentionClassifier(embed_dim, num_classes=len(classes), vocab_size=tokenizer.vocab_size)
	"""

	def __init__(self, embed_dim: int, seq_length: int = 16, cnn_channels: int = None, kernel_sizes=(2, 3, 4),
	             activation=nn.ReLU(inplace=True), num_classes: int = 2,
	             embedding: Union[nn.Embedding, torch.Tensor, List] = None, vocab_size: int = None,
				 hidden_size: int = 64, num_layers: int = 1,num_heads: int = 2, rnn=nn.GRU,
				 bidirectional=True, batch_norm=False, drop_out: float = 0.0, bias=False):
		"""
		:param embed_dim: word embedding维度
		:param seq_length: 句子序列长度
		:param cnn_channels: CNN out_channels
		:param kernel_sizes: size of each CNN kernel
		:param activation: CNN 激活函数
		:param num_classes: 类别数
		:param embedding: 出入的embedding
		:param vocab_size: vocab size
		:param hidden_size: RNN的hidden_size, RNN隐藏层维度
		:param num_layers: RNN的num_layers, RNN层数
		:param num_heads: 抽头数
		:param rnn: 所用的RNN模型：GRU和LSTM，默认是GRU
		:param bidirectional： 是否是双向RNN
		:param batch_norm：是否批正则化
		:param drop_out：
		:param bias：
		"""
		cnn_channels = cnn_channels or embed_dim
		classifier = RNNCNNAttention(embed_dim, seq_length, cnn_channels, kernel_sizes, activation, hidden_size,
		                             num_layers, num_heads, num_classes, rnn, bidirectional, batch_norm, drop_out, bias)
		super().__init__(classifier, embedding, vocab_size, embed_dim)


class ResRNNCNNAttentionClassifier(MaskEmbeddingClassifier):
	"""
	Examples
	--------
	>>> from nlpx.text_token import Tokenizer
	>>> from nlpx.models import CNNRNNAttentionClassifier
	>>> tokenizer = Tokenizer(corpus)
	>>> classifier = ResRNNCNNAttentionClassifier(embed_dim, num_classes=len(classes), vocab_size=tokenizer.vocab_size)
	"""

	def __init__(self, embed_dim: int, seq_length: int = 16, cnn_channels: int = None, kernel_sizes=(2, 3, 4),
	             activation=nn.ReLU(inplace=True), num_classes: int = 2,
	             embedding: Union[nn.Embedding, torch.Tensor, List] = None, vocab_size: int = None,
				 hidden_size: int = 64, num_layers: int = 1,num_heads: int = 2, rnn=nn.GRU,
				 bidirectional=True, batch_norm=False, drop_out: float = 0.0, bias=False):
		"""
		:param embed_dim: word embedding维度
		:param seq_length: 句子序列长度
		:param cnn_channels: CNN out_channels
		:param kernel_sizes: size of each CNN kernel
		:param activation: CNN 激活函数
		:param num_classes: 类别数
		:param embedding: 出入的embedding
		:param vocab_size: vocab size
		:param hidden_size: RNN的hidden_size, RNN隐藏层维度
		:param num_layers: RNN的num_layers, RNN层数
		:param num_heads: 抽头数
		:param rnn: 所用的RNN模型：GRU和LSTM，默认是GRU
		:param bidirectional： 是否是双向RNN
		:param batch_norm：是否批正则化
		:param drop_out：
		:param bias：
		"""
		cnn_channels = cnn_channels or embed_dim
		classifier = ResRNNCNNAttention(embed_dim, seq_length, cnn_channels, kernel_sizes, activation, hidden_size,
		                             num_layers, num_heads, num_classes, rnn, bidirectional, batch_norm, drop_out, bias)
		super().__init__(classifier, embedding, vocab_size, embed_dim)
	
