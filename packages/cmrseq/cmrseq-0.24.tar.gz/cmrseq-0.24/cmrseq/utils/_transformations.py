__all__ = ["mps_to_xyz", "xyz_to_mps", "get_rotation_matrix"]

import numpy as np

def mps_to_xyz(gradients: np.ndarray, slice_normal: np.ndarray = np.array([1., 0., 0.]),
               readout_direction : np.ndarray = np.array([0., 0., 1.])) -> np.ndarray:
    """ Converts from MPS formalism to scanner coordinates XYZ. Default scheme is Coronal slice
     with measurement in Z If M and S are not orthogonal, M is adjusted.

    :param gradients: (..., 3) np.array containing gradient waveforms defined in MPS coordinates
    :param slice_normal: np.array (3, ) containing the slice orientation in XYZ coordinates
    :param readout_direction: np.array (3, ) containing the readout direction in XYZ coordinates
    :return: (..., 3) rotated gradient waveform in XYZ coordinates
    """
    rotation_matrix = get_rotation_matrix(slice_normal, readout_direction, target_orientation="xyz")
    return np.einsum('ij,...j->...i', rotation_matrix, gradients)


def xyz_to_mps(gradients: np.ndarray, slice_normal: np.ndarray = np.array([1., 0., 0.]),
               readout_direction: np.ndarray = np.array([0., 0., 1.])) -> np.ndarray:
    """ Converts from XYZ formalism to scanner coordinates MPS. Default scheme is Coronal slice
     with measurement in Z If M and S are not orthogonal, M is adjusted.

    :param gradients: (..., 3) np.array containing gradient waveforms defined in XYZ coordinates
    :param slice_normal: np.array (3, ) containing the slice orientation in XYZ coordinates
    :param readout_direction: np.array (3, ) containing the readout direction in XYZ coordinates
    :return: (..., 3) rotated gradient waveform in MPS coordinates
    """
    rotation_matrix = get_rotation_matrix(slice_normal, readout_direction, target_orientation="mps")
    return np.einsum('ij,...j->...i', rotation_matrix, gradients)


def get_rotation_matrix(slice_normal: np.ndarray,
                        readout_direction: np.ndarray,
                        target_orientation: str = "xyz") -> np.ndarray:
    """ Evaluates a rotation matrix according which can be used to transform between
    MPS and XYZ coordinates.
    If M and S are not orthogonal, M is adjusted.

    :param slice_normal: Slice normal vector in XYZ coordinates
    :param readout_direction: Readout vector in XYZ coordinates
    :param target_orientation: str, either ('mps', 'xyz')
    :return: (3, 3) array the 0th axis indexes the M/P/S vector in cartesian coordinates

        - M = R[0, :]
        - P = R[1, :]
        - S = R[2, :]
    """
    readout_direction = readout_direction / np.linalg.norm(readout_direction)
    slice_normal = slice_normal / np.linalg.norm(slice_normal)
    phase_direction = np.cross(slice_normal, readout_direction)
    phase_direction = phase_direction / np.linalg.norm(phase_direction)

    if np.dot(slice_normal, readout_direction) != 0:
        readout_direction = np.cross(phase_direction, slice_normal)
        readout_direction = readout_direction / np.linalg.norm(readout_direction)

    rot_to_xyz = np.stack([readout_direction, phase_direction, slice_normal], axis=0)
    if target_orientation.lower() == "xyz":
        rot_mat = rot_to_xyz
    elif target_orientation.lower() == "mps":
        rot_mat = np.linalg.inv(rot_to_xyz)
    else:
        raise ValueError("Target direction not valid! Expected one of ['xyz', 'mps'] "
                         f"but got: {target_orientation}")
    return rot_mat
