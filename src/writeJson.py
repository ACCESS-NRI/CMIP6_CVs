#!/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
#import pdb
from CMIP6Lib import ascertainVersion, cleanString, dictDepth, entryCheck, \
    getFileHistory, versionHistoryUpdate
from durolib import readJsonCreateDict
import time
import sys
import subprocess
import shlex
import platform
import os
import json
import gc
import datetime
import calendar

# %% additional import statements
try:
    from urllib2 import urlopen  # py2
except ImportError:
    from urllib.request import urlopen  # py3

"""
Created on Mon Jul 11 14:12:21 2016

Paul J. Durack 11th July 2016

This script generates all controlled vocabulary (CV) json files residing this this subdirectory
"""
"""2016
PJD 11 Jul 2016    - Started
PJD 12 Jul 2016    - Read experiments from https://github.com/PCMDI/cmip6-cmor-tables/blob/CMIP6_CV/Tables/CMIP6_CV.json
PJD 12 Jul 2016    - Format tweaks and typo corrections
PJD 12 Jul 2016    - Added source_id ('GFDL-CM2-1': 'GFDL CM2.1' as example)
PJD 12 Jul 2016    - Corrected mip_era to be CMIP6-less
PJD 12 Jul 2016    - Indent/format cleanup
PJD 13 Jul 2016    - Further tweaks to cleanup experiment json
PJD 13 Jul 2016    - Added required_global_attributes (Denis Nadeau)
PJD 13 Jul 2016    - Further tweaks to resolve specifics https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1
PJD 13 Jul 2016    - Updating institution following https://github.com/WCRP-CMIP/CMIP6_CVs/issues/3
PJD 13 Jul 2016    - Further tweaks to institution
PJD 14 Jul 2016    - Updated source_id to include institution https://github.com/WCRP-CMIP/CMIP6_CVs/issues/8
PJD 14 Jul 2016    - Renamed experiment to experiment_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/10
PJD 14 Jul 2016    - Renamed institution to institution_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/12
PJD 14 Jul 2016    - Added coordinate https://github.com/WCRP-CMIP/CMIP6_CVs/issues/7
PJD 14 Jul 2016    - Added grid https://github.com/WCRP-CMIP/CMIP6_CVs/issues/6
PJD 14 Jul 2016    - Added formula_terms https://github.com/WCRP-CMIP/CMIP6_CVs/issues/5
PJD 15 Jul 2016    - Added further cleanup of imported dictionaries
PJD 20 Jul 2016    - Updated VolMIP experiment info https://github.com/WCRP-CMIP/CMIP6_CVs/issues/19
PJD 11 Aug 2016    - Added readJsonCreateDict function
PJD 11 Aug 2016    - Converted experiment_id source from github
PJD 11 Aug 2016    - Updated frequency to include 1hrClimMon https://github.com/WCRP-CMIP/CMIP6_CVs/issues/24
PJD 11 Aug 2016    - Updated LUMIP experiment names https://github.com/WCRP-CMIP/CMIP6_CVs/issues/27
PJD 15 Aug 2016    - Update experiment_id to be self-consistent (LUMIP renames complete)
PJD 15 Aug 2016    - Converted readJsonCreateDict to source from durolib
PJD 15 Aug 2016    - Further tweaks to LUMIP experiment_id @dlawrenncar https://github.com/WCRP-CMIP/CMIP6_CVs/issues/27
PJD 25 Aug 2016    - Added license https://github.com/WCRP-CMIP/CMIP6_CVs/issues/35
PJD 25 Aug 2016    - Updated source_id contents and format https://github.com/WCRP-CMIP/CMIP6_CVs/issues/34
PJD 25 Aug 2016    - Add CV name to json structure https://github.com/WCRP-CMIP/CMIP6_CVs/issues/36
PJD 26 Aug 2016    - Add repo version/metadata https://github.com/WCRP-CMIP/CMIP6_CVs/issues/28
PJD 31 Aug 2016    - Added mip_era to source_id
PJD 31 Aug 2016    - Correct repo user info
PJD 31 Aug 2016    - Remove CMIP6_variable.json from repo https://github.com/WCRP-CMIP/CMIP6_CVs/issues/45
PJD  1 Sep 2016    - Updated version info to per file (was repo) https://github.com/WCRP-CMIP/CMIP6_CVs/issues/28
PJD  1 Sep 2016    - Automated update of html
PJD 15 Sep 2016    - Further tweaks to version info https://github.com/WCRP-CMIP/CMIP6_CVs/issues/28
PJD 15 Sep 2016    - Updated source_id to maintain consistency with ES-DOCs https://github.com/WCRP-CMIP/CMIP6_CVs/issues/53
PJD 28 Sep 2016    - Correct activity_id to MIP -> CMIP typo https://github.com/WCRP-CMIP/CMIP6_CVs/issues/57
PJD 28 Sep 2016    - Add new grid_label entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/49
PJD  3 Oct 2016    - Added "cohort" to source_id ACCESS-1-0 example https://github.com/WCRP-CMIP/CMIP6_CVs/issues/64
PJD  3 Oct 2016    - Added institution_id NUIST https://github.com/WCRP-CMIP/CMIP6_CVs/issues/63
PJD  4 Oct 2016    - Added institution_id NIMS-KMA https://github.com/WCRP-CMIP/CMIP6_CVs/issues/67
PJD  4 Oct 2016    - Revised tiers for AerChemMIP experiments https://github.com/WCRP-CMIP/CMIP6_CVs/issues/69
PJD  4 Oct 2016    - Added AerChemMIP experiments piClim-SO2 piClim-OC piClim-NH3 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/68
PJD  1 Nov 2016    - Update to upstream sources; Convert to per-file commits
PJD  1 Nov 2016    - Add PCMDI-test-1-0 to source_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/102
PJD  2 Nov 2016    - Add CSIR to institution_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/100
PJD  2 Nov 2016    - Update BNU institution_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/98
PJD  2 Nov 2016    - Add EC-Earth-Consortium to institution_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/90
PJD  2 Nov 2016    - Update MIROC institution_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/89
PJD  2 Nov 2016    - Add CCCR-IITM to institution_id and IITM-ESM to source_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/96
PJD  2 Nov 2016    - Update deforest-globe experiment_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/97
PJD  2 Nov 2016    - Remove RFMIP experiment_ids piClim-aerO3x0p1 and piClim-aerO3x2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/79
PJD  2 Nov 2016    - Revise RFMIP experiment_ids hist-all-spAerO3 and hist-spAerO3 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/80
PJD  2 Nov 2016    - Revise RFMIP experiment_ids capitalization https://github.com/WCRP-CMIP/CMIP6_CVs/issues/81
PJD  2 Nov 2016    - Revise RFMIP experiment_ids spAerO3 -> spAer https://github.com/WCRP-CMIP/CMIP6_CVs/issues/82
PJD  2 Nov 2016    - Revise experiment_id ssp370 to include activity_id AerChemMIP https://github.com/WCRP-CMIP/CMIP6_CVs/issues/77
PJD  2 Nov 2016    - Revise experiment_id volc-cluster-mill https://github.com/WCRP-CMIP/CMIP6_CVs/issues/75
PJD  2 Nov 2016    - Revise experiment_id instances of LND -> LAND https://github.com/WCRP-CMIP/CMIP6_CVs/issues/74
PJD  2 Nov 2016    - Add experiment_id ism-ctrl-std https://github.com/WCRP-CMIP/CMIP6_CVs/issues/103
PJD  2 Nov 2016    - Add experiment_id ism-asmb-std https://github.com/WCRP-CMIP/CMIP6_CVs/issues/104
PJD  2 Nov 2016    - Add experiment_id ism-bsmb-std https://github.com/WCRP-CMIP/CMIP6_CVs/issues/105
PJD  3 Nov 2016    - Deal with invalid source_type syntax, rogue ","
PJD  8 Nov 2016    - Add CNRM to institution_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/129
PJD  8 Nov 2016    - Revise source_type https://github.com/WCRP-CMIP/CMIP6_CVs/issues/131
PJD 15 Nov 2016    - Remove coordinate, formula_terms and grids from repo https://github.com/WCRP-CMIP/CMIP6_CVs/issues/139
PJD 15 Nov 2016    - Rename grid_resolution to nominal_resolution and add new entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/141
PJD 15 Nov 2016    - Add MESSy-Consortium to institution_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/138
PJD 16 Nov 2016    - Revise AerChemMIP experiment model configurations https://github.com/WCRP-CMIP/CMIP6_CVs/issues/78
PJD 16 Nov 2016    - Add source_id VRESM-1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/101
PJD 17 Nov 2016    - Revise grid_label to include Antarctica and Greenland https://github.com/WCRP-CMIP/CMIP6_CVs/issues/130
PJD 21 Nov 2016    - Revise institution_id NCC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/83
PJD 21 Nov 2016    - Revise experiment_id 1pctCO2Ndep https://github.com/WCRP-CMIP/CMIP6_CVs/issues/73
PJD 21 Nov 2016    - Register source_id BNU-ESM-1-1 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/99
PJD 21 Nov 2016    - Register source_id EC-Earth-3 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/91
PJD 21 Nov 2016    - Register source_id EC-Earth-3-HR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/92
PJD 21 Nov 2016    - Register source_id EC-Earth-3-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/93
PJD 21 Nov 2016    - source_id cleanup, particularly for IITM-ESM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/96
PJD 21 Nov 2016    - Register institution_id CNRM-CERFACS https://github.com/WCRP-CMIP/CMIP6_CVs/issues/115
PJD 28 Nov 2016    - Register source_id NorESM2-LME https://github.com/WCRP-CMIP/CMIP6_CVs/issues/84
PJD 28 Nov 2016    - Register source_id NorESM2-MH https://github.com/WCRP-CMIP/CMIP6_CVs/issues/85
PJD 28 Nov 2016    - Register source_id NorESM2-LMEC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/86
PJD 28 Nov 2016    - Register source_id NorESM2-HH https://github.com/WCRP-CMIP/CMIP6_CVs/issues/87
PJD 28 Nov 2016    - Register source_id NorESM2-MM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/88
PJD 28 Nov 2016    - Register source_id NorESM2-LM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/156
PJD 28 Nov 2016    - Revise multiple source_id NorESM* https://github.com/WCRP-CMIP/CMIP6_CVs/issues/156
PJD  7 Dec 2016    - Update activity_id for experiment_id ssp370 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/169#issuecomment-264726036
PJD  7 Dec 2016    - Add experiment_id 1pctCO2-4xext https://github.com/WCRP-CMIP/CMIP6_CVs/issues/170
PJD  7 Dec 2016    - Add institution_id html https://github.com/WCRP-CMIP/CMIP6_CVs/issues/172
PJD 14 Dec 2016    - Add frequency_id 1hr https://github.com/WCRP-CMIP/CMIP6_CVs/issues/178
PJD 14 Dec 2016    - Add source_id GISS-E2-1 variants https://github.com/WCRP-CMIP/CMIP6_CVs/issues/177
"""
"""2017
PJD  3 Jan 2017    - Add institution_id NERC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/183
PJD  3 Jan 2017    - Update source_id EC-Earth-3-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/93
PJD  3 Jan 2017    - Register source_id EC-Earth-3-CC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/94
PJD  3 Jan 2017    - Register source_ids HadGEM3*4 and UKESM1*2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/184
PJD  3 Jan 2017    - Revise CMIP6 license text https://github.com/WCRP-CMIP/CMIP6_CVs/issues/133
PJD  3 Jan 2017    - Register source_ids CNRM-ESM2*2 and CNRM-CM6*2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/115
PJD  5 Jan 2017    - Revise multiple CNRM source_ids atmospheric chemistry entry https://github.com/WCRP-CMIP/CMIP6_CVs/issues/115
PJD  5 Jan 2017    - Register multiple EC-Earth3 source_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/191
PJD  5 Jan 2017    - Update DCPP experiment_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1#issuecomment-268357110
PJD 10 Jan 2017    - Register multiple EC-Earth3 source_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/195, 196, 197
PJD 13 Jan 2017    - Update table_id to reflect Data Request V1.0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/199
PJD 18 Jan 2017    - Update experiment_id highres-future start_year https://github.com/WCRP-CMIP/CMIP6_CVs/issues/201
PJD 18 Jan 2017    - Add experiment_id spinup-1950 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/202
PJD 19 Jan 2017    - Update institution_id FIO -> FIO-SOA https://github.com/WCRP-CMIP/CMIP6_CVs/issues/205
PJD 21 Jan 2017    - Register institution_id AWI https://github.com/WCRP-CMIP/CMIP6_CVs/issues/207
PJD 21 Jan 2017    - Register source_id AWI-CM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/210
PJD 23 Jan 2017    - Update institution_id FIO-SOA -> FIO-RONM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/209
PJD 23 Jan 2017    - Register source_id MRI-ESM2-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/208
PJD 23 Jan 2017    - Revise experiment_id values for ISMIP https://github.com/WCRP-CMIP/CMIP6_CVs/issues/168
PJD 23 Jan 2017    - Revise source_id MRI-ESM2-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/208
PJD 30 Jan 2017    - Register source_id EMAC-2-53-AerChem https://github.com/WCRP-CMIP/CMIP6_CVs/issues/217
PJD 31 Jan 2017    - Revise source_id EMAC-2-53-AerChem https://github.com/WCRP-CMIP/CMIP6_CVs/issues/217
PJD  6 Feb 2017    - Revise license details
PJD  6 Feb 2017    - Register source_id AWI-CM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/210
PJD  6 Feb 2017    - Revise multiple EC-Earth3 source_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/191
PJD 27 Feb 2017    - Update license info
PJD 27 Feb 2017    - Register institution_id THU https://github.com/WCRP-CMIP/CMIP6_CVs/issues/225
PJD 27 Feb 2017    - Register source_id CIESM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/226
PJD  3 Mar 2017    - Register source_id MRI-ESM2-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/234
PJD  3 Mar 2017    - Register source_id MIROC6 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/229
PJD  3 Mar 2017    - Update all source_id cohort entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/230
PJD  7 Mar 2017    - Register source_id EMAC-2-53-Vol https://github.com/WCRP-CMIP/CMIP6_CVs/issues/231
PJD  7 Mar 2017    - Register source_ids MIROC-ES and NICAM variants https://github.com/WCRP-CMIP/CMIP6_CVs/pull/238
PJD  7 Mar 2017    - Update experiment_id from external xlsx https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1, 61, 136, 137
PJD 14 Mar 2017    - Update source_id ACCESS-1-0 template
PJD 17 Mar 2017    - Cleanup required_global_attributes https://github.com/WCRP-CMIP/CMIP6_CVs/issues/250
PJD 17 Mar 2017    - Augment source_id info request https://github.com/WCRP-CMIP/CMIP6_CVs/issues/249
PJD 20 Mar 2017    - Register institution_id CAMS https://github.com/WCRP-CMIP/CMIP6_CVs/issues/245
PJD 22 Mar 2017    - Revise experiment_id names and details for 2 RFMIP experiments https://github.com/WCRP-CMIP/CMIP6_CVs/issues/258
PJD 29 Mar 2017    - Revise experiment_id piClim-aer https://github.com/WCRP-CMIP/CMIP6_CVs/issues/261
PJD  5 Apr 2017    - Remove deprecated table_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/266
PJD  5 Apr 2017    - Convert experiment_id parent* entries to list https://github.com/WCRP-CMIP/CMIP6_CVs/issues/267
PJD  7 Apr 2017    - Register GFDL source_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/244
PJD  7 Apr 2017    - Register source_id CAMS_CSM1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/246
PJD  8 Apr 2017    - Update multiple NorESM source_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/259
PJD  8 Apr 2017    - Update html markup https://github.com/WCRP-CMIP/CMIP6_CVs/issues/248
PJD 10 Apr 2017    - Revise source_id NorESM2-MH https://github.com/WCRP-CMIP/CMIP6_CVs/issues/259
PJD 12 Apr 2017    - Revise frequency to include yrClim https://github.com/WCRP-CMIP/CMIP6_CVs/issues/281
PJD 12 Apr 2017    - Add missing activity_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/276
PJD 17 Apr 2017    - Register institution_id INPE https://github.com/WCRP-CMIP/CMIP6_CVs/issues/286
PJD 17 Apr 2017    - Register institution_id CMCC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/284
PJD 17 Apr 2017    - Update realm format https://github.com/WCRP-CMIP/CMIP6_CVs/issues/285
PJD 18 Apr 2017    - Reconfigure source_id format to reflect all model components https://github.com/WCRP-CMIP/CMIP6_CVs/issues/264
PJD 18 Apr 2017    - Reconfigure json_to_html to deal with new source_id format
PJD 20 Apr 2017    - Revise AWI-CM source_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/210
PJD 21 Apr 2017    - Clean up None instances in source_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/301
PJD 21 Apr 2017    - Register source_id CMCC-CM2-SR5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/292
PJD 21 Apr 2017    - Register source_id CMCC-CM2-HR5 and correct ocean entry for CMCC-CM2-SR5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/293
PJD 21 Apr 2017    - Register source_id CMCC-CM2-HR4 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/294
PJD 21 Apr 2017    - Register source_id CMCC-CM2-VHR4 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/295
PJD 21 Apr 2017    - Register source_id CMCC-ESM2-SR5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/296
PJD 21 Apr 2017    - Register source_id CMCC-ESM2-HR5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/297
PJD 21 Apr 2017    - Revise CMCC source_id atmos entries (issues 292-294)
PJD 24 Apr 2017    - Revise source_id EMAC-2-53-AerChem https://github.com/WCRP-CMIP/CMIP6_CVs/issues/257
PJD 24 Apr 2017    - Revise source_id Revise source_id BNU-ESM-1-1 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/99
PJD 25 Apr 2017    - Register source_id BESM-2-7 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/287
PJD 26 Apr 2017    - Revise source_id CIESM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/226
PJD 26 Apr 2017    - Revise source_id BESM-2-7 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/287
PJD 11 May 2017    - Revise GFDL source_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/318
PJD 11 May 2017    - Revise source_id AWI-CM-1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/319
PJD 11 May 2017    - Register multiple AWI source_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/320-322
PJD 17 May 2017    - Revise source_id EMAC-2-53-Vol https://github.com/WCRP-CMIP/CMIP6_CVs/issues/231
PJD 27 May 2017    - Rename and revise sspxy to ssp119 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/329
PJD 27 May 2017    - Revise source_id CanESM5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/330
PJD 30 May 2017    - Revise institution_id NCAR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/335
PJD 30 May 2017    - Remove frequency 3hrClim https://github.com/WCRP-CMIP/CMIP6_CVs/issues/334
PJD  6 Jun 2017    - Revise multiple CNRM source_ids and CNRM-CERFACS institution_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/115
PJD 14 Jun 2017    - Revise multiple EC-EARTH3 source_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/191
PJD 14 Jun 2017    - Revise frequency decadal to dec https://github.com/WCRP-CMIP/CMIP6_CVs/issues/338
PJD 14 Jun 2017    - Rename experiment_id highresSST-4co2 -> highresSST-4xCO2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/341
PJD 14 Jun 2017    - Update frequency format with identifiers -> highresSST-4xCO2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/342
PJD 14 Jun 2017    - Rename experiment_id lfmip-pdL-princeton -> lfmip-pdLC-princeton https://github.com/WCRP-CMIP/CMIP6_CVs/issues/344
PJD 15 Jun 2017    - Correct experiment_id typo AeroChemMIP -> AerChemMIP in EC-Earth3-AerChem https://github.com/WCRP-CMIP/CMIP6_CVs/issues/352
PJD 15 Jun 2017    - Revise source_id MRI-ESM2-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/351
PJD 15 Jun 2017    - Revise multiple NASA-GISS source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/177
PJD 19 Jun 2017    - Revise INM institution_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/357
PJD 26 Jun 2017    - Register source_id INM-CM5-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/358
PJD 26 Jun 2017    - Register source_id INM-CM4-8 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/359
PJD 26 Jun 2017    - Register source_id INM-CM5-H https://github.com/WCRP-CMIP/CMIP6_CVs/issues/361
PJD 27 Jun 2017    - Revise multiple MOHC source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/184, 343
PJD 27 Jun 2017    - Fix INM source_id formatting https://github.com/WCRP-CMIP/CMIP6_CVs/issues/358, 359, 361
PJD 27 Jun 2017    - Correct source_type BGCM to BGC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/366
PJD 27 Jun 2017    - Remove unregistered institution_id entries (no source_id registrations) https://github.com/WCRP-CMIP/CMIP6_CVs/issues/362
PJD 29 Jun 2017    - Revise source_id IITM-ESM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/96
PJD 29 Jun 2017    - Revise multiple CNRM source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/115
PJD 29 Jun 2017    - Revise multiple MPI source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/197
PJD 29 Jun 2017    - Delete source_type ESM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/370
PJD 29 Jun 2017    - Correct source_id UKESM1-0-LL activity_participation error https://github.com/WCRP-CMIP/CMIP6_CVs/issues/371
PJD  5 Jul 2017    - Revise source_id CNRM-CM6-1 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/115
PJD 10 Jul 2017    - Revise multiple MPI source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/197
PJD 12 Jul 2017    - Revise multiple MOHC source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/184
PJD 17 Jul 2017    - Revise EC-EARTH3-HR source_id ocean description https://github.com/WCRP-CMIP/CMIP6_CVs/issues/191
PJD 26 Jul 2017    - Revise multiple MIROC source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/229
PJD 26 Jul 2017    - Register institution_id SNU https://github.com/WCRP-CMIP/CMIP6_CVs/issues/386
PJD 26 Jul 2017    - Register source_id SAM0-UNICON https://github.com/WCRP-CMIP/CMIP6_CVs/issues/387
PJD 27 Jul 2017    - Revise MIROC and SNU source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/pull/385#issuecomment-318256867,
                     https://github.com/WCRP-CMIP/CMIP6_CVs/issues/387#issuecomment-318308002
PJD  2 Aug 2017    - Start work on per file versioning
PJD 10 Aug 2017    - Register source_id IPSL-CM6A-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/392
PJD  7 Sep 2017    - Augment activity_id format with description https://github.com/WCRP-CMIP/CMIP6_CVs/issues/397
PJD  8 Sep 2017    - Augment source_type format with description https://github.com/WCRP-CMIP/CMIP6_CVs/issues/396
PJD  8 Sep 2017    - Augment grid_label format with description https://github.com/WCRP-CMIP/CMIP6_CVs/issues/395
PJD  8 Sep 2017    - Revise frequency entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/345
PJD 21 Sep 2017    - Register institution_id HAMMOZ-Consortium https://github.com/WCRP-CMIP/CMIP6_CVs/issues/402
PJD 21 Sep 2017    - Register institution_id BCC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/405
PJD 26 Sep 2017    - Register source_id MPIESM-1-2-HAM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/403
PJD 26 Sep 2017    - Register source_id MRI-AGCM3-2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/410
PJD  4 Oct 2017    - Add frequency monPt https://github.com/WCRP-CMIP/CMIP6_CVs/issues/413
PJD  8 Oct 2017    - Revise multiple GFDL source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/318
PJD 27 Oct 2017    - Further minor tweaks https://github.com/WCRP-CMIP/CMIP6_CVs/issues/318
PJD 27 Oct 2017    - Revise frequency 1hrCM definition https://github.com/WCRP-CMIP/CMIP6_CVs/issues/414#issuecomment-335032399
PJD 27 Oct 2017    - Revise MPI source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/195, 196, 197
PJD 27 Oct 2017    - Register multiple BCC source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/404, 406, 407
PJD 30 Oct 2017    - Register institution_id NIWA and add to UKESM1-0-LL https://github.com/WCRP-CMIP/CMIP6_CVs/issues/421
PJD  2 Nov 2017    - Register source_id HadGEM3-GC31-MH https://github.com/WCRP-CMIP/CMIP6_CVs/issues/424
PJD  6 Nov 2017    - Register institution_id CAS https://github.com/WCRP-CMIP/CMIP6_CVs/issues/426
PJD  7 Nov 2017    - Update missing nominal_resolution information for multiple source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/431
PJD  7 Nov 2017    - Further minor tweaks to GFDL-ESM2M https://github.com/WCRP-CMIP/CMIP6_CVs/issues/318
PJD  8 Nov 2017    - Correct model components for various LS3MIP/LUMIP experiments https://github.com/WCRP-CMIP/CMIP6_CVs/issues/423
PJD 15 Nov 2017    - Register multiple CAS source_id values FGOALS* https://github.com/WCRP-CMIP/CMIP6_CVs/issues/427, 428, 436
PJD  7 Dec 2017    - Revise THU source_id CIESM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/439
PJD 14 Dec 2017    - Update activity_participation for multiple MOHC source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/442
PJD 19 Dec 2017    - Update institution_id for HadGEM3-GC31-H* entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/441
PJD 19 Dec 2017    - Update experiment_id AerChemMIP and AMIP additional_allowed_model_components https://github.com/WCRP-CMIP/CMIP6_CVs/issues/438
"""
"""2018
PJD  8 Jan 2018    - Register institution_id DWD https://github.com/WCRP-CMIP/CMIP6_CVs/issues/446
PJD 10 Jan 2018    - Revise MPI-M source_id MPIESM-1-2-HR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/196
PJD 16 Jan 2018    - Register institution_id UHH https://github.com/WCRP-CMIP/CMIP6_CVs/issues/450
PJD 13 Feb 2018    - Revise institution_id NCAR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/456
PJD 22 Feb 2018    - Register institution_id AER https://github.com/WCRP-CMIP/CMIP6_CVs/issues/459
PJD 22 Feb 2018    - Remove source_id ACCESS-1-0, update PCMDI-test-1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/454
PJD 22 Feb 2018    - Revise descriptions for HadGEM3 and UKESM1 source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/457
PJD 23 Feb 2018    - Convert versioning for internal consistency https://github.com/WCRP-CMIP/CMIP6_CVs/issues/28
PJD 23 Feb 2018    - Added tag generation for each new version
PJD 23 Feb 2018    - Validate source_id entries against CVs https://github.com/WCRP-CMIP/CMIP6_CVs/issues/378
PJD 23 Feb 2018    - Register institution_id KIOST https://github.com/WCRP-CMIP/CMIP6_CVs/issues/469
PJD  5 Mar 2018    - Updated versionHistory to be obtained from the repo https://github.com/WCRP-CMIP/CMIP6_CVs/issues/468
PJD  5 Mar 2018    - Register source_id KIOST-ESM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/469
PJD  5 Mar 2018    - Update activity_participation for source_id CNRM-CM6-1 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/471
PJD  5 Mar 2018    - Update activity_participation entries to include CMIP https://github.com/WCRP-CMIP/CMIP6_CVs/issues/468
PJD  5 Mar 2018    - Update activity_id to include CDRMIP and PAMIP https://github.com/WCRP-CMIP/CMIP6_CVs/issues/455
PJD  5 Mar 2018    - Updated versionHistory to be obtained from the repo https://github.com/WCRP-CMIP/CMIP6_CVs/issues/468
PJD  5 Mar 2018    - Update README.md to include version badge https://github.com/WCRP-CMIP/CMIP6_CVs/issues/468
PJD  7 Mar 2018    - Register source_id CAS-ESM1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/479
PJD  8 Mar 2018    - Revise source_id VRESM-1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/101
PJD 12 Mar 2018    - Register UHH source_id ARTS-2-3 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/452
PJD 12 Mar 2018    - Register AER source_id LBLRTM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/460
PJD 12 Mar 2018    - Revise source_id GFDL-ESM4 to include CDRMIP https://github.com/WCRP-CMIP/CMIP6_CVs/issues/483
PJD 12 Mar 2018    - Add CMIP6 doc reference in version history https://github.com/WCRP-CMIP/CMIP6_CVs/issues/482
PJD  3 Apr 2018    - Register source_id NESM3 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/488
PJD  3 Apr 2018    - Register institution_id IIASA https://github.com/WCRP-CMIP/CMIP6_CVs/issues/490
PJD  3 Apr 2018    - Revise OMIP JRA55-do entry https://github.com/WCRP-CMIP/CMIP6_CVs/issues/493
PJD  3 Apr 2018    - Revise OMIP allowed_components https://github.com/WCRP-CMIP/CMIP6_CVs/issues/491
PJD  3 Apr 2018    - Revise years in experiment_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/489
PJD  3 Apr 2018    - Revise MPI-ESM1-2-HR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/196
PJD  3 Apr 2018    - Revise ICON-ESM-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/197
PJD  3 Apr 2018    - Revise MPI-ESM-1-2-HAM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/403
PJD  4 Apr 2018    - Revise CAS FGOALS* activity_participation https://github.com/WCRP-CMIP/CMIP6_CVs/issues/427
PJD  4 Apr 2018    - Revise NASA-GISS source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/177
PJD  4 Apr 2018    - Register source_id GISS-E2-1-MA-G https://github.com/WCRP-CMIP/CMIP6_CVs/issues/506
PJD  4 Apr 2018    - Register source_id GISS-E3-G https://github.com/WCRP-CMIP/CMIP6_CVs/issues/507
PJD  4 Apr 2018    - Register institution_id UofT, source_id UofT-CCSM4 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/511 + 512
PJD  6 Apr 2018    - Revise MOHC source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/494
PJD  6 Apr 2018    - Revise source_id MPI-ESM-1-2-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/195
PJD 20 Apr 2018    - Revise source_id BNU-ESM-1-1 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/99
PJD 20 Apr 2018    - Revise experiment_id deforest-globe https://github.com/WCRP-CMIP/CMIP6_CVs/issues/489#issuecomment-380183402
PJD 20 Apr 2018    - Revise institution_id EC-Earth-Consortium https://github.com/WCRP-CMIP/CMIP6_CVs/issues/515
PJD 20 Apr 2018    - Revise MIROC source_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/517
PJD 20 Apr 2018    - Revise institution_id MIROC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/518
PJD 20 Apr 2018    - Add experiment_id values for CDRMIP and PAMIP https://github.com/WCRP-CMIP/CMIP6_CVs/issues/455
PJD 24 Apr 2018    - Register source_id CESM2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/525
PJD 28 Apr 2018    - Revise CESM2 activity_participation https://github.com/WCRP-CMIP/CMIP6_CVs/issues/525
PJD  3 May 2018    - Revise institution_id NCC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/83
PJD 21 May 2018    - Revise source_id UKESM1-0-LL https://github.com/WCRP-CMIP/CMIP6_CVs/issues/531
PJD 21 May 2018    - Register source_id KACE-1-0-G https://github.com/WCRP-CMIP/CMIP6_CVs/issues/532
PJD 21 May 2018    - Register institution_id E3SM-Project https://github.com/WCRP-CMIP/CMIP6_CVs/issues/533
PJD 22 May 2018    - Register institution_id UTAS https://github.com/WCRP-CMIP/CMIP6_CVs/issues/535
PJD 22 May 2018    - Revise institution_id CSIRO-ARCCSS-BoM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/540
PJD 22 May 2018    - Register institution_id CSIRO https://github.com/WCRP-CMIP/CMIP6_CVs/issues/546
PJD 22 May 2018    - Register source_id GFDL-CM4C192 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/537
PJD 22 May 2018    - Register source_id ACCESS-ESM1-5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/538
PJD 22 May 2018    - Register source_id ACCESS-CM2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/539
PJD 22 May 2018    - Register source_id E3SM-1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/534
PJD 22 May 2018    - Revise AWI source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/526
PJD 23 May 2018    - Register source_id CSIRO-Mk3L-1-3 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/536
PJD 23 May 2018    - Revise source_id INM-CM4-8 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/359
PJD 23 May 2018    - Revise source_id E3SM-1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/534
PJD 23 May 2018    - Register source_id GFDL-OM4p5B https://github.com/WCRP-CMIP/CMIP6_CVs/issues/554
PJD 29 May 2018    - Revise source_id CSIRO-Mk3L-1-3 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/536
PJD  6 Jun 2018    - Register 3 additional source_id entries for EC-Earth-Consortia https://github.com/WCRP-CMIP/CMIP6_CVs/issues/559
PJD 12 Jun 2018    - Revise source_id EC-Earth3P-HR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/559
PJD 12 Jun 2018    - Register institution_id DKRZ https://github.com/WCRP-CMIP/CMIP6_CVs/issues/561
PJD 12 Jun 2018    - Register source_id IPSL-CM6A-ATM-HR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/562
PJD 25 Jun 2018    - Update for py3
PJD 25 Jun 2018    - Register institution_id UA https://github.com/WCRP-CMIP/CMIP6_CVs/issues/566
PJD 25 Jun 2018    - Register source_id MCM-UA-1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/568
PJD 27 Jun 2018    - Deregister institution_id IIASA https://github.com/WCRP-CMIP/CMIP6_CVs/issues/490
PJD 27 Jun 2018    - Register institution_id ECMWF https://github.com/WCRP-CMIP/CMIP6_CVs/issues/566
PJD 27 Jun 2018    - Register source_id ECMWF-IFS-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/571
PJD 27 Jun 2018    - Register source_id ECMWF-IFS-HR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/573
PJD 27 Jun 2018    - Register source_id ECMWF-IFS-MR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/574
PJD 27 Jun 2018    - Revise source_id MPI-ESM1-2-HR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/575
PJD 17 Jul 2018    - Revise institution_id FIO-RONM -> FIO-QLNM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/582
PJD 17 Jul 2018    - Register source_id FIO-ESM-2-0 -> FIO-QLNM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/583
PJD 17 Jul 2018    - Revise experiment_id G7cirrus https://github.com/WCRP-CMIP/CMIP6_CVs/issues/584
PJD 17 Jul 2018    - Revise experiment_id land-future https://github.com/WCRP-CMIP/CMIP6_CVs/issues/567
PJD 25 Jul 2018    - Revise LS3MIP experiment_ids, add land-ssp126 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/567
PJD 26 Jul 2018    - Revise source_id MIROC6 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/590
PJD 31 Jul 2018    - Revise multiple GFDL source_id values - release_year https://github.com/WCRP-CMIP/CMIP6_CVs/issues/318
PJD 31 Jul 2018    - Revise piClim experiment_ids allowed components - release_year https://github.com/WCRP-CMIP/CMIP6_CVs/issues/592
PJD 15 Aug 2018    - Rename nominal_resolution -> native_nominal_resolution in source_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/597
PJD 22 Aug 2018    - Revise CDRMIP experiment_id start_years and num years https://github.com/WCRP-CMIP/CMIP6_CVs/issues/594
PJD 12 Sep 2018    - Revise source_id BCC-CSM2-HR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/407, 600
PJD 14 Sep 2018    - Revise multiple GFDL source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/318
PJD 25 Sep 2018    - Revise multiple NICAM source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/606
PJD 25 Sep 2018    - Register source_id AWI-ESM-1-1-LR, amend AWI-CM-1-1-LR https://github.com/WCRP-CMIP/CMIP6_CVs/pull/608
PJD 28 Sep 2018    - Revise experiment_id esm-ssp534-over https://github.com/WCRP-CMIP/CMIP6_CVs/issues/607
PJD  6 Nov 2018    - Revise CNRM-CM6-1 activity_participation https://github.com/WCRP-CMIP/CMIP6_CVs/issues/617
PJD  6 Nov 2018    - Correct CNRM-ESM2-1 activity_participation https://github.com/WCRP-CMIP/CMIP6_CVs/issues/618
PJD  7 Nov 2018    - Revise CNRM-ESM2-1 activity_participation https://github.com/WCRP-CMIP/CMIP6_CVs/issues/621
PJD 29 Nov 2018    - Register institution_id AS-RCEC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/625
PJD 29 Nov 2018    - Register source_id TaiESM1 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/626
PJD 29 Nov 2018    - Revise experiment_id values, BGC as allowed component https://github.com/WCRP-CMIP/CMIP6_CVs/issues/623
PJD 23 Dec 2018    - Revise institution_id AS-RCEC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/625
"""
"""2019
PJD 16 Jan 2019    - Revise source_id values for EC-Earth3 configurations https://github.com/WCRP-CMIP/CMIP6_CVs/issues/559
PJD 16 Jan 2019    - Revise LS3MIP experiment_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/632 and 633
PJD 16 Jan 2019    - Revise DCPP experiment_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/631
PJD 31 Jan 2019    - Revise source_id LBLRTM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/460
PJD 31 Jan 2019    - Register source_id RRTMG-LW-4-91 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/638
PJD 31 Jan 2019    - Register source_id CESM2-WACCM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/639
PJD 31 Jan 2019    - Register source_id CESM2-SE https://github.com/WCRP-CMIP/CMIP6_CVs/issues/640
PJD 31 Jan 2019    - Register source_id RRTMG-SW https://github.com/WCRP-CMIP/CMIP6_CVs/issues/641
PJD 31 Jan 2019    - Revise experiment_id pa-futAntSIC-ext https://github.com/WCRP-CMIP/CMIP6_CVs/issues/648
PJD  6 Feb 2019    - Register institution_id RTE-RRTMGP-Consortium https://github.com/WCRP-CMIP/CMIP6_CVs/issues/650
PJD  6 Feb 2019    - Register source_id RTE-RRTMGP-181204 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/642
PJD 12 Feb 2019    - Revise source_id RTE-RRTMGP-181204 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/642
PJD 21 Feb 2019    - Register source_id MPI-ESM1-2-XR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/654
PJD 25 Feb 2019    - Revise source_id CanESM5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/655
PJD 21 Feb 2019    - Register source_id CanESM5-CanOE https://github.com/WCRP-CMIP/CMIP6_CVs/issues/656
PJD 26 Feb 2019    - Revise MPI-M source_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/654
PJD 27 Feb 2019    - Revise CCCma institution_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/662
PJD  5 Mar 2019    - Revise source_id UKESM1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/664
PJD  5 Mar 2019    - Revise GeoMIP experiment_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/665
PJD  7 Mar 2019    - Revise CNRM-CM6-1 source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/668
PJD 21 Mar 2019    - Revise OMIP*-spunup experiment_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/670
PJD 25 Mar 2019    - Register GFDL RFMIP model contributors https://github.com/WCRP-CMIP/CMIP6_CVs/issues/673
PJD 23 Apr 2019    - Update VRESM/CSIR-CSIRO registration https://github.com/WCRP-CMIP/CMIP6_CVs/issues/100 and 101
PJD 23 Apr 2019    - Revise multiple MIROC registrations https://github.com/WCRP-CMIP/CMIP6_CVs/issues/675
PJD 24 Apr 2019    - Update RFMIP experiment descriptions https://github.com/WCRP-CMIP/CMIP6_CVs/issues/676
PJD 24 Apr 2019    - Register 8 new C4MIP experiments https://github.com/WCRP-CMIP/CMIP6_CVs/issues/679
PJD 24 Apr 2019    - Register institution_id NASA-GSFC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/680
PJD 25 Apr 2019    - Update html page length defaults https://github.com/WCRP-CMIP/CMIP6_CVs/issues/658
PJD  7 May 2019    - Revise source_id EMAC-2-53-AerChem https://github.com/WCRP-CMIP/CMIP6_CVs/issues/695
PJD  8 May 2019    - Register source_id NorESM1-1-LM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/696
PJD  9 May 2019    - Revise HadGEM3-GC31 source_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/699
PJD  9 May 2019    - Rename source_id NorESM1-1-ME https://github.com/WCRP-CMIP/CMIP6_CVs/issues/696
PJD  9 May 2019    - Revise source_id NorESM1-LM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/696
PJD 13 May 2019    - Revise source_id NorESM1-LM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/696
PJD  5 Jun 2019    - Register source_id MRI-AGCM3-2-H and revise MRI-AGCM3-2 to MRI-AGCM3-2-S https://github.com/WCRP-CMIP/CMIP6_CVs/issues/696
PJD  5 Jun 2019    - Revise experiment_id ssp534-over-bgc https://github.com/WCRP-CMIP/CMIP6_CVs/issues/708
PJD  5 Jun 2019    - Revise numerous GeoMIP experiment_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/710
PJD  5 Jun 2019    - Revise source_id BESM-2-7 to BESM-2-9 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/711
PJD 12 Jun 2019    - Revise multiple AerChemMIP experiment_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/706
PJD 12 Jun 2019    - Revise multiple CFMIP experiment_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/709
PJD 12 Jun 2019    - Revise multiple DCPP experiment_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/716
PJD 17 Jun 2019    - Revise sub_experiment_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/720
PJD 17 Jun 2019    - Revise multiple OMIP experiment_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/704
PJD 28 Jun 2019    - Revise AerChemMIP experiment_id histSST-1950HC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/706
PJD 28 Jun 2019    - Revise source_id CNRM-CM6-1 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/723
PJD  1 Jul 2019    - Correct omip2 non-unicode char issue; implement checks description https://github.com/WCRP-CMIP/CMIP6_CVs/issues/726
PJD  3 Jul 2019    - Revise source_id CAMS-CSM1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/729
PJD  8 Jul 2019    - Revise source_id UKESM1-0-LL https://github.com/WCRP-CMIP/CMIP6_CVs/issues/731
PJD  8 Jul 2019    - Revise experiment_id omip2-spunup https://github.com/WCRP-CMIP/CMIP6_CVs/issues/704
PJD 11 Jul 2019    - Revise README.md https://github.com/WCRP-CMIP/CMIP6_CVs/issues/735
PJD 15 Jul 2019    - Revise multiple MPI source_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/734
PJD 17 Jul 2019    - Revise experiment_id ssp370SST-ssp126Lu https://github.com/WCRP-CMIP/CMIP6_CVs/issues/706
PJD 17 Jul 2019    - Add experiment_id histSST-noLu (AerChemMIP) https://github.com/WCRP-CMIP/CMIP6_CVs/issues/739
PJD 22 Jul 2019    - Revise experiment_id esm-hist-ext https://github.com/WCRP-CMIP/CMIP6_CVs/issues/740
PJD 23 Jul 2019    - Register source_id AWI-ESM-2-1-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/745
PJD 24 Jul 2019    - Revise source_id AWI-ESM-2-1-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/745
PJD 29 Jul 2019    - Revise source_id EC-Earth3 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/749
PJD  5 Aug 2019    - Revise source_id KIOST-ESM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/752
PJD 17 Aug 2019    - Register source_id CESM2-FV2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/754
PJD 17 Aug 2019    - Register source_id CESM2-WACCM-FV2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/755
PJD 22 Aug 2019    - Revise source_id GFDL-CM4 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/758
PJD 22 Aug 2019    - Register experiment_id ssp370pdSST https://github.com/WCRP-CMIP/CMIP6_CVs/issues/759
PJD 22 Jul 2019    - Revise experiment_id ssp370SST https://github.com/WCRP-CMIP/CMIP6_CVs/issues/760
PJD 22 Aug 2019    - Register institution_id RUBISCO https://github.com/WCRP-CMIP/CMIP6_CVs/issues/761
PJD 22 Aug 2019    - Register source_id IPSL-CM7A-ATM-HR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/763
PJD 22 Aug 2019    - Register source_id IPSL-CM7A-ATM-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/764
PJD  5 Sep 2019    - Revise institution_id FIO-QLNM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/582
PJD  5 Sep 2019    - Rename source_id NorESM1-LM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/772
PJD 10 Sep 2019    - Register source_id E3SM-1-1 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/775
PJD 10 Sep 2019    - Register source_id E3SM-1-1-ECA https://github.com/WCRP-CMIP/CMIP6_CVs/issues/776
PJD 12 Sep 2019    - Revise source_id FGOALS-f3-L https://github.com/WCRP-CMIP/CMIP6_CVs/issues/779
PJD 13 Sep 2019    - Revise experiment_id entries hist-spAer-aer and hist-spAer-all https://github.com/WCRP-CMIP/CMIP6_CVs/issues/781
PJD 19 Sep 2019    - Revise source_id E3SM-1-1 for 1024 char lim https://github.com/PCMDI/cmip6-cmor-tables/pull/260/files
PJD 19 Sep 2019    - Revise source_id E3SM-1-1-ECA for 1024 char lim https://github.com/PCMDI/cmip6-cmor-tables/pull/260/files
PJD 25 Sep 2019    - Register source_id CESM1-1-CAM5-CMIP5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/785
PJD 25 Sep 2019    - Register source_id NorESM1-F https://github.com/WCRP-CMIP/CMIP6_CVs/issues/786
PJD 25 Sep 2019    - Revise source_id NorESM1-F https://github.com/WCRP-CMIP/CMIP6_CVs/issues/786
PJD  2 Oct 2019    - Revise source_id E3SM-1-1 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/775
PJD  2 Oct 2019    - Revise source_id E3SM-1-1-ECA https://github.com/WCRP-CMIP/CMIP6_CVs/issues/776
PJD  2 Oct 2019    - Register source_id GISS-E2-1-G-CC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/793
PJD  2 Oct 2019    - Revise source_id GISS-E2-1-G https://github.com/WCRP-CMIP/CMIP6_CVs/issues/794
PJD  2 Oct 2019    - Revise and rename source_id GISS-E2-1-MA-G https://github.com/WCRP-CMIP/CMIP6_CVs/issues/795
PJD  2 Oct 2019    - Revise source_id FGOALS-g3 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/796
PJD  3 Oct 2019    - Register 3 new FAFMIP experiment_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/797
PJD 17 Oct 2019    - Revise source_id GFDL-ESM4 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/806
PJD 22 Oct 2019    - Revise institution_id CSIRO-ARCCSS-BoM; Update ACCESS* regos https://github.com/WCRP-CMIP/CMIP6_CVs/issues/809
PJD 22 Oct 2019    - Revise source_id ACCESS-CM2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/810
PJD 22 Oct 2019    - Revise source_id ACCESS-ESM1-5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/811
PJD 22 Oct 2019    - Revise source_id FGOALS-f3-L https://github.com/WCRP-CMIP/CMIP6_CVs/issues/812
PJD 22 Oct 2019    - Revise source_id ACCESS-ESM1-5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/817
PJD 30 Oct 2019    - Revise source_id AWI-CM-1-1-MR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/820
PJD  5 Nov 2019    - Revise source_id HadGEM3-GC31-LL https://github.com/WCRP-CMIP/CMIP6_CVs/issues/822
PJD  7 Nov 2019    - Revise source_id UKESM1-0-LL https://github.com/WCRP-CMIP/CMIP6_CVs/issues/824
PJD 14 Nov 2019    - Register institution_id UCI https://github.com/WCRP-CMIP/CMIP6_CVs/issues/826
PJD 14 Nov 2019    - Register source_id CESM1-WACCM-SC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/827
PJD 19 Nov 2019    - Register source_id 4AOP https://github.com/WCRP-CMIP/CMIP6_CVs/issues/831
PJD 19 Nov 2019    - Revise source_id INM-CM4-8 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/832
PJD 19 Nov 2019    - Revise source_id INM-CM5-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/833
PJD 21 Nov 2019    - Added missing DAMIP CMIP5-era experiment id values; Corrected ScenarioMIP tier levels https://github.com/WCRP-CMIP/CMIP6_CVs/issues/805
PJD  4 Dec 2019    - Register DAMIP experiment_id hist-totalO3 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/838
PJD  4 Dec 2019    - Cleanup experiment_id grammar inconsistencies https://github.com/WCRP-CMIP/CMIP6_CVs/issues/839
PJD  4 Dec 2019    - Revise source_id EC-Earth3-Veg https://github.com/WCRP-CMIP/CMIP6_CVs/issues/843
PJD  5 Dec 2019    - Added start/end_year validation - a new issue is required (commented) https://github.com/WCRP-CMIP/CMIP6_CVs/issues/845
PJD  6 Dec 2019    - Register CMIP5-era experiment_id entries (merge updated) https://github.com/WCRP-CMIP/CMIP6_CVs/issues/805
PJD 13 Dec 2019    - Revise multiple CMCC source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/846
PJD 13 Dec 2019    - Deregister multiple CMCC source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/846
PJD 19 Dec 2019    - Add external_variables to required_global_attributes https://github.com/WCRP-CMIP/CMIP6_CVs/issues/849
PJD 19 Dec 2019    - Reverting addition of external_variables to required_global_attributes https://github.com/WCRP-CMIP/CMIP6_CVs/issues/849
PJD 27 Dec 2019    - Revise source_id CAS-ESM1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/852
"""
"""2020
PJD  2 Jan 2020    - Revise source_id GISS-E2-1-H https://github.com/WCRP-CMIP/CMIP6_CVs/issues/858
PJD  2 Jan 2020    - Revise source_id FGOALS-f3-H https://github.com/WCRP-CMIP/CMIP6_CVs/issues/855
PJD 15 Jan 2020    - Revise source_ids GISS-E2-1-H, GISS-E3-G https://github.com/WCRP-CMIP/CMIP6_CVs/issues/858
PJD 15 Jan 2020    - Revise source_ids MIROC-ES2H-NB, MIROC-ES2H https://github.com/WCRP-CMIP/CMIP6_CVs/issues/856, 863
PJD 15 Jan 2020    - Register source_ids HiRAM-SIT-HR, HiRAM-SIT-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/860
PJD 15 Jan 2020    - Revise multiple IPSL-CM* source_ids https://github.com/WCRP-CMIP/CMIP6_CVs/issues/860
PJD 24 Jan 2020    - Revise experiment_id histSST-noLu https://github.com/WCRP-CMIP/CMIP6_CVs/issues/868
PJD 27 Jan 2020    - Register source_id UKESM1-ice-LL https://github.com/WCRP-CMIP/CMIP6_CVs/issues/868
PJD 28 Jan 2020    - Revise multiple ssp370SST-low* experiment_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/867
PJD  2 Feb 2020    - Register AerChemMIP experiment_id values ssp370-lowNTCFCH4, ssp370SST-lowNTCFCH4 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/873
PJD  2 Feb 2020    - Revise multiple MIROC source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/874
PJD  4 Mar 2020    - Revise source_id MIROC-ES2H-NB https://github.com/WCRP-CMIP/CMIP6_CVs/issues/880
PJD  4 Mar 2020    - Register source_id IPSL-CM6A-LR-INCA https://github.com/WCRP-CMIP/CMIP6_CVs/issues/882
PJD  4 Mar 2020    - Register source_id IPSL-CM5A2-INCA https://github.com/WCRP-CMIP/CMIP6_CVs/issues/881
PJD 11 Mar 2020    - Revise experiment_id histSST-noLu https://github.com/WCRP-CMIP/CMIP6_CVs/issues/739
PJD 19 Mar 2020    - Revise source_id ACCESS-ESM1-5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/889
PJD 19 Mar 2020    - Revise source_id NorESM2-LM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/890
PJD 19 Mar 2020    - Revise *-cmip5 experiment_id values https://github.com/WCRP-CMIP/CMIP6_CVs/issues/805
PJD  3 Apr 2020    - Revise source_id MIROC-ES2H https://github.com/WCRP-CMIP/CMIP6_CVs/issues/896
PJD 22 Apr 2020    - Revise source_id IPSL-CM6A-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/901
PJD 23 Apr 2020    - Revise source_id IPSL-CM6A-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/901
PJD 23 Apr 2020    - Revise source_id MCM-UA-1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/907
PJD 24 Apr 2020    - Revise multiple CNRM- source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/903
PJD 28 Apr 2020    - Revise source_id GISS-E2-1-H https://github.com/WCRP-CMIP/CMIP6_CVs/issues/905
PJD 28 Apr 2020    - Revise source_id CanESM5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/902
PJD 30 Apr 2020    - Register institution_id PNNL-WACCEM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/912
PJD 30 Apr 2020    - Register source_id CAM-MPAS https://github.com/WCRP-CMIP/CMIP6_CVs/issues/913
PJD 30 Apr 2020    - Address jquery security advisories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/916
PJD 30 Apr 2020    - Revise source_id CAM-MPAS https://github.com/WCRP-CMIP/CMIP6_CVs/issues/913
PJD  1 May 2020    - Revise source_id CAM-MPAS https://github.com/WCRP-CMIP/CMIP6_CVs/issues/913
PJD  4 May 2020    - Revise source_id INM-CM5-H https://github.com/WCRP-CMIP/CMIP6_CVs/issues/906
PJD  5 May 2020    - Revise source_id CESM2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/924
PJD  5 May 2020    - Revise source_id CESM2-WACCM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/925
PJD  6 May 2020    - Register additional PMIP experiment_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/898
PJD  7 May 2020    - Revise PMIP experiment_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/898
PJD 11 May 2020    - Validate source/institution_id entry lengths https://github.com/WCRP-CMIP/CMIP6_CVs/issues/933
PJD 11 May 2020    - Register source_id CESM1-CAM5-SE-HR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/932
PJD 11 May 2020    - Register source_id CESM1-CAM5-SE-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/931
PJD 20 May 2020    - Revise experiment_id ssp370-lowNTCFCH4 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/938
PJD  4 Jun 2020    - Register institution_id NTU https://github.com/WCRP-CMIP/CMIP6_CVs/issues/942
PJD  4 Jun 2020    - Register source_id TaiESM1-TIMCOM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/941
PJD 17 Jun 2020    - Revise source_id MPI-ESM-1-2-HAM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/937
PJD 17 Jun 2020    - Revise source_id ACCESS-ESM1-5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/946
PJD 17 Jun 2020    - Revise source_id ACCESS-CM2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/947
PJD 29 Jul 2020    - Revise source_ids UKESM1-0-LL, HadGEM3-GC31-LL https://github.com/WCRP-CMIP/CMIP6_CVs/issues/953
PJD 28 Aug 2020    - Revise source_id IPSL-CM6A-LR-INCA https://github.com/WCRP-CMIP/CMIP6_CVs/issues/955
PJD 24 Sep 2020    - Revise source_id HadGEM3-GC31-MM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/959
PJD  2 Oct 2020    - Register institution_id CSIRO-COSIMA https://github.com/WCRP-CMIP/CMIP6_CVs/issues/961
PJD  2 Oct 2020    - Register source_id ACCESS-OM2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/962
PJD  2 Oct 2020    - Register source_id ACCESS-OM2-025 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/963
PJD  2 Oct 2020    - Revise source_id MPI-ESM-1-2-HAM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/965
PJD  3 Oct 2020    - Revise source_ids EC-Earth3 and IITM-ESM https://github.com/WCRP-CMIP/CMIP6_CVs/issues/964
PJD  9 Oct 2020    - Register source_id CAM-MPAS-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/971
MSM 22 Oct 2020    - Register experiment_ids for "CovidMIP" https://github.com/WCRP-CMIP/CMIP6_CVs/issues/973
PJD 23 Oct 2020    - Revise source_id UKESM1-0-LL https://github.com/WCRP-CMIP/CMIP6_CVs/issues/975
PJD 28 Oct 2020    - Revise source_id MPI-ESM1-2-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/978
PJD 16 Nov 2020    - Register institution_id LLNL https://github.com/WCRP-CMIP/CMIP6_CVs/issues/983
PJD 16 Nov 2020    - Updated for Py2/3
PJD 16 Nov 2020    - Updated institution_id KIOST to exclude ampersand character (html problems)
PJD 16 Nov 2020    - Updated source_id MCM-UA-1-0to exclude <> characters (html problems)
PJD 16 Nov 2020    - Revise source_id E3SM-1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/984
PJD 16 Nov 2020    - Revise source_id CESM1-WACCM-SC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/981
PJD  7 Dec 2020    - Revise source_id TaiESM1 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/988
PJD  7 Dec 2020    - Revise multiple source_id entries E3SM* https://github.com/WCRP-CMIP/CMIP6_CVs/issues/989
PJD 15 Dec 2020    - Revise experiment_id historical parent experiments https://github.com/WCRP-CMIP/CMIP6_CVs/issues/957
PJD 15 Dec 2020    - Revise source_id MIROC-ES2L https://github.com/WCRP-CMIP/CMIP6_CVs/issues/993
"""
"""2021
MSM 15 Jan 2021    - Revise source_id MPI-ESM1-2-HR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/998
MSM 19 Jan 2021    - Revise source_id MPI-ESM1-2-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1000
PJD 20 Jan 2021    - Revise multiple EC-Earth source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1002
PJD 20 Jan 2021    - Revise source_id MIROC-ES2H https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1003
PJD 26 Jan 2021    - Revise source_ids IPSL-CM5A2-INCA, IPSL-CM6A-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1008
MSM 27 Jan 2021    - Revise source_ids GFDL-ESM4, GFDL-CM4 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1010
PJD  4 Feb 2021    - Revise source_id ACCESS-ESM1-5 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1012
PJD 16 Feb 2021    - Revise source_id E3SM-1-1 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1014
PJD  9 Mar 2021    - Revise source_id CMCC-ESM2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1016
PJD 30 Apr 2021    - Register source_id GISS-E2-2-H https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1018
MSM 24 May 2021    - Alter description for 3hr and 6hr frequencies
PJD 21 Jun 2021    - Register source_id IPSL-CM6A-MR1 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1023
PJD 21 Jun 2021    - Register source_id IPSL-CM6A-MR025 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1024
PJD 22 Jul 2021    - Revise source_id E3SM-1-0 add PAMIP https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1030
PJD 26 Jul 2021    - Revise source_id ICON-ESM-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1034
PJD 10 Nov 2021    - Revise source_id MPI-ESM1-2-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1038
PJD  7 Dec 2021    - Register source_id TaiESM1-TIMCOM2 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1040
"""
"""2022
MSM 25 Jan 2022    - Register multiple source_ids IPSL-CM6A-ATM-ICO series https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1043-1046
PJD 31 Jan 2022    - Revise source_id MPI-ESM1-2-LR https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1038
MSM 17 Feb 2022    - Added source_id character<=25 check https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1054
PJD 17 Feb 2022    - Updated json_to_html.py -> jsonToHtml.py; updated jquery and dataTables libraries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1053
PJD 18 Feb 2022    - Update IPSL source_ids, remove IPSL-CM7*, add IPSL-CM6A-ATM-LR-REPROBUS https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1051
PJD 18 Feb 2022    - Revise source_id E3SM-1-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1058
PJD 18 Feb 2022    - Added rights/license entries as placeholder https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1050
PJD  9 May 2022    - Revise source_id EC-Earth3-CC https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1063
PJD 16 May 2022    - Updated license to include all rights entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1050
PJD 17 May 2022    - Updated license to remove CC BY 3.0 (not used by any existing published model)
PJD 17 May 2022    - Updated source_id include extracted rights entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1050
PJD 18 May 2022    - Removed CMCC-ESM2-SR5 from upstream license info https://github.com/WCRP-CMIP/CMIP6_CVs/issues/296 & 900
PJD 18 May 2022    - Updated source_id entries rights -> license_info; update license option identifiers https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1050
PJD 19 May 2022    - Update HadGEM3* license info; updated upstreams
MSM 24 May 2022    - Removed UKESM1-0-MMh https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1067
PJD 24 May 2022    - Update with master; tweak license https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1050
PJD 24 May 2022    - Update source_id license info following https://github.com/WCRP-CMIP/CMIP6_CVs/pull/1069/files
MSM 26 May 2022    - Added UKESM1-1-LL https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1071
PJD 31 May 2022    - Revised UKESM1-ice-LL license history to reflect correct publication/relaxation dates https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1073
PJD  2 Jun 2022    - Revised MCM-UA-1-0 license history https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1075
PJD  6 Jun 2022    - Revised numerous EC-Earth3 license histories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1076
PJD  6 Jun 2022    - Revised numerous IPSL source_id license histories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1078
PJD  7 Jun 2022    - Add CMIP6 Data Reference Syntax (DRS) templates https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1042
PJD  8 Jun 2022    - Revised 5 NorESM2 source_id license histories; deregister NorESM2-LME, NorESM2-LMEC and NorESM2-MH https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1079
PJD  8 Jun 2022    - Revised 9 GFDL source_id license histories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1083
PJD  9 Jun 2022    - Correct erroneous deregistration of NorESM2-MH source_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1079
MSM 10 Jun 2022    - Revised license histories for AS-RCEC and NTU models (TaiESM*, HiRAM*) https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1088
MSM 10 Jun 2022    - Revised license histories for CSIRO, CSIRO-ARCCSS and CSIRO-COSIMA models (ACCESS-*) https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1089
PJD 13 Jun 2022    - Revised license histories for MIROC* models; Deregister NICAM16-9D-L78 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1092
PJD 15 Jun 2022    - Revised 3 MIROC NICAM* source_id license histories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1094
PJD 15 Jun 2022    - Revised 3 E3SM* source_id license histories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1095
PJD 16 Jun 2022    - Deregistered BNU-ESM-1-1 source_id and BNU institution_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1100
PJD 16 Jun 2022    - Deregistered CESM2-SE source_id and revised 8 CESM* source_id license histories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1102
PJD 17 Jun 2022    - Deregistered CNRM-ESM2-1-HR source_id, revised 3 CNRM* source_id license histories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1101 1107
PJD 17 Jun 2022    - Revised 4 MPI-M* source_id license histories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1099
PJD 20 Jun 2022    - Revised 3 MIROC NICAM* source_id license histories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1094
PJD 20 Jun 2022    - Revised 4 MIROC* source_id license histories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1094
PJD 21 Jun 2022    - Deregistered two EMAC-2* source_id entries https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1111
PJD 22 Jun 2022    - Revised 5 AWI* source_id license histories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1116
PJD 27 Jun 2022    - Revised 4 CMCC* source_id license histories https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1118
PJD 28 Jun 2022    - Deregistered VRESM-1-0 source_id and CSIR-Wits-CSIRO institution_id https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1122
PJD  1 Jul 2022    - Deregistered source_id UofT-CCSM4 and institution_id UofT https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1086
PJD  1 Jul 2022    - Deregistered source_id BESM-2-9 and institution_id INPE https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1120
PJD  1 Jul 2022    - Deregistered source_id CSIRO-Mk3L-1-3 and institution_id UTAS https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1121
PJD 19 Jul 2022    - Registered source_id E3SM-2-0 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1127
PJD 27 Jul 2022    - Added derived "source" test for CMOR3 1024 char limit https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1129
PJD 27 Jul 2022    - Revised source_id E3SM-2-0 to deal with 1024 char limit of CMOR3 https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1127
PJD 27 Jul 2022    - Tweaked derived "source" test for CMOR3 1024 char limit - added key and release year https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1129
PJD 27 Jul 2022    - Deregistered source_id GFDL-GLOBAL-LBL https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1083
                     - TODO: Review all start/end_year pairs for experiments https://github.com/WCRP-CMIP/CMIP6_CVs/issues/845
                     - TODO: Generate table_id from dataRequest https://github.com/WCRP-CMIP/CMIP6_CVs/issues/166

@author: durack1
"""

