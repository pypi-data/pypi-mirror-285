#!/usr/bin/env python
# -*- coding: utf-8 -*-

import torch
from kiwi3d.halfedges import halfedges
from kiwi3d.array_correspondence import array_correspondence

def triangle_triangle_adjacency(F):
    """Given a manifold triangle mesh with face indices F, computes adjacency
    info between triangles using PyTorch
    
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
    TT : (m,3) torch int tensor
        Index list specifying which face j is adjacent to which face i across
        the respective halfedge in position (i,j).
        If there is no adjacent face (boundary halfedge), the entry is -1.
    TTi : (m,3) torch int tensor
        Index list specifying which halfedge of face j (0,1,2) is adjacent to i
        in position (i,j).

    Examples
    --------
    ```python
    from gpytoolbox import regular_square_mesh, triangle_triangle_adjacency
    v, f = regular_square_mesh(10)
    TT, TTi = triangle_triangle_adjacency(f)
    ```
    """
    
    m = F.shape[0]
    assert m > 0
    assert F.shape[1] == 3

    he = halfedges(F)
    he_flat = torch.cat((he[:,0,:], he[:,1,:], he[:,2,:]), dim=0)
    he_flip_flat = torch.flip(he_flat, dims=[1])

    map_to_flip = array_correspondence(he_flat, he_flip_flat, axis=0)
    TT = torch.where(map_to_flip<0, -1, map_to_flip % m).reshape(F.T.shape).T.reshape(F.shape)
    TTi = torch.where(map_to_flip<0, -1, map_to_flip // m).reshape(F.T.shape).T.reshape(F.shape)

    return TT, TTi

if __name__ == '__main__':
    from gpytoolbox import regular_square_mesh
    v, f = regular_square_mesh(10) 
    TT_pt, TTi_pt = triangle_triangle_adjacency(torch.from_numpy(f))

