# Changelog

All notable changes to this project will be documented in this file.

## [1.1.X] - 2024
- Rewrote python SDK

## [1.1.0] - [1.1.27] - 2024-5-20
- Incremental improvements

## [1.1.28] - 2024-5-23
- Improved reliability of geosteering interpretation retrieval
- Improved make_blocks_and_faults function in datamodels/geosteering/calcs.py
- Moved make_blocks_and_faults function to datamodels/geosteering/calcs.py
- Added fields to CurveDef data structure to improve clarity

## [1.1.29] - 2024-5-31
- Added CRS Descriptors to make defining coordinate systems easier

## [1.1.31] - 2024-5-31
- Support for retrieving depth curves for well log curves and curve groups.
- Search for wells by location

## [1.1.32] - 2024-5-31
- Add support for owner_company_name, visibility and editability on Interpretation and InterpretationEntry

## [1.1.33] - 2024-6-19
- Fix Survey.find_md so that it does not truncate at the tvd of the last station
- Fix Survey.find_md so that it can treat surveys with no stations or a single 0 station as an infinite vertical straight hole
- Implement WellService.add_tops
- Speed up CoordinatesService by caching projections and zones
- Make make_blocks_and_faults handle interpretations with missing target well tops

## [1.1.34] - 2024-6-25
- Fix Survey.find_tvd so that it can treat surveys with no stations or a single 0 station as an infinite vertical straight hole
- Move starred interpretion logic into a function on Wellbore
- Allow access to the strat column on shared wells via a new function on WellService
- Allow access to all the strat columns on shared wells via a new function on WellService

## [1.1.35] - 2024-6-27
- Fix some zone percent calculation problems
- Do percent in zone calculations for all interpretations on well
- Add get_curves to Wellbore
- Add get_tuples to Curve
