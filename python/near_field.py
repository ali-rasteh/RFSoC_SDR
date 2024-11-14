from backend import *
from backend import be_np as np, be_scp as scipy
from signal_utils import Signal_Utils



class RoomModel(Signal_Utils):
    def __init__(self, xlim=np.array([-10,10]), ylim=np.array([-3,10])):

        # Define the walls of the room
        # Each row is a wall with the first two columns being the start points
        # of the wall and the last two columns being the end point 
        self.walls = np.array([[xlim[0],ylim[0],xlim[0],ylim[1]],
                               [xlim[0],ylim[1],xlim[1],ylim[1]],
                                 [xlim[1],ylim[1],xlim[1],ylim[0]] ] )
        
    def draw_walls(self, ax=None):
        """
        Draw the walls of the room.

        Parameters
        ----------
        ax : matplotlib axis
            Axis to draw the walls on.  If None, the current axis is used.
        """
        if ax is None:
            ax = plt.gca()
        for i in range(self.walls.shape[0]):
            ax.plot(self.walls[i,[0,2]], self.walls[i,[1,3]], 'b-', linewidth=2)

        return ax
    

    def find_reflection(self, x):
        """
        Find all the reflections of a point x in the room.
        """
        nwall = self.walls.shape[0]
        xref = np.zeros((nwall,2))
        for i in range(nwall):
            xref[i,:] = self.reflect_point(x, self.walls[i,:])

        return xref

    def reflect_point(self, x, wall):
        """
        Reflect a point x off a wall.
        """
        x1 = wall[0:2]
        x2 = wall[2:4]
        v = x2 - x1
        v = v/np.linalg.norm(v)
        n = np.array([-v[1], v[0]])
        d = np.dot(x - x1, n)
        xref = x - 2*d*n
        return xref

