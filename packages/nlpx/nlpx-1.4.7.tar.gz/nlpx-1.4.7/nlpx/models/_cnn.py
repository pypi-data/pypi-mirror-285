import torch
from torch import nn


class CNNLayer(nn.Module):
	
	def __init__(self, embed_dim: int, seq_length: int = 16, out_channels: int = None, kernel_sizes=(2, 3, 4),
	             activation=nn.ReLU(inplace=True), layer_norm=False, bias=False):
		"""
		:param embed_dim: word embedding维度
		:param seq_length: 句子序列长度
		:param out_channels: CNN out_channels, default embed_dim
		:param kernel_sizes: size of each CNN kernel
		:param activation: CNN 激活函数
		:param layer_norm: 是否层正则化
		:param bias:
		"""
		super().__init__()
		self.layer_norm = layer_norm
		out_channels = out_channels or embed_dim
		self.convs = nn.ModuleList([
			nn.Sequential(
				nn.Conv1d(in_channels=embed_dim, out_channels=out_channels, kernel_size=kernel_size, bias=bias),
				activation,  # inplace为True，将会改变输入的数据 ，否则不会改变原输入，只会产生新的输出
				nn.AdaptiveMaxPool1d(seq_length)
			) for kernel_size in kernel_sizes
		])
		if layer_norm:
			self.norm = nn.LayerNorm(out_channels)
	
	def forward(self, inputs: torch.Tensor):
		"""
		:param inputs: [(batch_size, sequence_length, embed_dim)]
		:return: [(batch_size, seq_length * len(kernel_sizes), out_channels)]
		"""
		inputs = inputs.transpose(2, 1)
		output = torch.cat([conv(inputs) for conv in self.convs], dim=-1)
		output = output.transpose(2, 1)
		if self.layer_norm:
			output = self.norm(output)
		return output