# %% Set commit message and author info
commitMessage = '\"Deregister source_id GFDL-GLOBAL-LBL\"'
#author = 'Matthew Mizielinski <matthew.mizielinski@metoffice.gov.uk>'
#author_institution_id = 'MOHC'
author = 'Paul J. Durack <durack1@llnl.gov>'
author_institution_id = 'PCMDI'

# %% List target controlled vocabularies (CVs)
masterTargets = [
    'activity_id',
    'DRS',
    'experiment_id',
    'frequency',
    'grid_label',
    'institution_id',
    'license',
    'mip_era',
    'nominal_resolution',
    'realm',
    'required_global_attributes',
    'source_id',
    'source_type',
    'sub_experiment_id',
    'table_id'
]

# %% Activities
activity_id = {
    'AerChemMIP': 'Aerosols and Chemistry Model Intercomparison Project',
    'C4MIP': 'Coupled Climate Carbon Cycle Model Intercomparison Project',
    'CDRMIP': 'Carbon Dioxide Removal Model Intercomparison Project',
    'CFMIP': 'Cloud Feedback Model Intercomparison Project',
    'CMIP': 'CMIP DECK: 1pctCO2, abrupt4xCO2, amip, esm-piControl, esm-historical, historical, and piControl experiments',
    'CORDEX': 'Coordinated Regional Climate Downscaling Experiment',
    'DAMIP': 'Detection and Attribution Model Intercomparison Project',
    'DCPP': 'Decadal Climate Prediction Project',
    'DynVarMIP': 'Dynamics and Variability Model Intercomparison Project',
    'FAFMIP': 'Flux-Anomaly-Forced Model Intercomparison Project',
    'GMMIP': 'Global Monsoons Model Intercomparison Project',
    'GeoMIP': 'Geoengineering Model Intercomparison Project',
    'HighResMIP': 'High-Resolution Model Intercomparison Project',
    'ISMIP6': 'Ice Sheet Model Intercomparison Project for CMIP6',
    'LS3MIP': 'Land Surface, Snow and Soil Moisture',
    'LUMIP': 'Land-Use Model Intercomparison Project',
    'OMIP': 'Ocean Model Intercomparison Project',
    'PAMIP': 'Polar Amplification Model Intercomparison Project',
    'PMIP': 'Palaeoclimate Modelling Intercomparison Project',
    'RFMIP': 'Radiative Forcing Model Intercomparison Project',
    'SIMIP': 'Sea Ice Model Intercomparison Project',
    'ScenarioMIP': 'Scenario Model Intercomparison Project',
    'VIACSAB': 'Vulnerability, Impacts, Adaptation and Climate Services Advisory Board',
    'VolMIP': 'Volcanic Forcings Model Intercomparison Project'
}

