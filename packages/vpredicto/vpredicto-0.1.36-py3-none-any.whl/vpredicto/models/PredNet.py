import torch
from torch import nn
from ..modules.prednet.convlstm import ConvLSTMCell
import torch.optim as optim
import torch.nn.functional as F
from tqdm import tqdm
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import numpy as np
import os

'''
PredNet is the main class that you will use to train, test, and evaluate the PredNet model
it has the following methods:
1. init method to initialize the model and device
2. forward method to pass the input to the model
3. train_model method to train the model
4. test_model method to test the model
5. evaluate_model method to evaluate the model
'''
class PredNet(nn.Module):
    def __init__(self, layer_sizes=[1,16,32,64]):
        super(PredNet, self).__init__()
        self.layer_sizes = layer_sizes
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        layers_list=[]
        conv_list=[]
        conv_e_list=[]
        for i, size in enumerate(layer_sizes[:-1]):
            layers_list.append(ConvLSTMCell(3 * size, size, kernel_size=3, padding=1).to(self.device))
            conv_list.append(nn.Conv2d(size, size, kernel_size=3, padding=1).to(self.device))
            conv_e_list.append(nn.Conv2d(2*size, layer_sizes[i + 1], kernel_size=3, padding=1).to(self.device))
        self.layers = nn.ModuleList(layers_list)
        self.conv = nn.ModuleList(conv_list)
        self.conv_e = nn.ModuleList(conv_e_list)
        self.downsample = nn.MaxPool2d(kernel_size=2, stride=2)
        self.upsample = nn.Upsample(scale_factor=2, mode='nearest')

    def forward(self, x):
        batch_size, sequence_length, _, height, width = x.shape
        outputs = []
        predicted_frame = torch.zeros(batch_size, self.layer_sizes[0], height, width, device=self.device)
        R = [torch.zeros(batch_size, size, height // (2 ** i), width // (2 ** i), device=self.device) for i, size in enumerate(self.layer_sizes)]
        H = [torch.zeros(batch_size, size, height // (2 ** i), width // (2 ** i), device=self.device) for i, size in enumerate(self.layer_sizes)]
        E = [torch.zeros(batch_size, 2 * size, height // (2 ** i), width // (2 ** i), device=self.device) for i, size in enumerate(self.layer_sizes)]
        
        for t in range(sequence_length):
            A = x[:, t, :, :, :].to(self.device)
            for i in reversed(range(len(self.layer_sizes) - 1)):
                layer_input = torch.cat([E[i], R[i]], dim=1)
                if i < len(self.layer_sizes) - 2:
                    upsampled = self.upsample(R[i + 1])
                    layer_input = torch.cat([layer_input, upsampled], dim=1)
                if i == len(self.layer_sizes) - 2:
                    R[i], H[i] = self.layers[i](layer_input, (R[i], R[i]))
                else:
                    R[i], H[i] = ConvLSTMCell(3 * self.layer_sizes[i] + self.layer_sizes[i + 1], self.layer_sizes[i], kernel_size=3, padding=1).to(self.device)(layer_input, (R[i], R[i]) if t == 0 else (H[i], H[i]))
            
            for i in range(len(self.layer_sizes) - 1):
                A_hat = F.relu(self.conv[i](R[i]))
                if i == 0:
                    A_hat = torch.clamp(A_hat, min=0, max=1.0)
                    predicted_frame = A_hat
                
                pos_diff = F.relu(torch.subtract(A_hat, A))
                neg_diff = F.relu(torch.subtract(A, A_hat))
                E[i] = torch.cat([neg_diff, pos_diff], dim=1)

                if i < len(self.layer_sizes) - 2:
                    A = self.downsample(self.conv_e[i](E[i]))
            outputs.append(predicted_frame.unsqueeze(1))
        
        return torch.cat(outputs, dim=1)


    '''
    train_model method to train the model: you can pass the train_loader, learning rate, and number of epochs as parameters
    It is the method that it will be called from the API - Predicto
    '''
    def train_model(self, train_loader, lr=0.001, epochs=10, device='cuda'):
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.parameters(), lr=lr)
        self.to(device)
        self.train()
        for epoch in range(epochs):
            train_loader = tqdm(train_loader , desc=f"Epoch {epoch+1}/{epochs}")
            self.train()
            for batch in train_loader:
                inputs, targets = batch
                inputs = inputs.to(device)
                targets = targets.to(device)

                optimizer.zero_grad()
                outputs = self(inputs)
                loss = criterion(outputs, targets)  # Adjust loss calculation
                loss.backward()
                optimizer.step()
                train_loader.set_postfix(loss=loss.item())
            print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')


    '''
    test_model method to test the model: you can pass the test_loader as a parameter
    It is the method that it will be called from the API - Predicto
    '''
    def test_model(self, test_loader, device='cpu', save=True):
        self.eval()
        total_loss = 0.0
        criterion = nn.MSELoss()
        self.to(device)

        save_dir = 'pred_results'
        if save and not os.path.exists(save_dir):
            os.makedirs(save_dir)

        all_output_frames = []

        with torch.no_grad():
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = self(inputs)
                loss = criterion(outputs, labels)
                total_loss += loss.item()

                # Show sample predictions and save if specified
                for i in range(min(3, inputs.size(0))):  # Show up to 3 samples
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

                break 

        print(f"Test Loss: {total_loss / len(test_loader)}")
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

        print(f'Test Loss: {avg_loss:.4f}, SSIM: {avg_ssim:.4f}, PSNR: {avg_psnr:.4f}')
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