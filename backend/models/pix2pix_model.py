import torch
import torch.nn as nn

class UNetGenerator(nn.Module):
    def __init__(self, in_channels=3, out_channels=3, features=64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, features, 4, 2, 1),
            nn.ReLU(),
            nn.Conv2d(features, features * 2, 4, 2, 1),
            nn.ReLU(),
            nn.Conv2d(features * 2, features * 4, 4, 2, 1),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(features * 4, features * 2, 4, 2, 1),
            nn.ReLU(),
            nn.ConvTranspose2d(features * 2, features, 4, 2, 1),
            nn.ReLU(),
            nn.ConvTranspose2d(features, out_channels, 4, 2, 1),
            nn.Tanh()
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x