import math
import torch
from torch import nn
import torch.nn.functional as F
from ._cnn import CNNLayer
from ._rnn import RNNLayer


def attention(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor):
	batch_size, length, d_k = key.size()
	key = key.contiguous()
	scores = torch.matmul(query, key.view(batch_size, d_k, length)) / math.sqrt(d_k)
	scores = F.softmax(scores, dim=-1)
	return torch.matmul(scores, value).sum(dim=1)


class ClassifySelfAttention(nn.Module):

	def __init__(self, embed_dim: int):
		super().__init__()
		self.w_omega = nn.Parameter(torch.Tensor(embed_dim, embed_dim))
		self.u_omega = nn.Parameter(torch.Tensor(embed_dim, 1))
		nn.init.uniform_(self.w_omega, -0.1, 0.1)
		nn.init.uniform_(self.u_omega, -0.1, 0.1)

	def forward(self, inputs: torch.Tensor):
		"""
		:param inputs: [(batch_size, sequence_length, embed_dim)]
		:return: [(batch_size, embed_dim)]
		"""
		u = torch.tanh(torch.matmul(inputs, self.w_omega))
		att = torch.matmul(u, self.u_omega)
		att_score = F.softmax(att, dim=1)
		scored_x = inputs * att_score
		return torch.sum(scored_x, dim=1)


class MultiHeadClassifySelfAttention(nn.Module):

	def __init__(self, embed_dim: int, num_heads: int = 1):
		super().__init__()
		self.num_heads = num_heads
		self.attention = ClassifySelfAttention(num_heads * embed_dim)

	def forward(self, inputs: torch.Tensor):
		"""
		:param inputs: [(batch_size, sequence_length, embed_dim)]
		:return: [(batch_size, num_heads * embed_dim)]
		"""
		if self.num_heads > 1:
			inputs = torch.concat([inputs for _ in range(self.num_heads)], dim=-1)
		return self.attention(inputs)


class RNNAttention(nn.Module):
	"""
	Examples
	--------
	>>> from nlpx.text_token import Tokenizer
	>>> from nlpx.models import RNNAttention
	>>> tokenizer = Tokenizer(corpus)
	>>> classifier = RNNAttention(embed_dim, out_features=len(classes))
	"""

	def __init__(self, embed_dim: int, hidden_size: int = 64, num_layers: int = 1, num_heads: int = 1,
				 out_features: int = 2, rnn=nn.GRU, bidirectional=True, layer_norm=False, residual=False,
				 drop_out: float = 0.0):
		"""
		如果是英文、分词, 不用residual 效果比较好
		
		:param embed_dim: RNN的input_size，word embedding维度
		:param hidden_size: RNN的hidden_size, RNN隐藏层维度
		:param num_layers: RNN的num_layers, RNN层数
		:param num_layers: RNN的num_layers, RNN层数
		:param num_heads: 抽头数
		:param rnn: 所用的RNN模型：GRU和LSTM，默认是GRU
		:param bidirectional： 是否是双向RNN
		:param layer_norm：是否层正则化
		:param residual: 是否残差
		:param drop_out：
		"""
	
		super().__init__()
		self.residual = residual
		rnn_output_size = hidden_size << 1 if bidirectional else hidden_size
		attn_embed_dim = rnn_output_size + embed_dim if residual else rnn_output_size
		self.rnn = RNNLayer(embed_dim, hidden_size, num_layers, rnn, bidirectional, layer_norm, drop_out)
		self.attention = MultiHeadClassifySelfAttention(attn_embed_dim, num_heads)
	
		# 定义全连接层
		self.fc = nn.Linear(attn_embed_dim * num_heads, out_features)
		if 0.0 < drop_out < 1.0:
			self.fc = nn.Sequential(
				nn.Dropout(drop_out),
				self.fc
			)

	def forward(self, inputs: torch.Tensor, labels: torch.LongTensor = None, sequence_lengths: torch.IntTensor = None):
		"""
		:param inputs: [(batch_size, sequence_length, embed_dim)]
		:param labels: [torch.LongTensor]
		:param sequence_lengths: [torch.IntTensor] 序列实际长度
		:return: [(batch_size, out_features)] when labels is None
		:return: (loss, [(batch_size, out_features)]) when labels is not None
		"""
		output = self.rnn(inputs, sequence_lengths)  # [(batch_size, sequence_length, rnn_output_size)]
		if self.residual:
			output = torch.cat((output, inputs), dim=2)
		output = self.attention(output)  # [(batch_size, attn_embed_dim)]
		logits = self.fc(output)
		if labels is None:
			return logits

		loss = F.cross_entropy(logits, labels)
		return loss, logits


