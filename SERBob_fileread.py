import copy
import numpy as np
import multiprocessing as multip


def get_metadata(msname):

    ms.open(msname,nomodify=False)
    metadata=ms.metadata()

    ## Source list
    source_lookup=metadata.namesforfields()
    source_list={}
    for i in xrange(len(source_lookup)):
        srce = source_lookup[i]
        if not srce == '':
            source_list[i] = srce
    source_lookup = [x for x in source_lookup if x]
    source_temp = copy.copy(source_lookup)
    if flag_sources == 'choose':
        # print flag_list
        for srce in source_temp:
            if srce in flag_list:
                # print 'yes',srce
                continue
            else:
                # print 'no',srce
                source_lookup.remove(srce)
                for k in source_list.keys():
                    if source_list[k] == srce:
                        # print k, source_list[k]
                        del source_list[k]
    del(source_temp)
    print " Flagging sources: %s" % ', '.join(str(x) for x in source_lookup)


    ## Name of Telescope:
    telescope = metadata.observatorynames()
    # sets up local variable
    nvis = int(metadata.nrows()) ## prints the number of visibilities
    print " Total number of visibilities (nvis): %i" % nvis

    ## Find the Frequency of the observation
    frequency = metadata.reffreq(0)
    #print " Frequency of the first spw: %s" % freq_prefix(frequency)
    #print " Frequency band of the Observation: %s" % freq_band(frequency)



    ## Figure out polarisations ##

    # CASA metadata.corrtypesforpol(0) i.e. correlation types for polarisation setup 0
    # CASA has inbuilt reference list for corrtype numbers and stokes parms.
    # Taken from here: 
    # http://casa.nrao.edu/active/docs/doxygen/html/classcasa_1_1Stokes.html#ae3cb0ef26262eb3fdfbef8273c455e0c
    # Dictionary created from above list
    casacorrdir = {0:'', 1:'I', 2:'Q', 3:'U', 4:'V', 5:'RR', 6:'RL', 7:'LR', 8:'LL', 9:'XX', 10:'XY', 11:'YX', 12:'YY', 13:'RX', 14:'RY', 15:'LX', 16:'LY', 17:'XR', 18:'XL', 19:'YR', 20:'YL', 21:'PP', 22:'PQ', 23:'QP', 24:'QQ', 25:'RCircular', 26:'LCircular', 27:'Linear', 28:'Ptotal', 29:'Plinear', 30:'PFtotal', 31:'PFlinear',32:'Pangle'}
    # Assuming only one polarisation setup for now #
    # Also assuming data ordered in polarisation in the same order as given in corrtypes #
    corrtypes = metadata.corrtypesforpol(0)
    polnames = {}
    bpolnames = {}
    orderedpols = {}
    for i in xrange(len(corrtypes)):
        polnames[casacorrdir[corrtypes[i]]] = i
        bpolnames[i] = casacorrdir[corrtypes[i]]
        orderedpols[casacorrdir[corrtypes[i]]] = corrtypes[i]


    # If selected stokes requested, remove extra from polnames, bpolnames and orderedpols
    if select_stokes == 'yes':
        if not stokes:
            print ' No stokes specified, processing all'
        else:
            for pol in polnames.keys():
                if pol not in stokes:
                    # print pol
                    # print 'no'
                    del polnames[pol]
                    del orderedpols[pol]
            for key in list(bpolnames.keys()):
                if bpolnames[key] not in stokes:
                    del bpolnames[key]

    print " Flagging pols: %s" % ', '.join(str(x) for x in polnames.keys())


    ## Figure out number of IFs/SPWs
    nif = metadata.nspw()
    if spwlist == 'all':
        descids = list(metadata.datadescids())
    else:
        descids = []
        for spw in spwlist:
            niflist = metadata.datadescids(spw=spw)
            # print niflist, 'niflist[i]'
            for polset in niflist:
                descids.append(polset) 

    chanlist=[]
    for i in xrange(nif):
        chanlist.append(metadata.nchan(i))
    # print chanlist
    print " Flagging spws: %s" % ', '.join(str(x) for x in descids)
    print " Number of spws with channels: %i" % nif, '--', ', '.join(str(x) for x in chanlist)

    return metadata,source_lookup,source_list,telescope,nvis,frequency,polnames,bpolnames,orderedpols,descids,chanlist







