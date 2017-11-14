import numpy as np
import wx
import wx.lib.buttons as buttons

import matplotlib
matplotlib.interactive(False)
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure
from matplotlib.pyplot import gcf,setp

import RFI_fits as RFI
#import RFI
#import smooth

import cPickle as pic
import sys

global uv,baseline


class Baseline_Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.parent = args[0]

        self.rfi_Window = self.parent.rfi_Window
        a1,a2 = uv.base_name[uv.bl[self.rfi_Window.baseline]]
        base_name = "%i %s-%s" % (bl,a1,a2)

        self.heading = wx.StaticText(self,label='Baseline',pos=(20,0))

        self.next_button = wx.Button(self,-1,'Prev',pos=(0,20),size=(40,24))
        self.prev_button = wx.Button(self,-1,'Next',pos=(50,20),size=(40,24))
        self.baseText = wx.StaticText(self,-1,base_name,pos=(10,50),size=(60,24))
        self.rb1 = wx.RadioButton(self, -1, 'RR', (10, 70), style=wx.RB_GROUP)
        self.rb2 = wx.RadioButton(self, -1, 'LL', (50, 70))

        self.next_button.Bind(wx.EVT_BUTTON,self.set_baseline)
        self.prev_button.Bind(wx.EVT_BUTTON,self.set_baseline)

        self.rb1.Bind(wx.EVT_RADIOBUTTON,self.set_pol)
        self.rb2.Bind(wx.EVT_RADIOBUTTON,self.set_pol)

    def set_baseline(self,e):

        btn = e.GetEventObject()
        lab = btn.GetLabel()

        nbas = len(uv.amp)
        bl = self.rfi_Window.baseline

        if lab=="Next":
            bl += 1
        elif lab=="Prev":
            bl -= 1

        if bl==nbas:
            bl = 0

        if bl<0:
            bl = nbas-1

        rfi_window = self.parent.rfi_Window
        tpanel = self.parent.controls.threshold_panel

        if rfi_window.rms_thres[bl]==0:
            rfi_window.rms_thres[bl] = tpanel.rms_slider.GetValue()/100.
        else:
            tpanel.set_rms_thres(rfi_window.rms_thres[bl])

        if rfi_window.amp_thres[bl]==0:
            rfi_window.amp_thres[bl] = tpanel.amp_slider.GetValue()/100.
        else:
            tpanel.set_amp_thres(rfi_window.amp_thres[bl])

        a1,a2 = uv.base_name[uv.bl[bl]]
        base_name = "%i %s-%s" % (bl,a1,a2)
        self.baseText.SetLabel(base_name)
        self.rfi_Window.set_baseline(bl)

    def set_pol(self,evt):
        btn = evt.GetEventObject()
        lab = btn.GetLabel()

        if lab=='RR':
            pol = 0
        elif lab=='LL':
            pol=1

        self.rfi_Window.set_polarization(pol)


class Smoothing_Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.parent = args[0]
        self.rfi_Window = self.parent.rfi_Window

        self.heading = wx.StaticText(self,label='Smoothing scale',pos=(30,0))

        self.smooth_slider = wx.Slider(self,-1,style=wx.SL_HORIZONTAL,pos=(0,20),size=(150,20))
        self.smooth_slider.SetMax(200)
        self.smooth_slider.SetPageSize(1)
        self.smooth_slider.SetValue(100)
        self.smooth_slider.Bind(wx.EVT_SCROLL, self.smooth_Slider_Handler)

        smooth_val = self.smooth_slider.GetValue()
        self.smooth_text = wx.StaticText(self,label="%2.1f" % (smooth_val/10.), pos=(10,40))

        self.go_Button = wx.Button(self,-1,'Set',pos=(70,50),size=(40,25))
        self.go_Button.Bind(wx.EVT_BUTTON,self.set_smoothing_scale)

    def smooth_Slider_Handler(self,evt):
        val = self.smooth_slider.GetValue()/10.
        self.smooth_text.SetLabel("%2.1f" % val)

    def set_smoothing_scale(self,evt):
        val = self.smooth_slider.GetValue()/10.
        self.rfi_Window.set_smoothing_scale(val)