# %% DRS - directory and filename templates
DRS = {}
DRS["directory_path_template"] = "<mip_era>/<activity_id>/<institution_id>/<source_id>/<experiment_id>/<member_id>/<table_id>/<variable_id>/<grid_label>/<version>"
DRS["directory_path_example"] = "CMIP6/CMIP/MOHC/HadGEM3-GC31-MM/historical/r1i1p1f3/Amon/tas/gn/v20191207/"
DRS["directory_path_sub_experiment_example"] = "CMIP6/DCPP/MOHC/HadGEM3-GC31-MM/dcppA-hindcast/s1960-r1i1p1f2/Amon/tas/gn/v20200417/"
DRS["filename_template"] = "<variable_id>_<table_id>_<source_id>_<experiment_id >_<member_id>_<grid_label>[_<time_range>].nc"
DRS["filename_example"] = "tas_Amon_HadGEM3-GC31-MM_historical_r1i1p1f3_gn_185001-186912.nc"
DRS["filename_sub_experiment_example"] = "tas_Amon_HadGEM3-GC31-MM_dcppA-hindcast_s1960-r1i1p1f2_gn_196011-196012.nc"

# %% Experiments
tmp = [['experiment_id',
        'https://raw.githubusercontent.com/WCRP-CMIP/CMIP6_CVs/master/CMIP6_experiment_id.json']
       ]
