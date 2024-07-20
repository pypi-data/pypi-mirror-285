#region: Modules.
import h5py
import numpy as np 
#endregion

#region: Variables.
#endregion

#region: Functions.
#endregion

#region: Classes.
class WfnFile:
    def __init__(
        self, 
        filename: str
    ):
        self.filename: str = filename

    def _get_coeffs(self, handle):
        coeffs = handle['']

    def get_coeffs_grid(self):
        with h5py.File(self.filename, 'r') as r:
            coeffs_gk = np.vectorize(complex)(r['/wfns/coeffs'][..., 0], r['/wfns/coeffs'][..., 1]) 
            gvecs = r['/wfns/gvecs'][:] 
            ngk_init = r['/mf_header/kpoints/ngk'][:]
            ngk = np.zeros(ngk_init.size+1)
            ngk[1:] = np.cumsum(ngk_init)
            fft_grid = r['/mf_header/gspace/FFTgrid'][:]

        coeffs = np.zeros(
            coeffs_gk.shape[0],
            coeffs_gk.shape[1],
            fft_grid[0],
            fft_grid[1],
            fft_grid[2],
        )
#endregion
