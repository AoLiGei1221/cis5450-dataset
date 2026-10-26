# Attribution and changes

© OpenStreetMap contributors, Overture Maps Foundation. OpenStreetMap extract distributed by Geofabrik.

U.S. Census Bureau: 2024 ACS five-year estimates (2020–2024) and 2024 TIGER/Line California census tracts.

Overture Maps Foundation, overturemaps.org, Places release 2026-10-21.0, accessed 2026-10-25. Provider attributions and license identifiers remain in the raw `sources` column and the clean table's separate provenance file. See https://docs.overturemaps.org/attribution/#places.

Changes made for this project: geographic bounding-box extraction with an approximately 2 km buffer; added audit columns; retailer scope filtering; entity resolution; target proxy labeling; spatial assignment to Census tracts; ACS joins; and derived demographic and spatial context features. Local Overture files are extracts, not the complete original global shards. `points.parquet` is a convenience projection, not the full source schema.

The published table has 58,513 mapped source-qualified retailer records. It is not a list of individually confirmed currently operating stores, and its labels do not indicate profitability or verified unmet demand.
