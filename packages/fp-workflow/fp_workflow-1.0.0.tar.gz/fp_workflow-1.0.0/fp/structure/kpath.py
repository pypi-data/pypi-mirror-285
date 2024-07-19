#region: Modules.
from ase import Atoms 
from ase.dft.kpoints import BandPath
import numpy as np 
import pickle
#endregion

#region: Variables.
#endregion

#region: Functions.
#endregion

#region: Classes.
class KPath:
    def __init__(
            self, 
            atoms: Atoms, 
            path_string: str, 
            npoints: int
        ):
        self.atoms: Atoms = atoms
        self.path_string: str = path_string
        self.npoints: int = npoints

        # generate bandpath.
        self.bandpath = atoms.cell.bandpath(path=self.path_string, npoints=self.npoints)

    def get_kpts(self):
        return self.bandpath.kpts
    
    def get_axis(self):
        return self.bandpath.get_linear_kpoint_axis()
    
    def find_K_from_k(k, M):
        """Gets a k vector in scaled coordinates and returns a K vector and the
        unfolding G in scaled Coordinates."""

        KG = np.dot(M, k)
        G = np.zeros(3, dtype=int)

        for i in range(3):
            if KG[i] > 0.5000001:
                G[i] = int(np.round(KG[i]))
                KG[i] -= np.round(KG[i])
            elif KG[i] < -0.4999999:
                G[i] = int(np.round(KG[i]))
                KG[i] += abs(np.round(KG[i]))

        return KG, G


    def get_sc_path(self, sc_grid: np.ndarray):
        M = np.diag(sc_grid)
        kpts = self.bandpath.kpts

        Kpts = np.zeros_like(kpts)
        for kpt_idx, kpt in enumerate(kpts):
            Kpt = self.find_K_from_k(kpt, M)[0]
            Kpts[kpt_idx, :] = Kpt

        return Kpts 

    def save_bandpath(self, filename='bandpath.pkl'):
        with open(filename, 'wb') as f: pickle.dump(self, f)

    @staticmethod
    def load_bandpath(filename='bandpath.pkl'):
        with open(filename, 'rb') as f: output = pickle.load(f)
#endregion
