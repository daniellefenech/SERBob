import numpy as np
import pylab as plt
#import smooth
#import pyfits as fits
import astropy.io.fits as fits  # Select fts as apropiate
import sys

ant_ID = {'LO':1, 'MK2':2, 'KN':5, 'DE':6, 'PI':7, 'DA':8, 'CM':9}
ant_no = {1:1, 2:2, 5:3, 6:4, 7:5, 8:6, 9:7}
ant_name = ['LO','MK2','KN','DE','PI','DA','CM']

class VisData:
    """Class to store visiility data for RFI module"""
    def __init__(self,hdu):
        self.hdu = hdu

    def get_nvis(self):
        nobs = len(self.hdu)-5
        nvis = 0
        for i in np.arange(nobs):
            nvis += self.hdu[i+5].header['NAXIS2']

        self.nobs = nobs
        self.nvis_tot = nvis

    def get_start_time(self):
        self.start_time = self.hdu[5].data.TIME[0]

    def get_freq(self):
        self.freq = self.hdu[5].header['REF_FREQ']
        self.dfrq = self.hdu[5].header['CHAN_BW']
        self.pfrq = self.hdu[5].header['REF_PIXL']

        self.nstoke = self.hdu[5].header['MAXIS2']
        self.nchan  = self.hdu[5].header['MAXIS3']
        self.nif    = self.hdu[5].header['MAXIS4']

    def get_ants(self):
        self.nant = len(self.hdu[1].data)-1


    def reset_flags(self):
        for i in range(len(self.flg)):
            self.flg[i][:,:] = 1

    def write_flag_table(self):
        """Append flags into new FG fits file"""

        hdulist = []

        prihdu = fits.PrimaryHDU()

        hdulist.append(prihdu)

        for i in range(len(self.bl)):

          print i,self.vtim[i].shape,self.flg[i].shape

          col1 = fits.Column(name='TIME',format='D',array=self.vtim[i])
          col2 = fits.Column(name='FLAG',format='1024B',array=self.flg[i])

          cols = fits.ColDefs([col1,col2])

#          hdu = fits.BinTableHDU.from_columns(cols) # new version
          hdu = fits.new_table(cols)

          a1,a2 = self.base_name[self.bl[i]]
          ant1 = ant_ID[a1]
          ant2 = ant_ID[a2]

          hdu.header['StartT'] = self.start_time
          hdu.header['DeltaT'] = self.dt
          hdu.header['ANT1'] = ant1
          hdu.header['ANT2'] = ant2
          hdu.header['A1'] = a1
          hdu.header['A2'] = a2

          hdulist.append(hdu)

        hdulist = fits.HDUList(hdulist)

        hdulist.writeto('Test_Flags.fits')

def read_fits(fits_file,dch=4,dt=10,progress=False,MAD=0):
#    """Routine to read given uvdata into a VisData class"""

    hdu = fits.open(fits_file)

  # Extract header information to put in visdata

    vd = VisData(hdu)
    vd.src = fits_file
    vd.dchan = dch
    vd.dt = dt/86400.
    vd.get_nvis()
    vd.get_start_time()
    vd.get_freq()
    vd.get_ants()
    vd.nbas = vd.nant*(vd.nant-1)/2 + vd.nant
    vd.nvis = vd.nvis_tot/vd.nbas
#    vd.nif,vd.nchan,vd.nstoke,vd.nval = uvdata[0].visibility.shape

    vd.base_ant = []
    vd.base_name = []
    for i in np.arange(vd.nant+1):
        for j in np.arange(i+1,vd.nant+1):
            vd.base_ant.append((i+1,j+1))
            print "b/l=",ant_name[i],ant_name[j]
            vd.base_name.append((ant_name[i],ant_name[j]))

  # Intialise lists to contain visibility data

    vis  = [[] for i in range(vd.nbas)]
    vis2 = [[] for i in range(vd.nbas)]
    vhit = [[] for i in range(vd.nbas)]
    vd.vtim = [[] for i in range(vd.nbas)]

    nb = 0
    tdic = [{} for i in range(vd.nbas)]

  # Read in visibility arrays and append lists

    ipos = np.zeros(vd.nbas,'i')
    itot = 0

    for io in np.arange(vd.nobs):
      nvis_obs = vd.hdu[5+io].header['NAXIS2']
      for i in np.arange(nvis_obs):
        itot += 1
        baseline = vd.hdu[5+io].data.BASELINE[i]
        ant1 = baseline/256
        ant2 = baseline%256


        if ant1==ant2:
            continue

        if ant1<ant2:
            a1 = ant_no[ant1]
            a2 = ant_no[ant2]
        else:
            a1 = ant_no[ant2]
            a2 = ant_no[ant1]

        ib = (2*vd.nant+2-a1)*(a1-1)/2 + a2 - a1 -1

