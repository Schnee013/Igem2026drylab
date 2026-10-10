"""Render the six-arm mechanism delivery from measured tables and coordinates."""
from pathlib import Path
import json
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch

ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
cfg=json.loads(Path(a.config).read_text());out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
font=FontProperties(fname='/usr/share/fonts/google-droid-sans-fonts/DroidSansFallbackFull.ttf')
plt.rcParams.update({'font.family':['DejaVu Sans',font.get_name()],'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'path','axes.unicode_minus':False})
colors={'wt':'#607080','n84v':'#137e78','v368r':'#ab5d2a'}
cases=cfg['cases'];labels={c['id']:c['genotype'].upper().replace('WT','WT')+'–'+c['ligand'] for c in cases}
data={c['id']:pd.read_csv(Path(c['output'])/'frame_metrics.csv') for c in cases}
def case(g,l):return next(c for c in cases if c['genotype']==g and c['ligand']==l)
def smooth(y):return pd.Series(y).rolling(11,center=True,min_periods=1).mean()
def save(fig,name):
    fig.savefig(out/(name+'.png'),dpi=180,bbox_inches='tight');fig.savefig(out/(name+'.pdf'),bbox_inches='tight');fig.savefig(out/(name+'.svg'),bbox_inches='tight');plt.close(fig)

# Three fits are displayed together, rather than hiding the global fit.
fig,axes=plt.subplots(2,3,figsize=(15,8),sharex=True,sharey=True)
for ax,c in zip(axes.flat,cases):
    d=data[c['id']]
    for k,col,label in [('global','#94a1b2','全受体拟合'),('core','#137e78','膜内核心拟合'),('pocket','#a55791','口袋骨架拟合')]:
        ax.plot(d.time_ns,smooth(d[f'ligand_rmsd_{k}_A']),color=col,label=label,lw=1.6)
    ax.axvspan(50,100,color='#eef3f5',zorder=-5);ax.set_title(labels[c['id']]);ax.set_xlabel('时间 / ns');ax.set_ylabel('配体 RMSD / Å');ax.set_ylim(0,12)
axes[0,0].legend(fontsize=9);fig.suptitle('局部拟合后仍有哪些配体移动？',fontsize=18)
fig.text(.5,.005,'曲线为 100 ps 采样后 1 ns 居中移动平均；每组单条轨迹，相对各自起点。阴影：50–100 ns。',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.03,1,.95));save(fig,'alignment_sensitivity')

# No temporal order across separate trajectories is treated as causation.
fig,axes=plt.subplots(2,2,figsize=(14,8),sharex=True)
for j,lig in enumerate(['ascr18','ascr3']):
    c=case('n84v',lig);p=Path(c['output']);d=data[c['id']];pair=pd.read_csv(p/'pair_details/receptor_pair_atoms.csv')
    q=pair[(pair.site==84)&(pair.neighbor==171)]
    axes[0,j].plot(q.time_ns,smooth(q.distance_A),label='Val84侧链—Gly171',color='#8054a1')
    for n,col in [(186,'#ca8050'),(189,'#137e78')]:axes[0,j].plot(d.time_ns,smooth(d[f'res{n}_ligand_distance_A']),label=f'{n}位—配体',color=col)
    axes[0,j].set_title('N84V–'+lig);axes[0,j].set_ylim(0,16)
    c=case('v368r',lig);p=Path(c['output']);d=data[c['id']];q=pd.read_csv(p/'pair_details/Arg368_Asp70_geometry.csv')
    axes[1,j].plot(q.time_ns,smooth(q.guanidinium_Asp70_distance_A),label='Arg368胍基—Asp70羧酸端',color='#8054a1')
    axes[1,j].plot(d.time_ns,smooth(d.res345_ligand_distance_A),label='Arg345—配体',color='#137e78')
    q=pd.read_csv(p/'pair_details/receptor_pair_atoms.csv');q=q[(q.site==368)&(q.neighbor==364)]
    axes[1,j].plot(q.time_ns,smooth(q.distance_A),label='Arg368侧链—Lys364',color='#ca8050');axes[1,j].set_title('V368R–'+lig);axes[1,j].set_ylim(0,12)
for ax in axes.flat:
    ax.axhline(4,color='grey',ls=':',lw=.8);ax.axvspan(50,100,color='#eef3f5',zorder=-5);ax.set_xlabel('时间 / ns');ax.set_ylabel('最短距离 / Å');ax.legend(fontsize=8)
fig.suptitle('局部位点、口袋锚定与时间顺序',fontsize=18);fig.text(.5,.005,'虚线仅为 4 Å 接触口径；实线为 1 ns 移动平均。时间先后及共同变化均不等于因果。',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.03,1,.95));save(fig,'local_timeline')