'''
#print sys.argv
if len(sys.argv) > 3:
    if sys.argv[3] == '--v' or sys.argv[3] == '--version':
        print 'SERPent4casa version is %s: %s dated %s' % (version_name, version_number, version_date)
        sys.exit(0)
    else:
        print 'ERROR: unrecognised option'
        sys.exit(0)
print '\n Started running SERPent4casa version %s: %s' % (version_name, version_number), 'on %s' % strftime("%d-%b-%y"), 'at:', strftime("%H:%M:%S", localtime()),'\n'
'''



## Execute the serpent4casa_input.py file with all the observation information 
## and flagging parameters...
try:
    execfile("SERPent4casa_input.py")
    
except:
    print "\n Could not find SERPent4casa_input.py!"
    print " Make sure input file is in the same folder as this script (SERPent.py)"
    print " Aborting!"
    sys.exit(0)
## Test to see whether all variables have been set:
try:
    Name
    path2data
    NCPU
    path2folder
    spwlist
    path2folder = os.path.join(path2folder, '')
    oldflags_dir = path2folder
    if os.path.exists(path2folder) == False:
        print " Folder for outputs does not exist! Please check inputs and try again."
        print " Aborting SERPent!\n"
        sys.exit(0)
    do_Lovell_scan
    phasecal
    if do_Lovell_scan == 'no':
        phasecal = []
    do_lovell_cross
    zero_level
    which_baselines
    flagging_options
    flag_sources
    if flag_sources == 'choose':
        flag_list
    do_sumthreshold
    if flagging_options == 'choose' or flagging_options == 'source':
        aggressiveness_first_run
        max_subset_first_run
        aggressiveness_second_run
        max_subset_second_run
        rho
        kickout_sigma_level
    if which_baselines == 'choose':
        baselines
    dobline_specific
    dosource_specific
    select_stokes
    if select_stokes == 'yes':
        flag_all_stokes 
        stokes
    coadd_polarization_flags
    if coadd_polarization_flags == 'no':
        coadd_zero_flags
        coadd_lovell_flags
    flag_coinc_chans
    flag_coinc_times
    zero_flag_allif
    # keep_oldflags
except NameError:
    print " Please check you\'ve set all the variables in the input file."
    print " ABORTING SERPent!\n"
    sys.exit(0)






name=Name
msname=path2data+Name
metadata,source_lookup,source_list,telescope,nvis,frequency,polnames,bplonames,orderedpols,descids,chanlist = get_metadata(msname)

print '\nBacking up old flag state before doing any flagging'
ctim = time.localtime()
flagfilename = 'pre_SERPent_'+str(ctim.tm_year)+'-'+str(ctim.tm_mon)+'-'+str(ctim.tm_mday)+'-'+str(ctim.tm_hour)+'.'+str(ctim.tm_min)+'.'+str(ctim.tm_sec)+'.flag'
print '\nSaving flags with flagmanager as '+ flagfilename
flagmanager(vis=msname,mode='save',versionname=flagfilename)

if dobline_specific == 'no' and dosource_specific == 'no' and which_baselines == 'all':
    
    print "\n ALL baselines have been selected for flagging..." 
    ant_names = metadata.antennanames()
    ant_ids = metadata.antennaids()
    sbline = [[] for i in range(len(source_list))]
    sblinenamedict = {}
    sblinedict = {}
    for srce in source_list:
        ms.selectinit()
        ms.select({'field_id':[srce]})
        blinelist = ms.getdata(['axis_info'],ifraxis=True)['axis_info']['ifr_axis']['ifr_name']
        sblinenamedict[srce] = blinelist
    for srce in source_list:
        sdi = source_lookup.index(source_list[srce])
        blinenum = []
        for bline in sblinenamedict[srce]:
            ants = bline.split('-')
            antnum1 = ant_ids[ant_names.index(ants[0])]
            antnum2 = ant_ids[ant_names.index(ants[1])]    
            antnumstr = str(antnum1)+'-'+str(antnum2)
            blinenum.append(antnumstr)
        sblinedict[srce] = blinenum
        sbline[sdi] = blinenum