#        print i, a1, a2, ib

        t = vd.hdu[io+5].data.TIME[i]
        it = int((t-vd.start_time)/vd.dt)
        flux = vd.hdu[io+5].data.FLUX[i,:]
        flux.shape = (8,512,4,2)
        a = np.sqrt(flux[:,:,:,0]**2+flux[:,:,:,1]**2)
        a = a.reshape(vd.nif*vd.nchan/4,4,vd.nstoke).sum(axis=1)

        if progress:
          if itot%1000==0:
            pc = itot*101/vd.nvis_tot
            pc5 = pc/5
            sys.stdout.write('\r')
            sys.stdout.write('Loading %s [%-20s] %d%%' % (vd.src,'='*pc5,pc))
            sys.stdout.flush()

        if not tdic[ib].has_key(it):
            tdic[ib][it] = ipos[ib]
            vis[ib].append(a)
            vis2[ib].append(a**2)
            vhit[ib].append(4)
            vd.vtim[ib].append(it)
            ipos[ib] += 1
        else:
            ip = tdic[ib][it]
            vis[ib][ip] += a
            vis2[ib][ip] += a**2
            vhit[ib][ip] += 4

    vd.end_time = vd.hdu[vd.nobs+4].data.TIME[-1]
    vd.nt = int((vd.end_time-vd.start_time)/vd.dt)+1

    print '\n Calculating stats'

  # Convert lists to arrays

    for i in np.arange(vd.nbas):
        vis[i] =  np.array(vis[i])
        vis2[i] = np.array(vis2[i])
        vhit[i] = np.array(vhit[i])
        vhit[i] = vhit[i][:,np.newaxis,np.newaxis]
        vd.vtim[i] = np.array(vd.vtim[i])

  # For each baseline generate amp and error arrays in visdata

    vd.amp = []
    vd.err = []
    vd.bl = []
    vd.flg = []

    print len(vd.base_ant)

    for i in np.arange(vd.nbas):

        print vd.base_ant[i][0],vd.base_ant[i][1]
        if vd.base_ant[i][0]==vd.base_ant[i][1]:
            continue

        vd.bl.append(i)

        Avis = vis[i]/vhit[i]

        Avis_err = np.sqrt(vis2[i]-vis[i]**2/vhit[i])
        Avis_err /= np.sqrt(vhit[i]*(vhit[i]-1))

        Avis = np.where(vhit[i]==0,0,Avis)
        Avis_err = np.where(vhit[i]==0,1e10,Avis_err)
        Avis_err = np.where(Avis_err<1e-6,1e10,Avis_err)

        Avis_err = np.where(Avis==np.nan,1e10,Avis_err)
        Avis = np.where(Avis==np.nan,0,Avis)

        print i,Avis_err.shape
        vd.amp.append(Avis)
        vd.err.append(Avis_err)

        vd.flg.append(np.ones(Avis.shape[:2],dtype='b'))


    return vd


def flag_via_amp(vd,thres=1.5,sig=4,ndx=20):
    """Flag based on ratio of amps to smoothed weighted amps"""

    x = np.arange(-ndx,ndx+1)
    y = x[:,np.newaxis]
    r2 = x**2 + y**2
    g = np.exp(-r2/2/sig**2)

    for i in range(len(vd.amp)):
      for j in range(2):
        if vd.amp[i].shape[0]==0:
            continue
        a = vd.amp[i][:,:,j]
        e = vd.err[i][:,:,j]
        w   = 1./e**2
        smo = smooth.weighted(a,w,g)
        vd.flg[i] *= np.where(e/smo>thres,0,1)


def flag_via_rms(vd,thres=1.5,sig=4,ndx=20):
    """Flag based on ratio of errs to smoothed weighted"""

    x = np.arange(-ndx,ndx+1)
    y = x[:,np.newaxis]
    r2 = x**2 + y**2
    g = np.exp(-r2/2/sig**2)

    for i in range(len(vd.amp)):
      for j in range(2):
        if vd.amp[i].shape[0]==0:
            continue
        e = vd.err[i][:,:,j]
        w   = 1./e**2
        smo = smooth.weighted(e,w,g)
        vd.flg[i] *= np.where(e/smo>thres,0,1)


def flag_via_s2n(vd,thres=0.8,sig=2,ndx=20):
    """Flag based on ratio of amps to smoothed weighted amps"""

    x = np.arange(-ndx,ndx+1)
    y = x[:,np.newaxis]
    r2 = x**2 + y**2
    g = np.exp(-r2/2/sig**2)

    for i in range(len(vd.amp)):
      for j in range(2):
        if vd.amp[i].shape[0]==0:
            continue
        s2n = vd.amp[i][:,:,j]/vd.err[i][:,:,j]
        e = vd.err[i][:,:,j]
        w   = 1./e**2
        smo = smooth.weighted(s2n,w,g)
        vd.flg[i] *= np.where(s2n/smo<thres,0,1)

def flag_via_amp_median_threshold(vd,thres=2.0):
    """Flag above signal*thres*median(signal)"""
    for i in range(len(vd.amp)):
      ix,iy = np.where(vd.flg[i][:,:]==1)
      for j in range(2):
        if vd.amp[i].shape[0]==0:
            continue
        med_amp = np.median(vd.amp[i][ix,iy,j])
        vd.flg[i] *= np.where((vd.amp[i][:,:,j]>med_amp*thres),0,1)

def flag_via_rms_median_threshold(vd,thres=2.0):
    """Flag above err*thres*median(err)"""
    for i in range(len(vd.err)):
      ix,iy = np.where(vd.flg[i][:,:]==1)
      for j in range(2):
        if vd.amp[i].shape[0]==0:
            continue
        med_err = np.median(vd.err[i][ix,iy,j])
        vd.flg[i] *= np.where((vd.err[i][:,:,j]>med_err*thres),0,1)
