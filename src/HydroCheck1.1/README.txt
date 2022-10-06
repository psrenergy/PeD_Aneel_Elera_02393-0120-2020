This file contains a brief explanation on how to run the HydroCheck module. 

-> Files to provide - Files should be saved the folder "Files"
"input.csv"  -> Contains general inputs for running the module.
	"nb_stages" : 12 when monthly based; 52 when weekly based.
	"path" : Path to folder containing files needed to run the module.
	"rerun" : Flag informing whether R script "HydroCheck.R" for generating analysis should be run. If the analysis was already performed,
	"HydroCheck.RData" is generated. Setting rerun = 0 will simply load the latest generated "HydroCheck.RData".(1-rerun,0-no rerun). 
	When rerunning the analysis, the field rerun is automatically set to 0. Therefore, the file "input.csv" should not be left open. 
"hinflw.dat"-> Contains historical inflows for all stations.
"chidro.csv" -> Contains general information about each plant. Chidro files for all systems should be included.
"htopol.dat" -> Contains information about cascades. Needed to build incremental inflows.
"sistem.dat" -> Contains the systems defined in the SDDP base.
"estima.dat" -> Contains information about the parameter estimation, namely the "Min. Year for estimation" and "Max. Year for estimation" 

The R Console is written in a text file with random name to avoid name colision. You can identify the last run of the module by sorting by Date modified.
Open the file in your text editor in case of problems when trying to run the module. Files can be deribelately deleted. 
It will eventually be necessary to "manually" close the port (by default 8888) by witting in the Command Prompt:
	netstat -ano | findstr :8888
This will inform the PID being used by the module. To kill the task, please copy the PID and write in the Command Prompt:
	taskkill /PID <typeyourPIDhere> /F
	
Sometimes Google Chrome Portable may find problems when closing. In this case, it is suggested to End Task "Google Chrome Portable" in the Task Manager.