experiment_id = readJsonCreateDict(tmp)
experiment_id = experiment_id.get('experiment_id')
# Fudge to extract duplicate level
experiment_id = experiment_id.get('experiment_id')
del(tmp)

# Fix issues

'''
# xlsx import
# Fields
# Alpha/json order, xlsx column old, xlsx column new, type, value
# 1  0  0  str  experiment_id string
# 2  1  1  list activity_id list
# 3  8  7  list additional_allowed_model_components list
# 4  13 12 str  description string
# 5  10 10 str  end_year string
# 6  2  2  str  experiment string
# 7  11 11 str  min_number_yrs_per_sim string
# 8  12 5  list parent_activity_id list
# 9  6  6  list parent_experiment_id list
# 10 7  8  list required_model_components list
# 11 9  9  str  start_year string
# 12 5  -  -    sub_experiment string
# 13 4  4  list sub_experiment_id string
# 14 3  3  str tier string

os.chdir('/sync/git/CMIP6_CVs/src')
inFiles = ['180421_1927_DavidKeller_CMIP6-CDRMIP-ExpList.xlsx',
           '180421_1927_DougSmith_CMIP6-PAMIP-ExpList.xlsx']
for inFile in inFiles:
    data = pyx.get_data(inFile)
    data = data['Sheet1']
    headers = data[3]
    #experiment_id = {} ; Already defined and loaded
    for count in range(4,len(data)): # Start on 5th row, headers
        if data[count] == []:
            #print count,'blank field'
            continue
        row = data[count]
        key = row[0] ; #replace(row[0],'_ ','_')
        experiment_id[key] = {}
        for count2,entry in enumerate(headers):
            #if count2 == 5:
            #    continue ; # Skip sub_experiment - removed in update
            entry = replace(entry,'_ ','_') ; # clean up spaces
            entry = replace(entry,' ', '_') ; # replace spaces with underscores
            if count2 >= len(row):
                experiment_id[key][entry] = ''
                continue
            value = row[count2]
            if count2 in [1,4,6,7,8,12]:
                if value == None:
                    pass
                elif value == 'no parent':
                    pass
                elif 'no parent,' in value:
                    value = ['no parent',replace(value,'no parent,','').strip()] ; # deal with multiple entries (including 'no parent')
                    pass
                else:
                    value = replace(value,',','') ; # remove ','
                    value = value.split() ; # Change type to list
                    #print value
            if type(value) == long:
                experiment_id[key][entry] = str(value) ; #replace(str(value),' ','')
            elif type(value) == list:
                experiment_id[key][entry] = ' '.join(value)
            elif value == None:
                experiment_id[key][entry] = '' ; # changed from none to preserve blank entries
            elif type(value) == float:
                #print 'elif type(value):',value
                value = str(int(value))
                experiment_id[key][entry] = value
            else:
                #print 'else:',value
                value = replace(value,'    ',' ') ; # replace whitespace
                value = replace(value,'   ',' ') ; # replace whitespace
                value = replace(value,'  ',' ') ; # replace whitespace
                experiment_id[key][entry] = unidecode(value) ; #replace(unidecode(value),' ','')
                try:
                    #print 'try:',value
                    unidecode(value)
                except:
                    print count,count2,key,entry,value
            # Now sort by type
            if count2 in [1,4,6,7,8]:
                experiment_id[key][entry] = list(value)
            elif count2 == 5:
                experiment_id[key][entry] = list([value])
    del(inFile,data,headers,count,row,key,entry,value) ; gc.collect()
'''
# ==============================================================================
# Example new experiment_id entry
#key = 'ssp119'
#experiment_id[key] = {}
#experiment_id[key]['activity_id'] = ['ScenarioMIP']
#experiment_id[key]['additional_allowed_model_components'] = ['AER','CHEM','BGC']
#experiment_id[key]['description'] = 'Future scenario with low radiative forcing throughout reaching about 1.9 W/m2 in 2100 based on SSP1. Concentration-driven'
#experiment_id[key]['end_year'] = '2100'
#experiment_id[key]['experiment'] = 'low-end scenario reaching 1.9 W m-2, based on SSP1'
#experiment_id[key]['experiment_id'] = key
#experiment_id[key]['min_number_yrs_per_sim'] = '86'
#experiment_id[key]['parent_activity_id'] = ['CMIP']
#experiment_id[key]['parent_experiment_id'] = ['historical']
#experiment_id[key]['required_model_components'] = ['AOGCM']
#experiment_id[key]['start_year'] = '2015'
#experiment_id[key]['sub_experiment_id'] = ['none']
#experiment_id[key]['tier'] = '2'
# Rename
#experiment_id['land-noShiftCultivate'] = experiment_id.pop('land-noShiftcultivate')
# Remove
# experiment_id.pop('land-noShiftcultivate')