class Sim(Signal_Utils):
    """
    Describes the configuration of the simulation.

    Parameters
    ----------
    fc : float
        Carrier frequency.
    fsamp : float
        Sampling frequency.
    bw : float
        Sounding bandwidth relative to the sample rate.
    nfft : int
        Number of FFT points.
    snr : float
        Signal to noise ratio in dB.
    nantrx : int
        Number of antennas at the RX.
    antsep : nparray of floats
        Separation between antennas in wavelengths.
    rxlocsep : nparray of floats
        Maximum separation between RX locations in meters
    sepdir : np.array of shape (p,)
        Direction of separation between antennas and locations
    nrxloc : int
        Number of RX locations.  The RX locations are placed on a line
        from the origin the rxlocsep.  At each rx location, the RX antennas are
        separated by antsep.  So, the total number of RX measurements is
        nmeas = nrxloc*len(antsep).
    npath : int
        Number of paths from the TX which is assumed to be the 
        same for all RX locations.
    lossavg : float
        Average loss of the paths in dB.
    tx : (npath, p) array or None
        List of the TX locations.  If None, the TX locations are randomly
        generated in the region.
    npath_est : int
        Number of paths to estimate.
    stop_thresh : float
        Relative peak size at which the search stops
    region : np.array of shape (2,p) or None
        Region in which the TX locations are generated.  If None, the region
        is set to include all the TX image points.
    """
    def __init__(self, fc=6e9, fsamp=1e9, bw=0.8, nfft=1024, snr=20, nantrx=2,
                antsep=None, rxlocsep=None, sepdir=None, npath=4,
                lossavg=10, tx=None, npath_est=4, stop_thresh=0.03, region=None):
        # Parameters
        self.fc = fc  # Carrier frequency
        self.c = constants.c  # Speed of light
        self.lam = self.c/self.fc  # Wavelength
        self.fsamp = fsamp  # Sampling frequency
        self.bw = bw    # Sounding bandwidth relative to the sampling rate
        self.nfft = nfft  # Number of FFT points
        self.snr = snr  # Signal to noise ratio in dB
        self.nantrx = nantrx # Number of antennas at the RX
        if antsep is None:
            antsep=np.array([0.5,1,2])
        self.antsep = antsep
        if rxlocsep is None:
            rxlocsep = np.array([0,1])  
        if sepdir is None:
            sepdir=np.array([1,0])
        self.sepdir = sepdir
        self.rxlocsep = rxlocsep
        self.npath = npath
        self.sepdir = sepdir
        self.nrxlocsep = len(self.rxlocsep)
        self.nantsep = len(self.antsep)
        self.nmeas = self.nrxlocsep * self.nantsep
        self.lossavg = lossavg
        self.tx = tx
        self.npath_est = npath_est
        self.stop_thresh = stop_thresh
        self.region = region

        self.points = []    # List of points to plot
        self.sparse_dly_est = np.zeros((self.npath_est, self.nantrx, self.nmeas))
        self.sparse_peaks_est = np.zeros((self.npath_est, self.nantrx, self.nmeas))


        # # Generate the TX positions and search region
        # self.gen_tx_pos()

        # # Compute the RX locations and antenna positions
        # self.compute_rx_pos()

        # # Compute the channel frequency response
        # self.compute_freq_resp()

        # # Create the test points for the TX locations
        # self.create_tx_test_points()

        # # Initialize the path estimates
        # self.path_est_init()

        # self.locate_tx()

    def gen_tx_pos(self):
        """
        Generate random TX image positions and reflection losses
        from each TX
        """
        # Generate the TX locations
        if self.tx is None:
            # Region for the transmitter
            if self.region is None:
                self.region = np.array([[-10,10], [0,30]] )  
            self.p = self.region.shape[1]  # Dimension of region

            wid = self.region[:,1] - self.region[:,0]
            self.tx = np.random.uniform(0,1, (self.npath, self.p))*wid[None,:]\
                    + self.region[None,:,0]
            
        else:

            # Set region to include all the TX image points
            self.p = self.tx.shape[1]
            if self.region is None:
                xmin = np.min(self.tx, axis=0)
                xmax = np.max(self.tx, axis=0)
                self.region = np.array([[xmin[0]-5, xmax[0]+5], [0, xmax[1]+5]])
            self.npath = self.tx.shape[0]

        # Sort the TX locations in distance from the origin
        dist = np.linalg.norm(self.tx, axis=1)
        idx = np.argsort(dist)
        self.tx = self.tx[idx,:]

        # Generate the reflection losses in dB
        # The first path has zero loss since it is LOS
        # The exponential should be in linear TODO
        self.loss = np.random.exponential(self.lossavg, (self.npath,))
        self.loss[0] = 0




    def compute_rx_pos(self):
        """
        Compute the locations of the RX antennas across all measurements.

        rxantpos[i,m,:] is the location of the i-th RX antenna in the m-th
        measurement
        """
        # Generate the RX locations
        self.rxloc = self.rxlocsep[:,None]*self.sepdir[None,:]

        # Generate the RX antenna positions
        self.rxantpos = np.zeros((self.nantrx, self.nmeas, self.p))
        for k in range(self.nrxlocsep):
            for i in range(self.nantsep):
                m = k*self.nantsep + i

                # Linear distance of the RX antennas from the origin
                t = self.rxlocsep[k] + self.antsep[i]*np.arange(self.nantrx)*self.lam

                # Position of the RX antennas
                self.rxantpos[:,m,:] = t[:,None]*self.sepdir[None,:]
            
        

    def compute_freq_resp(self):
        """
        Computes the frequency response from all TX locations at all measurements


        chan[:,i,m] is the channel frequency response from
        TX location itx, measurement m to RX antenna i.

        distref[m] is the reference distance for measurement m.  This is the time
        at which the measurement was taken and changes from measurement to measurement
        since the measurements are not synchronized.

        distrel[i,m,itx] is the relative distance from TX location itx to RX antenna i
        """


        # Compute the frequency response of the channel sounder
        nbw = int(self.bw*self.nfft/2)
        self.gresp = np.zeros(self.nfft, dtype=np.complex64)
        self.gresp[0:nbw+1] = 1
        self.gresp[self.nfft-nbw:] = 1

        # Frequency of each FFT bin
        self.freq = self.fc + (np.arange(self.nfft)/self.nfft-0.5)*self.fsamp
        
        # Compute the distance from each TX location to each RX antenna
        #  dist[i,m,itx] is the distance from TX location itx to RX antenna i
        #  in measurement m
        self.dist = self.rxantpos[:,:,None,:] - self.tx[None,None,:,:]
        self.dist = np.sum(self.dist**2, axis=3)**0.5

        # Compute the free space path loss using Friis' formula
        #  pathloss[i,m,itx] is the path loss from TX location itx to RX antenna i
        #  in measurement m
        self.pathloss = -20*np.log10(self.lam/(4*np.pi*self.dist))   

        # Add the reflection losses
        self.pathloss += self.loss[None,None,:]

        # Compute the channel coefficients from the path loss values
        self.coeffs = 10**(-self.pathloss/20)
        
        # Add random phase to the channel coefficients
        # why?
        phase = np.exp(1j*2*np.pi*
                  np.random.uniform(0,1,(self.nmeas,self.npath)))
        self.coeffs = self.coeffs*phase[None,:,:]

        # Find the reference distance for each measurement from the first path
        dsamp = self.c/self.fsamp  # Distance traveled in one sample period
        # What is dnom?
        dnom = 10*dsamp
        self.distref = np.mean(self.dist[:,:,0], axis=0) - dnom + np.random.uniform(-0.5,0.5,self.nmeas)*dsamp
        self.distrel = self.dist - self.distref[None,:,None]

        # Compute the frequency-domain channel response
        self.chan = self.mpath_chan(self.distrel, self.coeffs)

        # Find the power from the strongest path
        chan_pow = np.mean(np.abs(self.chan[:,:,0])**2)
        wvar = chan_pow*10**(-self.snr/10)

        # Add noise to the channel
        self.chan_fd = self.chan + np.random.normal(0, np.sqrt(wvar/2), self.chan.shape) + \
            1j*np.random.normal(0, np.sqrt(wvar/2), self.chan.shape)

        # Compute the time-domain channel response
        self.chan_td = np.fft.ifft(self.chan_fd, axis=0)

    def plot_chan_td(self, indsamp=None, indrx=0, indmeas=0):
        """
        Plots the channel response in the time domain.

        Parameters
        ----------
        indsamp : slice
            The range of samples to plot.
        indrx : int or slice
            The indices of the RX antenna to plot.
        indmeas : int or slice
            The indices of the measurement to plot.
        """

        # Set default sample range to the entire range
        if indsamp is None:
            indsamp = slice(0,self.nfft)

        # Compute the expected path locations in samples
        self.path_samp = self.distrel / self.c * self.fsamp
        self.path_pow = 20*np.log10(np.abs(self.coeffs))
        self.chan_pow =  20*np.log10(np.abs(self.chan_td))

        # Find the max value of y for the plot
        samp_ind = np.arange(self.nfft)
        chan_pow1 = self.chan_pow[indsamp,indrx,indmeas]
        path_samp1 = self.path_samp[indrx,indmeas,:]
        path_pow1 = self.path_pow[indrx,indmeas,:]
        ymax = np.max([np.max(chan_pow1), np.max(path_pow1)]) + 5

        # Find the 25% percentile value of of the chan_pow1 to estimate the noise
        ymin = np.percentile(chan_pow1.flatten(), 25)-5
       
        # Plot the channel power
        plt.plot(samp_ind[indsamp], chan_pow1)
        plt.stem(path_samp1.flatten(), path_pow1.flatten(), 
                 'r-', bottom=ymin, basefmt=' ')
        plt.grid()
        plt.ylim([ymin, ymax])

        plt.show()


    def mpath_chan(self, dist, coeffs=None, basis_fn=False):
        """
        Creates the channel frequency response for a given set of delays
        and coefficients.  If the `basis_fn` is True, then the coefficients
        are ignored and the method returns the basis functions.

        Parameters
        ----------
        coeffs : np.array of shape (d1,d2,...,dk,npath)
            The coefficients of the path.
        dist : np.array of shape (d1,d2,...,dk,npath) 
            The relative distances of the paths

        Returns
        -------
        h : np.array of shape (nfft,d1,...,dk) 
            The channel frequency response.
        """
        #t = np.arange(self.nfft)
        
        # Reshape the distance to add a dimension at the beginning
        dist1 = dist.reshape((1,) + dist.shape)
        if basis_fn:
            coeffs1 = 1
        else:
            coeffs1 = coeffs.reshape((1,) + dist.shape)

        # Reshape the frequency to add dimensions at the end
        ndims = len(dist.shape)
        freq1 = self.freq.reshape(self.freq.shape + (1,)*ndims)
        gresp1 = self.gresp.reshape(self.gresp.shape + (1,)*ndims)
        
        # Compute the phase
        phase = 2*np.pi*freq1*dist1 / self.c
        h = gresp1*coeffs1*np.exp(-1j*phase)

        # If we are not computing the basis functions, we sum over the 
        # final dimension corresponding to the paths
        if not basis_fn:
            h = np.sum(h, axis=-1)

        return h


        
    def plot_tx_rx(self):
        """
        Plot the TX and RX locations.
        """
        # Plot the RX locations as red circles
        plt.plot(self.rxloc[:,0], self.rxloc[:,1], 'ro')

        # Plot the TX locations as blue circles
        plt.plot(self.tx[:,0], self.tx[:,1], 'bo')

        #plt.grid(True)
        # plt.show()


    def create_tx_test_points(self):
        """
        Create a set of test points over the region using meshgrid.
        """

        # Create a set of points x uniformly distributed in the area
        # using meshgrid
        npoints = 100
        x1 = np.linspace(self.region[0,0],self.region[0,1],npoints)
        x2 = np.linspace(self.region[1,0],self.region[1,1],npoints)
        X1, X2 = np.meshgrid(x1,x2)
        X = np.zeros((npoints**2,2))
        X[:,0] = X1.flatten()
        X[:,1] = X2.flatten()
        self.xtest0 = X1
        self.xtest1 = X2
        self.Xtest = X
        self.npoints = npoints

        # Find the distances from each TX test location to each RX antenna
        dist = self.rxantpos[:,:,None,:] - X[None,None,:,:]
        self.dtest = np.sqrt(np.sum(dist**2, axis=3))


    def path_est_init(self):
        """
        Initializes the path estimate data structures
        """

        # For each measurement, find the peak location of the channel response
        # and circularly rotate the response to that location, so the peaks
        # all align to sample 0
        self.chan_td_rot = np.zeros((self.nfft, self.nantrx, self.nmeas), dtype=np.complex64)
        self.chan_fd_rot = np.zeros((self.nfft, self.nantrx, self.nmeas), dtype=np.complex64)
        f = np.arange(self.nfft)[:,None]
        for i in range(self.nmeas):
            chan_pow = np.sum(np.abs(self.chan_td[:,:,i])**2, axis=1)
            im = np.argmax(chan_pow)
            self.chan_td_rot[:,:,i] = np.roll(self.chan_td[:,:,i], -im, axis=0)
            self.chan_fd_rot[:,:,i] = self.chan_fd[:,:,i]*np.exp(1j*2*np.pi*im*f/self.nfft)

        # Estimated reference distance for each measurement.
        # This is a measure of the point at which the measurement was made
        self.distref_est = np.zeros(self.nmeas)

        # Estimate TX locations, absolute distance, and coefficients for each path
        self.tx_est = np.zeros((self.npath_est, self.p))
        self.dist_est = np.zeros((self.nantrx, self.nmeas, self.npath_est))
        self.coeffs_est = np.zeros((self.nmeas, self.npath_est), dtype=np.complex64)
        self.abs_delay = np.zeros((self.npath_est, self.nantrx, self.nmeas))


    def locate_tx(self, npath_est=None):
        """
        Iteratively locates the TX image points
        """

        if npath_est is None:
            npath_est = self.npath_est

        # Initialize the correlation estimates for each iteration
        ntest = self.dtest.shape[-1]
        self.rho = np.zeros((ntest, npath_est))

        # Compute the phase difference
        dexp = np.exp(2*np.pi*1j/self.lam*self.dtest)
        
        for ipath in range(npath_est):
        
            if ipath == 0:

                # For each measurement find the peak of the channel response
                # and take the response at that sample frequency
                aresp = self.chan_td_rot[0,:,:]

                # Compute the correlation
                self.rho[:,ipath] = np.sum( np.abs(np.sum(aresp[:,:,None]*dexp, axis=0))**2, axis=0 )


                # Find the location that maximizes the correlation
                im = np.argmax(self.rho[:,ipath])

                # Check stopping condition
                if ipath == 0:
                    rho_max = np.max(self.rho[:,0])
                    done = False
                else:
                    done = np.max(self.rho[:,ipath]) < self.stop_thresh*rho_max

            else:
                
                aresp = np.zeros((self.nantrx, self.nmeas, ntest), dtype=np.complex64)
                for i in range(ntest):
                    for m in range(self.nmeas):
                
                        # Get the array response from the appropriate sample offset
                        isamp = self.samp_offset[m,i]
                        aresp[:,m,i] = self.resid[isamp,:,m]

                # Compute the correlation
                self.rho[:,ipath] = np.sum( np.abs(np.sum(aresp*dexp, axis=0))**2, axis=0 )

                # Find the location that maximizes the correlation
                im = np.argmax(self.rho[:,ipath])

                # Check stopping condition
                done = np.max(self.rho[:,ipath]) < self.stop_thresh*rho_max



                # dly = self.sparse_dly_est[ipath] - self.sparse_dly_est[0]
                # dist_rel = dly * self.c
                # d_diff = np.sum(np.abs(self.dtest[:,:,:] - dist_rel[:,:,None]), axis=(0,1))
                # im = np.argmin(d_diff)

                # done = (np.min(np.abs(self.sparse_dly_est[ipath])) == 0)


            if done:
                break
            else:
                self.npath_det = ipath+1

            self.tx_est[ipath,:] = self.Xtest[im,:]

            # Set the disances for the path
            self.dist_est[:,:,ipath] = self.dtest[:,:,im] 

            # For the first path, we estimate the reference distance
            # and the sample locations of the other paths
            if ipath == 0:
                self.set_ref_distances()

            # Fit the coefficients and find the residual
            self.fit_coeffs(npath_fit=ipath+1)

            self.abs_delay[ipath] = self.dist_est[:,:,ipath] / self.c
            

    def set_ref_distances(self):
        """
        Set the reference distances for each measurement.

        Computes

        samp_offset[m,i] = sample offset for test location i in measurement m
        """

        # Set the reference distance
        self.distref_est = np.mean(self.dist_est[:,:,0], axis=0)

        # Compute the sample offset for all other distances
        dtest_mean = np.mean(self.dtest, axis=0)
        self.abs_delay_offset = (dtest_mean - self.distref_est[:,None])/self.c
        self.samp_offset = self.abs_delay_offset * self.fsamp
        self.samp_offset = np.round(self.samp_offset).astype(int)
        self.samp_offset = np.maximum(0, self.samp_offset)
        self.samp_offset = np.minimum(self.nfft-1, self.samp_offset)



    def fit_coeffs(self, npath_fit=1):
        
        # Compute the relative distances of the paths
        dist_rel = self.dist_est[:,:,:npath_fit] - self.distref_est[None,:,None]

        # Compute the basis functions
        self.basis = self.mpath_chan(dist_rel, basis_fn=True)

        # Stack the basis functions for the antennas 
        self.basis1 = self.basis.reshape((self.nfft*self.nantrx, self.nmeas, npath_fit), order='F')

        # Stack the channel responses for the antennas
        chan_fd_rot1 = self.chan_fd_rot.reshape((self.nfft*self.nantrx, self.nmeas), order='F')

        # On each measurement, find the least squares estimate of the coefficients
        self.coeffs_est = np.zeros((self.nmeas, npath_fit), dtype=np.complex64)
        for i in range(self.nmeas):
            self.coeffs_est[i,:] = np.linalg.lstsq(self.basis1[:,i,:], chan_fd_rot1[:,i], rcond=None)[0]

        # Compute channel from the sum of the estimated paths
        self.chan_fd_paths = np.sum(self.coeffs_est[None,:,:]*self.basis1, axis=2)
        self.chan_fd_paths = self.chan_fd_paths.reshape((self.nfft, self.nantrx, self.nmeas), order='F')

        # Compute the time-domain channel response
        self.chan_td_paths = np.fft.ifft(self.chan_fd_paths, axis=0)

        # Compute the residual 
        self.resid = self.chan_td_rot - self.chan_td_paths
        #self.resid = np.sum(self.coeffs_est[:,None,:]*self.basis1, axis=2) - chan_fd_rot1
        #self.resid = np.sum(np.abs(np.sum(self.coeffs_est[:,None,:]*self.basis, axis=2) - chan_fd_rot1)**2, axis=0)



    def nf_channel_param_est(self, n_paths=0, n_epochs=1000, lr_init=0.1, ch_gt=None, tx_ant_vec=None, rx_ant_vec=None, trx_unit_vec=None, path_delay=None, path_gain=None, freq=None):
        # Initialize model, loss function, and optimizer
        self.t_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        if n_paths == 0:
            n_paths = self.npath_det
        self.nf_ch_model = NF_Channel_Model(n_path=n_paths, fc=self.fc, device=self.t_device)
        self.nf_ch_model = self.nf_ch_model.to(self.t_device)

        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.nf_ch_model.parameters(), lr=lr_init)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=n_epochs//5, gamma=0.1)

        ch_gt = torch.tensor(ch_gt, dtype=torch.complex64, requires_grad=True).to(self.t_device)
        tx_ant_vec = torch.tensor(tx_ant_vec, dtype=torch.float32, requires_grad=True).to(self.t_device)
        rx_ant_vec = torch.tensor(rx_ant_vec, dtype=torch.float32, requires_grad=True).to(self.t_device)
        trx_unit_vec = torch.tensor(trx_unit_vec, dtype=torch.float32, requires_grad=True).to(self.t_device)
        if path_delay is not None:
            path_delay = torch.tensor(path_delay, dtype=torch.float32, requires_grad=True).to(self.t_device)
        if path_gain is not None:
            path_gain = torch.tensor(path_gain, dtype=torch.complex64, requires_grad=True).to(self.t_device)
        freq = torch.tensor(freq, dtype=torch.float32, requires_grad=True).to(self.t_device)

        txid = 1

        # Training loop
        print("alpha: ", self.nf_ch_model.alpha)
        print("s: ", self.nf_ch_model.s)

        for epoch in range(n_epochs):  # Number of epochs
            output = self.nf_ch_model(tx_ant_vec=tx_ant_vec, rx_ant_vec=rx_ant_vec, trx_unit_vec=trx_unit_vec, path_delay=path_delay, path_gain=path_gain, freq=freq)
            loss = criterion(output[:,:,txid,:].real, ch_gt[:,:,txid,:].real) + criterion(output[:,:,txid,:].imag, ch_gt[:,:,txid,:].imag)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            if epoch % (n_epochs//20) == 0:
                print(f'Epoch {epoch+1}/{n_epochs}, Loss: {loss.item()}, LR: {scheduler.get_last_lr()}')
                # print("alpha: ", self.nf_ch_model.alpha)
                # print("s: ", self.nf_ch_model.s)

            scheduler.step()

        print("alpha: ", self.nf_ch_model.alpha)
        print("s: ", self.nf_ch_model.s)


    def plot_results(self, ax=None, RoomModel=None, plot_type='init_est'):
        """
        Plots the heatmaps of the estimated TX locations in each iteration
        """
        if plot_type == 'init_est':
            nplots = 1
        else:
            nplots = self.npath_det

        if ax is None:
            fig, ax = plt.subplots(1, nplots)
            if nplots == 1:
                ax = [ax]

            for i in range(nplots):
            
                # Plot the estimated heatmap
                rho1 = self.rho[:,i].reshape(self.npoints,self.npoints)
                ax[i].contourf(self.xtest0, self.xtest1, rho1)

                # Draw the room walls
                if RoomModel is not None:
                    RoomModel.draw_walls(ax[i])
                    
                
                # Plot the TX locations as blue circles
                ax[i].plot(self.tx[:,0], self.tx[:,1], 'ro')
                ax[i].plot(self.tx_est[i,0], self.tx_est[i,1], 'bx')
                ax[i].set_xlim(self.region[0])
                ax[i].set_ylim(self.region[1])
                if (nplots > 1):
                    ax[i].set_title(f'Iter {i}')
                if (i > 0):
                    ax[i].set_yticks([])
                
                
            plt.tight_layout()
            plt.show()

        else:
            # ax.clear()  # Clear the previous frame
            for c in ax.collections:
                c.remove()
            for point in self.points:
                point.remove()

            i_path = 0
            # Update heatmap
            rho1 = self.rho[:, i_path].reshape(self.npoints, self.npoints)
            contour = ax.contourf(self.xtest0, self.xtest1, rho1)

            # Draw room walls if RoomModel is provided
            if RoomModel is not None:
                RoomModel.draw_walls(ax)

            # Plot TX locations and estimated TX locations
            self.points = []
            point = ax.plot(self.tx[:, 0], self.tx[:, 1], 'ro', markersize=15)  # Actual TX
            self.points.append(point[0])
            for i_path in range(self.npath_det):
                if i_path == 0:
                    color = 'gx'
                else:
                    color = 'bx'
                point = ax.plot(self.tx_est[i_path, 0], self.tx_est[i_path, 1], color, markersize=15)  # Estimated TX
                self.points.append(point[0])

            # # Set plot limits and titles
            # ax.set_xlim(self.region[0])
            # ax.set_ylim(self.region[1])

            # ax.set_title('Heatmap of TX Location probability in the room')
            # ax.set_xlabel("X (m)")
            # ax.set_ylabel("Y (m)")
            # ax.set_yticks([])

            # ax.title.set_fontsize(18)
            # ax.xaxis.label.set_fontsize(15)
            # ax.yaxis.label.set_fontsize(15)
            # ax.tick_params(axis='both', which='both', labelsize=12)  # For major ticks
            # ax.set_xticks(np.arange(self.region[0,0], self.region[0,1], 1.0))
            # ax.set_yticks(np.arange(self.region[1,0], self.region[1,1], 2.0))

        return ax






class NF_Channel_Model(nn.Module):
    def __init__(self, n_path=1, n_rx=2, n_tx=2, n_meas=1, fc=10e9, device='cpu'):
        super(NF_Channel_Model, self).__init__()

        # Initialize learnable parameters for angles of arrival and path coefficients
        self.fc = fc
        self.n_path = n_path
        self.n_rx = n_rx
        self.n_tx = n_tx
        self.n_meas = n_meas
        self.device = device

        self.alpha = nn.Parameter(0.1 * torch.randn(self.n_path), requires_grad=True)  # Rotation angles
        self.s = nn.Parameter(0.1 * torch.randn(self.n_path), requires_grad=True)  # parameter S, the parity of number of reflections

        self.path_gain = torch.complex(torch.randn(self.n_path, self.n_rx, self.n_tx, self.n_meas), torch.randn(self.n_path, self.n_rx, self.n_tx, self.n_meas))      # parameter G, the gain of the path
        self.path_gain = nn.Parameter(self.path_gain)
        # self.path_gain = None

        self.path_delay = torch.randn(self.n_path, self.n_rx, self.n_tx, self.n_meas)  # parameter tau, the delay of the path
        self.path_delay = nn.Parameter(self.path_delay)
        # self.path_delay = None


    def rotation_matrix(self, angle):
        # Define the 2D rotation matrix
        cos_a = torch.cos(angle)
        sin_a = torch.sin(angle)
        return torch.stack([torch.stack([cos_a, -sin_a]), torch.stack([sin_a, cos_a])])


    def forward(self, tx_ant_vec=None, rx_ant_vec=None, trx_unit_vec=None, path_delay=None, path_gain=None, freq=None):
        '''
        Compute the channel response for a given TX and RX antenna vector.
        tx_ant_vec: (t,m,p), t: number of TX antennas, m: number of measurements, p: dimension of the region
        rx_ant_vec: (r,m,p), r: number of RX antennas, m: number of measurements, p: dimension of the region
        trx_unit_vec: (np,m,p), np:number of estimated paths, m: number of measurements, p: dimension of the region
        '''

        n_rx = rx_ant_vec.shape[0]
        n_tx = tx_ant_vec.shape[0]
        n_meas = rx_ant_vec.shape[1]
        n_fft = freq.shape[0]
        p = rx_ant_vec.shape[-1]

        if path_delay is None:
            path_delay = self.path_delay
        if path_gain is None:
            path_gain = self.path_gain

        # print("tx_ant_vec: ", tx_ant_vec)
        # print("rx_ant_vec: ", rx_ant_vec)
        # print("trx_unit_vec: ", trx_unit_vec)
        # print("path_delay: ", path_delay)
        # print("path_gain: ", path_gain)
        H = torch.zeros(n_fft, n_rx, n_tx, n_meas, dtype=torch.complex64)

        # Sum the contributions from each path
        for i in range(self.n_path):

            rotation_mat = self.rotation_matrix(self.alpha[i])
            rot_tx_ant_vec = torch.matmul(tx_ant_vec.reshape(-1, p), rotation_mat.T)
            rot_tx_ant_vec = rot_tx_ant_vec.reshape(tx_ant_vec.size())

            tanh_scale = 1
            dist_vec = rx_ant_vec[:,None,:,:] - (constants.c*(path_delay[i])[:,:,:,None]*(trx_unit_vec[i])[None,None,None,:]) - (torch.tanh(tanh_scale*self.s[i])*rot_tx_ant_vec)[None,:,:,:]
            dist = torch.linalg.norm(dist_vec, dim=-1)
            f = self.fc + freq
            H += (path_gain[i])[None,:,:,:] * torch.exp(1j*2*np.pi/constants.c * f[:,None,None,None] * dist[None,:,:,:])

        return H




if __name__ == '__main__':
    # Parameters
    fc = 12e9  # Carrier frequency   
    fsamp = 1e9 # Sample freq in Hz
    nantrx=2  # Number of antennas per array
    antsep=np.array([0.5,1,2,4]) # Separation between antennas in wavelengths
    rxlocsep = np.array([0,1])    # Separation between RX locations
    npath=4   # Number of paths
    npath_est = [20, 5]  # Maximum number of paths to estimate
    plot_type = 'init_est' 



    from rfsoc_test import Params_Class
    from signal_utilsrfsoc import Signal_Utils_Rfsoc
    params = Params_Class()
    params.channel_limit = False
    params.sc_range_ch = [-1*params.nfft_trx//2, params.nfft_trx//2-1]
    params.freq_hop_list = [fsamp]
    params.fs = fsamp
    params.fs_tx=params.fs
    params.fs_rx=params.fs
    params.fs_trx=params.fs

    params.nf_npath_max = npath_est
    params.nf_rx_loc_sep = rxlocsep
    params.nf_tx_ant_sep = 0.5
    params.nf_rx_ant_sep = antsep
    params.n_rx_ant = nantrx

    # Construct the room
    rm = RoomModel()

    # Place a source
    xsrc = np.array([6,4])
    params.nf_tx_loc = xsrc

    # Find the reflections
    xref = rm.find_reflection(xsrc)

    # Create all the transmitters
    xtx =  np.vstack((xsrc, xref))

    params.initialize()
    signals_inst = Signal_Utils_Rfsoc(params)

    # Create the simulation object and run the simulation
    sim = Sim(fc=fc, fsamp=fsamp, nantrx=nantrx,
            rxlocsep=rxlocsep, antsep=antsep, npath=npath,
            tx=xtx,npath_est=npath_est[1])


    # Generate the TX positions and search region
    sim.gen_tx_pos()

    # Compute the RX locations and antenna positions
    sim.compute_rx_pos()

    # Compute the channel frequency response
    sim.compute_freq_resp()

    # Create the test points for the TX locations
    sim.create_tx_test_points()

    #================================================================================================
    h = np.expand_dims(sim.chan_td, axis=2)
    h = np.repeat(h, 2, axis=2)

    dly_est_nf = []
    peaks_nf = []
    npaths_nf = []
    for i in range(h.shape[-1]):
        h_ = h[:,:,:,i]
        h_ = np.expand_dims(h_, axis=3)
        h_ = np.repeat(h_, params.n_rd_rep, axis=3)
        sparse_est_params = signals_inst.sparse_est(h=h_, g=None, sc_range_ch=signals_inst.sc_range_ch, npaths=signals_inst.nf_npath_max, nframe_avg=1, ndly=5000, drange=[-1,100], cv=True, n_ignore=200)
        (h_tr, dly_est, peaks, npath_est) = sparse_est_params
        dly_est_nf.append(dly_est)
        peaks_nf.append(peaks)
        npaths_nf.append(npath_est)
    dly_est = np.array(dly_est_nf)
    peaks = np.array(peaks_nf)
    npaths = np.array(npaths_nf)
    

    #================================================================================================
    signals_inst.nf_model = sim
    h = h.transpose((3,1,2,0))
    sim.plot_chan_td(slice(0,100))
    signals_inst.est_nf_param(h, dly_est, peaks, npaths)

    # dly_est = np.transpose(dly_est.copy(), (3,1,2,0))
    # peaks = np.transpose(peaks.copy(), (3,1,2,0))
    # npaths = np.transpose(npaths.copy(), (1,2,0))
    # n_paths_min = np.min(npaths)
    
    # txid = 0

    # sim.sparse_dly_est = dly_est[:,:,txid,:]
    # sim.sparse_peaks_est = peaks[:,:,txid,:]
    # # sim.npath_est = n_paths_min
    # signals_inst.print("Number of paths estimated: {}".format(n_paths_min), thr=0)

    # sim.path_est_init()
    # sim.locate_tx(npath_est=n_paths_min)
    # # sim.plot_results(RoomModel=signals_inst.RoomModel, plot_type='')

    # n_epochs = 10000
    # lr_init = 0.1
    # ch_gt = h.copy()
    # tx_ant_vec = signals_inst.nf_tx_ant_loc[:,:,:] - (signals_inst.nf_tx_ant_loc[0,0,:])[None,None,:] + 0.01
    # rx_ant_vec = signals_inst.nf_rx_ant_loc[:,:,:] - (signals_inst.nf_rx_ant_loc[0,0,:])[None,None,:]
    # phase_diff = peaks[:n_paths_min,1,0,:]-peaks[:n_paths_min,0,0,:]        # TODO: Maybe 0-1 instead of 1-0
    # phase_diff = np.mean(phase_diff, axis=-1)
    # aoa = signals_inst.phase_to_aoa(phase_diff, wl=signals_inst.wl, ant_dim=signals_inst.ant_dim, ant_dx_m=signals_inst.ant_dx_m, ant_dy_m=signals_inst.ant_dy_m)
    # trx_unit_vec = np.stack((np.sin(aoa), np.cos(aoa)), axis=-1)
    # path_delay = sim.abs_delay.copy()[:n_paths_min,:,None,:] * np.ones(dly_est.shape)
    # path_gain = peaks.copy()[:n_paths_min]
    # # path_delay = None
    # # path_gain = None
    # freq = signals_inst.freq_ch.copy()
    # sim.nf_channel_param_est(n_paths=n_paths_min, n_epochs=n_epochs, lr_init=lr_init, ch_gt=ch_gt, tx_ant_vec=tx_ant_vec, rx_ant_vec=rx_ant_vec, trx_unit_vec=trx_unit_vec, path_delay=path_delay, path_gain=path_gain, freq=freq)
    #================================================================================================

    
    if (plot_type == 'init_est') or (plot_type == 'iter_est'):
        """
        Plots the heatmaps of the estimated TX locations in each iteration
        """
        if plot_type == 'init_est':
            nplots = 1
        else:
            nplots = sim.npath_det

        fig, ax = plt.subplots(1, nplots)
        if nplots == 1:
            ax = [ax]
        for i in range(nplots):
        
            # Plot the estimated heatmap
            rho1 = sim.rho[:,i].reshape(sim.npoints,sim.npoints)
            ax[i].contourf(sim.xtest0, sim.xtest1, rho1)

            # Draw the room walls
            rm.draw_walls(ax[i])
                
            
            # Plot the TX locations as blue circles
            ax[i].plot(sim.tx[:,0], sim.tx[:,1], 'ro')
            ax[i].plot(sim.tx_est[i,0], sim.tx_est[i,1], 'gx')
            ax[i].set_xlim(sim.region[0])
            ax[i].set_ylim(sim.region[1])
            if (nplots > 1):
                ax[i].set_title(f'Iter {i}')
            if (i > 0):
                ax[i].set_yticks([])
            
            
        plt.tight_layout()
        plt.show()