class Threshold_Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.parent = args[0]
        self.rfi_Window = self.parent.rfi_Window

        self.heading = wx.StaticText(self,label='Threshold levels',pos=(30,0))

        self.rms_slider = wx.Slider(self,-1,style=wx.SL_HORIZONTAL,pos=(0,20),size=(400,20))
        self.rms_slider.SetMax(1000)
        self.rms_slider.SetPageSize(5)
        self.rms_slider.SetValue(200)
        self.rms_slider.Bind(wx.EVT_SCROLL, self.rms_Slider_Handler)

        rms_thres = self.rms_slider.GetValue()
        self.rms_thres_text = wx.StaticText(self,label="RMS threshold %2.2f" % (rms_thres/100.), pos=(20,40))


        self.amp_slider = wx.Slider(self,-1,style=wx.SL_HORIZONTAL,pos=(0,50),size=(400,20))
        self.amp_slider.SetMax(2000)
        self.amp_slider.SetPageSize(10)
        self.amp_slider.SetValue(1000)
        self.amp_slider.Bind(wx.EVT_SCROLL, self.amp_Slider_Handler)

        amp_thres = self.amp_slider.GetValue()
        self.amp_thres_text = wx.StaticText(self,label="Amp threshold %2.2f" % (amp_thres/100.), pos=(20,70))


    def rms_Slider_Handler(self,evt):
        val = self.rms_slider.GetValue()/100.
        self.rms_thres_text.SetLabel("RMS threshold %2.2f" % val)
        self.rfi_Window.set_rms_threshold(val)

    def set_rms_thres(self,val):
        self.rms_thres_text.SetLabel("RMS threshold %2.2f" % val)
        self.rms_slider.SetValue(val*100)

    def amp_Slider_Handler(self,evt):
        val = self.amp_slider.GetValue()/100.
        self.amp_thres_text.SetLabel("Amp threshold %2.2f" % val)
        self.rfi_Window.set_amp_threshold(val)

    def set_amp_thres(self,val):
        self.amp_thres_text.SetLabel("Amp threshold %2.2f" % val)
        self.amp_slider.SetValue(val*100)