# %% Frequencies
frequency = {
    '1hr': 'sampled hourly',
    '1hrCM': 'monthly-mean diurnal cycle resolving each day into 1-hour means',
    '1hrPt': 'sampled hourly, at specified time point within an hour',
    '3hr': '3 hourly mean samples',
    '3hrPt': 'sampled 3 hourly, at specified time point within the time period',
    '6hr': '6 hourly mean samples',
    '6hrPt': 'sampled 6 hourly, at specified time point within the time period',
    'day': 'daily mean samples',
    'dec': 'decadal mean samples',
    'fx': 'fixed (time invariant) field',
    'mon': 'monthly mean samples',
    'monC': 'monthly climatology computed from monthly mean samples',
    'monPt': 'sampled monthly, at specified time point within the time period',
    'subhrPt': 'sampled sub-hourly, at specified time point within an hour',
    'yr': 'annual mean samples',
    'yrPt': 'sampled yearly, at specified time point within the time period'
}

# %% Grid labels
grid_label = {
    'gm': 'global mean data',
    'gn': 'data reported on a model\'s native grid',
    'gna': 'data reported on a native grid in the region of Antarctica',
    'gng': 'data reported on a native grid in the region of Greenland',
    'gnz': 'zonal mean data reported on a model\'s native latitude grid',
    'gr': 'regridded data reported on the data provider\'s preferred target grid',
    'gr1': 'regridded data reported on a grid other than the native grid and other than the preferred target grid',
    'gr1a': 'regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid',
    'gr1g': 'regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid',
    'gr1z': 'regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid',
    'gr2': 'regridded data reported on a grid other than the native grid and other than the preferred target grid',
    'gr2a': 'regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid',
    'gr2g': 'regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid',
    'gr2z': 'regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid',
    'gr3': 'regridded data reported on a grid other than the native grid and other than the preferred target grid',
    'gr3a': 'regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid',
    'gr3g': 'regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid',
    'gr3z': 'regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid',
    'gr4': 'regridded data reported on a grid other than the native grid and other than the preferred target grid',
    'gr4a': 'regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid',
    'gr4g': 'regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid',
    'gr4z': 'regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid',
    'gr5': 'regridded data reported on a grid other than the native grid and other than the preferred target grid',
    'gr5a': 'regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid',
    'gr5g': 'regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid',
    'gr5z': 'regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid',
    'gr6': 'regridded data reported on a grid other than the native grid and other than the preferred target grid',
    'gr6a': 'regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid',
    'gr6g': 'regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid',
    'gr6z': 'regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid',
    'gr7': 'regridded data reported on a grid other than the native grid and other than the preferred target grid',
    'gr7a': 'regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid',
    'gr7g': 'regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid',
    'gr7z': 'regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid',
    'gr8': 'regridded data reported on a grid other than the native grid and other than the preferred target grid',
    'gr8a': 'regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid',
    'gr8g': 'regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid',
    'gr8z': 'regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid',
    'gr9': 'regridded data reported on a grid other than the native grid and other than the preferred target grid',
    'gr9a': 'regridded data reported in the region of Antarctica on a grid other than the native grid and other than the preferred target grid',
    'gr9g': 'regridded data reported in the region of Greenland on a grid other than the native grid and other than the preferred target grid',
    'gr9z': 'regridded zonal mean data reported on a grid other than the native latitude grid and other than the preferred latitude target grid',
    'gra': 'regridded data in the region of Antarctica reported on the data provider\'s preferred target grid',
    'grg': 'regridded data in the region of Greenland reported on the data provider\'s preferred target grid',
    'grz': 'regridded zonal mean data reported on the data provider\'s preferred latitude target grid'
}

