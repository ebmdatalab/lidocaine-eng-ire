*** Set directory ****
*cd "XXXXX"

/*SET-UP*/
import delimited "https://raw.githubusercontent.com/ebmdatalab/lidocaine-eng-ire/master/data/list_size.csv", clear

rename month date_string
gen date=date(date_string,"YMD#####")
format date %td
gen month=month(date)
gen year=year(date)
gen month_year=ym(year, month)
format month_year %tm

display tm(2017m8)

drop if month_year<684
egen tag_pct=tag(pct)
keep if tag==1


save list_size.dta, replace

import delimited "https://raw.githubusercontent.com/ebmdatalab/lidocaine-eng-ire/master/data/lidocaine.csv", clear

rename month date_string
gen date=date(date_string,"YMD#####")
format date %td
gen month=month(date)
gen year=year(date)
gen month_year=ym(year, month)
format month_year %tm

merge m:1 pct using list_size.dta, force

drop if _merge==2

save nhs_merged.dta, replace


*** Analysis of merged data ***

use nhs_merged.dta, clear

collapse (sum) quantity_of_plasters rx_items actual_cost net_cost list_size, by(month_year year pct)
gen rate_quantity = quantity_of_plasters / list_size *1000
gen rate_items = rx_items / list_size *1000
display tm(2017m8)
gen intervention = .
replace intervention = 0 if month_year <=690
replace intervention = 1 if month_year >690

display tm(2019m12)
drop if month_year>719

egen total_quantity=total( quantity_of_plasters ), by(year)
tabdisp year, c( total_quantity)
egen total_items=total( rx_items ), by(year)
tabdisp year, c( total_items)
egen total_actualcost=total( actual_cost ), by(year)
format %20.0g total_actualcost
tabdisp year, c( total_actualcost)

encode pct, gen(PCT)
tsset PCT month_year, monthly

capture: ssc install xtitsa

xtitsa rate_quantity, single trperiod(2017m8) replace posttr figure
xtitsa rate_items, single trperiod(2017m8) replace posttr figure