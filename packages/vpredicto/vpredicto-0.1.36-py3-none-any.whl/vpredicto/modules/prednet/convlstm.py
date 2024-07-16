import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.parameter import Parameter

'''
ConvLSTMCell The main cell in the PredNet model
It has the following methods:
1. init method to initialize the ConvLSTM cell
2. reset_parameters method to reset the parameters of the ConvLSTM cell
3. forward method to compute the next hidden state and next cell state
'''
class ConvLSTMCell(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=None, bias=True):
        super(ConvLSTMCell, self).__init__()
        '''
        in_channels == Number of channels in the input tensor
        out_channels == Number of channels in the hidden state tensor
        kernel_size == Size of the convolutional kernel
        stride == Stride of the convolutional kernel
        padding == Padding of the convolutional kernel
        bias == Boolean value to include bias in the convolutional kernel
        '''
        if padding is None:
            padding = kernel_size // 2  # Default to same padding
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.bias = bias
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.weight_ih = Parameter(torch.Tensor(4 * out_channels, in_channels, kernel_size, kernel_size))
        self.weight_hh = Parameter(torch.Tensor(4 * out_channels, out_channels, kernel_size, kernel_size))
        if bias:
            self.bias_ih = Parameter(torch.Tensor(4 * out_channels))
            self.bias_hh = Parameter(torch.Tensor(4 * out_channels))
        else:
            self.register_parameter('bias_ih', None)
            self.register_parameter('bias_hh', None)

        self.reset_parameters()

    '''
    Method to reset the parameters of the ConvLSTM cell
    '''
    def reset_parameters(self):
        nn.init.xavier_uniform_(self.weight_ih)
        nn.init.xavier_uniform_(self.weight_hh)
        if self.bias_ih is not None:
            nn.init.zeros_(self.bias_ih)
        if self.bias_hh is not None:
            nn.init.zeros_(self.bias_hh)


    def forward(self, input_tensor, hx):
        '''
        Method to compute the next hidden state and next cell state
        input_tensor == Input tensor to the ConvLSTM cell
        hx == Tuple of hidden state and cell state

        output == Tuple of next hidden state and next cell state
        '''
        h_cur, c_cur = hx
        input_tensor, h_cur, c_cur = input_tensor.to(self.device), h_cur.to(self.device), c_cur.to(self.device)

        gates_ih = F.conv2d(input_tensor, self.weight_ih, self.bias_ih, self.stride, self.padding)
        gates_hh = F.conv2d(h_cur, self.weight_hh, self.bias_hh, self.stride, self.padding)
        gates = gates_ih + gates_hh

        ingate, forgetgate, cellgate, outgate = gates.chunk(4, 1)
        ingate = torch.sigmoid(ingate)
        forgetgate = torch.sigmoid(forgetgate)
        cellgate = torch.tanh(cellgate)
        outgate = torch.sigmoid(outgate)

        c_next = forgetgate * c_cur + ingate * cellgate
        h_next = outgate * torch.tanh(c_next)

        return h_next, c_next