# %% Institutions
institution_id = {
    'AER': 'Research and Climate Group, Atmospheric and Environmental Research, 131 Hartwell Avenue, Lexington, MA 02421, USA',
    'AS-RCEC': 'Research Center for Environmental Changes, Academia Sinica, Nankang, Taipei 11529, Taiwan',
    'AWI': 'Alfred Wegener Institute, Helmholtz Centre for Polar and Marine Research, Am Handelshafen 12, 27570 Bremerhaven, Germany',
    'BCC': 'Beijing Climate Center, Beijing 100081, China',
    'CAMS': 'Chinese Academy of Meteorological Sciences, Beijing 100081, China',
    'CAS': 'Chinese Academy of Sciences, Beijing 100029, China',
    'CCCR-IITM': 'Centre for Climate Change Research, Indian Institute of Tropical Meteorology Pune, Maharashtra 411 008, India',
    'CCCma': 'Canadian Centre for Climate Modelling and Analysis, Environment and Climate Change Canada, Victoria, BC V8P 5C2, Canada',
    'CMCC': 'Fondazione Centro Euro-Mediterraneo sui Cambiamenti Climatici, Lecce 73100, Italy',
    'CNRM-CERFACS': ''.join(['CNRM (Centre National de Recherches Meteorologiques, Toulouse 31057, France), CERFACS (Centre Europeen de Recherche ',
                             'et de Formation Avancee en Calcul Scientifique, Toulouse 31057, France)']),
    'CSIRO': 'Commonwealth Scientific and Industrial Research Organisation, Aspendale, Victoria 3195, Australia',
    'CSIRO-ARCCSS': ' '.join(['CSIRO (Commonwealth Scientific and Industrial Research Organisation, Aspendale, Victoria 3195, Australia),',
                              'ARCCSS (Australian Research Council Centre of Excellence for Climate System Science).',
                              'Mailing address: CSIRO, c/o Simon J. Marsland,',
                              '107-121 Station Street, Aspendale, Victoria 3195, Australia']),
    'CSIRO-COSIMA': ' '.join(['CSIRO (Commonwealth Scientific and Industrial Research Organisation, Australia),',
                              'COSIMA (Consortium for Ocean-Sea Ice Modelling in Australia).',
                              'Mailing address: CSIRO, c/o Simon J. Marsland,',
                              '107-121 Station Street, Aspendale, Victoria 3195, Australia']),
    'DKRZ': 'Deutsches Klimarechenzentrum, Hamburg 20146, Germany',
    'DWD': 'Deutscher Wetterdienst, Offenbach am Main 63067, Germany',
    'E3SM-Project': ''.join(['LLNL (Lawrence Livermore National Laboratory, Livermore, CA 94550, USA); ',
                             'ANL (Argonne National Laboratory, Argonne, IL 60439, USA); ',
                             'BNL (Brookhaven National Laboratory, Upton, NY 11973, USA); ',
                             'LANL (Los Alamos National Laboratory, Los Alamos, NM 87545, USA); ',
                             'LBNL (Lawrence Berkeley National Laboratory, Berkeley, CA 94720, USA); ',
                             'ORNL (Oak Ridge National Laboratory, Oak Ridge, TN 37831, USA); ',
                             'PNNL (Pacific Northwest National Laboratory, Richland, WA 99352, USA); ',
                             'SNL (Sandia National Laboratories, Albuquerque, NM 87185, USA). ',
                             'Mailing address: LLNL Climate Program, c/o David C. Bader, ',
                             'Principal Investigator, L-103, 7000 East Avenue, Livermore, CA 94550, USA']),
    'EC-Earth-Consortium': ''.join(['AEMET, Spain; BSC, Spain; CNR-ISAC, Italy; DMI, Denmark; ENEA, Italy; FMI, Finland; Geomar, Germany; ICHEC, ',
                                    'Ireland; ICTP, Italy; IDL, Portugal; IMAU, The Netherlands; IPMA, Portugal; KIT, Karlsruhe, Germany; KNMI, ',
                                    'The Netherlands; Lund University, Sweden; Met Eireann, Ireland; NLeSC, The Netherlands; NTNU, Norway; Oxford ',
                                    'University, UK; surfSARA, The Netherlands; SMHI, Sweden; Stockholm University, Sweden; Unite ASTR, Belgium; ',
                                    'University College Dublin, Ireland; University of Bergen, Norway; University of Copenhagen, Denmark; ',
                                    'University of Helsinki, Finland; University of Santiago de Compostela, Spain; Uppsala University, Sweden; ',
                                    'Utrecht University, The Netherlands; Vrije Universiteit Amsterdam, the Netherlands; Wageningen University, ',
                                    'The Netherlands. Mailing address: EC-Earth consortium, Rossby Center, Swedish Meteorological and Hydrological ',
                                    'Institute/SMHI, SE-601 76 Norrkoping, Sweden']),
    'ECMWF': 'European Centre for Medium-Range Weather Forecasts, Reading RG2 9AX, UK',
    'FIO-QLNM': ''.join(['FIO (First Institute of Oceanography, Ministry of Natural Resources, Qingdao 266061, China), ',
                         'QNLM (Qingdao National Laboratory for Marine Science and Technology, Qingdao 266237, China)']),
    'HAMMOZ-Consortium': ''.join(['ETH Zurich, Switzerland; Max Planck Institut fur Meteorologie, Germany; Forschungszentrum Julich, ',
                                  'Germany; University of Oxford, UK; Finnish Meteorological Institute, Finland; Leibniz Institute for Tropospheric ',
                                  'Research, Germany; Center for Climate Systems Modeling (C2SM) at ETH Zurich, Switzerland']),
    'INM': 'Institute for Numerical Mathematics, Russian Academy of Science, Moscow 119991, Russia',
    'IPSL': 'Institut Pierre Simon Laplace, Paris 75252, France',
    'KIOST': 'Korea Institute of Ocean Science and Technology, Busan 49111, Republic of Korea',
    'LLNL': ' '.join(['Lawrence Livermore National Laboratory, Livermore,',
                      'CA 94550, USA. Mailing address: LLNL Climate Program,',
                      'c/o Stephen A. Klein, Principal Investigator, L-103,',
                      '7000 East Avenue, Livermore, CA 94550, USA']),
    'MESSy-Consortium': ''.join(['The Modular Earth Submodel System (MESSy) Consortium, represented by the Institute for Physics of the Atmosphere, ',
                                 'Deutsches Zentrum fur Luft- und Raumfahrt (DLR), Wessling, Bavaria 82234, Germany']),
    'MIROC': ''.join(['JAMSTEC (Japan Agency for Marine-Earth Science and Technology, Kanagawa 236-0001, Japan), ',
                      'AORI (Atmosphere and Ocean Research Institute, The University of Tokyo, Chiba 277-8564, Japan), ',
                      'NIES (National Institute for Environmental Studies, Ibaraki 305-8506, Japan), ',
                      'and R-CCS (RIKEN Center for Computational Science, Hyogo 650-0047, Japan)']),
    'MOHC': 'Met Office Hadley Centre, Fitzroy Road, Exeter, Devon, EX1 3PB, UK',
    'MPI-M': 'Max Planck Institute for Meteorology, Hamburg 20146, Germany',
    'MRI': 'Meteorological Research Institute, Tsukuba, Ibaraki 305-0052, Japan',
    'NASA-GISS': 'Goddard Institute for Space Studies, New York, NY 10025, USA',
    'NASA-GSFC': 'NASA Goddard Space Flight Center, Greenbelt, MD 20771, USA',
    'NCAR': 'National Center for Atmospheric Research, Climate and Global Dynamics Laboratory, 1850 Table Mesa Drive, Boulder, CO 80305, USA',
    'NCC': ''.join(['NorESM Climate modeling Consortium consisting of ',
                    'CICERO (Center for International Climate and Environmental Research, Oslo 0349), ',
                    'MET-Norway (Norwegian Meteorological Institute, Oslo 0313), ',
                    'NERSC (Nansen Environmental and Remote Sensing Center, Bergen 5006), ',
                    'NILU (Norwegian Institute for Air Research, Kjeller 2027), ',
                    'UiB (University of Bergen, Bergen 5007), ',
                    'UiO (University of Oslo, Oslo 0313) ',
                    'and UNI (Uni Research, Bergen 5008), Norway. Mailing address: NCC, c/o MET-Norway, ',
                    'Henrik Mohns plass 1, Oslo 0313, Norway']),
    'NERC': 'Natural Environment Research Council, STFC-RAL, Harwell, Oxford, OX11 0QX, UK',
    'NIMS-KMA': ' '.join(['National Institute of Meteorological Sciences/Korea',
                          'Meteorological Administration, Climate Research',
                          'Division, Seoho-bukro 33, Seogwipo-si, Jejudo 63568,',
                          'Republic of Korea']),
    'NIWA': 'National Institute of Water and Atmospheric Research, Hataitai, Wellington 6021, New Zealand',
    'NOAA-GFDL': 'National Oceanic and Atmospheric Administration, Geophysical Fluid Dynamics Laboratory, Princeton, NJ 08540, USA',
    'NTU': 'National Taiwan University, Taipei 10650, Taiwan',
    'NUIST': 'Nanjing University of Information Science and Technology, Nanjing, 210044, China',
    'PCMDI': 'Program for Climate Model Diagnosis and Intercomparison, Lawrence Livermore National Laboratory, Livermore, CA 94550, USA',
    'PNNL-WACCEM': 'PNNL (Pacific Northwest National Laboratory), Richland, WA 99352, USA',
    'RTE-RRTMGP-Consortium': ''.join(['AER (Atmospheric and Environmental Research, Lexington, MA 02421, USA); UColorado (University of Colorado, ',
                                      'Boulder, CO 80309, USA). Mailing address: AER c/o Eli Mlawer, 131 Hartwell Avenue, Lexington, MA 02421, USA']),
    'RUBISCO': ''.join(['ORNL (Oak Ridge National Laboratory, Oak Ridge, TN 37831, USA); ANL (Argonne National Laboratory, Argonne, IL 60439, USA); ',
                        'BNL (Brookhaven National Laboratory, Upton, NY 11973, USA); LANL (Los Alamos National Laboratory, Los Alamos, NM 87545); ',
                        'LBNL (Lawrence Berkeley National Laboratory, Berkeley, CA 94720, USA); NAU (Northern Arizona University, Flagstaff, AZ 86011, USA); ',
                        'NCAR (National Center for Atmospheric Research, Boulder, CO 80305, USA); UCI (University of California Irvine, Irvine, CA 92697, USA); ',
                        'UM (University of Michigan, Ann Arbor, MI 48109, USA). Mailing address: ORNL Climate Change Science Institute, c/o Forrest M. Hoffman, ',
                        'Laboratory Research Manager, Building 4500N Room F106, 1 Bethel Valley Road, Oak Ridge, TN 37831-6301, USA']),
    'SNU': 'Seoul National University, Seoul 08826, Republic of Korea',
    'THU': 'Department of Earth System Science, Tsinghua University, Beijing 100084, China',
    'UA': 'Department of Geosciences, University of Arizona, Tucson, AZ 85721, USA',
    'UCI': 'Department of Earth System Science, University of California Irvine, Irvine, CA 92697, USA',
    'UHH': 'Universitat Hamburg, Hamburg 20148, Germany',
}

# %% CMIP6 License
license = {}
license["license"] =\
    ''.join(['CMIP6 model data produced by <Your Institution; see CMIP6_institution_id.json> is ',
             'licensed under a <Creative Commons; select and insert a license_id; see below> License ',
             '(<insert the matching license_url; see below>). Consult ',
             'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use governing CMIP6 output, ',
             'including citation requirements and proper acknowledgment. Further information about ',
             'this data, including some limitations, can be found via the further_info_url (recorded ',
             'as a global attribute in this file)[ and at <some URL maintained by modeling group>]. ',
             'The data producers and data providers make no warranty, either express or implied, ',
             'including, but not limited to, warranties of merchantability and fitness for a ',
             'particular purpose. All liabilities arising from the supply of the information ',
             '(including any liability arising in negligence) are excluded to the fullest extent ',
             'permitted by law.'])
license["license_options"] = {}
license["license_options"]["CC0 1.0"] = {}
license["license_options"]["CC0 1.0"]["license_id"] = "Creative Commons CC0 1.0 Universal Public Domain Dedication"
license["license_options"]["CC0 1.0"]["license_url"] = "https://creativecommons.org/publicdomain/zero/1.0/"
license["license_options"]["CC BY 4.0"] = {}
license["license_options"]["CC BY 4.0"]["license_id"] = "Creative Commons Attribution 4.0 International"
license["license_options"]["CC BY 4.0"]["license_url"] = "https://creativecommons.org/licenses/by/4.0/"
license["license_options"]["CC BY-SA 4.0"] = {}
license["license_options"]["CC BY-SA 4.0"]["license_id"] = "Creative Commons Attribution-ShareAlike 4.0 International"
license["license_options"]["CC BY-SA 4.0"]["license_url"] = "https://creativecommons.org/licenses/by-sa/4.0/"
license["license_options"]["CC BY-NC-SA 4.0"] = {}
license["license_options"]["CC BY-NC-SA 4.0"]["license_id"] = "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International"
license["license_options"]["CC BY-NC-SA 4.0"]["license_url"] = "https://creativecommons.org/licenses/by-nc-sa/4.0/"

# %% MIP eras
mip_era = ['CMIP1', 'CMIP2', 'CMIP3', 'CMIP5', 'CMIP6']

# %% Nominal resolutions
nominal_resolution = [
    '0.5 km',
    '1 km',
    '10 km',
    '100 km',
    '1000 km',
    '10000 km',
    '1x1 degree',
    '2.5 km',
    '25 km',
    '250 km',
    '2500 km',
    '5 km',
    '50 km',
    '500 km',
    '5000 km'
]

# %% Realms
realm = {
    'aerosol': 'Aerosol',
    'atmos': 'Atmosphere',
    'atmosChem': 'Atmospheric Chemistry',
    'land': 'Land Surface',
    'landIce': 'Land Ice',
    'ocean': 'Ocean',
    'ocnBgchem': 'Ocean Biogeochemistry',
    'seaIce': 'Sea Ice'
}

# %% Required global attributes
required_global_attributes = [
    'Conventions',
    'activity_id',
    'creation_date',
    'data_specs_version',
    'experiment',
    'experiment_id',
    'forcing_index',
    'frequency',
    'further_info_url',
    'grid',
    'grid_label',
    'initialization_index',
    'institution',
    'institution_id',
    'license',
    'mip_era',
    'nominal_resolution',
    'physics_index',
    'product',
    'realization_index',
    'realm',
    'source',
    'source_id',
    'source_type',
    'sub_experiment',
    'sub_experiment_id',
    'table_id',
    'tracking_id',
    'variable_id',
    'variant_label'
]

# %% Source identifiers
tmp = [['source_id', 'https://raw.githubusercontent.com/WCRP-CMIP/CMIP6_CVs/master/CMIP6_source_id.json']
       ]
source_id = readJsonCreateDict(tmp)
source_id = source_id.get('source_id')
source_id = source_id.get('source_id')  # Fudge to extract duplicate level
del(tmp)

# Fix issues
key = "GFDL-GLOBAL-LBL"
source_id.pop(key)

# Example license update, including email
# source_ids_to_relax_list = [
#     "E3SM-1-0",
#     "E3SM-1-1",
#     "E3SM-1-1-ECA",
# ]
#
# for key in source_ids_to_relax_list:
#     print("processing:", key)
#     licenseId = "CC BY 4.0"
#     source_id[key]["license_info"]["exceptions_contact"] = "@llnl.gov <- e3sm-data-support"
#     source_id[key]["license_info"]["history"] += "; 2022-06-15: relaxed to CC BY 4.0"
#     source_id[key]["license_info"]["id"] = licenseId
#     licenseStr = license["license_options"][licenseId]["license_id"]
#     licenseUrl = license["license_options"][licenseId]["license_url"]
#     source_id[key]["license_info"]["license"] = "".join(
#         [licenseStr, " (", licenseId, "; ", licenseUrl, ")"])
#     source_id[key]["license_info"]["url"] = licenseUrl

