"""A fixed-parameter diagnostic of proxy-label predictability, not site profitability."""
from pathlib import Path
import sys, json, time, hashlib, platform
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'validation/signal_audit_deps'))
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from sklearn import __version__ as sklearn_version
from sklearn.base import clone
from sklearn.preprocessing import FunctionTransformer,StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier,HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import average_precision_score,roc_auc_score
from threadpoolctl import threadpool_limits

PATH=ROOT/'data/clean_v3/california_retail_clean_master_v3.parquet'
START_SHA=hashlib.sha256(PATH.read_bytes()).hexdigest()
SPEC=json.loads((ROOT/'data/clean_v3/model_feature_spec_v3.json').read_text())
FEATURES=SPEC['predictor_allowlist']
table=pq.read_table(PATH,columns=FEATURES+['id','is_mapped_specialist','county_geoid','tract_geoid','is_bay_area_9county'])
X=np.column_stack([table[x].to_numpy() for x in FEATURES]).astype(float)
y=table['is_mapped_specialist'].to_numpy().astype(int)
groups=table['county_geoid'].to_numpy()
bay=table['is_bay_area_9county'].to_numpy().astype(bool)
assert np.isfinite(X).all()
assert not set(table['tract_geoid'].to_numpy()[bay]) & set(table['tract_geoid'].to_numpy()[~bay])
skew=np.array([i for i,x in enumerate(FEATURES) if 'count_' in x or 'distance_' in x or 'density_' in x or 'income_2024' in x])

def transform(a):
    z=a.copy();z[:,skew]=np.log1p(z[:,skew]);return z

MODELS={
 'logistic_log1p':make_pipeline(FunctionTransformer(transform),StandardScaler(),LogisticRegression(C=1,class_weight='balanced',max_iter=1000,random_state=5450)),
 'random_forest':RandomForestClassifier(n_estimators=160,max_depth=10,min_samples_leaf=30,max_features=.8,class_weight='balanced_subsample',random_state=5450,n_jobs=4),
 'hist_gradient_boosting':HistGradientBoostingClassifier(max_iter=120,learning_rate=.05,max_leaf_nodes=7,max_depth=3,min_samples_leaf=50,l2_regularization=5,class_weight='balanced',early_stopping=False,random_state=5450),
}

def metrics(truth,score):
    p=float(truth.mean());ap=float(average_precision_score(truth,score))
    result={'rows':len(truth),'positives':int(truth.sum()),'constant_score_average_precision':p,'average_precision':ap,'average_precision_lift_over_prevalence':ap/p,'roc_auc':float(roc_auc_score(truth,score))}
    for frac in [.01,.05,.10]:
        k=int(np.ceil(len(truth)*frac));idx=np.argsort(-score,kind='stable')[:k];tp=int(truth[idx].sum())
        result[f'top_{int(frac*100)}pct']={'k':k,'positives':tp,'precision':tp/k,'recall':tp/int(truth.sum())}
    return result

train_idx=np.flatnonzero(~bay);test_idx=np.flatnonzero(bay)
report={'diagnostic_only':True,'date':'2026-10-26','input_sha256':START_SHA,'features':FEATURES,
 'target':'is_mapped_specialist','training_rows':len(train_idx),'training_positives':int(y[train_idx].sum()),
 'test_rows':len(test_idx),'test_positives':int(y[test_idx].sum()),
 'protocol':'Fixed parameters specified before fitting; five county-group folds on non-Bay counties; Bay9 diagnostic test. No category, name, coordinates, audit flags, or target-competition inputs. No feature selection or hyperparameter tuning against Bay results. Scores are uncalibrated; metrics assess mapped proxy labels, not real-world success or underserved demand.',
 'future_holdout_caution':'Bay9 outcomes are now inspected. Any future model or feature revision must disclose this diagnostic and use new prespecified geographic evaluation or nested CV; do not portray adaptive retesting as untouched external validation.',
 'versions':{'python':platform.python_version(),'sklearn':sklearn_version,'numpy':np.__version__},'models':{}}
oof={name:np.full(len(train_idx),np.nan)for name in MODELS}
start=time.monotonic()
splitter=GroupKFold(n_splits=5)
with threadpool_limits(limits=4):
 for fold,(itr,iva) in enumerate(splitter.split(X[train_idx],y[train_idx],groups[train_idx]),1):
    tr=train_idx[itr];va=train_idx[iva]
    assert not set(groups[tr])&set(groups[va])
    for name,prototype in MODELS.items():
        model=clone(prototype);model.fit(X[tr],y[tr]);score=model.predict_proba(X[va])[:,1]
        oof[name][iva]=score
        item=metrics(y[va],score);item.update(fold=fold,counties=sorted(set(groups[va])))
        report['models'].setdefault(name,{'county_cv':[]})['county_cv'].append(item)
        print(json.dumps({'phase':'county_cv','model':name,'fold':fold,'AP':round(item['average_precision'],6),'null_AP':round(item['constant_score_average_precision'],6),'lift':round(item['average_precision_lift_over_prevalence'],3)}),flush=True)
 for name in MODELS:
    assert np.isfinite(oof[name]).all()
    report['models'][name]['pooled_oof']=metrics(y[train_idx],oof[name])
 chosen=max(MODELS,key=lambda name:report['models'][name]['pooled_oof']['average_precision'])
 report['selected_by_nonbay_cv']=chosen
 predictions={}
 for name,prototype in MODELS.items():
    model=clone(prototype);model.fit(X[train_idx],y[train_idx]);score=model.predict_proba(X[test_idx])[:,1]
    predictions[name]=score;report['models'][name]['bay9']=metrics(y[test_idx],score)
    print(json.dumps({'phase':'bay9','model':name,**report['models'][name]['bay9']}),flush=True)

# Coarse county-cluster bootstrap: only nine clusters; descriptive uncertainty, not gold-label validation.
rng=np.random.default_rng(5450);test_counties=np.unique(groups[test_idx]);values=[]
county_codes=np.searchsorted(test_counties,groups[test_idx]);truth=y[test_idx]
for _ in range(1000):
    counts=np.bincount(rng.integers(0,len(test_counties),size=len(test_counties)),minlength=len(test_counties))
    weight=counts[county_codes]
    prev=float(np.average(truth,weights=weight));ap=float(average_precision_score(truth,predictions[chosen],sample_weight=weight))
    values.append([ap,prev,ap-prev,ap/prev])
v=np.array(values)
report['selected_model_bay_county_bootstrap']={'clusters':len(test_counties),'replicates':1000,'percentile_2_5_and_97_5':{name:np.quantile(v[:,i],[.025,.975]).tolist()for i,name in enumerate(['AP','prevalence','AP_minus_prevalence','AP_lift'])},'limitation':'Only nine county clusters; intervals conditional on the fitted model and mapped proxy labels, do not include label noise or model-selection uncertainty.'}
out=ROOT/'validation/predictive_signal_diagnostic_20261026.json'
report['elapsed_seconds']=round(time.monotonic()-start,2)
report['input_unchanged']=hashlib.sha256(PATH.read_bytes()).hexdigest()==START_SHA
assert report['input_unchanged']
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
pred={'id':table['id'].to_numpy()[test_idx],'is_mapped_specialist':truth,'county_geoid':groups[test_idx],**predictions}
pq.write_table(pa.Table.from_pydict(pred),ROOT/'validation/predictive_signal_bay_predictions_20261026.parquet')
print('FINISHED',out,'selected',chosen,'elapsed',report['elapsed_seconds'],flush=True)
