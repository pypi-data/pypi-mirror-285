import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


class RNNLayer(nn.Module):
	"""
	Examples
	--------
	>>> from nlpx.text_token import Tokenizer
	>>> from nlpx.models import RNNAttention
	>>> tokenizer = Tokenizer(corpus)
	>>> rnn = RNNLayer(embed_dim)
	"""
	
	def __init__(self, embed_dim: int, hidden_size: int = 64, num_layers: int = 1, rnn=nn.GRU,
	             bidirectional=True, layer_norm=False, drop_out: float = 0.0):
		"""
		:param embed_dim: RNN的input_size，word embedding维度
		:param hidden_size: RNN的hidden_size, RNN隐藏层维度
		:param num_layers: RNN的num_layers, RNN层数
		:param num_layers: RNN的num_layers, RNN层数
		:param rnn: 所用的RNN模型：GRU和LSTM，默认是GRU
		:param layer_norm：是否层正则化
		:param drop_out：
		"""
		
		super().__init__()
		self.layer_norm = layer_norm
		self.rnn = rnn(input_size=embed_dim, hidden_size=hidden_size, num_layers=num_layers,
		               bidirectional=bidirectional, batch_first=True, dropout=drop_out)
		if layer_norm:
			self.norm = nn.LayerNorm((hidden_size << 1) if bidirectional else hidden_size)
			
	def forward(self, inputs: torch.Tensor, sequence_lengths: torch.IntTensor = None):
		"""
		:param inputs: [(batch_size, sequence_length, embed_dim)], sequence_length是不确定的
		:param sequence_lengths: [torch.IntTensor] 序列实际长度
		:return: [(batch_size, sequence_length, 2 * hidden_size)] when bidirectional is True
		:return: [(batch_size, sequence_length, hidden_size)] when bidirectional is False
		"""
		if sequence_lengths is None:
			output, _ = self.rnn(inputs)  # [(batch_size, sequence_length, 2 * hidden_size)]
		else:
			output = pack_padded_sequence(inputs, sequence_lengths, batch_first=True, enforce_sorted=False)
			output, _ = self.rnn(output)
			output, _ = pad_packed_sequence(output, batch_first=True)
			
		if self.layer_norm:
			output = self.norm(output)
		return output