class File_Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.parent = args[0]

        self.heading = wx.StaticText(self,label='Settings',pos=(50,0))

        self.load_button = wx.Button(self,-1,'Load',pos=(0,20),size=(40,24))
        self.load_button.Bind(wx.EVT_BUTTON,self.load_settings)

        self.save_button = wx.Button(self,-1,'Save',pos=(100,20),size=(40,24))
        self.save_button.Bind(wx.EVT_BUTTON,self.save_settings)

        self.filename = wx.StaticText(self,label='Default',pos=(0,60))


    def save_settings(self,evt):

        saveFileDialog = wx.FileDialog(self, "Save settings pic file", "", "",
                        "Settings (*.pic)|*.pic", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if saveFileDialog.ShowModal() == wx.ID_CANCEL:
            return

        filename = saveFileDialog.GetPath()
        pf = open(filename,'wb')

        smo_val = self.parent.controls.smoothing_panel.smooth_slider.GetValue()/10.
        pic.dump(smo_val,pf)

        rms_thres = self.parent.rfi_Window.rms_thres
        pic.dump(rms_thres,pf)

        amp_thres = self.parent.rfi_Window.amp_thres
        pic.dump(amp_thres,pf)

        pf.close()

        filename = filename.split('/')[-1]
        self.filename.SetLabel(filename)


    def load_settings(self,evt):

        openFileDialog = wx.FileDialog(self, "Open settings pic file", "", "",
                        "Settings (*.pic)|*.pic", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return

        filename = openFileDialog.GetPath()
        pf = open(filename,'rb')

        smo_val = pic.load(pf)
        rms_thres = pic.load(pf)
        amp_thres = pic.load(pf)
        pf.close()

        bl = self.parent.rfi_Window.baseline
        self.parent.rfi_Window.rms_thres = rms_thres
        val = rms_thres[bl]
        self.parent.controls.threshold_panel.rms_thres_text.SetLabel("RMS threshold %2.2f" % val)
        self.parent.controls.threshold_panel.rms_slider.SetValue(val*100)

        self.parent.rfi_Window.amp_thres = amp_thres
        val = amp_thres[bl]
        self.parent.controls.threshold_panel.amp_thres_text.SetLabel("Amp threshold %2.2f" % val)
        self.parent.controls.threshold_panel.amp_slider.SetValue(val*100)

        self.parent.controls.smoothing_panel.smooth_text.SetLabel("%2.1f" % smo_val)
        self.parent.controls.smoothing_panel.smooth_slider.SetValue(smo_val*10)
        self.parent.rfi_Window.set_smoothing_scale(smo_val)

class Flags_Panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.parent = args[0]

        self.heading = wx.StaticText(self,label='Write Flags',pos=(20,0))
        self.write_button = wx.Button(self,-1,'Go',pos=(0,30),size=(100,35))
        self.write_button.Bind(wx.EVT_BUTTON,self.write_flags)
        self.status = wx.StaticText(self,label='       ',pos=(10,70))

    def write_flags(self,evt):
        self.status.SetLabel('Writing flags')
        uv.write_flag_table()
        self.status.SetLabel('Done')

class Controls():
    def __init__(self,parent):
        self.parent = parent

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.baseline_panel = Baseline_Panel(parent)
        self.smoothing_panel = Smoothing_Panel(parent)
        self.threshold_panel = Threshold_Panel(parent)
        self.file_panel = File_Panel(parent)
        self.flags_panel = Flags_Panel(parent)

        sizer.Add(self.baseline_panel,1,wx.EXPAND)
        sizer.Add(wx.StaticLine(self.parent, -1, style=wx.LI_VERTICAL),1,wx.EXPAND)
        sizer.Add(self.smoothing_panel,2,wx.EXPAND)
        sizer.Add(wx.StaticLine(self.parent, -1, style=wx.LI_VERTICAL),1,wx.EXPAND)
        sizer.Add(self.threshold_panel,2,wx.EXPAND)
        sizer.Add(wx.StaticLine(self.parent, -1, style=wx.LI_VERTICAL),1,wx.EXPAND)
        sizer.Add(self.file_panel,2,wx.EXPAND)
        sizer.Add(wx.StaticLine(self.parent, -1, style=wx.LI_VERTICAL),1,wx.EXPAND)
        sizer.Add(self.flags_panel,2,wx.EXPAND)

        self.sizer = sizer

class RFI_Frame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.rfi_Window = RFI_Window(self)
        self.controls = Controls(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.rfi_Window,0,wx.EXPAND)
        sizer.Add(self.controls.sizer,0,wx.EXPAND)

        self.SetSizer(sizer)


class RFI_Window(wx.Window):

    def __init__(self, *args, **kwargs):
        wx.Window.__init__(self, *args, **kwargs)

        self.baseline = 0

        nbas = len(uv.amp)
        self.rms_thres = np.zeros(nbas,'f')
        self.amp_thres = np.zeros(nbas,'f')
        self.sig = 10.0
        self.pol = 0

        print uv.err[self.baseline].shape
        self.rms_smooth = self.smooth(uv.err[self.baseline][:,:,1],self.sig)
        self.amp_smooth = self.smooth(uv.amp[self.baseline][:,:,1],self.sig)

        self.figure = Figure(figsize=(12,7.5),dpi=100)
        self.canvas = FigureCanvasWxAgg(self,-1,self.figure)

        main_box = wx.BoxSizer(wx.HORIZONTAL)
        main_box.Add(self.canvas, flag=wx.EXPAND, proportion=1)
        self.SetSizer(main_box)

        self.draw()


    def smooth(self,e,sig,ndx=25):
        x = np.arange(-ndx,ndx+1)
        y = x[:,np.newaxis]
        r2 = x**2 + y**2
        g = np.exp(-r2/2/sig**2)

        w   = 1./e**2
        smo = smooth.weighted(e,w,g)

        return smo

    def set_baseline(self,bl):
        self.baseline = bl
        self.rms_smooth_rr = self.smooth(uv.err[self.baseline][:,:,0],self.sig)
        self.rms_smooth_ll = self.smooth(uv.err[self.baseline][:,:,1],self.sig)
#        self.amp_smooth = self.smooth(uv.amp[self.baseline][:,:,1],self.sig)
        self.apply_thres()
        self.draw()
        self.repaint()

    def set_polarization(self,pol):
        self.pol = pol
        self.draw()
        self.repaint()

    def set_smoothing_scale(self,smooth):
        self.sig = smooth
        self.rms_smooth_rr = self.smooth(uv.err[self.baseline][:,:,0],self.sig)
        self.rms_smooth_ll = self.smooth(uv.err[self.baseline][:,:,1],self.sig)
#        self.amp_smooth = self.smooth(uv.amp[self.baseline][:,:,1],self.sig)
        self.apply_thres()
        self.draw()
        self.repaint()

    def set_rms_threshold(self,rms_thres):
        self.rms_thres[self.baseline] = rms_thres
        self.apply_thres()
        self.draw()
        self.repaint()

    def set_amp_threshold(self,amp_thres):
        self.amp_thres[self.baseline] = amp_thres
        self.apply_thres()
        self.draw()
        self.repaint()

    def apply_thres(self):
        bl = self.baseline
        uv.flg[bl][:,:]  = np.where(uv.err[bl][:,:,0]/self.rms_smooth_rr>self.rms_thres[bl],0,1)
        uv.flg[bl][:,:] *= np.where(uv.err[bl][:,:,1]/self.rms_smooth_ll>self.rms_thres[bl],0,1)
        med_amp_rr = np.median(uv.amp[bl][:,:,0]*uv.flg[bl])
        med_amp_ll = np.median(uv.amp[bl][:,:,1]*uv.flg[bl])
        uv.flg[bl][:,:] *= np.where(uv.amp[bl][:,:,0]/med_amp_rr>self.amp_thres[bl],0,1)
        uv.flg[bl][:,:] *= np.where(uv.amp[bl][:,:,1]/med_amp_ll>self.amp_thres[bl],0,1)


    def draw(self):
        bl = self.baseline
        pol = self.pol
        print bl

        print uv.amp[bl].shape,uv.flg[bl].shape
        if not hasattr(self,'subplot'):

            self.subplot = self.figure.add_subplot(111)
            print uv.amp[bl][:,:,pol].shape,uv.flg[bl].shape
            self.imshow = self.subplot.imshow(uv.amp[bl][:,:,pol]*uv.flg[bl],aspect='auto')
        else:
            self.imshow.set_data(uv.amp[bl][:,:,pol]*uv.flg[bl])

        vmin = np.min(uv.amp[bl][:,:,pol]*uv.flg[bl])
        vmax = np.max(uv.amp[bl][:,:,pol]*uv.flg[bl])
        self.imshow.set_clim(vmin=vmin,vmax=vmax)

    def repaint(self):
        print self.baseline
        self.canvas.draw()


class App(wx.App):
    def OnInit(self):

        self.frame1 = RFI_Frame(parent=None,title='RFI removal tool',size=(1200,850))
        self.frame1.Show()
        return True

if __name__=='__main__':

    fits_file = sys.argv[1]

    uv = RFI.read_fits(fits_file,progress=1)
    bl = 0

#    pf = open('BP_pickle.pic')
#    bpr1,bpi1 = pic.load(pf)
#    bpr2,bpi2 = pic.load(pf)
#    pf.close()

#    bpr1.shape = (9,1024,4)
#    bp1 = np.mean(bpr1,axis=2)
#    bp1 = bp1[:,np.newaxis,:]

#    bpr2.shape = (9,1024,4)
#    bp2 = np.mean(bpr2,axis=2)
#    bp2 = bp2[:,np.newaxis,:]

#    bp1 = np.where(bp1!=bp1,1,bp1)
#    bp1 = np.where(bp1<1e-2,1,bp1)

#    bp2 = np.where(bp2!=bp2,1,bp2)
#    bp2 = np.where(bp2<1e-2,1,bp2)

#    for i in range(21):
#        a1,a2 = uv.base_name[i+1]
#        a1 = RFI.ant_ID[a1]-1
#        a2 = RFI.ant_ID[a2]-1

#        bp_corr = np.sqrt(bp1[a1,:,:]*bp2[a2,:,:])

#        print  uv.amp[i].shape, bp_corr.shape
#        uv.amp[i][:,:,0] = uv.amp[i][:,:,0]/bp_corr
#        uv.amp[i][:,:,1] = uv.amp[i][:,:,1]/bp_corr
#        uv.err[i][:,:,0] = uv.err[i][:,:,0]/bp_corr
#        uv.err[i][:,:,1] = uv.err[i][:,:,1]/bp_corr

    app = App()
    app.MainLoop()
