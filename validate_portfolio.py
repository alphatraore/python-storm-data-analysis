"""Independent QC of the rerun notebook; pass the extracted project directory."""
from pathlib import Path
import sys, json
import pandas as pd
p = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
s = pd.read_csv(p/'data/processed/storm_summary_clean.csv', keep_default_na=False)
d = pd.read_sas(p/'data/raw/storm_detail.sas7bdat', encoding='latin1')
w = pd.read_csv(p/'output/tables/wind_statistics_2016.csv', keep_default_na=False)
c = pd.read_csv(p/'output/tables/damage_detail.csv', keep_default_na=False)
r = d.loc[d.Season.eq(2016)].groupby(['Season','Basin','Name']).Wind.agg(AvgWind='mean', MinWind='min', MaxWind='max').round(0).reset_index()
keys=['Season','Basin','Name']
pd.testing.assert_frame_equal(w.sort_values(keys).reset_index(drop=True), r.sort_values(keys).reset_index(drop=True), check_dtype=False)
audit=pd.read_csv(p/'output/tables/damage_link_audit.csv',keep_default_na=False)
complete=s[['Season','Basin','Name']].ne('').all(axis=1)
checks = {
 'summary_rows':len(s),'detail_rows':len(d),'wind_summary_rows':len(w),'damage_rows':len(c),
 'wind_recomputed_matches':True,
 'duration_matches_dates':bool((pd.to_datetime(s.EndDate)-pd.to_datetime(s.StartDate)).dt.days.eq(pd.to_numeric(s.StormLength)).all()),
 'damage_exports_match':c.equals(pd.read_csv(p/'data/processed/damage_detail.csv',keep_default_na=False)),
 'damage_sorted_descending':bool(c.Cost.is_monotonic_decreasing),
 'duplicate_complete_storm_ids':int(s.loc[complete,'StormID'].duplicated().sum()),
 'incomplete_identities_quarantined':int((~complete).sum()),
 'ambiguous_season_name_candidates_quarantined':len(pd.read_csv(p/'output/tables/ambiguous_link_candidates.csv',keep_default_na=False)),
 'damage_input_rows':len(pd.read_excel(p/'data/raw/storm.xlsx',sheet_name='Storm_Damage')),
 'damage_link_status':audit.LinkStatus.value_counts().to_dict(),
 'missing_max_wind_retained':int(s.MaxWindMPH.eq('').sum()),
 'detail_2016_missing_group_identity':int(d.loc[d.Season.eq(2016),keys].isna().any(axis=1).sum()),
 'excel_sheets':pd.ExcelFile(p/'output/tables/storm_report_2016.xlsx').sheet_names,
 'notebook_execution':json.loads((p/'output/tables/notebook_execution.json').read_text())
}
def require(condition, message):
    if not condition:
        raise ValueError(message)

require(checks['duplicate_complete_storm_ids']==0, 'Duplicate complete StormIDs')
require(checks['damage_input_rows']==len(audit), 'Damage merge multiplied or lost rows')
require(checks['damage_exports_match'] and checks['duration_matches_dates'], 'Duration or duplicate-export mismatch')
require(len(c)==checks['damage_link_status'].get('matched',0), 'Damage output count differs from matched audit')
require(checks['notebook_execution']['status']=='passed', 'Notebook execution did not pass')
# Rebuild damage eligibility and values independently from original inputs.
raw = pd.concat([
    pd.read_sas(p/'data/raw/storm_summary.sas7bdat', encoding='latin1'),
    pd.read_sas(p/'data/raw/storm_2017.sas7bdat', encoding='latin1').rename(columns={'Year':'Season'}).drop(columns='Location',errors='ignore')
],ignore_index=True)
raw['Name'] = raw.Name.str.strip().str.upper()
raw['Basin'] = raw.Basin.str.upper()
raw['Season'] = raw.Season.astype('Int64')
valid = raw[['Season','Basin','Name']].notna().all(axis=1) & raw.Name.fillna('').ne('')
raw = raw.loc[valid].copy()
raw['key'] = raw.Season.astype('string') + raw.Name
raw = raw.loc[~raw.key.duplicated(keep=False)]
events = pd.read_excel(p/'data/raw/storm.xlsx',sheet_name='Storm_Damage')
events['Season'] = pd.to_datetime(events.Date).dt.year.astype('Int64')
events['Name'] = events.Event.str.split().str[-1].str.upper()
events['key'] = events.Season.astype('string') + events.Name
expected = events.merge(raw,on='key',how='inner',suffixes=('_damage','_storm'),validate='many_to_one')
expected['StormLength'] = (pd.to_datetime(expected.EndDate)-pd.to_datetime(expected.StartDate)).dt.days
expected['BasinName'] = expected.Basin.map({'NA':'North Atlantic','SA':'South Atlantic','WP':'West Pacific','EP':'East Pacific','SP':'South Pacific','NI':'North Indian','SI':'South Indian'})
expected = expected.rename(columns={'Name_damage':'Name','Season_damage':'Season'})[c.columns]
pd.testing.assert_frame_equal(c.sort_values(['Season','Name']).reset_index(drop=True), expected.sort_values(['Season','Name']).reset_index(drop=True),check_dtype=False)
checks['damage_recomputed_from_raw_matches'] = True
require(checks['wind_summary_rows']==90, 'Unexpected 2016 wind-summary count')
require(checks['notebook_execution']['executed_code_cells']==80, 'Incomplete notebook execution')
import hashlib
for filename, expected_hash in checks['notebook_execution']['input_sha256'].items():
    require(hashlib.sha256((p/'data/raw'/filename).read_bytes()).hexdigest()==expected_hash, 'Raw data changed after execution: '+filename)
checks['execution_input_hashes_match'] = True

print(json.dumps(checks,indent=2))
