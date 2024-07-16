# utils.py

import math
import torch
import numpy as np
from torch.utils.data import DataLoader, Dataset
import os
import cv2
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader, random_split
from torchvision.datasets import MovingMNIST



'''
show_video_line method - Display a video sequence as a line of frames.
it is called from the MIM class
Inputs:
- data: The video data to visualize.
- ncols: The number of columns to display the video frames.
- vmax: The maximum value for the colorbar.
- vmin: The minimum value for the colorbar.
- cmap: The colormap to use for the visualization.
- norm: The normalization function to use for the visualization.
- cbar: Whether to display the colorbar.
- format: The format to save the image in.
- out_path: The path to save the image to.
- use_rgb: Whether to use RGB color channels.
'''
def show_video_line(data, ncols, vmax=0.6, vmin=0.0, cmap='gray', norm=None, cbar=False, format='png', out_path=None, use_rgb=False):
    """generate images with a video sequence"""
    fig, axes = plt.subplots(nrows=1, ncols=ncols, figsize=(3.25 * ncols, 3))
    plt.subplots_adjust(wspace=0.01, hspace=0)

    if len(data.shape) > 3:
        data = data.swapaxes(1,2).swapaxes(2,3)

    images = []
    if ncols == 1:
        if use_rgb:
            im = axes.imshow(cv2.cvtColor(data[0], cv2.COLOR_BGR2RGB))
        else:
            im = axes.imshow(data[0], cmap=cmap, norm=norm)
        images.append(im)
        axes.axis('off')
        im.set_clim(vmin, vmax)
    else:
        for t, ax in enumerate(axes.flat):
            if use_rgb:
                im = ax.imshow(cv2.cvtColor(data[t], cv2.COLOR_BGR2RGB), cmap='gray')
            else:
                im = ax.imshow(data[t], cmap=cmap, norm=norm)
            images.append(im)
            ax.axis('off')
            im.set_clim(vmin, vmax)

    if cbar and ncols > 1:
        cbaxes = fig.add_axes([0.9, 0.15, 0.04 / ncols, 0.7])
        cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.1, cax=cbaxes)

    plt.show()
    if out_path is not None:
        fig.savefig(out_path, format=format, pad_inches=0, bbox_inches='tight')
    plt.close()


'''
patch_images method - Patch images into smaller patches.
it is called from the MIM and ConvLSTM classes
Inputs:
- input_tensor: The input tensor to patch.
- patch_size: The size of the patches to create.
'''
def patch_images(input_tensor , patch_size):
    # Ensure the input tensor has 5 dimensions
    assert 5 == input_tensor.ndim

    # Extract the shape of the input tensor
    batch_size, frames_length, height, width, channels_num = input_tensor.shape

    # Reshape the input tensor to create patches
    input_tensor_reshaped = input_tensor.reshape(batch_size, frames_length,
                                                 height // patch_size, patch_size,
                                                 width // patch_size, patch_size,
                                                 channels_num)

    # Transpose the tensor to reorder dimensions for patching
    input_tensor_reshaped_transpose = input_tensor_reshaped.transpose(3, 4)

    # Reshape the transposed tensor to get the final patched tensor
    patched_input_tensor = input_tensor_reshaped_transpose.reshape(batch_size, frames_length,
                                                                   height // patch_size,
                                                                   width // patch_size,
                                                                   patch_size * patch_size * channels_num)

    # Return the patched tensor
    return patched_input_tensor