class CNNRNNAttention(nn.Module):
	"""
	Examples
	--------
	>>> from nlpx.text_token import Tokenizer
	>>> from nlpx.models import CNNRNNAttention
	>>> tokenizer = Tokenizer(corpus)
	>>> classifier = CNNRNNAttention(embed_dim, out_features=len(classes), vocab_size=tokenizer.vocab_size)
	"""
	
	def __init__(self, embed_dim: int, seq_length: int = 16, cnn_channels: int = 64, kernel_sizes=(2, 3, 4),
	             activation=nn.ReLU(inplace=True), hidden_size: int = 64, num_layers: int = 1, num_heads: int = 1,
	             out_features: int = 2, rnn=nn.GRU, bidirectional=True, layer_norm=False,  residual=False,
	             drop_out: float = 0.0, bias=False):
		"""
		:param embed_dim: RNN的input_size，word embedding维度
		:param cnn_channels: CNN out_channels
		:param kernel_sizes: size of each CNN kernel
		:param activation: CNN 激活函数
		:param hidden_size: RNN的hidden_size, RNN隐藏层维度
		:param num_layers: RNN的num_layers, RNN层数
		:param num_heads: 抽头数
		:param out_features:
		:param rnn: 所用的RNN模型：GRU和LSTM，默认是GRU
		:param bidirectional： 是否是双向RNN
		:param layer_norm：是否层正则化
		:param residual: 是否残差
		:param drop_out：
		:param bias：
		"""
		
		super().__init__()
		cnn_channels = cnn_channels or embed_dim
		self.cnn = CNNLayer(embed_dim, seq_length, cnn_channels, kernel_sizes, activation, layer_norm, bias)
		self.attn = RNNAttention(cnn_channels, hidden_size, num_layers, num_heads, out_features, rnn, bidirectional,
		                         layer_norm, residual, drop_out)
		
	def forward(self, inputs: torch.Tensor, labels: torch.LongTensor = None):
		"""
		:param inputs: [(batch_size, sequence_length, embed_dim)]
		:param labels: [torch.LongTensor]
		:return: [(batch_size, out_features)] when labels is None
		:return: (loss, [(batch_size, out_features)]) when labels is not None
		"""
		output = self.cnn(inputs)
		return self.attn(output, labels)


class RNNCNNAttention(nn.Module):
	"""
	Examples
	--------
	>>> from nlpx.text_token import Tokenizer
	>>> from nlpx.models import CNNRNNAttention
	>>> tokenizer = Tokenizer(corpus)
	>>> classifier = RNNCNNAttention(embed_dim, out_features=len(classes), vocab_size=tokenizer.vocab_size)
	"""
	
	def __init__(self, embed_dim: int, seq_length: int = 16, cnn_channels: int = 64, kernel_sizes=(2, 3, 4),
	             activation=nn.ReLU(inplace=True), hidden_size: int = 64, num_layers: int = 1, num_heads: int = 1,
	             out_features: int = 2, rnn=nn.GRU, bidirectional=True, layer_norm=False, drop_out: float = 0.0, bias=False):
		"""
		:param embed_dim: RNN的input_size，word embedding维度
		:param cnn_channels: CNN out_channels
		:param kernel_sizes: size of each CNN kernel
		:param activation: CNN 激活函数
		:param hidden_size: RNN的hidden_size, RNN隐藏层维度
		:param num_layers: RNN的num_layers, RNN层数
		:param num_heads: 抽头数
		:param out_features:
		:param rnn: 所用的RNN模型：GRU和LSTM，默认是GRU
		:param bidirectional： 是否是双向RNN
		:param layer_norm：是否层正则化
		:param drop_out：
		:param bias：
		"""
		super().__init__()
		cnn_channels = cnn_channels or embed_dim
		rnn_output_size = (hidden_size << 1) if bidirectional else hidden_size
		self.rnn = RNNLayer(embed_dim, hidden_size, num_layers, rnn, bidirectional, layer_norm, drop_out)
		self.cnn = CNNLayer(rnn_output_size, seq_length, cnn_channels, kernel_sizes, activation, layer_norm, bias)
		self.attention = MultiHeadClassifySelfAttention(cnn_channels, num_heads)
	
		# 定义全连接层
		self.fc = nn.Linear(cnn_channels * num_heads, out_features)
		if 0.0 < drop_out < 1.0:
			self.fc = nn.Sequential(
				nn.Dropout(drop_out),
				self.fc
			)

	def forward(self, inputs: torch.Tensor, labels: torch.LongTensor = None, sequence_lengths: torch.IntTensor = None):
		"""
		:param inputs: [(batch_size, sequence_length, embed_dim)]
		:param labels: [torch.LongTensor]
		:param sequence_lengths: [torch.IntTensor] 序列实际长度
		:return: [(batch_size, out_features)] when labels is None
		:return: (loss, [(batch_size, out_features)]) when labels is not None
		"""
		output = self.rnn(inputs, sequence_lengths)
		output = self.cnn(output)
		output = self.attention(output)
		logits = self.fc(output)
		if labels is None:
			return logits

		loss = F.cross_entropy(logits, labels)
		return loss, logits


