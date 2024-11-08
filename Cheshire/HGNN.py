import torch
import torch.nn as nn
import torch.nn.functional as F
from HGNN_layers import HGNN_embedding, HGNN_classifier, HGNN_conv
from utils import create_hyperedge_index
from HGNN_utils import *


class HGNN(nn.Module):
    def __init__(self, input_dim, hidden_dim, n_class=1, dropout=0.5):
        super(HGNN, self).__init__()
        self.embedding = HGNN_embedding(input_dim[1], hidden_dim, dropout)
        self.classifier = HGNN_classifier(hidden_dim, n_class)

    def forward(self, feature, incidence_matrix):
        H = incidence_matrix.cpu().numpy()
        G_np = generate_G_from_H(H, variable_weight=False) 
        G = torch.tensor(G_np, dtype=torch.float, device=feature.device)

        x = self.embedding(feature, G) 

        reaction_features = torch.matmul(incidence_matrix.T, x) 
        reaction_features = reaction_features / (incidence_matrix.T.sum(dim=1, keepdim=True) + 1e-5) 

        output = self.classifier(reaction_features)
        return torch.sigmoid(output).squeeze()