fig,axes=plt.subplots(1,2,figsize=(13,5))
for c in cases:
    d=data[c['id']];style='-' if c['ligand']=='ascr18' else '--'
    axes[0].plot(d.time_ns,smooth(d.lid_rmsd_core_A),color=colors[c['genotype']],ls=style,label=labels[c['id']])
    axes[1].plot(d.time_ns,smooth(d.lid_pocket_centroid_distance_A),color=colors[c['genotype']],ls=style,label=labels[c['id']])
axes[0].set_title('lid 相对膜内核心的变化');axes[0].set_ylabel('lid 主链 RMSD / Å')
axes[1].set_title('lid 至口袋骨架的位置');axes[1].set_ylabel('几何质心距离 / Å')
for ax in axes:ax.set_xlabel('时间 / ns');ax.axvspan(50,100,color='#eef3f5',zorder=-5)
axes[0].legend(fontsize=8,ncol=2);fig.text(.5,.005,'164–178 为共同 lid 编号；两条 ascr3 的 lid 经重构。该距离不是经过验证的孔径或功能开放态判据。',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.04,1,1));save(fig,'lid_geometry')

# A mechanism evidence diagram: a missing causal connection is visibly missing.
fig,ax=plt.subplots(figsize=(15,9));ax.set_xlim(0,15);ax.set_ylim(0,9);ax.axis('off')
ax.text(.25,8.6,'机制线索与尚未接上的环节',fontsize=22,weight='bold')
ax.text(.25,8.12,'六组 rep1 × 100 ns ｜ 本图汇总结构观察，不宣称选择性已增强',fontsize=12,color='#536477')
def box(x,y,w,h,title,body,color='#137e78',dashed=False):
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.16',fc='#f6f8fa',ec=color,lw=1.7,ls='--' if dashed else '-');ax.add_patch(p)
    ax.text(x+.12,y+h-.35,title,fontsize=13,weight='bold',color=color,va='top');ax.text(x+.12,y+h-.86,body,fontsize=11,va='top',linespacing=1.7)
ax.text(.25,7.52,'N84V：观察到 ascr18 锚定和较小移动，位点到锚定的联系未建立',fontsize=14,color='#137e78')
box(.4,4.75,4.25,2.4,'84 位附近的局部堆积','N84V–ascr18：84—Gly171 约4.33 Å\nWT–ascr18：约9.26 Å\n两组在起点已存在距离差异')
box(5.2,4.75,4.25,2.4,'尚缺的联系','84 位如何影响 Phe186 / Arg189？\n未发现符合本次定义的两步近接路径\n未检验更长或水介导路径','#b07130',True)
box(10,4.75,4.25,2.4,'已观察到的配体锚定','Arg189—羧酸端：100%近接\n任一几何氢键：93.6%\n锚定在 t=0 已存在；核心拟合 RMSD 1.70 Å')
ax.plot([4.83,5.02],[5.9,5.9],ls='--',color='#b07130');ax.plot([9.63,9.82],[5.9,5.9],ls='--',color='#b07130')
ax.text(.25,4.13,'V368R：局部重排可见；不能据此认定 ascr3 选择性增强',fontsize=14,color='#ab5d2a')
box(.4,1.25,4.25,2.4,'Arg368—Asp70 发生分化','ascr18：带电端距离约2.74 Å\n             几何氢键占有率92.6%\nascr3：带电端距离约6.49 Å，氢键0%',color='#ab5d2a')
box(5.2,1.25,4.25,2.4,'空间联系与时间顺序','368—Lys364—Arg345—配体\nascr3 联合近接60.5%；WT为44.3%\n带电端分离约8.0 ns；锚定约8.6 ns',color='#ab5d2a')
box(10,1.25,4.25,2.4,'尚未获得的结论','WT同样具有Arg345锚定\n缺少“突变→选择性增强”的归因证据\n不能将近接图解释为因果传递通路',color='#b07130',dashed=True)
ax.plot([4.83,5.02],[2.4,2.4],color='#ab5d2a');ax.plot([9.63,9.82],[2.4,2.4],ls='--',color='#b07130')
ax.text(.25,.45,'数值为50–100 ns描述；接触≤4 Å，两步蛋白近接边≤4.5 Å。不同母体/lid/pose，单条轨迹；线段不表示因果。',fontsize=10,color='#536477')
save(fig,'mechanism_evidence_map')

