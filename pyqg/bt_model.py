import numpy as np
import model
from numpy import pi


class BTModel(model.Model):
    """A subclass that represents the single-layer QG model."""
    
    def __init__(
        self,
        beta=0.,                    # gradient of coriolis parameter
        #rek=0.,                     # linear drag in lower layer
        rd=0.,                      # deformation radius
        H = 1.,                     # depth of layer
        U=0.,                       # max vel. of base-state
        #filterfac = 23.6,           # the factor for use in the exponential filter
        **kwargs
        ):
        """Initialize the single-layer (barotropic) QG model.

        beta -- gradient of coriolis parameter, units m^-1 s^-1
        rek -- linear drag in lower layer, units seconds^-1
        rd -- deformation radius, units meters
        (NOTE: currently some diagnostics assume delta==1)
        U -- upper layer flow, units m/s
        filterfac -- amplitdue of the spectral spherical filter
                     (originally 18.4, later changed to 23.6)
        """

        # physical
        self.beta = beta
        #self.rek = rek
        self.rd = rd
        self.H = H
        self.U = U
        #self.filterfac = filterfac
        
        self.nz = 1
       
        # deformation wavenumber
        if rd:
            self.kd2 = rd**-2
        else:
            self.kd2 = 0.
    
        super(BTModel, self).__init__(**kwargs)
     
        # initial conditions: (PV anomalies)
        self.set_q(1e-3*np.random.rand(1,self.ny,self.nx))
 
    ### PRIVATE METHODS - not meant to be called by user ###
        
    def _initialize_background(self):
        """Set up background state (zonal flow and PV gradients)."""
        
        # the meridional PV gradients in each layer
        self.Qy = np.asarray(self.beta)[np.newaxis, ...]

        # background vel.
        self.set_U(self.U)        

        # complex versions, multiplied by k, speeds up computations to pre-compute
        self.ikQy = self.Qy * 1j * self.k
        
        self.ilQx = 0.

    def _initialize_inversion_matrix(self):
        """ the inversion """ 
        # The bt model is diagonal. The inversion is simply qh = -kappa**2 ph
        self.a = -(self.wv2i+self.kd2)[np.newaxis, np.newaxis, :, :]

    def _initialize_forcing(self):
        pass

    # def _initialize_forcing(self):
    #     """Set up frictional filter."""
    #     # this defines the spectral filter (following Arbic and Flierl, 2003)
    #     cphi=0.65*pi
    #     wvx=np.sqrt((self.k*self.dx)**2.+(self.l*self.dy)**2.)
    #     self.filtr = np.exp(-self.filterfac*(wvx-cphi)**4.)
    #     self.filtr[wvx<=cphi] = 1.
    #
    # def _filter(self, q):
    #     return self.filtr * q

    def set_U(self, U):
        """Set background zonal flow"""
        self.Ubg = np.asarray(U)[np.newaxis, ...]

    def _calc_diagnostics(self):
        # here is where we calculate diagnostics
        if (self.t>=self.dt) and (self.tc%self.taveints==0):
            self._increment_diagnostics()

    ### All the diagnostic stuff follows. ###
    def _calc_cfl(self):
        return np.abs(
            np.hstack([self.u + self.Ubg, self.v])
        ).max()*self.dt/self.dx

    # calculate KE: this has units of m^2 s^{-2}
    def _calc_ke(self):
        ke = .5*self.spec_var(self.wv*self.ph)
        return ke.sum()

    # calculate eddy turn over time 
    # (perhaps should change to fraction of year...)
    def _calc_eddy_time(self):
        """ estimate the eddy turn-over time in days """
        ens = .5*self.H * self.spec_var(self.wv2*self.ph)
        return 2.*pi*np.sqrt( self.H / ens ) / year

    # def _calc_derived_fields(self):
    #     self.p = self.ifft2( self.ph)
    #     self.xi =self.ifft2( -self.wv2*self.ph)
    #     self.Jptpc = -self.advect(self.p,self.u,self.v)
    #     self.Jpxi = self.advect(self.xi, self.u, self.v)

        


