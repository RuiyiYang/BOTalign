


import numpy as np
from numpy.linalg import norm
from numpy.random import normal,uniform
import time
import matplotlib.pyplot as plt
import mrcfile
from scipy.ndimage import shift
from aspire.utils.rotation import Rotation
from aspire.volume import Volume




from utils_BO import get_angle, center, align_BO, q_to_rot





'''
Import code for EMalign
'''
from src.align_volumes_3d import align_volumes
from src.fastrotate3d import fastrotate3d 
from src.SymmetryGroups import genSymGroup



'''
Import code for alignOT
'''
from utils import sample, SGD





def generate_data_compare(data_name,order_shift,threshold,inv_SNR):
    with mrcfile.open('data/'+data_name) as mrc:
        template=mrc.data
    L=template.shape[1]; shape=(L,L,L); ns_std=np.sqrt(inv_SNR*norm(template)**2/L**3);      
       
    vol0=center(template,order_shift,threshold)+np.float32(normal(0,ns_std,shape)); 
    
    r=Rotation.generate_random_rotations(1); R_true=r._matrices[0];
    vol_rot=Volume(vol0).rotate(r)._data[0]; 
    s=uniform(-1,1,3)*int(L*0.1);  
    vol_given=np.float32(shift(vol_rot,s,order=order_shift,mode='constant'))+np.float32(normal(0,ns_std,shape));
    
    return vol0, vol_given, L, R_true 




'''
The following records the threshold used for computing the center of mass.
'''
Data_names=['emd_25892.mrc','emd_4547.mrc','emd_9515.mrc','EMD-1717.mrc',
            'emd-3683.mrc','emd_10180.mrc','EMD-3342.mrc','EMD-2660.mrc'];  
Threshold=[2.3, 0.0316, 0.0145, 22, 0.0258, 0.06, 0.015, 0.18]; 



'''
The two matrices below are used to convert rotations between the three
methods due to different conventions. 
'''
flipEM=np.array([[0,1,0],
                 [1,0,0],
                 [0,0,1]])
 
flipOT=np.array([[0,-1,0],
                 [-1,0,0],
                 [0,0,-1]])



'''
Below we use the test volume emd-3683.mrc.
Change ntrial to repeat the experiment. 
'''
for I in range(4,5):
    ntrial=1; 
    data_name=Data_names[I]; threshold=Threshold[I]; inv_SNR=0; order=0;

    
    angle_BO=np.zeros(ntrial); time_BO=np.zeros(ntrial);
    angle_EM=np.zeros(ntrial); time_EM=np.zeros(ntrial);
    angle_OT=np.zeros(ntrial); time_OT=np.zeros(ntrial);


             
    for trial in range(ntrial):
        
        [vol0,vol_given,L,R_true]=generate_data_compare(data_name,order,threshold,inv_SNR); 
       
        '''
        BOTalign
        '''                                      
        tic=time.perf_counter(); para1=['wemd',32,200,True];   
        vol_b=center(vol_given,order,threshold);
        [R_init_BO,R_rec_BO]=align_BO(Volume(vol0),Volume(vol_b),para1); 
        fastrotate3d(vol_given,R_rec_BO);
        toc=time.perf_counter(); 
        time_BO[trial]=toc-tic;
        angle_BO[trial]=get_angle(R_rec_BO,R_true.T); 
        
        
        
        '''
        EMalign
        '''
        G = genSymGroup('C1')
        class Struct:
            pass
                
        opt=Struct(); opt.sym='C1'; opt.Nprojs=30; opt.G=G;  
        opt.downsample=32; opt.trueR=R_true; opt.no_refine=False;
        tic=time.perf_counter();
        [bestR, bestdx, reflect, vol2aligned, bestcorr]=align_volumes(vol0,vol_given,0,opt)
        toc=time.perf_counter();
        
        angle_EM[trial]=get_angle(bestR,flipEM@R_true@flipEM); time_EM[trial]=toc-tic;
        
        
        '''
        AlignOT
        '''
        vol_b=center(vol_given,order,threshold); 
        with mrcfile.new('data/vol0.mrc',overwrite=True) as mrc:
            mrc.set_data(vol0);
        with mrcfile.new('data/vol_b.mrc',overwrite=True) as mrc:
            mrc.set_data(vol_b);
        tic=time.perf_counter();
        N=500; x,y,z=sample('data/vol0.mrc',threshold,N);
        xr,yr,zr=sample('data/vol_b.mrc',threshold,N); 
        q,costs=SGD(x,y,z,xr,yr,zr,lr=0.000005,max_iter=500,reg=30,num_samples=1,verbose=False);
        R_recOT=flipOT@q_to_rot(q[-1])@flipOT; 
        fastrotate3d(vol_given,R_recOT)
        toc=time.perf_counter(); 
        
        angle_OT[trial]=get_angle(R_recOT,flipEM@R_true.T@flipEM); time_OT[trial]=toc-tic;

    

    '''
    plot the results
    '''
    plt.figure(I);
    
    bp1=plt.boxplot(angle_BO,positions=[1],notch=True,patch_artist=True,boxprops=dict(facecolor="C1")); 
    bp2=plt.boxplot(angle_EM,positions=[2],notch=True,patch_artist=True,boxprops=dict(facecolor="C2")); 
    bp3=plt.boxplot(angle_OT,positions=[3],notch=True,patch_artist=True,boxprops=dict(facecolor="C3")); 
    plt.title('EMD-'+data_name[4:8]);      
    ax=plt.gca(); ax.set_xticklabels(['%1.1f'%np.mean(time_BO), 
                                      '%1.1f'%np.mean(time_EM),
                                      '%1.1f'%np.mean(time_OT)])
                                      
    ax.yaxis.grid(True,linestyle='-',which='major',color='lightgrey',alpha=0.5)
    ax.xaxis.grid(True,linestyle='-',which='major',color='lightgrey',alpha=0.5)

    
    
    
    
    