# Example source_id registration
# key = "E3SM-2-0"
# source_id[key] = {}
# source_id[key]["activity_participation"] = [
#     "CFMIP",
#     "CMIP",
#     "DAMIP",
#     "RFMIP",
#     "ScenarioMIP",
# ]
# source_id[key]["cohort"] = [
#     "Registered",
# ]
# source_id[key]["institution_id"] = [
#     "E3SM-Project",
# ]
# source_id[key]["label"] = "E3SM 2.0"
# source_id[key]["label_extended"] = "E3SM 2.0 (Energy Exascale Earth System Model)"
# source_id[key]["model_component"] = {}
# source_id[key]["model_component"]["aerosol"] = {}
# source_id[key]["model_component"]["aerosol"]["description"] = " ".join(["MAM4 with new resuspension,",
#                                                                        "marine organics, secondary organics,",
#                                                                         "and dust (atmos grid)"])
# source_id[key]["model_component"]["aerosol"]["native_nominal_resolution"] = "100 km"
# source_id[key]["model_component"]["atmos"] = {}
# source_id[key]["model_component"]["atmos"]["description"] = " ".join(["EAM (v2.0, cubed sphere spectral-element grid;",
#                                                                       "5400 elements, 30x30 per cube face. Dynamics:",
#                                                                       "degree 3 (p=3) polynomials within each spectral",
#                                                                       "element, 112 km average resolution. Physics: 2x2",
#                                                                       "finite volume cells within each spectral element,",
#                                                                       "1.5 degree (168 km) average grid spacing; 72",
#                                                                       "vertical layers; top level 60 km)"])
# source_id[key]["model_component"]["atmos"]["native_nominal_resolution"] = "100 km"
# source_id[key]["model_component"]["atmosChem"] = {}
# source_id[key]["model_component"]["atmosChem"]["description"] = " ".join(["Troposphere specified oxidants (except",
#                                                                           "passive ozone with the lower boundary sink)",
#                                                                           "for aerosols. Stratosphere linearized",
#                                                                           "interactive ozone (LINOZ v2) (atmos grid)"])
# source_id[key]["model_component"]["atmosChem"]["native_nominal_resolution"] = "100 km"
# source_id[key]["model_component"]["land"] = {}
# source_id[key]["model_component"]["land"]["description"] = " ".join(["ELM (v1.0, satellite phenology mode, atmos grid),",
#                                                                      "MOSART (v1.0, 0.5 degree latitude/longitude)"])
# source_id[key]["model_component"]["land"]["native_nominal_resolution"] = "100 km"
# source_id[key]["model_component"]["landIce"] = {}
# source_id[key]["model_component"]["landIce"]["description"] = 'none'
# source_id[key]["model_component"]["landIce"]["native_nominal_resolution"] = 'none'
# source_id[key]["model_component"]["ocean"] = {}
# source_id[key]["model_component"]["ocean"]["description"] = " ".join(["MPAS-Ocean (E3SMv2.0, EC30to60E2r2 unstructured",
#                                                                       "SVTs mesh with 236853 cells, 719506 edges,",
#                                                                       "variable resolution 60 to 30 km; 60 levels;",
#                                                                       "top grid cell 0-10 m)"])
# source_id[key]["model_component"]["ocean"]["native_nominal_resolution"] = "50 km"
# source_id[key]["model_component"]["ocnBgchem"] = {}
# source_id[key]["model_component"]["ocnBgchem"]["description"] = 'none'
# source_id[key]["model_component"]["ocnBgchem"]["native_nominal_resolution"] = 'none'
# source_id[key]["model_component"]["seaIce"] = {}
# source_id[key]["model_component"]["seaIce"]["description"] = " ".join(["MPAS-Seaice (E3SMv2.0, ocean grid,",
#                                                                        "variable resolution 60 to 30 km; 5 ice",
#                                                                        "categories; 7 ice, 5 snow layers)"])
# source_id[key]["model_component"]["seaIce"]["native_nominal_resolution"] = "50 km"
# source_id[key]["release_year"] = "2022"
# source_id[key]["source_id"] = key
# # License info
# licenseId = "CC BY 4.0"
# source_id[key]["license_info"] = {}
# source_id[key]["license_info"]["exceptions_contact"] = "@llnl.gov <- e3sm-data-support"
# source_id[key]["license_info"]["history"] = "" #"2022-xx-xx: initially published under CC BY 4.0"
# source_id[key]["license_info"]["id"] = licenseId
# licenseStr = license["license_options"][licenseId]["license_id"]
# licenseUrl = license["license_options"][licenseId]["license_url"]
# source_id[key]["license_info"]["license"] = "".join(
# [licenseStr, " (", licenseId, "; ", licenseUrl, ")"])
# source_id[key]["license_info"]["url"] = licenseUrl

# Rename
#source_id[key2] = source_id.pop(key1)
# Remove
# source_id.pop(key1)

'''
Apply a check on the length of source ids. Raise a RuntimeError if any are found.
'''
MAX_SOURCE_ID_LENGTH = 25
MAX_SOURCE_ID_MSG_TEMPLATE = 'Source id "{}" is {} characters long which is above the limit of {}'
# Check all source ids for length
long_source_ids = [i for i in source_id if len(i) > MAX_SOURCE_ID_LENGTH]
errors = [MAX_SOURCE_ID_MSG_TEMPLATE.format(
    i, len(i), MAX_SOURCE_ID_LENGTH) for i in long_source_ids]
# Raise exception if any found
if errors:
    raise RuntimeError('. '.join(errors))

del(long_source_ids, errors)

'''
Apply a check on the length of the source (generated in cmip6-cmor-tables/Tables/cmip6_CV.json)
Raise a runtime error if this string is >1024 characters
https://github.com/WCRP-CMIP/CMIP6_CVs/issues/1129
https://github.com/PCMDI/cmip6-cmor-tables/issues/377
'''
MAX_SOURCE_LENGTH = 1024
MAX_SOURCE_MSG_TEMPLATE = 'source "{}" is {} characters long, above the {} limit'
# Create concatenated string
test_source_ids = [i for i in source_id]
errors = []
for key in test_source_ids:
    source = source_id[key]["label"] + \
        " (" + source_id[key]["release_year"] + "): " + chr(10)
    for realm_test in source_id[key]["model_component"].keys():
        if (source_id[key]["model_component"][realm_test]["description"].find("None") == -1):
            source += realm_test + ': '
            source += source_id[key]["model_component"][realm_test]["description"] + \
                chr(10)
    source = source.rstrip()
    #print(key, len(source), MAX_SOURCE_LENGTH)
    if len(source) > MAX_SOURCE_LENGTH:
        errors.append([MAX_SOURCE_MSG_TEMPLATE.format(
            key, len(source), MAX_SOURCE_LENGTH)])
    # if key == "E3SM-2-0":
    #    print(len(source))
    #    print(source)
# Raise exception if any found
if errors:
    raise RuntimeError(errors)
# cleanup
del(source, key, test_source_ids, errors, realm_test)

'''
CMIP5 Descriptors were documented in http://pcmdi.github.io/projects/cmip5/CMIP5_output_metadata_requirements.pdf?id=76
Format defined following AR5 Table 9.A.1 http://www.climatechange2013.org/images/report/WG1AR5_Chapter09_FINAL.pdf#page=114
'''

# %% Source types
source_type = {
    'AER': 'aerosol treatment in an atmospheric model where concentrations are calculated based on emissions, transformation, and removal processes (rather than being prescribed or omitted entirely)',
    'AGCM': 'atmospheric general circulation model run with prescribed ocean surface conditions and usually a model of the land surface',
    'AOGCM': 'coupled atmosphere-ocean global climate model, additionally including explicit representation of at least the land and sea ice',
    'BGC': 'biogeochemistry model component that at the very least accounts for carbon reservoirs and fluxes in the atmosphere, terrestrial biosphere, and ocean',
    'CHEM': 'chemistry treatment in an atmospheric model that calculates atmospheric oxidant concentrations (including at least ozone), rather than prescribing them',
    'ISM': 'ice-sheet model that includes ice-flow',
    'LAND': 'land model run uncoupled from the atmosphere',
    'OGCM': 'ocean general circulation model run uncoupled from an AGCM but, usually including a sea-ice model',
    'RAD': 'radiation component of an atmospheric model run \'offline\'',
    'SLAB': 'slab-ocean used with an AGCM in representing the atmosphere-ocean coupled system'
}

# %% Sub experiment ids
sub_experiment_id = {}
sub_experiment_id['none'] = 'none'
sub_experiment_id['s1910'] = 'initialized near end of year 1910'
sub_experiment_id['s1920'] = 'initialized near end of year 1920'
sub_experiment_id['s1950'] = 'initialized near end of year 1950'
for yr in range(1960, 2030):
    sub_experiment_id[''.join(['s', str(yr)])] = ' '.join(
        ['initialized near end of year', str(yr)])
del(yr)

# %% Table ids
table_id = [
    '3hr',
    '6hrLev',
    '6hrPlev',
    '6hrPlevPt',
    'AERday',
    'AERhr',
    'AERmon',
    'AERmonZ',
    'Amon',
    'CF3hr',
    'CFday',
    'CFmon',
    'CFsubhr',
    'E1hr',
    'E1hrClimMon',
    'E3hr',
    'E3hrPt',
    'E6hrZ',
    'Eday',
    'EdayZ',
    'Efx',
    'Emon',
    'EmonZ',
    'Esubhr',
    'Eyr',
    'IfxAnt',
    'IfxGre',
    'ImonAnt',
    'ImonGre',
    'IyrAnt',
    'IyrGre',
    'LImon',
    'Lmon',
    'Oclim',
    'Oday',
    'Odec',
    'Ofx',
    'Omon',
    'Oyr',
    'SIday',
    'SImon',
    'day',
    'fx'
]

# %% Prepare experiment_id and source_id for comparison
for jsonName in ['experiment_id', 'source_id']:
    if jsonName in ['experiment_id', 'source_id']:
        dictToClean = eval(jsonName)
        # for key, value in dictToClean.iteritems(): # Py2
        for key, value in iter(dictToClean.items()):  # Py3
            # for values in value.iteritems(): # values is a tuple # Py2
            for values in iter(value.items()):  # values is a tuple # Py3
                # test for dictionary
                if type(values[1]) is list:
                    new = []
                    for count in range(0, len(values[1])):
                        string = values[1][count]
                        string = cleanString(string)  # Clean string
                        new += [string]
                    # print 'new',new
                    # new.sort() ; # Sort all lists - not experiment_id model components
                    # print 'sort',new
                    dictToClean[key][values[0]] = new
                elif type(values[1]) is dict:
                    # determine dict depth
                    pdepth = dictDepth(values[1])
                    keyInd = values[0]
                    keys1 = values[1].keys()
                    if pdepth == 1:
                        # deal with flat dict "rights"
                        for d1Key in keys1:
                            string = dictToClean[key][keyInd][d1Key]
                            string = cleanString(string)  # Clean string
                            dictToClean[key][keyInd][d1Key] = string
                    else:
                        # deal with nested dict "model_components"
                        for d1Key in keys1:
                            #print("d1Key:", d1Key)
                            keys2 = values[1][d1Key].keys()
                            for d2Key in keys2:
                                string = dictToClean[key][keyInd][d1Key][d2Key]
                                string = cleanString(string)  # Clean string
                                dictToClean[key][keyInd][d1Key][d2Key] = string
                elif type(values[0]) == str:  # Py3
                    string = dictToClean[key][values[0]]
                    string = cleanString(string)  # Clean string
                    dictToClean[key][values[0]] = string
        vars()[jsonName] = dictToClean
del(jsonName, dictToClean, key, value, values, new, count, string, pdepth, keyInd, keys1,
    d1Key, keys2, d2Key)

# %% Validate source_id and experiment_id entries
RFMIPOnlyList = [
    '4AOP-v1-5',
    'ARTS-2-3',
    'GFDL-GLOBAL-LBL',
    'GFDL-GRTCODE',
    'GFDL-RFM-DISORT',
    'LBLRTM-12-8',
    'RRTMG-LW-4-91',
    'RRTMG-SW-4-02',
    'RTE-RRTMGP-181204'
]

# source_id
for key in source_id.keys():
    # Validate source_id format
    if not entryCheck(key):
        print('Invalid source_id format for entry:', key, '- aborting')
        sys.exit()
    if len(key) > 16:
        if key == 'CESM1-1-CAM5-CMIP5':
            print(key, 'skipped checks - continue')
            break
        print('Invalid source_id format for entry (too many chars):',
              key, '- aborting')
        sys.exit()
    # Validate activity_participation/activity_id
    val = source_id[key]['activity_participation']
    # print key,val
    if 'CMIP' not in val:
        if key in RFMIPOnlyList:
            print(key, 'RFMIP only - continue')
        elif 'AerChemMIP' in val:  # Case AerChemMIP only - IPSL-CM6A-LR-INCA, IPSL-CM5A2-INCA
            print(key, 'AerChemMIP no CMIP required - continue')
        elif 'FAFMIP' in val:  # Case FAFMIP only - GFDL-ESM2M
            print(key, 'OMIP no CMIP required - continue')
        elif 'HighResMIP' in val:  # Case HighResMIP only
            print(key, 'HighResMIP no CMIP required - continue')
        elif 'ISMIP6' in val:  # Case ISMIP6 only
            print(key, 'ISMIP6 no CMIP required - continue')
        elif 'OMIP' in val:  # Case OMIP only
            print(key, 'OMIP no CMIP required - continue')
        elif 'PAMIP' in val:  # Case PAMIP only - CESM1-WACCM-sc
            print(key, 'PAMIP no CMIP required - continue')
        else:
            print('Invalid activity_participation for entry:',
                  key, 'no CMIP listed - aborting')
            sys.exit()
    for act in val:
        if act not in activity_id:
            print('Invalid activity_participation for entry:',
                  key, ':', act, '- aborting')
            sys.exit()
    # Validate institution_id
    vals = source_id[key]['institution_id']
    for val in vals:
        if val not in institution_id:
            print('Invalid institution_id for entry:',
                  key, ';', val, '- aborting')
            sys.exit()
        if len(val) > 21:
            print(
                'Invalid institution_id format for entry (too many chars):', key, '- aborting')
            sys.exit()
    # Validate nominal resolution
    vals = source_id[key]['model_component'].keys()
    for val1 in vals:
        val2 = source_id[key]['model_component'][val1]['native_nominal_resolution']
        if val2 == 'none':
            pass
        elif val2 not in nominal_resolution:
            print('Invalid native_nominal_resolution for entry:',
                  key, val1, val2, '- aborting')
            sys.exit()
    # Validate source_id
    val = source_id[key]['source_id']
    if key != val:
        print('Invalid source_id for entry:',
              val, 'not equal', key, '- aborting')
        sys.exit()
# experiment_ids
experiment_id_keys = experiment_id.keys()
for key in experiment_id_keys:
    # Validate source_id format
    if not entryCheck(key):
        print('Invalid experiment_id format for entry:', key, '- aborting')
        sys.exit()
    # Validate internal key
    val = experiment_id[key]['experiment_id']
    if not val == key:
        print('Invalid experiment_id for entry:', key, '- aborting')
        sys.exit()
    # Validate activity_id
    val = experiment_id[key]['activity_id']
    for act in val:
        if act not in activity_id:
            print('Invalid activity_participation for entry:',
                  key, act, '- aborting')
            sys.exit()
    # Validate additional_allowed_model_components
    vals = experiment_id[key]['additional_allowed_model_components']
    for val in vals:
        if val == '':
            pass
        elif val not in source_type:
            print('Invalid additional_allowed_model_components for entry:',
                  key, val, '- aborting')
            sys.exit()
    # Validate required_model_components
    vals = experiment_id[key]['required_model_components']
    for val in vals:
        if val not in source_type:
            print('Invalid required_model_components for entry:',
                  key, val, '- aborting')
            sys.exit()
    # Validate parent_activity_id
    vals = experiment_id[key]['parent_activity_id']
    for val in vals:
        if val == 'no parent':
            pass
        elif val not in activity_id:
            print('Invalid parent_activity_id for entry:', key, val, '- aborting')
            sys.exit()
    # Validate parent_experiment_id
    vals = experiment_id[key]['parent_experiment_id']
    for val in vals:
        if val == 'no parent':
            pass
        elif val not in experiment_id_keys:
            print('Invalid experiment_id_keys for entry:', key, val, '- aborting')
            sys.exit()

