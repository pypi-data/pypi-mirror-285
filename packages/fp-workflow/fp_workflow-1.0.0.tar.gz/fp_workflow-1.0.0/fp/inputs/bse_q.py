#region: Modules.
import numpy as np 
from fp.schedulers import *
from fp.inputs.atoms import *
from fp.inputs.kernel import *
from fp.inputs.abs import *
from fp.structure.kpts import Kgrid
#endregion

#region: Variables.
#endregion

#region: Functions.
#endregion

#region: Classes.
class BseqInput:
    def __init__(
        self,
        atoms,
        val_bands_coarse,
        cond_bands_coarse,
        val_bands_fine,
        cond_bands_fine,
        Qdim,
        wfn_co_link,
        wfnq_co_link,
        wfn_fi_link,
        wfnq_fi_link,
        num_evec,
        pol_dir,
        job_desc
    ):
        self.atoms: AtomsInput = atoms
        self.val_bands_coarse = val_bands_coarse  
        self.cond_bands_coarse = cond_bands_coarse 
        self.val_bands_fine = val_bands_fine 
        self.cond_bands_fine = cond_bands_fine 
        self.Qdim: np.ndarray = np.array(Qdim).astype(dtype='i4')
        self.wfn_co_link: str = wfn_co_link
        self.wfnq_co_link: str = wfnq_co_link
        self.wfn_fi_link: str = wfn_fi_link
        self.wfnq_fi_link: str = wfnq_fi_link
        self.num_evec: int = num_evec
        self.pol_dir: np.ndarray = np.array(pol_dir)
        self.job_desc: JobProcDesc = job_desc

    def get_Qpts(self):
        return Kgrid(self.atoms, self.Qdim, is_reduced=False).get_kpts()
#endregion
