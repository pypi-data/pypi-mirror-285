import torch
import torch.nn as nn
import torch.optim as optim
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import numpy as np
import matplotlib.pyplot as plt
from ..modules.predrnnpp.ghu import GHU
from ..modules.predrnnpp.causal_lstm import CausalLSTMCell
import os
from tqdm import tqdm

'''
PredRNN++ Model
__init__ method to initialize the PredRNN++ Model: you can pass the input_channels, hidden_channels, kernel_size, num_layers, and output_channels as parameters
forward method to pass the input and hidden state through the PredRNN++ Model
the input is the input and hidden state
the output is the predicted frames
'''
class PredRNNpp_Model(nn.Module):
    def __init__(self, input_channels=1, hidden_channels=64, kernel_size=3, num_layers=4, output_channels=1):
        super(PredRNNpp_Model, self).__init__()
        self.hidden_channels = hidden_channels
        self.num_layers = num_layers

        # Initial convolution to get the hidden state
        self.initial_conv = nn.Conv2d(input_channels, hidden_channels, kernel_size=3, padding=1)
        
        # Causal LSTM cells
        self.cells = nn.ModuleList([
            CausalLSTMCell(hidden_channels, hidden_channels, kernel_size)
            for _ in range(num_layers)
        ])
        # GHU for the first layer
        self.ghu = GHU(hidden_channels, hidden_channels, kernel_size)
        # Final convolution to get the output
        self.final_conv = nn.Conv2d(hidden_channels, output_channels, kernel_size=3, padding=1)

    def forward(self, x, pred_frames=10):
        '''
        x is the input sequence
        pred_frames is the number of frames to predict after the initial sequence
        '''
        batch_size, seq_len, _, height, width = x.size()

        h_t = [torch.zeros(batch_size, self.hidden_channels, height, width).to(x.device) for _ in range(self.num_layers)]
        c_t = [torch.zeros(batch_size, self.hidden_channels, height, width).to(x.device) for _ in range(self.num_layers)]
        m_t = torch.zeros(batch_size, self.hidden_channels, height, width).to(x.device)

        z_t = None
        outputs = []

        # Encode the input sequence
        for t in range(seq_len):
            x_t = x[:, t, :, :, :]
            x_t = self.initial_conv(x_t)

            h_t[0], c_t[0], m_t = self.cells[0](x_t, h_t[0], c_t[0], m_t)
            for i in range(1, self.num_layers):
                if i == 1:
                    z_t = self.ghu(x_t, z_t)
                    x_t = z_t
                h_t[i], c_t[i], m_t = self.cells[i](h_t[i-1], h_t[i], c_t[i], m_t)

            outputs.append(h_t[-1].unsqueeze(1))

        # Predict future frames
        for t in range(pred_frames):
            x_t = self.final_conv(h_t[-1])  # Use the last hidden state to predict next frame
            x_t = self.initial_conv(x_t)

            h_t[0], c_t[0], m_t = self.cells[0](x_t, h_t[0], c_t[0], m_t)
            for i in range(1, self.num_layers):
                if i == 1:
                    z_t = self.ghu(x_t, z_t)
                    x_t = z_t
                h_t[i], c_t[i], m_t = self.cells[i](h_t[i-1], h_t[i], c_t[i], m_t)

            outputs.append(h_t[-1].unsqueeze(1))

        outputs = torch.cat(outputs, dim=1)
        final_outputs = []

        # Apply final_conv to each time step separately
        for t in range(outputs.size(1)):
            final_outputs.append(self.final_conv(outputs[:, t, :, :, :]).unsqueeze(1))

        final_outputs = torch.cat(final_outputs, dim=1)
        return final_outputs[:, -pred_frames:]  # Return only the predicted frames

    '''
    train_model method to train the model: you can pass the train_loader, learning rate, and number of epochs as parameters
    It is the method that it will be called from the API - Predicto
    '''
    def train_model(self, train_loader, lr=0.001, epochs=10, device='cpu'):
        '''
        Train_loader is the DataLoader object for training data
        lr is the learning rate
        epochs is the number of epochs to train the model
        device is the device to train the model on
        '''
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.parameters(), lr=lr)
        self.to(device)

        num_epochs = epochs
        pred_frames = 10  # Number of frames to predict after the initial sequence

        # Training loop
        for epoch in range(0, num_epochs):
            self.train()
            train_loader = tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs} - Training')
            for batch in train_loader:
                inputs, targets = batch
                inputs = inputs.to(device)
                targets = targets.to(device)

                optimizer.zero_grad()
                outputs = self(inputs, pred_frames=pred_frames)  # Include pred_frames argument
                loss = criterion(outputs, targets)  # Adjust loss calculation
                loss.backward()
                optimizer.step()

            # Print loss after each epoch
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')


    '''
    test_model method to test the model: you can pass the test_loader as a parameter
    It is the method that it will be called from the API - Predicto
    '''
    def test_model(self, test_loader, device='cpu', save=True):
        self.eval()
        total_loss = 0.0
        criterion = nn.MSELoss()
        self.to(device)

        save_dir = 'output_frames'
        if save and not os.path.exists(save_dir):
            os.makedirs(save_dir)

        all_output_frames = []

        with torch.no_grad():
            for batch_idx, (inputs, labels) in enumerate(test_loader):
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = self(inputs)
                loss = criterion(outputs, labels)
                total_loss += loss.item()
                all_output_frames.append(outputs.cpu())

                # if save:
                for i in range(min(3, inputs.size(0))):  # Save up to 3 samples
                    input_seq = inputs[i].cpu().numpy().squeeze()
                    target_seq = labels[i].cpu().numpy().squeeze()
                    output_seq = outputs[i].cpu().numpy().squeeze()

                    fig, axes = plt.subplots(3, input_seq.shape[0], figsize=(15, 5))
                    for t in range(input_seq.shape[0]):
                        axes[0, t].imshow(input_seq[t], cmap='gray')
                        axes[0, t].axis('off')
                        axes[0, t].set_title(f'Input {t+1}')

                        axes[1, t].imshow(output_seq[t], cmap='gray')
                        axes[1, t].axis('off')
                        axes[1, t].set_title(f'Output {t+1}')

                        axes[2, t].imshow(target_seq[t], cmap='gray')
                        axes[2, t].axis('off')
                        axes[2, t].set_title(f'Target {t+1}')

                    plt.tight_layout()
                    plt.show()

                    if save:
                        save_path = os.path.join(save_dir, f'batch_{i}_outputs.pt')
                        torch.save({
                            'input_seq': input_seq,
                            'output_seq': output_seq,
                            'target_seq': target_seq
                        }, save_path)
                        print(f"Saved predictions for batch {i} to {save_path}")

                    all_output_frames.append(outputs.cpu())

                break  # Only visualize and save for the first batch

        print(f"Test Loss: {total_loss / len(test_loader)}")

        # Save all output frames as a tensor
        if save:
            all_outputs = torch.cat(all_output_frames, dim=0)
            torch.save(all_outputs, os.path.join(save_dir, 'all_output_frames.pt'))

        return torch.cat(all_output_frames, dim=0)


    '''
    evaluate_model is the method that will evaluate the model and return the evaluation metrics
    This method that is called from the SSIM, MSE, and PSNR methods if it is called from the Predicto class
    '''
    def evaluate_model(self, test_loader, criterion, pred_frames, device='cuda'):
        self.eval()
        self.to(device)
        total_loss = 0
        ssim_scores = []
        psnr_scores = []
        with torch.no_grad():
            for batch in test_loader:
                inputs, targets = batch
                inputs = inputs.to(device)
                targets = targets.to(device)

                outputs = self(inputs)
                loss = criterion(outputs[:, -pred_frames:], targets)
                total_loss += loss.item()

                for i in range(outputs.size(0)):
                    output = outputs[i, -pred_frames:].cpu().numpy().squeeze()
                    target = targets[i].cpu().numpy().squeeze()

                    # Compute SSIM and PSNR
                    ssim_scores.append(ssim(output, target, data_range=target.max() - target.min()))
                    psnr_scores.append(psnr(output, target, data_range=target.max() - target.min()))

        avg_loss = total_loss / len(test_loader)
        avg_ssim = np.mean(ssim_scores)
        avg_psnr = np.mean(psnr_scores)

        # print(f'Test Loss: {avg_loss:.4f}, SSIM: {avg_ssim:.4f}, PSNR: {avg_psnr:.4f}')
        return avg_loss, avg_ssim, avg_psnr

    def evaluate_ssim(self, test_loader, device='cuda'):
        _, ssim, __ = self.evaluate_model(test_loader, nn.MSELoss(), 10, device)
        print(f'Average SSIM: {ssim:.4f}')

    def evaluate_MSE(self, test_loader, device='cuda'):
        mse, _, __ = self.evaluate_model(test_loader, nn.MSELoss(), 10, device)
        print(f'Average MSE: {mse:.4f}')

    def evaluate_PSNR(self, test_loader, device='cuda'):
        __, __, psnr = self.evaluate_model(test_loader, nn.MSELoss(), 10, device)
        print(f'Average PSNR: {psnr:.4f}')