"""Private owner-review figures, from the executed local reconstruction only."""
import os,json
from pathlib import Path
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out=Path(os.environ.get('RESEARCH_OUTPUT_DIR','local_results'));r=json.loads((out/'results.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
names=['training_mean','linear','random_forest_fixed'];labels=['Training mean','Linear regression','Fixed random forest']
fig,ax=plt.subplots(figsize=(8,4.8));values=[r['metrics'][n]['rmse'] for n in names]
bars=ax.barh(labels,values,color=['#a8b4bc','#3d718c','#007ea8'])
for bar,value in zip(bars,values):ax.text(value+.12,bar.get_y()+bar.get_height()/2,f'{value:.2f}',va='center')
ax.set(xlim=(0,15),xlabel='Held-out RMSE (return yards; lower is better)',title='2018 kickoff returns · train Weeks 1–12, test Weeks 13–17')
fig.text(.1,.02,f"{r['test_plays']} held-out returns in {r['test_games']} games. Separate extension; not the archived 0.529 experiment.",fontsize=9,color='#526475')
fig.tight_layout(rect=[0,.07,1,1]);fig.savefig(out/'model_comparison.png',dpi=160);plt.close(fig)
t=pd.read_csv(out/'reception_rows.csv');p=pd.read_csv(out/'eligible_plays.csv');f=pd.read_csv(out/'features.csv')
example=f.merge(p[['gameId','playId','week']],on=['gameId','playId'],validate='one_to_one').query('week >= 13').sort_values(['gameId','playId']).iloc[0]
g=t[(t.gameId==example.gameId)&(t.playId==example.playId)].copy();pr=p[(p.gameId==example.gameId)&(p.playId==example.playId)].iloc[0]
kr=g.nflId.eq(float(pr.returnerId))
assert kr.sum()==1
if g.playDirection.iloc[0]=='left':g['x']=120-g.x;g['y']=160/3-g.y
fig,ax=plt.subplots(figsize=(12,6));ax.set_facecolor('#edf5ef')
for x in range(10,111,10):ax.axvline(x,color='#b4cbb9',lw=.8)
ax.axvspan(0,10,color='#d0e1d3');ax.axvspan(110,120,color='#d0e1d3')
ax.scatter(g.loc[~kr,'x'],g.loc[~kr,'y'],c='#007ea8',s=45,label='Other tracked players')
ax.scatter(g.loc[kr,'x'],g.loc[kr,'y'],c='#9b6b00',s=130,marker='*',label='Identified returner',zorder=3)
ax.set(xlim=(0,120),ylim=(0,160/3),xlabel='Normalized tracking x (yards)',ylabel='Tracking y (yards)',
    title=f"Actual reception snapshot · historical game {int(example.gameId)}, play {int(example.playId)}")
ax.set_aspect('equal');ax.legend(loc='upper left',frameon=False)
fig.text(.1,.02,'Reception event only. Other players are not assigned coverage/blocker roles; no tactical lane or causal benefit is inferred.',fontsize=10,color='#526475')
fig.tight_layout(rect=[0,.07,1,1]);fig.savefig(out/'reception_snapshot.png',dpi=160);plt.close(fig)
print('Private model-comparison and real reception-snapshot figures generated.')
