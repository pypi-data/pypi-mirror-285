import torch

def halfedges(F):
    """Given a triangle mesh with face indices F, returns all oriented halfedges
    as indices into the vertex array using PyTorch.

    The ordering convention for halfedges is the following:
    [halfedge opposite vertex 0,
     halfedge opposite vertex 1,
     halfedge opposite vertex 2]

    Parameters
    ----------
    F : (m,3) torch int tensor
        face index list of a triangle mesh

    Returns
    -------
    he : (m,3,2) torch int tensor
        halfedge list as per above conventions

    Examples
    --------
    ```python
    # Sample mesh
    v = torch.tensor([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    f = torch.tensor([[0, 1, 2]], dtype=torch.int)
    # Call to halfedges
    he = halfedges(f)
    ```
    """
    
    assert F.shape[0] > 0
    assert F.shape[1] == 3

    he = torch.cat([F[:, [1, 2]].unsqueeze(1),
                    F[:, [2, 0]].unsqueeze(1),
                    F[:, [0, 1]].unsqueeze(1)], dim=1)
    
    return he

if __name__ == '__main__':
    # Example usage
    v = torch.tensor([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    f = torch.tensor([[0, 1, 2]], dtype=torch.int)
    he = halfedges(f)
    print(he)  # Should match the expected halfedge list