class ResRNNCNNAttention(nn.Module):
	"""
	Examples
	--------
	>>> from nlpx.text_token import Tokenizer
	>>> from nlpx.models import CNNRNNAttention
	>>> tokenizer = Tokenizer(corpus)
	>>> classifier = ResRNNCNNAttention(embed_dim, out_features=len(classes), vocab_size=tokenizer.vocab_size)
	"""
	
	def __init__(self, embed_dim: int, seq_length: int = 16, cnn_channels: int = 64, kernel_sizes=(2, 3, 4),
	             activation=nn.ReLU(inplace=True), hidden_size: int = 64, num_layers: int = 1, num_heads: int = 1,
	             out_features: int = 2, rnn=nn.GRU, bidirectional=True, layer_norm=False, drop_out: float = 0.0, bias=False):
		"""
		:param embed_dim: RNN的input_size，word embedding维度
		:param cnn_channels: CNN out_channels
		:param kernel_sizes: size of each CNN kernel
		:param activation: CNN 激活函数
		:param hidden_size: RNN的hidden_size, RNN隐藏层维度
		:param num_layers: RNN的num_layers, RNN层数
		:param num_heads: 抽头数
		:param out_features:
		:param rnn: 所用的RNN模型：GRU和LSTM，默认是GRU
		:param drop_out：
		:param bidirectional： 是否是双向RNN
		:param layer_norm：是否层正则化
		:param bias：
		"""
		super().__init__()
		cnn_channels = cnn_channels or embed_dim
		rnn_output_size = (hidden_size << 1) if bidirectional else hidden_size
		self.rnn = RNNLayer(embed_dim, hidden_size, num_layers, rnn, bidirectional, layer_norm, drop_out)
		self.cnn = CNNLayer(rnn_output_size, seq_length, cnn_channels, kernel_sizes, activation, layer_norm, bias)
		self.attention = MultiHeadClassifySelfAttention(cnn_channels, num_heads)
		self.res_attention = MultiHeadClassifySelfAttention(embed_dim + rnn_output_size, num_heads)
	
		# 定义全连接层
		self.fc = nn.Linear((embed_dim + cnn_channels + rnn_output_size) * num_heads, out_features)
		if 0.0 < drop_out < 1.0:
			self.fc = nn.Sequential(
				nn.Dropout(drop_out),
				self.fc
			)
		# if batch_norm:
		# 	self.fc = nn.Sequential(
		# 		nn.BatchNorm1d((embed_dim + cnn_channels + rnn_output_hidden_size) * num_heads),
		# 		self.fc
		# 	)

	def forward(self, inputs: torch.Tensor, labels: torch.LongTensor = None, sequence_lengths: torch.IntTensor = None):
		"""
		:param inputs: [(batch_size, sequence_length, embed_dim)]
		:param labels: [torch.LongTensor]
		:param sequence_lengths: [torch.IntTensor] 序列实际长度
		:return: [(batch_size, out_features)] when labels is None
		:return: (loss, [(batch_size, out_features)]) when labels is not None
		"""
		rnn_output = self.rnn(inputs, sequence_lengths)  # [(batch_size, sequence_length, 2 * hidden_size)]
		rnn_cnn_output = self.cnn(rnn_output)     # [(batch_size, seq_length * len(kernel_sizes), cnn_channels)]
		rnn_cnn_attn_output = self.attention(rnn_cnn_output)   # [(batch_size, num_heads * out_channels)]
		
		# [(batch_size, num_heads * (embed_dim + 2 * hidden_size))]
		res_output = self.res_attention(torch.cat((inputs, rnn_output), dim=2))
		
		output = torch.cat([res_output, rnn_cnn_attn_output], dim=1)
		logits = self.fc(output)
		if labels is None:
			return logits

		loss = F.cross_entropy(logits, labels)
		return loss, logits