# Molecular panels use actual representative coordinates, not invented cartoons.
def fit(x,ref,ids):
    a=x[ids].mean(0);b=ref[ids].mean(0);U,_,V=np.linalg.svd((x[ids]-a).T@(ref[ids]-b));D=np.diag([1,1,np.linalg.det(U@V)]);return (x-a)@U@D@V+b
refcase=case('wt','ascr18');refz=np.load(Path(refcase['output'])/'representative_coordinates.npz');reference=refz['coordinates_A'][0].astype(float)
fig=plt.figure(figsize=(15,10));cmap={84:'#8054a1',368:'#c05621',70:'#e4aa3a',171:'#778b9f',186:'#cb5eaa',189:'#147db3',345:'#1b9c85'}
for j,lig in enumerate(['ascr18','ascr3']):
 for k,g in enumerate(['wt','n84v','v368r']):
    c=case(g,lig);z=np.load(Path(c['output'])/'representative_coordinates.npz');ids=z['core_fit_indices'];refids=refz['core_fit_indices']
    x=z['coordinates_A'][4].astype(float);a0=x[ids].mean(0);b0=reference[refids].mean(0);U,_,V=np.linalg.svd((x[ids]-a0).T@(reference[refids]-b0));D=np.diag([1,1,np.linalg.det(U@V)]);x=(x-a0)@U@D@V+b0
    ax=fig.add_subplot(2,3,j*3+k+1,projection='3d');ca=z['ca_indices'];rs=z['resids'];ns=z['names'];lr=z['ligand_indices']
    ax.plot(*x[ca].T,color='#c1c9d1',lw=.65,alpha=.7)
    for n,color in cmap.items():
        use=np.flatnonzero((rs==n)&np.array([not str(s).startswith('H') for s in ns]));center=x[use].mean(0)
        ax.scatter(*x[use].T,color=color,s=9,alpha=.95);ax.text(*center,str(n),fontsize=9,color=color)
    ax.scatter(*x[lr].T,color='#b89a1e',s=14)
    mapping=pd.read_csv(Path(c['output'])/'ligand_atom_mapping.csv');lookup={str(n):int(i) for n,i in zip(ns[lr],lr)}
    for r in mapping.itertuples():
        if r.atom not in lookup:continue
        for other in r.bonded_atoms.split():
            if other in lookup and lookup[r.atom]<lookup[other]:ax.plot(*x[[lookup[r.atom],lookup[other]]].T,color='#b89a1e',lw=1.5)
    center=reference[refz['ligand_indices']].mean(0);ax.set_xlim(center[0]-20,center[0]+20);ax.set_ylim(center[1]-20,center[1]+20);ax.set_zlim(center[2]-20,center[2]+20)
    ax.view_init(elev=22,azim=-50);ax.set_title(labels[c['id']],fontsize=13);ax.set_axis_off();ax.set_box_aspect([1,1,1])
fig.suptitle('实际75 ns代表构象：突变位点与口袋节点',fontsize=19)
fig.text(.5,.025,'六组统一拟合至 WT–ascr18 起始核心；金色为配体，灰色为受体CA轨迹。仅显示口袋附近视野；数字为残基编号。\n单帧用于定位，不代表占有率或机制证明。可编辑坐标见 structures。',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.07,1,.94));save(fig,'representative_structures_75ns')
print('FIGURES_COMPLETE',out)
