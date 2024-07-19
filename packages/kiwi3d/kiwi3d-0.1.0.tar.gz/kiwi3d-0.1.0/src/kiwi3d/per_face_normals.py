import torch

def per_face_normals(V, F, unit_norm=True):
    """Vector perpedicular to all faces on a mesh using PyTorch
    
    Computes per face (optionally unit) normal vectors for a triangle mesh.

    Parameters
    ----------
    V : (n,d) torch tensor
        vertex list of a triangle mesh
    F : (m,d) torch int tensor
        face index list of a triangle mesh
    unit_norm : bool, optional (default True)
        Whether to normalize each face's normal before outputting

    Returns
    -------
    N : (n,d) torch double tensor
        Matrix of per-face normals

    See Also
    --------
    per_vertex_normals.
    """     

    dim = V.shape[1]

    if dim == 2:
        # Edge vectors
        v0 = V[F[:, 0], :]
        v1 = V[F[:, 1], :]
        # Difference between edge vectors
        e = v1 - v0
        # Rotate by 90 degrees
        N = torch.cat((e[:, 1][:, None], -e[:, 0][:, None]), dim=1)
    elif dim == 3:     
        v0 = V[F[:, 0], :]
        v1 = V[F[:, 1], :]
        v2 = V[F[:, 2], :]

        # It's basically just a cross product
        N = torch.cross(v1 - v0, v2 - v0, dim=1)

    if unit_norm:
        N = N / N.norm(dim=1, keepdim=True)

    return N

if __name__ == '__main__':
    from gpytoolbox import read_mesh
    v, f = read_mesh('./spot_triangulated.obj')
    n_pt = per_face_normals_pt(torch.from_numpy(v), torch.from_numpy(f))

