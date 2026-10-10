"""Plot a saved six-state model run without recomputing its trajectory."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    data=np.genfromtxt(args.csv,delimiter=',',names=True)
    fig,axes=plt.subplots(1,3,figsize=(12,3.7))
    for dose in np.unique(data['ligand_normalized']):
        row=data[data['ligand_normalized']==dose]
        early=row['time_s']<=900
        axes[0].plot(row['time_s'][early]/60,row['MAPK_fraction'][early],label=f'L = {dose:g}')
        axes[1].plot(row['time_s']/3600,row['MAPK_fraction'])
        axes[2].plot(row['time_s']/3600,row['color_au'])
    for ax in axes:
        ax.grid(alpha=.2)
        ax.set_ylim(bottom=0)
    axes[0].set(xlabel='Time (min)',ylabel='Active Fus3 / total',title='Early core response')
    axes[1].set(xlabel='Time (h)',ylabel='Active Fus3 / total',title='Sustained-input scenario')
    axes[2].set(xlabel='Time (h)',ylabel='Color (arbitrary units)',title='Effective color output')
    axes[0].legend(fontsize=8)
    fig.suptitle('Six-state ODE prototype | normalized ligand | uncalibrated endpoints',fontsize=11)
    fig.tight_layout()
    out=args.output or args.csv.with_suffix('.png')
    fig.savefig(out,dpi=180)
    plt.close(fig)
    print(out)


if __name__=='__main__':
    main()