'''
patch_images_back method - Revert patches into original images.
it is called from the MIM and ConvLSTM classes
Inputs:
- output_tensor: The output tensor to revert patches.
- patch_size: The size of the patches to revert.
'''
def patch_images_back(output_tensor , patch_size):
    # Extract the shape of the output tensor
    batch_size, frames_length, height, width, channels_num = output_tensor.shape

    # Calculate the original number of channels
    channels = channels_num // (patch_size * patch_size)

    # Reshape the output tensor to revert patches
    output_tensor_reshaped = output_tensor.reshape(batch_size, frames_length,
                                                   height, width,
                                                   patch_size, patch_size,
                                                   channels)

    # Transpose the tensor to reorder dimensions back to original
    output_tensor_transposed = output_tensor_reshaped.transpose(3, 4)

    # Reshape the transposed tensor to get the final image tensor
    out_img = output_tensor_transposed.reshape(batch_size, frames_length,
                                               height * patch_size,
                                               width * patch_size,
                                               channels)

    # Return the final image tensor
    return out_img


'''
schedule_sampling method - Schedule sampling for training.
it is called from the MIM and ConvLSTM classes
Inputs:
- batch_size: The batch size for the input tensor.
- eta: The sampling rate.
- itr: The current iteration.
- args: The arguments for the model.
'''

def schedule_sampling(batch_size, eta, itr, args):
    # Extract shape parameters from the arguments
    T, channels_num, height, width = args["in_shape"]

    # Initialize a tensor of zeros for the input flag
    zeros = np.zeros((batch_size,
                      args["out_frames_length"]-1,
                      height // args["patch_size"],
                      width // args["patch_size"],
                      args["patch_size"] * args["patch_size"] * channels_num))


    # Update eta based on the iteration and sampling stop iteration
    if itr < args["sampling_stop_iter"]:
        eta -= args["sampling_changing_rate"]
    else:
        eta = 0.0

    # Generate random samples for determining true tokens
    random_sample_flipping = np.random.random_sample(
        (batch_size, args["out_frames_length"] - 1))

    # Determine which tokens are true based on eta
    true_token = (random_sample_flipping < eta)

    # Create tensors of ones and zeros for true and false tokens
    ones = np.ones((height // args["patch_size"],
                    width // args["patch_size"],
                    args["patch_size"] * args["patch_size"] * channels_num))
    zeros = np.zeros((height // args["patch_size"],
                      width // args["patch_size"],
                      args["patch_size"] * args["patch_size"] * channels_num))

    # Initialize a list to hold the input flag
    input_flag = []

    # Populate the input flag based on true tokens
    for i in range(batch_size):
        for j in range(args["out_frames_length"] - 1):
            if true_token[i, j]:
                input_flag.append(ones)
            else:
                input_flag.append(zeros)

    # Convert the input flag list to a numpy array
    input_flag = np.array(input_flag)

    # Reshape the input flag array to the required dimensions
    input_flag = np.reshape(input_flag,
                            (batch_size,
                             args["out_frames_length"] - 1,
                             height // args["patch_size"],
                             width // args["patch_size"],
                             args["patch_size"] * args["patch_size"] * channels_num))

    # Convert the input flag to a torch FloatTensor and move it to the specified device
    return eta, torch.FloatTensor(input_flag).to(args["device"])


'''
MovingMNIST class - Dataset class for Moving MNIST dataset.
Inputs:
- root: The root directory of the dataset.
- file_name: The name of the file to load.
- input_frames: The number of input frames.
- output_frames: The number of output frames.
- train_data: Whether the data is for training.
- test_data: Whether the data is for testing.
'''
class MovingMNIST_Class(Dataset):
    def __init__(self, root,file_name ,
                 input_frames=10, output_frames=10,train_data=True,test_data=False):
        super(MovingMNIST, self).__init__()
        # the number of the input frames
        self.input_frames = input_frames
        #the number of the output frames
        self.output_frames = output_frames
         # load the file from the root dir
        self.dataset = np.expand_dims(
            np.load(os.path.join(root, file_name)),
            axis=-1
        )
        # check if the data for training or not to split the data

        if train_data:
            self.dataset = self.dataset[:,:8000]
        elif test_data:
            self.dataset = self.dataset[:,8000:9000]
        else:
            self.dataset = self.dataset[:,9000:]


    def change_torch(self,data_images_in , data_images_out):
      return torch.from_numpy(data_images_in / 255.0).contiguous().float() , torch.from_numpy(data_images_out / 255.0).contiguous().float()



    def __getitem__(self, idx):

        # get the item by the index
        frames_data = self.dataset[:, idx, ...]
        # transpose the item
        frames_data = frames_data.transpose(0, 3, 1, 2)

        # get the total lenght of the frames input and output
        total_lenght = self.input_frames + self.output_frames

        # split the data to the in and out data frames
        in_data = frames_data[:self.input_frames]
        out_data = frames_data[self.input_frames:total_lenght]

        return self.change_torch(in_data , out_data)

    def __len__(self):
        return self.dataset.shape[1]



