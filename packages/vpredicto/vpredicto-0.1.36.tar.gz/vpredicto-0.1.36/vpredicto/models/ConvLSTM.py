from torchvision.datasets.utils import download_url
import torch
import torch.utils.data
from torch.utils.data import DataLoader, Dataset
import torch.nn as nn
import torch.optim as optim
from pytorch_lightning import LightningModule, Trainer
from pytorch_lightning.loggers import TensorBoardLogger
import os
import pytorch_lightning as pl
from ..Utils.utils import show_video_line, patch_images, patch_images_back, schedule_sampling
from ..modules.convlstm.conv import ConvLSTM
# from ..modules.convlstm.cell import ConvLSTMCell
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import numpy as np
import os



'''
ConvLSTMModule is the main class that you will use to train, test, and evaluate the ConvLSTM model
it has default configs that you can change and pass to the model or even call the model without passing any configs
it has the following methods:
1. init method to initialize the model and device
2. forward method to pass the input to the model
3. training_step method to train the model
4. configure_optimizers method to configure the optimizer
5. validation_step method to validate the model
6. test_step method to test the model
7. train_model method to train the model
8. test_model method to test the model
9. evaluate_model method to evaluate the model
'''
class ConvLSTMModule(LightningModule):
    def __init__(self, model = None, configs = None, lr=0.001):
        super(ConvLSTMModule, self).__init__()
        self.configs = configs or {
            'in_shape': [10, 1, 64, 64],
            'filter_size': 5,
            'stride': 1,
            'patch_size':2,
            'in_frames_length': 10,
            'out_frames_length': 10,
            "total_length":20,
            "batch_size" : 16,
            "r_sampling_step_1" : 25000,
            "r_sampling_step_2" : 50000,
            "r_exp_alpha" : 5000,
            "sampling_stop_iter" : 50000,
            "sampling_start_value" : 1.0,
            "sampling_changing_rate" : 0.00002,
            'device':"cuda"
        }
        self.model = model or ConvLSTM(configs=configs)
        self.lr = lr
        self.eta = 1.0
        self.criterion = nn.MSELoss()
        # in the init method, print the default configs of the model
        if configs is None:
            print("Default Configs of the Model \n")
            print(self.configs)


    def forward(self, x, mask_true):


        mask_input = self.configs["in_frames_length"]
        _, channels, height, width = self.configs["in_shape"]

        # preprocess
        test_ims = torch.cat([x, mask_true], dim=1).permute(0, 1, 3, 4, 2).contiguous()
        test_dat = patch_images(test_ims, self.configs["patch_size"]) # frames tensor
        test_ims = test_ims[:, :, :, :, :channels]

        real_input_flag = torch.zeros(
            (x.shape[0],
            self.configs["total_length"] - mask_input - 1,
            height // self.configs["patch_size"],
            width // self.configs["patch_size"],
            self.configs["patch_size"] ** 2 * channels)).to(self.device)

        new_frames, _ = self.model(test_dat , real_input_flag)

        new_frames = patch_images_back(new_frames, self.configs["patch_size"])

        pred_frames = new_frames[:, -self.configs["out_frames_length"]:].permute(0, 1, 4, 2, 3).contiguous()

        return pred_frames

    # Training Step is the main method that will return the loss of the model
    def training_step(self, batch, batch_idx):
        frames, mask_true = batch
        test_ims = torch.cat([frames, mask_true], dim=1).permute(0, 1, 3, 4, 2).contiguous()

        test_dat = patch_images(test_ims, self.configs["patch_size"]) # frames tensor

        self.eta, real_input = schedule_sampling( test_dat.shape[0], self.eta, self.global_step, self.configs)

        new_frames , loss = self.model(test_dat, real_input)

        self.log('val_loss', loss, on_step=True, on_epoch=True, prog_bar=False)

        return loss

    # Configure Optimizers is the method that will return the optimizer of the model
    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=self.lr)
        return optimizer

    # Validation Step is the method that will return the loss of the model in the validation step
    def validation_step(self, batch, batch_idx):
        frames, mask_true = batch
        pred_frames = self(frames, mask_true)
        loss = self.criterion(pred_frames, mask_true)
        self.log('val_loss', loss, on_step=True, on_epoch=True, prog_bar=False)
        return loss

    # Test Step is the method that will return the output of the model in the test step
    def test_step(self, batch, batch_idx):
        frames, mask_true = batch
        pred_frames = self(frames, mask_true)
        outputs = {'inputs': frames.cpu().numpy(), 'preds': pred_frames.cpu().numpy(), 'trues': mask_true.cpu().numpy()}
        return outputs

    '''
    train_model method is the method that is called from the Predicto class to train the model
    '''
    def train_model(self, train_loader, lr=0.001, epochs=10, device='cpu'):
        self.to(device)
        self.lr = lr
        logger = TensorBoardLogger('tb_logs', name='ConvLSTM9')
        trainer = Trainer(max_epochs=epochs, logger=logger , devices=[0], accelerator="gpu")
        trainer.fit(self, train_loader)

    '''
    test_model method is the method that is called from the Predicto class to test the model
    '''
    def test_model(self, test_loader, device='cpu', save=True):
        self.to(device)
        self.eval()
        pre_seq_length = self.configs['in_frames_length']
        aft_seq_length = self.configs['out_frames_length']

        save_dir='pred_images'
        if save and not os.path.exists(save_dir):
            os.makedirs(save_dir)

        all_output_frames = []

        for batch_idx, batch in enumerate(test_loader):
            frames, mask_true = batch
            frames = frames.to(device)
            mask_true = mask_true.to(device)

            print('>' * 35 + ' Input ' + '<' * 35)
            show_video_line(frames[0].cpu().numpy(), ncols=pre_seq_length, vmax=0.6, cbar=False, out_path=None, format='png', use_rgb=True)

            print('>' * 35 + ' True Output ' + '<' * 35)
            show_video_line(mask_true[0].cpu().numpy(), ncols=aft_seq_length, vmax=0.6, cbar=False, out_path=None, format='png', use_rgb=True)

            with torch.no_grad():
                pred_y = self(frames, mask_true)
                all_output_frames.append(pred_y.cpu())

            print('>' * 35 + ' Predicted Output ' + '<' * 35)
            show_video_line(pred_y[0].cpu().numpy(), ncols=aft_seq_length, vmax=0.6, cbar=False, out_path=None, format='png', use_rgb=False)

            if save:
                save_path = os.path.join(save_dir, f'batch_{batch_idx}_output.png')
                show_video_line(pred_y[0].cpu().numpy(), ncols=aft_seq_length, vmax=0.6, cbar=False, out_path=save_path, format='png', use_rgb=False)

            break  # Only visualize for the first batch

        return torch.cat(all_output_frames, dim=0)

    '''
    evaluate_model method is the method that is called to evaluate the model from the PSNR, SSIM, and MSE metrics
    '''
    def evaluate_model(self, test_loader, criterion, pred_frames, device='cuda'):
        self.eval()
        total_loss = 0
        ssim_scores = []
        psnr_scores = []
        with torch.no_grad():
            for batch in test_loader:
                inputs, targets = batch
                inputs = inputs.to(device)
                targets = targets.to(device)

                outputs = self(inputs, targets)  # Unpack both values, use only the outputs here

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

    def evaluate_ssim(self, test_loader, device='cpu'):
        _, ssim, __ = self.evaluate_model(test_loader, nn.MSELoss(), 10, device)
        print(f'Average SSIM: {ssim:.4f}')

    def evaluate_MSE(self, test_loader, device='cpu'):
        mse, _, __ = self.evaluate_model(test_loader, nn.MSELoss(), 10, device)
        print(f'Average MSE: {mse:.4f}')

    def evaluate_PSNR(self, test_loader, device='cpu'):
        __, __, psnr = self.evaluate_model(test_loader, nn.MSELoss(), 10, device)
        print(f'Average PSNR: {psnr:.4f}')

