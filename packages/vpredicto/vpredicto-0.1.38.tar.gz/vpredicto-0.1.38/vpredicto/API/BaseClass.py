import torch
from ..models.ConvLSTM import ConvLSTMModule
from ..models.MIM import MIMLightningModel
from ..models.PredRNNPlusPlus import PredRNNpp_Model
from ..models.SimVP import SimVP
from ..models.GAN import GANModel
from ..models.PredNet import PredNet
from torch.utils.data import DataLoader, random_split
from torchvision.datasets import MovingMNIST

# Base class for all models
'''
Predicto class is the main class that you will use to train, test, and evaluate the models
it has the following methods:
1. init method to initialize the model and device
2. train method to train the model
3. Predict method to test the model
4. evaluate method to evaluate the model
5. save method to save the model
6. load method to load the model
'''
class Predicto:
    '''
    init method to initialize the model and device: you can pass the model that you chose and device as parameters
    '''
    def __init__(self, model=None, device='cuda'):
        if device == "cuda":
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
            else:
                self.device = torch.device("cpu")
                print("CUDA is not available, CPU will be used")
        else:
            self.device = torch.device("cpu")


        self.model = model.to(self.device) if model else ConvLSTMModule().to(self.device)

    '''
    train method to train the model: you can pass the train_loader, learning rate, and number of epochs as parameters
    the input is the train_loader, learning rate, and number of epochs
    the output is the trained model
    '''
    def train(self, train_loader, lr=0.001, epochs=10):
        self.model.train_model(train_loader, lr, epochs, self.device)

    '''
    predict method to test the model: you can pass the test_loader as a parameter
    the input is the test_loader
    the output is the output of test data from the model
    '''
    def Predict(self, test_loader, save=True):
        self.model.test_model(test_loader, self.device, save=save)


    '''
    evaluate method to evaluate the model: you can pass the test_loader as a parameter
    the input is the test_loader
    the output is the evaluation of the model
    '''
    # We can do it in the base class (same logic)
    def evaluate(self, test_loader, SSIM=False, MSE=True, PSNR= False): # Here Adding any new evaluation metric
        if SSIM:
            self.model.evaluate_ssim(test_loader, self.device)
        if MSE:
            self.model.evaluate_MSE(test_loader, self.device)
        if PSNR:
            self.model.evaluate_PSNR(test_loader, self.device)
        # else:
        #     self.model.test_model(test_loader, self.device)

    '''
    save method to save the model: you can pass the path as a parameter
    the input is the path
    the output is the saved model
    '''
    def save(self, path='model.pth'):
        if isinstance(self.model, GANModel):
            torch.save(self.model.generator.state_dict(), path)
            print(f"Generator model saved to {path}")
        else:
            torch.save(self.model.state_dict(), path)
            print(f"Model saved to {path}")
    '''
    load method to load the model: you can pass the path as a parameter
    the input is the path
    the output is the saved model
    '''
    def load(self, path='model.pth'):
        if isinstance(self.model, GANModel):
            self.model.generator.load_state_dict(torch.load(path, map_location=self.device))
            print(f"Generator model loaded from {path}")
        elif isinstance(self.model, SimVP):
            try:
                self.model.load_state_dict(torch.load(path, map_location=self.device))
                print(f"Model loaded from {path}")
            except Exception as e:
                model_state = torch.load(path)
                if 'model_state_dict' in model_state:
                    self.model.load_state_dict(model_state['model_state_dict'])
                else:
                    self.model.load_state_dict(model_state)
        else:
            self.model.load_state_dict(torch.load(path, map_location=self.device))
            print(f"Model loaded from {path}")


    '''
    load_pkl method to load the model from a .pkl file: you can pass the path as a parameter
    the input is the path to the .pkl file
    the output is the loaded model
    '''
    def load_pkl(self, pkl_file_path='model.pkl'):
        state_dict = torch.load(pkl_file_path)
        self.model.load_state_dict(state_dict)
        print(f"Model loaded from {pkl_file_path}")