'''
get_dataset method to get the dataset: you can pass the data root directory, file name, train batch size, validation batch size, test batch size, and number of workers as parameters
The parameters are:
- data_root_dir: The root directory of the dataset.
- file_name: The name of the file to load.
- train_batch_size: The batch size for training.
- val_batch_size: The batch size for validation.
- test_batch_size: The batch size for testing.
- num_workers: The number of workers for the data loader.
- in_length: The number of input frames.
- out_length: The number of output frames.

output: the train, validation, and test data loaders
'''
def get_dataset( data_root_dir , file_name, train_batch_size, val_batch_size , test_batch_size , num_workers=4,
              in_length=10, out_length=10):

    # get the training dataset
    dataset_training = MovingMNIST_Class(root=data_root_dir,file_name=file_name, train_data=True,test_data=False,
                            input_frames=in_length,
                            output_frames=out_length)

    # get the test dataset
    dataset_test = MovingMNIST_Class(root=data_root_dir,file_name=file_name, train_data=False,test_data=True,
                            input_frames=in_length,
                            output_frames=out_length)
    # get the Validation dataset
    dataset_validation = MovingMNIST_Class(root=data_root_dir,file_name=file_name, train_data=False,test_data=False,
                            input_frames=in_length,
                            output_frames=out_length)

    dataloader_train =  DataLoader(
            dataset= dataset_training,
            batch_size=train_batch_size,
            shuffle=True,
            num_workers=num_workers
        )


    dataloader_validation = DataLoader(
            dataset= dataset_validation,
            batch_size=val_batch_size,
            shuffle=False,
            num_workers=num_workers
        )


    dataloader_test =  DataLoader(
            dataset= dataset_test,
            batch_size=test_batch_size,
            shuffle=False,
            num_workers=num_workers
        )

    return dataloader_train, dataloader_validation, dataloader_test



'''
get_data_loaders method to get the train and test data loaders: you can pass the batch size and train size as parameters
the input is the batch size and train size
the output is the train and test data loaders.
'''
def get_data_loaders(batch_size=4, train_size=0.9):
    dataset = MovingMNIST(root='data/', download=True)
    num_samples = len(dataset)
    train_size = int(train_size * num_samples)
    test_size = num_samples - train_size
    input_frames = 10
    predicted_frames = 10
    train_dataset, test_dataset = random_split(dataset[:num_samples], [train_size, test_size])
    x_train, y_train = split_dataset(train_dataset, input_frames, predicted_frames)
    x_test, y_test = split_dataset(test_dataset, input_frames, predicted_frames)
    train_loader = DataLoader(list(zip(x_train, y_train)), batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(list(zip(x_test, y_test)), batch_size=batch_size, shuffle=False)

    return train_loader, test_loader

# Function to split sequence into X and Y
def split_dataset(dataset, input_frames, predicted_frames):
    X, Y = [], []
    for sequence in dataset:
        for i in range(len(sequence) - input_frames - predicted_frames + 1):
            X.append(sequence[i:i+input_frames].float())
            Y.append(sequence[i+input_frames:i+input_frames+predicted_frames].float())
    return torch.stack(X), torch.stack(Y)