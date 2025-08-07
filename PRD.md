
APP MUST BE IN FRENCH 
# BGU-ONE Data Center Monitoring Dashboard - Product Requirements Document (PRD)

## 1. Product Overview

### 1.1 Product Vision
The BGU-ONE Data Center Monitoring Dashboard is a comprehensive web-based analytics platform designed to provide real-time monitoring, analysis, and optimization insights for data center operations. The system transforms raw operational data into actionable intelligence through advanced visualization, statistical analysis, and predictive modeling, with special focus on IT power consumption analysis and CLIM system efficiency.

### 1.2 Product Mission
To enable data center operators to maximize operational efficiency, minimize downtime, and optimize energy consumption through data-driven insights and proactive monitoring of critical infrastructure systems. Detect anomalies that raises energy consumption of the pop and the product must display those anomalies through charts and clear structured reporting system. Also at the end product must enhance AI to prevent this energy over-consumption by optimizing IT power usage separate from HVAC consumption.

##initial dashbording reporting requirements
—go have a look on how data is it in /data folder. 
1- Main time series analysis where we can select DATA we want to display and time range and then display selected data how it change over time. try to play with colors so that even if we mix everything we can have visibilite. for example if the thing that is in. histogram should be in color that we can look through so we can see courbe that are below that ( superpose mais on peiut voir les deux).  be smart xo we can see things good. make it interactive that we can move through it like as if its a shopify sahbording or trading view. its user friendly and big enough to easy see. i want this app to be user firendly and easy to manipulate.
DATA SELECTION : CLIMS STATUS FOR EACH ONE, TEMP INDOOR OUTDOOR, PUISSANCE IT( PUISSANCE GENERAL - ACTIVE ) , PUISSANCE ACTIVE GENERAL, PUISSANCE ACTIVE CLIM, DOOR ACCESS.
 
2-  Display all graphs on EDA.ipynb

3- -graph that shows how temp change 5 min after each clim is OFF ( how temperature has changed since 5 min from the moment when clim was turned off ) this graph ( or whatever it called) should be displayed showing data points, each data point has a color that represent a clim and each data point contain which CLIM , and how temp changed, then below this graph a table summary for each clim for any important data that we should know from all datapoints like min temp change avg, …… get smart with it. ( temp interieure that is in question)
4- graph that shows how temp changed after door closed LIKE GRAPH BELOW AS DATA POINTS BUT HERE AT EACH EVENT OF DOOR CLOSE WE CALCULATE HOW TEMP INTERIEUR CHANGED SINCE MOMENT WE OPENED DOOR UNTIL THE EVENT OF DOOR CLOSED. then below a table of summary

5- a correlation matrix between IT puissance, puissance clim, temp intereure, temp exterieur and a summary texy below it  based on those correlation if there is a way 

IMPORTANT
6- As far as DATA CLEANING IS CONCERNED YOU ARE ASKED TO: 

  1. Trend Flags Column Removal - Automatically detects and drops 'Trend Flags' columns from all CSV files
  2. Status Filtering - Removes all rows where Status ≠ '{ok}' (case-insensitive matching)
  3. Date Validation - Drops rows with missing or invalid dates
  4. Data Standardization - Converts CLIM status (ON/OFF→1/0) and door status (Ouverte/Fermé→1/0)

   handles encoding issues and date parsing with timezone support ( est west, ... )