'''
    # Validate start/end years
    excludeList = [
            'aqua-p4K',
            'dcppA-assim', # start = before 1961
            'dcppA-hindcast',
            'dcppA-hindcast-niff',
            'dcppA-historical-niff',
            'dcppB-forecast',
            'dcppC-amv-neg',
            'dcppC-atl-pacemaker',
            'dcppC-atl-spg',
            'dcppC-forecast-addAgung',
            'dcppC-forecast-addElChichon',
            'dcppC-forecast-addPinatubo',
            'dcppC-hindcast-noAgung',
            'dcppC-hindcast-noElChichon',
            'dcppC-hindcast-noPinatubo',
            'dcppC-ipv-pos',
            'dcppC-ipv-NexTrop-pos',
            'dcppC-pac-control',
            'dcppC-pac-pacemaker',
            'esm-bell-1000PgC',
            'esm-bell-2000PgC',
            'esm-hist-ext', # end_year = present
            'faf-all',
            'futSST-pdSIC',
            'G6SST1', # Should be 2020 start
            'historical-ext', # end_year present
            'ism-1pctCO2to4x-self',
            'ism-piControl-self',
            'modelSST-futArcSIC',
            'modelSST-pdSIC',
            'pa-futAntSIC', # PAMIP start/end 2000/2001 should be min_num 2 not 1
            'pa-futArcSIC',
            'pa-pdSIC',
            'pa-piArcSIC',
            'pa-piAntSIC',
            'pdSST-futAntSIC',
            'pdSST-futArcSIC',
            'pdSST-futArcSICSIT',
            'pdSST-futBKSeasSIC',
            'pdSST-futOkhotskSIC',
            'pdSST-pdSIC',
            'pdSST-pdSICSIT',
            'pdSST-piAntSIC',
            'pdSST-piArcSIC',
            'piClim-2xDMS',
            'piClim-NH3',
            'piSST-4xCO2',
            'piSST-4xCO2-solar',
            'piSST-pdSIC',
            'piSST-piSIC'
            ]
'''
'''     LUMIP
            'land-cClim', # start_year 1850 or 1700
            'land-cCO2',
            'land-crop-grass',
            'land-crop-noFert',
            'land-crop-noIrrig',
            'land-crop-noIrrigFert',
            'land-hist',
            'land-hist-altLu1',
            'land-hist-altLu2',
            'land-hist-altStartYear',
            'land-noFire',
            'land-noLu',
            'land-noPasture',
            'land-noShiftCultivate',
            'land-noWoodHarv',
        Not sure
            'piControl-spinup-cmip5',
        No values in 3 fields
            'rad-irf'
'''
'''
    if key in excludeList:
        print('Skipping start/end_year test for:',key)
        continue
    #print('Start/end_year test for',key)
    valStart = experiment_id[key]['start_year']
    valEnd = experiment_id[key]['end_year']
    minNumYrsSim = experiment_id[key]['min_number_yrs_per_sim']
    if valStart == '' and valEnd == '':
        print('Start/end_year blank, skipping for:',key)
        continue
    # Deal with all LUMIP simulations
    if valStart == '1850 or 1700':
        valStart = 1850
        #print('land-* experiment identified, continuing')
    elif valStart: # Falsy test https://stackoverflow.com/questions/9573244/how-to-check-if-the-string-is-empty
        valStart = int(valStart)
    # Deal with all sspxxx simulations
    if valEnd == '2100 or 2300':
        valEnd = 2100
        #print('sspxxx experiment, skipping')
    elif valEnd:
        valEnd = int(valEnd)
    if minNumYrsSim:
        minNumYrsSim = int(minNumYrsSim)
    if valStart and valEnd and minNumYrsSim:
        pass
    else:
        print('Test values failed')
        print('start_year:',valStart,'end_year:',valEnd,'min_number_yrs_per_sim:',minNumYrsSim)
        sys.exit()
    #print('valStart:',valStart,type(valStart))
    #print('valEnd:',valEnd,type(valEnd))
    test = (int(valEnd)+1)-int(valStart)
    if int(minNumYrsSim) != test:
        print('Invalid start/end_year pair for entry:',key,'- aborting')
        print('start_year:',valStart,'end_year:',valEnd)
        print('min_number_yrs_per_sim:',test,minNumYrsSim)
        sys.exit()

del(experiment_id_keys,key,act,val,val1,val2,vals,valStart,valEnd,minNumYrsSim,test)
'''

del(experiment_id_keys, key, act, val, val1, val2, vals)
'''
print('***FINISH***')
sys.exit() ; # Turn back on to catch errors prior to running commit
'''

# %% Load remote repo versions for comparison - generate version identifier
for jsonName in masterTargets:
    target = ''.join(['test', jsonName])
    testVal = ''.join(['testVal_', jsonName])
    if jsonName == 'mip_era':
        url = ''.join(
            ['https://raw.githubusercontent.com/WCRP-CMIP/CMIP6_CVs/master/', jsonName, '.json'])
    else:
        url = ''.join(
            ['https://raw.githubusercontent.com/WCRP-CMIP/CMIP6_CVs/master/CMIP6_', jsonName, '.json'])
    # composite components
    tmp = [[jsonName, url]]
    print("url:", url)
    # Create input list and load from web
    # force add DRS to repo
    # if jsonName == "DRS":
    #    testVal_DRS = {}
    #    testDRS = {}
    # continue with existing entries
    # else:
    vars()[target] = readJsonCreateDict(tmp)
    vars()[target] = eval(target).get(jsonName)
    # Fudge to extract duplicate level
    vars()[target] = eval(target).get(jsonName)
    # Test for updates
    # print(eval(target))
    # print(eval(jsonName))
    # print('---')
    # print(platform.python_version())
    # print(platform.python_version().split('.')[0])
    if platform.python_version().split('.')[0] == '3':
        vars()[testVal] = not(eval(target) == eval(jsonName))  # Py3
        # print(platform.python_version())
    #print(not(eval(target) == eval(jsonName)))
    # print('---')
    del(vars()[target], target, testVal, url, tmp)
del(jsonName)
# Use binary test output to generate
versionId = ascertainVersion(testVal_activity_id, testVal_DRS,
                             testVal_experiment_id, testVal_frequency, testVal_grid_label,
                             testVal_institution_id, testVal_license,
                             testVal_mip_era, testVal_nominal_resolution,
                             testVal_realm, testVal_required_global_attributes,
                             testVal_source_id, testVal_source_type,
                             testVal_sub_experiment_id, testVal_table_id,
                             commitMessage)
versionHistory = versionId[0]
versionId = versionId[1]
print('Version:', versionId)
# sys.exit() ; # Use to evaluate changes

# %% Validate UTF-8 encoding - catch omip2 error https://github.com/WCRP-CMIP/CMIP6_CVs/issues/726
for jsonName in masterTargets:
    testDict = eval(jsonName)
    # print(jsonName,type(testDict))
    try:
        if platform.python_version().split('.')[0] == '2':
            if type(testDict) is list:
                #print('enter list')
                ''.join(testDict).decode('utf-8')
            else:
                for key1, val1 in testDict.items():
                    #print('type key1:',type(key1))
                    key1.decode('utf-8')
                    if type(val1) is dict:
                        for key2, val2 in val1.items():
                            key2.decode('utf-8')
                            if type(val2) is list:
                                # Deal with list types
                                ''.join(val2).decode('utf-8')
                            elif type(val2) is dict:
                                for key3, val3 in val2.items():
                                    if type(val3) is list:
                                        # Deal with list types
                                        ''.join(val3).decode('utf-8')
                                    elif type(val3) is dict:
                                        for key4, val4 in val3.items():
                                            val4.decode('utf-8')
                                    else:
                                        val3.decode('utf-8')
                            else:
                                val2.decode('utf-8')
                    else:
                        val1.decode('utf-8')
        elif platform.python_version().split('.')[0] == '3':
            if type(testDict) is list:
                #print('enter list')
                ''.join(testDict).encode('utf-8')
            else:
                for key1, val1 in testDict.items():
                    #print('type key1:',type(key1))
                    key1.encode('utf-8')
                    if type(val1) is dict:
                        for key2, val2 in val1.items():
                            key2.encode('utf-8')
                            if type(val2) is list:
                                # Deal with list types
                                ''.join(val2).encode('utf-8')
                            elif type(val2) is dict:
                                for key3, val3 in val2.items():
                                    if type(val3) is list:
                                        # Deal with list types
                                        ''.join(val3).encode('utf-8')
                                    elif type(val3) is dict:
                                        for key4, val4 in val3.items():
                                            val4.encode('utf-8')
                                    else:
                                        val3.encode('utf-8')
                            else:
                                val2.encode('utf-8')
                    else:
                        val1.encode('utf-8')
    except UnicodeEncodeError:
        # If left as UnicodeDecodeError - prints traceback
        print('UTF-8 failure for:', jsonName, 'exiting')
        sys.exit()

# %% Write variables to files
timeNow = datetime.datetime.now().strftime('%c')
offset = (calendar.timegm(time.localtime()) -
          calendar.timegm(time.gmtime()))/60/60  # Convert seconds to hrs
# offset = ''.join(['{:03d}'.format(offset),'00']) # Pad with 00 minutes # Py2
offset = ''.join(['{:03d}'.format(int(offset)), '00']
                 )  # Pad with 00 minutes # Py3
timeStamp = ''.join([timeNow, ' ', offset])
del(timeNow, offset)

for jsonName in masterTargets:
    # Write file
    if jsonName == 'mip_era':
        outFile = ''.join(['../', jsonName, '.json'])
    else:
        outFile = ''.join(['../CMIP6_', jsonName, '.json'])
    # Get repo version/metadata - from src/writeJson.py

    # Extract last recorded commit for src/writeJson.py
    # print(os.path.realpath(__file__))
    versionInfo1 = getFileHistory(os.path.realpath(__file__))
    versionInfo = {}
    versionInfo['author'] = author
    versionInfo['institution_id'] = author_institution_id
    versionInfo['CV_collection_modified'] = timeStamp
    versionInfo['CV_collection_version'] = versionId

    # force DRS addition
    # if jsonName == "DRS":
    #     versionInfo['_'.join([jsonName, 'CV_modified'])
    #                 ] = timeStamp
    #     versionInfo['_'.join([jsonName, 'CV_note'])
    #                 ] = commitMessage
    # else:
    versionInfo['_'.join([jsonName, 'CV_modified'])
                ] = versionHistory[jsonName]['timeStamp']
    versionInfo['_'.join([jsonName, 'CV_note'])
                ] = versionHistory[jsonName]['commitMessage']

    versionInfo['previous_commit'] = versionInfo1.get('previous_commit')
    versionInfo['specs_doc'] = 'v6.2.7 (10th September 2018; https://goo.gl/v1drZl)'
    del(versionInfo1)

    # Check file exists
    if os.path.exists(outFile):
        print('File existing, purging:', outFile)
        os.remove(outFile)
    # Create host dictionary
    jsonDict = {}
    jsonDict[jsonName] = eval(jsonName)
    # Append repo version/metadata
    jsonDict['version_metadata'] = versionInfo
    fH = open(outFile, 'w')
    if platform.python_version().split('.')[0] == '2':
        json.dump(
            jsonDict,
            fH,
            ensure_ascii=True,
            sort_keys=True,
            indent=4,
            separators=(
                ',',
                ':'),
            encoding="utf-8")
    elif platform.python_version().split('.')[0] == '3':
        json.dump(
            jsonDict,
            fH,
            ensure_ascii=True,
            sort_keys=True,
            indent=4,
            separators=(
                ',',
                ':'))
    fH.close()

# Cleanup
del(jsonName, jsonDict, outFile)
del(activity_id, DRS, experiment_id, frequency, grid_label, institution_id, license,
    masterTargets, mip_era, nominal_resolution, realm, required_global_attributes,
    source_id, source_type, sub_experiment_id, table_id)
gc.collect()

# %% Update version info from new file/commit history
# Extract fresh recorded commit for src/writeJson.py
versionInfo1 = getFileHistory(os.path.realpath(__file__))
MD5 = versionInfo1.get('previous_commit')
# Now update versionHistory - can use list entries, as var names aren't locatable
if testVal_activity_id:
    key = 'activity_id'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_DRS:
    key = 'DRS'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_experiment_id:
    key = 'experiment_id'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_frequency:
    key = 'frequency'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_grid_label:
    key = 'grid_label'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_license:
    key = 'license'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_mip_era:
    key = 'mip_era'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_nominal_resolution:
    key = 'nominal_resolution'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_realm:
    key = 'realm'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_required_global_attributes:
    key = 'required_global_attributes'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_source_type:
    key = 'source_type'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_sub_experiment_id:
    key = 'sub_experiment_id'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_table_id:
    key = 'table_id'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_institution_id:
    key = 'institution_id'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
if testVal_source_id:
    key = 'source_id'
    versionHistoryUpdate(key, commitMessage, timeStamp, MD5, versionHistory)
# Test for changes and report
test = [testVal_activity_id, testVal_DRS, testVal_experiment_id, testVal_frequency,
        testVal_grid_label, testVal_license, testVal_mip_era,
        testVal_nominal_resolution, testVal_realm,
        testVal_required_global_attributes, testVal_source_type,
        testVal_sub_experiment_id, testVal_table_id, testVal_institution_id,
        testVal_source_id]
if any(test):
    # Create host dictionary
    jsonDict = {}
    jsonDict['versionHistory'] = versionHistory
    outFile = 'versionHistory.json'
    if os.path.exists(outFile):
        os.remove(outFile)
    fH = open(outFile, 'w')
    if platform.python_version().split('.')[0] == '2':
        json.dump(
            jsonDict,
            fH,
            ensure_ascii=True,
            sort_keys=True,
            indent=4,
            separators=(
                ',',
                ':'),
            encoding="utf-8")
    elif platform.python_version().split('.')[0] == '3':
        json.dump(
            jsonDict,
            fH,
            ensure_ascii=True,
            sort_keys=True,
            indent=4,
            separators=(
                ',',
                ':'))
    fH.close()
    print('versionHistory.json updated')
# Cleanup anyway
del(testVal_activity_id, testVal_DRS, testVal_experiment_id, testVal_frequency, testVal_grid_label,
    testVal_institution_id, testVal_license, testVal_mip_era, testVal_nominal_resolution,
    testVal_realm, testVal_required_global_attributes, testVal_source_id,
    testVal_source_type, testVal_sub_experiment_id, testVal_table_id)

# %% Generate revised html - process experiment_id, institution_id and source_id (alpha order)
# json_to_html.py ../CMIP6_experiment_id.json experiment_id CMIP6_experiment_id.html
args = shlex.split(''.join(['python ./jsonToHtml.py ', versionId]))
# print(args)
p = subprocess.Popen(args, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, cwd='./')
stdOut, stdErr = p.communicate()
print('Returncode:', p.returncode)  # If not 0 there was an issue
print('stdOut:', stdOut)
print('stdErr:', stdErr)
# if 'Traceback' in stdErr: # Py2
if b'Traceback' in stdErr:  # Py3
    print('json_to_html failure:')
    print('Exiting..')
    sys.exit()
del(args, p)
gc.collect()

# %% Now all file changes are complete, update README.md, commit and tag
# Load master history direct from repo
tmp = [['versionHistory', 'https://raw.githubusercontent.com/WCRP-CMIP/CMIP6_CVs/master/src/versionHistory.json']
       ]
versionHistory = readJsonCreateDict(tmp)
versionHistory = versionHistory.get('versionHistory')
# Fudge to extract duplicate level
versionHistory = versionHistory.get('versionHistory')
del(tmp)
# Test for version change and push tag
versions = versionHistory['versions']
versionOld = '.'.join([str(versions['versionMIPEra']), str(versions['versionCVStructure']),
                       str(versions['versionCVContent']), str(versions['versionCVCommit'])])
del(versionHistory)

if versionId != versionOld:
    # %% Now update Readme.md
    target_url = 'https://raw.githubusercontent.com/WCRP-CMIP/CMIP6_CVs/master/README.md'
    # txt = urllib.urlopen(target_url).read() # Py2
    txt = urlopen(target_url).read().decode('utf-8')  # Py3
    txt = txt.replace(versionOld, versionId)
    # Now delete existing file and write back to repo
    readmeH = '../README.md'
    os.remove(readmeH)
    fH = open(readmeH, 'w')
    fH.write(txt)
    fH.close()
    print('README.md updated')
    del(target_url, txt, readmeH, fH)

# Commit all changes

args = shlex.split(''.join(['git commit -am ', commitMessage]))
print(args)
p = subprocess.Popen(args, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, cwd='./')

'''
# Merging branches changes the checksum, so the below doesn't work, UNLESS it's a direct master push
if versionId != versionOld:
    # Generate composite command and execute
    cmd = ''.join(['git ','tag ','-a ',versionId,' -m',commitMessage])
    print cmd
    subprocess.call(cmd,shell=True) ; # Shell=True required for string
    # And push all new tags to remote
    subprocess.call(['git','push','--tags'])
    print 'tag created and pushed'
'''
