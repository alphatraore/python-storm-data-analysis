# Data notes and interpretation

## Provenance

The four raw files came from the user-supplied storm-analysis project. Their authoritative upstream source, dataset version, collection methods, and redistribution terms were not supplied. Input SHA-256 hashes identify the exact bytes used in the verified run; they do not establish upstream provenance.

## Sources

| File | Role |
|---|---|
| `storm_summary.sas7bdat` | Historical storm-level characteristics |
| `storm_2017.sas7bdat` | Additional 2017 summary records; `Year` becomes `Season` |
| `storm_detail.sas7bdat` | Timestamped storm observations |
| `storm.xlsx`, `Storm_Damage` sheet | Historical event dates, names, and reported costs |

## Fields and units

| Field | Interpretation |
|---|---|
| `Season` | Season/year used in grouping and linkage |
| `Name` | Normalized storm name; not unique across basins/seasons |
| `Basin` | Basin code; `NA` means North Atlantic, not a missing value |
| `StormID` | Derived season/basin/name identifier; only complete identities qualify for linkage |
| `StormLength` | End date minus start date in days; not an inclusive day count |
| `MaxWindMPH` | Summary maximum wind explicitly labeled mph |
| Detail `Wind` | Recorded detail wind; units unverified |
| `AvgWind`, `MinWind`, `MaxWind` | Statistics in the original detail Wind units; rounded to whole units |
| `Cost` | Supplied reported cost values; underlying currency basis/year requires upstream documentation |
| `Lat`, `Lon` | Supplied summary coordinates used in the scatter figure; not complete storm tracks |

When reading exported CSVs, use `keep_default_na=False` if preserving literal basin `NA`. Apply explicit missing-value handling afterward.

## Boundaries

Mean wind depends on observation frequency and is not exposure-weighted. Counts reflect these supplied records, not calibrated risk. No missing wind values are imputed. The geographic scatter figure is not a storm-track reconstruction. Basin-less damage records are matched only when season/name identifies exactly one eligible summary record.
