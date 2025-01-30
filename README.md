# rac
work-in-progress tool to compute (approximately) optimal housing assignments in new vassar.

## input files

**please note that all confidential info should be put in the `data/confidential` directory.** (do not commit confidential information into this public repo lol, `data/confidential` is in the gitignore)

on the house sheet, data from the housing intent forms are spread over multiple tabs: all the frosh are in one special tab, and building switches/supplemental requests are in a special tab, for instance. these *must* be combined into one csv `data/confidential/housing_intent.csv`
this is for two reasons:
- the different tabs have slightly different formatting sometimes (extra columns, typos in section headers, etc.). we will require the csv headers to be formatted [exactly like it currently is]
- there will exist duplicates, e.g. if someone fills in the housing intent form, goes to NV, and then fills in a supplemental request. it is not only rather hard, but also imprudent, to try and combine these duplicates automatically. someone should resolve such duplicates manually; to help you do this, the code will throw an error if it finds duplicated kerbs in `housing_intent.csv` so that you can throw everything together and then weed out the detected duplicates

`data/government_points.json` are extra housing points (per semester) granted for various house gov positions, per the NV constitution (or bylaws or whatever). `data/government_positions.json` tracks kerbs of people in roles.
<!-- TODO: the data for government positions is compiled by me, by looking at my email history. it probably contains mistakes. idk who was in house gov prior to 2023 or wtv -->

house sheet MUST have all the beds listed (even if some are empty). sorting is not required.

## usage

also note that non-frosh are assigned around march/april (after whenever HRS finalizes building placements), but frosh are assigned much later than this. so we actually have to support "read a bunch of existing assignments from the house sheet and then fill in everybody else".

<!-- TODO - under this scheme it will probably be a little annoying if a non-frosh wants to live in a double with a frosh. I do not expect this is really something that happens but can think of cases where this exists. At least one should come up with a reasonable scheme, even if somewhat hard-coded, to input such a request.
UPDATE - looks like this can probably be done by making a "temp" person for the frosh during the non-frosh assignment round, then just editing in the frosh manually before assigning the rest of the frosh. so when you assign the frosh, you do it on top of the file loaded with all the non-frosh assignments + this one frosh-->


## algorithm

### parameters

### heuristic-selection component

### min-cost-flow compoment
