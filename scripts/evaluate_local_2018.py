"""Historical extension from authorized local 2018 data; never redistributes inputs."""
import os,json,hashlib,subprocess
from pathlib import Path
import pandas as pd,numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error,mean_absolute_error,r2_score

root=Path(__file__).resolve().parents[1]
data=Path(os.environ['BDB_DATA_DIR']);out=Path(os.environ.get('RESEARCH_OUTPUT_DIR',root/'local_results'))
out.mkdir(exist_ok=True,parents=True)
source_names=['tracking2018.csv','plays.csv','games.csv']
sources=[]
for name in source_names:
    path=data/name;h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
    sources.append({'file':name,'bytes':path.stat().st_size,'sha256':h.hexdigest()})
plays=pd.read_csv(data/'plays.csv',dtype={'returnerId':str})
plays=plays[(plays.specialTeamsPlayType=='Kickoff')&(plays.specialTeamsResult=='Return')&
    plays.kickReturnYardage.notna()&plays.penaltyYards.isna()&plays.returnerId.str.fullmatch(r'\d+',na=False)]
games=pd.read_csv(data/'games.csv');games=games[games.season==2018]
plays=plays.merge(games[['gameId','week','gameDate']],on='gameId',validate='many_to_one')
keys=set(zip(plays.gameId,plays.playId));parts=[];scanned=0
cols=['gameId','playId','frameId','nflId','event','x','y','playDirection']
for chunk in pd.read_csv(data/'tracking2018.csv',usecols=cols,chunksize=250000):
    scanned+=len(chunk);g=chunk[chunk.event.eq('kick_received')&chunk.nflId.notna()]
    g=g[[k in keys for k in zip(g.gameId,g.playId)]]
    if len(g):parts.append(g)
tracking=pd.concat(parts,ignore_index=True)
tracking.to_csv(out/'reception_rows.csv',index=False);plays.to_csv(out/'eligible_plays.csv',index=False)
r_code='''args<-commandArgs(TRUE);source(file.path(args[1],"R/snapshot_features.R"));
t<-read.csv(args[2]);p<-read.csv(args[3]);f<-snapshot_features(t,p);write.csv(f,args[4],row.names=FALSE)'''
subprocess.run(['Rscript','--vanilla','-e',r_code,str(root),str(out/'reception_rows.csv'),str(out/'eligible_plays.csv'),str(out/'features.csv')],check=True)
features=pd.read_csv(out/'features.csv').merge(plays[['gameId','playId','week','gameDate']],on=['gameId','playId'],validate='one_to_one')
missing_reception=len(plays)-len(features)
train=features[features.week<=12];test=features[features.week>=13]
assert len(train)>50 and len(test)>20 and set(train.gameId).isdisjoint(test.gameId)
assert max(train.gameDate)<min(test.gameDate)
predictors=['returner_x','returner_y','nearest_player','mean_player_distance']
models={'linear':LinearRegression(),'random_forest_fixed':RandomForestRegressor(n_estimators=300,min_samples_leaf=10,random_state=89,n_jobs=2)}
metrics={};scored=test[['gameId','playId','week','kickReturnYardage']].copy()
def score(pred):
    return {'rmse':float(np.sqrt(mean_squared_error(test.kickReturnYardage,pred))),
        'mae':float(mean_absolute_error(test.kickReturnYardage,pred)),
        'heldout_r_squared':float(r2_score(test.kickReturnYardage,pred))}
baseline=np.repeat(train.kickReturnYardage.mean(),len(test));metrics['training_mean']=score(baseline)
for name,m in models.items():
    m.fit(train[predictors],train.kickReturnYardage);pred=m.predict(test[predictors]);metrics[name]=score(pred);scored[name]=pred
scored['baseline']=baseline
scored['y_sum']=scored.kickReturnYardage
scored['y_sq']=scored.kickReturnYardage**2
scored['sse_rf']=(scored.kickReturnYardage-scored.random_forest_fixed)**2
scored['sse_baseline']=(scored.kickReturnYardage-scored.baseline)**2
g=scored.groupby('gameId').agg(n=('playId','size'),y_sum=('y_sum','sum'),y_sq=('y_sq','sum'),sse_rf=('sse_rf','sum'),sse_baseline=('sse_baseline','sum'))
idx=np.random.default_rng(89).integers(0,len(g),(2000,len(g)))
sums={c:g[c].to_numpy()[idx].sum(axis=1) for c in g}
sst=sums['y_sq']-sums['y_sum']**2/sums['n']
uncertainty={'random_forest_r_squared_interval':np.quantile(1-sums['sse_rf']/sst,[.025,.975]).tolist(),
    'random_forest_minus_baseline_rmse_interval':np.quantile(np.sqrt(sums['sse_rf']/sums['n'])-np.sqrt(sums['sse_baseline']/sums['n']),[.025,.975]).tolist(),
    'method':'2000 complete-game percentile bootstrap draws; fixed model and predictions; seed 89'}
result={'status':'EXECUTED_HISTORICAL_EXTENSION','scope':'2018 returned kickoffs without recorded penalties and with a single identified returner',
    'tracking_rows_scanned':scanned,'eligible_plays':len(plays),'feature_plays':len(features),'missing_reception_plays':missing_reception,
    'train_weeks':'1–12','test_weeks':'13–17','train_plays':len(train),'test_plays':len(test),
    'train_games':train.gameId.nunique(),'test_games':test.gameId.nunique(),'metrics':metrics,'uncertainty':uncertainty,'sources':sources,
    'limitations':['2018 rule regime; not a current kickoff model.','No tuned model selection or causal conclusions.',
        'All-player proximity lacks coverage/blocker role assignments.','One-season temporal test is not cross-season validation.',
        'This does not reproduce archived KR_X Rsquared=0.5290068.','Source dataset redistribution rights remain separate; outputs retained privately.']}
(out/'results.json').write_text(json.dumps(result,indent=2,default=int));scored.to_csv(out/'heldout_predictions.csv',index=False)
print(json.dumps(result,indent=2,default=int))
