import torch
from torch import nn
from torch.nn import functional as F


class TextCNN(nn.Module):
    """
    Examples
    --------
    >>> import torch
    >>> from nlpx.models import TextCNN
    >>> X = torch.randn(batch_size, 10, word_dim)
    >>> targets = torch.randint(0, num_classes, (batch_size,))
    >>> model = TextCNN(embed_dim, cnn_channels=64, kernel_sizes=(2, 3, 4), out_features=num_classes)
    >>> output = model(X)
    >>> loss, output = model(X, targets)
    """

    def __init__(self, embed_dim: int, kernel_sizes=(2, 3, 4), cnn_channels: int = 64, out_features: int = 2,
                 activation=nn.ReLU(inplace=True), num_hidden_layer: int = 0, batch_norm=False, layer_norm=False,
                 residual=False, drop_out: float = 0.0):
        """ TextCNN model
        
        Parameters
        ----------
        embed_dim: int, dim of embedding, in_channels of cnn
        cnn_channels: int, out_channels of cnn
        kernel_sizes: size of each cnn kernel
        out_features: dim of output
        activation:
        num_hidden_layer:
		residual: 是否残差
        drop_out:
        """
        super().__init__()
        self.residual = residual
        self.num_hidden_layer = num_hidden_layer or 0
        if batch_norm:
            self.convs = nn.ModuleList([
                nn.Sequential(
                    nn.Conv1d(in_channels=embed_dim, out_channels=cnn_channels, kernel_size=kernel_size, bias=False),
                    nn.BatchNorm1d(num_features=cnn_channels),
                    activation,  # inplace为True，将会改变输入的数据 ，否则不会改变原输入，只会产生新的输出
                    nn.AdaptiveMaxPool1d(1)
                ) for kernel_size in kernel_sizes
            ])
        else:
            self.convs = nn.ModuleList([
                nn.Sequential(
                    nn.Conv1d(in_channels=embed_dim, out_channels=cnn_channels, kernel_size=kernel_size, bias=False),
                    activation,  # inplace为True，将会改变输入的数据 ，否则不会改变原输入，只会产生新的输出
                    nn.AdaptiveMaxPool1d(1)
                ) for kernel_size in kernel_sizes
            ])

        num_features = cnn_channels * len(kernel_sizes)
        fc_features = num_features
        if self.num_hidden_layer > 0:
            if residual:
                fc_features = fc_features << 1
            if layer_norm:
                self.hidden_layers = nn.ModuleList([
                    nn.Sequential(
                        nn.Linear(in_features=num_features, out_features=num_features),
                        nn.LayerNorm(normalized_shape=num_features),
                        activation
                    ) for _ in range(num_hidden_layer)
                ])
            else:
                self.hidden_layers = nn.ModuleList([
                    nn.Sequential(
                        nn.Linear(in_features=num_features, out_features=num_features),
                        activation
                    ) for _ in range(num_hidden_layer)
                ])

        self.fc = nn.Linear(in_features=fc_features, out_features=out_features)
        if 0.0 < drop_out < 1.0:
            self.fc = nn.Sequential(
                nn.Dropout(drop_out),
                self.fc
            )

    def forward(self, inputs: torch.Tensor, labels: torch.LongTensor = None):
        """
        :param inputs: [(batch_size, sequence_length, embed_dim)]
        :param labels: [long]
        """

        # Conv1d期望输入的形状是：(batch_size, embed_dim, sequence_length)
        input_embeddings = inputs.transpose(2, 1)

        # conv输出的形状是：(batch_size, cnn_channels, 1)
        # output的形状是：(batch_size, cnn_channels * len(kernel_sizes), 1)
        output = torch.cat([conv(input_embeddings) for conv in self.convs], dim=1)

        # 确保张量是连续的
        output = output.contiguous()
        # output：(batch_size, cnn_channels * len(kernel_sizes))
        output = output.view(inputs.size(0), -1)

        if self.num_hidden_layer > 0:
            hidden_output = output
            for hidden_layer in self.hidden_layers:
                hidden_output = hidden_layer(hidden_output)
            if self.residual:
                logits = self.fc(torch.cat((output, hidden_output), dim=1))
            else:
                logits = self.fc(output)
        else:
            logits = self.fc(output)

        if labels is None:
            return logits

        loss = F.cross_entropy(logits, labels)
        return loss, logits
