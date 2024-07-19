import h5py
import numpy as np


def _get_vertices(h5f):
  verts_ds=h5f['tstt']['nodes']['coordinates']
  return verts_ds

def _modify_vertices(v,tol=1e-6):
  for i in range(len(v)):
    print(f'{i} of {len(v)}')
    for j in range(i+1,len(v)):
      delta=np.linalg.norm(v[i]-v[j])
      if (delta<tol and delta>0):
        print(f'close but no cigar {i}:{v[i]} {j}:{v[j]} {delta}')
  return v

def heal_h5m(filename:str='dagmc.h5m'):
  with h5py.File(filename,'r+') as h5f:
    verts=_get_vertices(h5f)
    healed=_modify_vertices(verts,tol=1e-6)

if __name__=='__main__':
  heal_h5m() 
