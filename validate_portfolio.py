"""Independent QC of the rerun notebook; pass the extracted project directory."""
from pathlib import Path
import sys, json
import pandas as pd
p = Path(sys.argv[1])
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
assert checks['duplicate_complete_storm_ids']==0
assert checks['damage_input_rows']==len(audit)
assert checks['damage_exports_match'] and checks['duration_matches_dates']
assert len(c)==checks['damage_link_status'].get('matched',0)
assert checks['notebook_execution']['status']=='passed'
print(json.dumps(checks,indent=2))
