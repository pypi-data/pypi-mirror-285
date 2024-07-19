import torch

def unique(x, return_inverse=False, dim=-1):
    unique, inverse = torch.unique(x, return_inverse=True, dim=dim)
    perm = torch.arange(inverse.size(dim), dtype=inverse.dtype, device=inverse.device)
    inverse_, perm = inverse.flip([dim]), perm.flip([dim])
    if return_inverse:
        return unique, inverse_.new_empty(unique.size(dim)).scatter_(dim, inverse_, perm), inverse

    return unique, inverse_.new_empty(unique.size(dim)).scatter_(dim, inverse_, perm)

def array_correspondence(A, B, axis=None):
    """Computes a map from A to the equal elements in B

    Parameters
    ----------
    A : (a,) or (a,k) torch tensor (must be 1-dim or 2-dim)
    B : (b,) or (b,k) torch tensor (must be 1-dim or 2-dim)
    axis : int or None, optional (default None)
        If None, will treat A and B as flat arrays.
        If a number, will check for equality of the entire axis, in which case
        the dimension of A and B across that axis must be equal.

    Returns
    -------
    f : (a,) torch long tensor 
        index list mapping from A to B, with -1 if there is no
        matching entry.
        If b contains multiple eligible entries, return an arbitrary one.
        If there are no -1s, `b[f] == a`

    Examples
    --------
    Example with simple array correspondence:
    ```python
    >>> A = np.array([1,7,2,7,9,3,7,0])
    >>> B = np.array([7,7,3,2,7,8])
    >>> f = gpy.array_correspondence(A, B)
    >>> f
    array([-1,  0,  3,  0, -1,  2,  0, -1])
    ```
    Example with row correspondence:
    ```python
    >>> A = np.array([[1,3],[5,2],[1,2],[5,2]])
    >>> B = np.array([[1,2],[6,9],[5,2]])
    >>> f = gpy.array_correspondence(A, B, axis=0)
    >>> f
    array([-1,  2,  0,  2])
    ```
    
    """
    if axis not in (None, 0, 1, -1, -2):
        raise Exception("Axis can only be None, 0, 1, -1, -2")
    if len(A.shape) > 2 or len(B.shape) > 2:
        raise Exception("Inputs A, B can only be up to 2 dimensional")

    if axis == 1 or axis == -1:
        A = A.transpose(0, 1)
        B = B.transpose(0, 1)
        axis = 0

    if axis is None:
        A = A.flatten()
        B = B.flatten()
        axis = 0

    # Convert tensors to contiguous memory
    A = A.contiguous()
    B = B.contiguous()

    # Get unique elements and their first occurrence indices
    uB, mapB = unique(B, dim=axis)

    # Concatenate unique B with A
    concatenated = torch.cat((uB, A), dim=axis)

    # Get unique elements of concatenated array and their inverse indices
    _, idx, inv = unique(concatenated, return_inverse=True, dim=axis)

    # Calculate the mapping
    imap = idx[inv[uB.shape[0]:]]
    imap[imap>=uB.shape[0]] = -1
    f = torch.where(imap < 0, torch.tensor(-1, dtype=torch.long), mapB[imap])

    return f

if __name__ == '__main__':
    A = torch.Tensor([1, 7, 2, 7, 9, 3, 7, 0])
    B = torch.Tensor([7, 7, 3, 2, 7, 8])
    f = array_correspondence(A, B)
    print(f)