def read_msdata(msfile,baseline_list,source_list, source_index_list):
    srce_arr_posn = [[] for i in range(len(source_list))]
    for srce in source_list:
        sdi = source_lookup.index(source_list[srce])
        for did in descids:
            ms.selectinit(datadescid=did)
            for bline in sblinedict[srce]:
                ant1 = int(bline.split('-')[0])
                ant2 = int(bline.split('-')[1])
                ms.select({'field_id':[srce],'antenna1':[ant1], 'antenna2':[ant2]})
                data = ms.getdata('amplitude')['amplitude']
                old_flags = ms.getdata('flag')['flag']
                times_array = ms.getdata('time')['time']
    return data, old_flags, times_array


def read_data2file(msfile,srce,bline,did,oldflags_dir):
    ms.open(msfile)
    ant1 = int(bline.split('-')[0])
    ant2 = int(bline.split('-')[1])
    ms.selectinit(datadescid=did)
    ms.select({'field_id':[srce],'antenna1':[ant1], 'antenna2':[ant2]})
    data = ms.getdata('amplitude')['amplitude']
    old_flags = ms.getdata('flag')['flag']
    times_array = ms.getdata('time')['time']
    visoutfile = open(path2folder + "data__"+ str(srce) + '__ID' + str(did) + '__' + str(bline)+'.npy',"wb")
    np.save(visoutfile,np.absolute(data))
    visoutfile.close()
    flagoutfile = open(oldflags_dir + "oldflags__"+ str(srce) + '__ID' + str(did) + '__' + str(bline)+'.npy',"wb")
    np.save(flagoutfile,old_flags)
    flagoutfile.close()
    timesoutfile = open(path2folder + "times__"+ str(srce) + '__ID' + str(did) + '__' + str(bline)+'.npy',"wb")
    np.save(timesoutfile,times_array)
    timesoutfile.close()
    print 'Finished reading '
    ms.close()

def read_data(send_q, rec_q, cpu):
    
    for value in iter(send_q.get, 'STOP'):
        msfile,srce,bline,did,oldflags_dir = value[:]
        #ms.open(msfile)
        read_data2file(msfile,srce,bline,did,oldflags_dir)
        #ms.close()

        JOBS = 'JOB: '
        finish_str = "\n"+JOBS+" Not running SumThreshold flagger on :" + str(srce) + ", SPW:" +str(did)+", Baseline:"+bline
        print finish_str
        rec_q.put(finish_str)



### Test parallel locking in casa


jobcount = 1
joblist = []

for srce in source_list:
    sdi = source_lookup.index(source_list[srce])
    for bline in sblinedict[srce]:
        for j in xrange(len(descids)):
            joblist.append([msname,srce,bline,descids[j],oldflags_dir])
            jobcount +=1


print '\n Beginning flagging processes...\n'
send_q = multip.Queue()
rec_q = multip.Queue()
ncpus = multip.cpu_count()
ncpus=1
for i in xrange(len(joblist)):
    print 'Sending to queue job', i+1, 'of', len(joblist)
    # print "CPU", c, "will flag baselines and IFs: \n"
    send_q.put(joblist[i])
for i in xrange(ncpus):
    proc = multip.Process(target=read_data, args=(send_q,rec_q,i))
    proc.start()
    print 'Starting process on CPU:', i


results = []
for i in xrange(len(joblist)):
    results.append(rec_q.get())


for i in xrange(ncpus):
    send_q.put('STOP')

