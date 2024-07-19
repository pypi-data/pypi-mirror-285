from typing import List, Union

import numpy as np
import torch
from numpy import ndarray
from torch import Tensor
from torch_geometric.utils import add_self_loops

from tsl.nn.layers.graph_convs.gpvar import GraphPolyVAR
from tsl.ops.graph_generators import build_tri_community_graph

from .synthetic import GaussianNoiseSyntheticDataset


class _GPVAR(GraphPolyVAR):

    def forward(self, x, edge_index, edge_weight=None):
        out = super(_GPVAR, self).forward(x, edge_index, edge_weight)
        return torch.tanh(out)


class GPVARDataset(GaussianNoiseSyntheticDataset):
    """Generator for synthetic datasets from a graph polynomial VAR filter on
    triangular community graphs as shown in the paper `"AZ-whiteness test: a
    test for uncorrelated noise on spatio-temporal graphs"
    <https://arxiv.org/abs/2204.11135>`_ (Zambon et al., NeurIPS 22).

    Args:
        num_communities (int): Number of communities (triangles) in the graph.
        num_steps (int): Length of the generated sequence.
        filter_params (iterable): Parameters of the graph polynomial filter
            used to generate the dataset.
        sigma_noise (float): Standard deviation of the noise.
        norm (str): The normalization used for edges and edge weights. The
            available options are: :obj:`'gcn'`, :obj:`'asym'` and
            :obj:`'none'`.
            (default: :obj:`'none'`)
        name (optional, str): Name of the dataset.
    """

    def __init__(self,
                 num_communities: int,
                 num_steps: int,
                 filter_params: Union[List, Tensor, ndarray],
                 sigma_noise: float = .2,
                 norm: str = 'none',
                 name: str = None):
        if name is None:
            name = "GP-VAR"
        node_idx, edge_index, _ = build_tri_community_graph(
            num_communities=num_communities)
        num_nodes = len(node_idx)
        # add self loops
        edge_index, _ = add_self_loops(edge_index=torch.tensor(edge_index),
                                       num_nodes=num_nodes)

        if not isinstance(filter_params, Tensor):
            filter_params = torch.as_tensor(filter_params, dtype=torch.float32)

        filter = _GPVAR.from_params(filter_params=filter_params,
                                    norm=norm,
                                    cached=True)
        super(GPVARDataset, self).__init__(num_features=1,
                                           num_nodes=num_nodes,
                                           num_steps=num_steps,
                                           connectivity=edge_index,
                                           min_window=filter.temporal_order,
                                           model=filter,
                                           sigma_noise=sigma_noise,
                                           name=name)


class GPVARDatasetAZ(GPVARDataset):
    """:class:`~tsl.datasets.GPVARDataset` generated with the same configuration
    used in the paper `"AZ-whiteness test: a test for uncorrelated noise on
    spatio-temporal graphs" <https://arxiv.org/abs/2204.11135>`_ (Zambon et al.,
    NeurIPS 22).

    Args:
        root (str, optional): Path to the directory to use for data storage.
            (default: :obj:`None`)
    """
    seed = 1234
    NUM_COMMUNITIES = 5
    NUM_STEPS = 30000
    SIGMA_NOISE = 0.4

    def __init__(self, root: str = None):
        self.root = root
        filter_params = [[5., 2.], [-4., 6.], [-1., 0.]]
        super(GPVARDatasetAZ,
              self).__init__(num_communities=self.NUM_COMMUNITIES,
                             num_steps=self.NUM_STEPS,
                             filter_params=filter_params,
                             sigma_noise=self.SIGMA_NOISE,
                             norm='none',
                             name='GPVAR-AZ')

    @property
    def required_file_names(self):
        return ['GPVAR_AZ.npy']

    def build(self) -> None:
        x, y_opt, _ = self.generate_data(seed=self.seed)
        np.save(self.required_files_paths[0], np.stack([x, y_opt]))

    def load_raw(self, *args, **kwargs):
        self.maybe_build()
        x, y_opt = np.load(self.required_files_paths[0])
        return x, y_opt, np.ones_like(x)
