rm(list = ls())
library(lattice)
library(crayon)
library(dplyr)
library(stats)
library(pracma)
library(plotly)
library(shinythemes)
library(shiny)
library(urca)
# library(stringr)


source("dictLoader.R")
dicTranslateCurrent <- dicTranslateCurrent

#--------------------------------------------------------------------------------------------------
# Function definitions
#--------------------------------------------------------------------------------------------------
naturalToIncremental_Flow <- function(hidro_hist, hinflow_dat, htopol, PV_info)
{
  for (i in 1:length(htopol[,2])) 
  {
    # index_PV <- i
    PV_num <- htopol[i,2]
    index_PV <- grep(paste("^",PV_num,"$",sep = ""),colnames(hinflow_dat)[3:length(colnames(hinflow_dat))])
    
    PV_incremented <- htopol[i,4]
    if (PV_incremented != 0 && PV_incremented != "0*")
    {
      index_name_incremented <- grep(paste("^",PV_incremented,"$",sep = ""),colnames(hinflow_dat)[3:length(colnames(hinflow_dat))])
      hidro_hist[[index_name_incremented]] <- hidro_hist[[index_name_incremented]] - hinflow_list[[index_PV]]
    }
  }
  
  return(hidro_hist)
}

calculate_CV <- function(data)
{
  CV = sd(data, na.rm = TRUE)/mean(data, na.rm = TRUE)
  return(CV)
}

mean_noNA <- function(data)
{
  mean_noNA = mean(data,na.rm = TRUE) 
}

calculate_KPSS_constant <- function(hidro_hist)
{
  x = ur.kpss(as.vector(t(hidro_hist)),type = "mu")
  return(x)
}

# calculate_KPSS_linear <- function(hidro_hist)
# {
#   x = ur.kpss(as.vector(t(hidro_hist)),type = "tau")
#   return(x)
# }

get_testValue <- function(KPSS_test)
{
  return(KPSS_test@teststat)
}

calculate_Delta <- function(hidro_hist)
{
  means = c()
  for (i in 1:2)
  {
    means[i] = mean(hidro_hist[((i-1)*(length(hidro_hist)%/%2)+1):(i*(length(hidro_hist)%/%2))],na.rm = T)
  }
  delta = (means[2]/means[1]-1)
  return(delta)
}

apply_years_estima <- function(hidro_hist, min_year_estim, max_year_estim, years_hist)
{
  pos_min = which(years_hist == min_year_estim)
  if (length(pos_min) == 0)
    pos_min = 1
  pos_max = which(years_hist == max_year_estim)
  if (length(pos_max) == 0)
    pos_min = nrow(hidro_hist)
  hidro_hist_estima = hidro_hist[pos_min:pos_max,]
}

#--------------------------------------------------------------------------------------------------
# Load files
#--------------------------------------------------------------------------------------------------
cat("----------------- metrics_generation File ---------------------\n")
cat("----------------- Loading input Files ---------------------\n")

path_files = commandArgs(trailingOnly = TRUE)
check_path = paste(path_files,"hydrocheck.ok", sep = "/")
if( file.exists(check_path) )
{
  file.remove(check_path)
}

# Load SDDP files
estima  <- read.delim(file = paste(path_files,"estima.dat", sep = "/"), sep = ":", header = F)
sddp    <- read.delim(file = paste(path_files,"sddp.dat",   sep = "/"), sep = "", header = F)
htopol  <-   read.fwf(file = paste(path_files,"htopol.dat", sep = "/"), c(5,15,21,14,6), strip.white = T)
systems <- read.delim(file = paste(path_files,"sistem.dat", sep = "/"), sep = "", header = T, colClasses = c(rep("factor",4)))

# Load CHIDRO files
chidro_all = c()
for (i in 1:nrow(systems))
{
  fname = paste(path_files,paste("chidro",systems$ID[i],".dat", sep = ""), sep = "/")
  if( file.exists(fname) )
  {
    chidro_ID <- read.fwf(file = fname, c(4,14,4,5,5,5,5,8), header=F ,strip.white = T,fill=TRUE)
    
    chidro_ID = chidro_ID[2:nrow(chidro_ID),]
    chidro_ID$new_col <- rep(systems$NOME[i],nrow(chidro_ID))
    
    chidro_all = rbind(chidro_all,chidro_ID)
  }
}
names(chidro_all) = c("NUM","NAME","PV","VAA","TAA","UNIT","TYPE","Pot","Subsistema")

# Load HINFLOW
nb_plants <- length(unique(htopol[,3]))
col_pos_hinf = rep(7,nb_plants+1)
hinflow_dat <- read.fwf(file = paste(path_files,"hinflw.dat", sep = "/"), col_pos_hinf, strip.white = F, header = F)
header_hinf = hinflow_dat[1,]
names(hinflow_dat) = header_hinf
hinflow_dat = hinflow_dat[2:nrow(hinflow_dat),]
names(hinflow_dat)[1] = "Date" 
df_date = data.frame(matrix(unlist(strsplit(as.character(hinflow_dat[,1]),"/")),ncol = 2, byrow = T))
df_date[,1] = as.vector(df_date[,1])
df_date[,2] = as.vector(df_date[,2])
names(df_date) = c("Stag","Year")
hinflow_dat = data.frame(df_date,hinflow_dat[,2:ncol(hinflow_dat)], check.names = F)
nums_PV <- names(hinflow_dat)[-1:-2]

#Create dataframe with pv, subsystem and power
df1 = data.frame(nums_PV)
df2 = data.frame(chidro_all)
df = unique(merge(x = df1, y = df2[ , c(3,8,9)], by.x=names(df1), by.y=names(df2)[3],all.x = TRUE, sort=F))

#--------------------------------------------------------------------------------------------------
# Build data structure
# -------------------------------------------------------------------------------------------------
hbasin_path = paste(path_files,"hbasin.dat", sep = "/")
if( file.exists(hbasin_path) )
{
  hbasin  <- read.delim(file = hbasin_path, sep = ",", header = T, skip = 1)
  PV_basin_name = c()
  hydro_basin_name = c()
  
  hbasin_index = match(htopol[,5],hbasin[,1])			# Relates gauging station to its basin
  PV_basin_name = hbasin[hbasin_index,2] 				# Names of the basins ordered as htopol
  PV_basin_name = replace(as.character(PV_basin_name),is.na(PV_basin_name), as.character(dicTranslateCurrent['OTHER']))
  
  htopol_index = match(chidro_all[,3],htopol[,2]) 		# Relates hydro to gauging station
  hbasin_index = match(htopol[htopol_index,5],hbasin[,1]) # And then to its basin
  hydro_basin_name = hbasin[hbasin_index,2] 				# Names of the basins ordered as chidro_all
  hydro_basin_name = replace(as.character(hydro_basin_name),is.na(hydro_basin_name), as.character(dicTranslateCurrent['OTHER']))
}else
{
  PV_basin_name = rep("No basin data",length(htopol[,1]))
}

#--------------------------------------------------------------------------------------------------
# Parameters
# -------------------------------------------------------------------------------------------------
if(sddp[5,2]==1)
{
  nb_stages = 52
  cv_title = dicTranslateCurrent["CVSTAGE_WEEK"]
  cv_axis = dicTranslateCurrent["WEEK"]
}else
{
  nb_stages = 12
  cv_title = dicTranslateCurrent["CVSTAGE_MONTH"]
  cv_axis = dicTranslateCurrent["MONTH"]
}

min_year_estim = estima$V2[6]
max_year_estim = estima$V2[7]

years_hist  <- as.numeric(unique(hinflow_dat[,2]))
years_hist_estim = years_hist[(years_hist <= max_year_estim)]
years_hist_estim = years_hist_estim[(years_hist_estim >= min_year_estim)]
nb_years_hist <-length(years_hist)
nb_years_hist_estim = length(years_hist_estim)
inflows <- list()
names <- as.vector(htopol[,3])
usines <- names
nb_hidros <- nrow(names)
PV_info <- list()
hidro_hist <- list()
hist_index = c()
hinflow_list <- list()


# Replace -99 for NA
for (i in 1:(nb_plants))
{
  hidro_hist[[i]] <- matrix(pull(hinflow_dat,c(i+2)),nrow = nb_years_hist, ncol = nb_stages, byrow = T)
  hidro_hist[[i]] <- replace(hidro_hist[[i]],hidro_hist[[i]]==-99,NA)
  hinflow_list[[i]] <- hidro_hist[[i]]
  hist_index[i] = i # Depending on the tests results, some posts will be eliminated, so it is necessary to keep track of the hidro history index
}

PV_names <- c()
for (i in 1:(nb_plants))
{
  index_PV_name = grep(paste("^",colnames(hinflow_dat)[3:length(colnames(hinflow_dat))][i],"$",sep = ""),as.vector(htopol[,2]))
  PV_names[i] = names[index_PV_name]
}

##### Calculate CVs and means of all types ####
# Calculate incremental flows
cat("\nCalculating metrics....\n")
hidro_hist <- naturalToIncremental_Flow(hidro_hist,hinflow_dat, htopol, PV_info)
hidro_hist <- lapply(hidro_hist, apply_years_estima, min_year_estim , max_year_estim, years_hist)
hinflow_list <- lapply(hinflow_list, apply_years_estima, min_year_estim , max_year_estim, years_hist) 

CV                   <- matrix(nrow = length(hidro_hist),   ncol = nb_stages )
CV_tot               <- matrix(nrow = length(hinflow_list), ncol = nb_stages )
CV_annual            <- matrix(nrow = length(hidro_hist),   ncol = nb_years_hist_estim )
CV_annual_tot        <- matrix(nrow = length(hinflow_list), ncol = nb_years_hist_estim )
mean_hist            <- matrix(nrow = length(hidro_hist),   ncol = nb_stages )
mean_hist_tot        <- matrix(nrow = length(hinflow_list), ncol = nb_stages )
sd_hist              <- matrix(nrow = length(hidro_hist),   ncol = nb_stages )
sd_hist_tot          <- matrix(nrow = length(hinflow_list), ncol = nb_stages )
mean_hist_annual     <- matrix(nrow = length(hidro_hist),   ncol = nb_years_hist_estim )
mean_hist_annual_tot <- matrix(nrow = length(hinflow_list), ncol = nb_years_hist_estim )
sd_hist_annual       <- matrix(nrow = length(hidro_hist),   ncol = nb_years_hist_estim )
sd_hist_annual_tot   <- matrix(nrow = length(hinflow_list), ncol = nb_years_hist_estim )

for (i in 1:length(hidro_hist))
{
  for (j in 1:ncol(hidro_hist[[i]])) 
  {
    mean_hist[i,j] <- mean(hidro_hist[[i]][,j], na.rm = TRUE)
    mean_hist_tot[i,j] <- mean(hinflow_list[[i]][,j], na.rm = TRUE)
    sd_hist[i,j] <-  sd(hidro_hist[[i]][,j], na.rm = TRUE)
    sd_hist_tot[i,j] <-  sd(hinflow_list[[i]][,j], na.rm = TRUE)
    CV[i,j] <- sd_hist[i,j]/mean_hist[i,j]
    CV_tot[i,j] <- sd_hist_tot[i,j]/mean_hist_tot[i,j]
  }
  for (j in 1:nrow(hidro_hist[[i]])) 
  {
    mean_hist_annual[i,j] <- mean(hidro_hist[[i]][j,])
    mean_hist_annual_tot[i,j] <- mean(hinflow_list[[i]][j,])
    sd_hist_annual[i,j] <-  sd(hidro_hist[[i]][j,])
    sd_hist_annual_tot[i,j] <-  sd(hinflow_list[[i]][j,])
    CV_annual[i,j] <- sd_hist_annual[i,j]/mean_hist_annual[i,j]
    CV_annual_tot[i,j] <- sd_hist_annual_tot[i,j]/mean_hist_annual_tot[i,j]
  }
}

CV_average = apply(CV_annual,1, mean_noNA)
CV_mean_annual = apply(mean_hist_annual,1, calculate_CV)
CV_mean_annual_tot = apply(mean_hist_annual_tot,1, calculate_CV)
mean_longterm = apply(mean_hist_annual,1, mean_noNA)
mean_longterm_tot = apply(mean_hist_annual_tot,1, mean_noNA)

##### Plot parameters (axis, labels) ####
stages = c()
for (i in 1:nrow(hidro_hist[[1]]))
{
  stages = c(stages, rep(i,length(nums_PV)))
}
CV_annual_heatmap <- replace(CV_annual,CV_annual < 0,NA)
PVs = rep(nums_PV,nb_stages)
v_CV = as.vector(CV_annual_heatmap)
v_mean = as.vector(mean_hist_annual)
xlabel_years = c()
for (i in 1:nb_years_hist_estim)
{
  xlabel_years = c(xlabel_years,rep(years_hist[i],nb_stages))
}

##### Construct table #####
data_longterm <- data.frame(CV_mean_annual,CV_mean_annual_tot,mean_longterm,mean_longterm_tot)

first_plot <<- T
old_click <<- NULL

### Calculations ###
KPSS_test_const = lapply(hidro_hist,calculate_KPSS_constant)
KPSS_test_const_tot = lapply(hinflow_list,calculate_KPSS_constant)
KPSS_values_const = unlist(lapply(KPSS_test_const, get_testValue))
KPSS_values_const_tot = unlist(lapply(KPSS_test_const_tot, get_testValue))

# KPSS_test_lin = lapply(hidro_hist,calculate_KPSS_linear)
# KPSS_test_lin_tot = lapply(hinflow_list,calculate_KPSS_linear)
# KPSS_values_lin = unlist(lapply(KPSS_test_lin, get_testValue))
# KPSS_values_lin_tot = unlist(lapply(KPSS_test_lin_tot, get_testValue))

## Delta Analysis ##
int = 2
delta_values = c()
delta_values_tot = c()
for (i in 1:nb_plants)
{
  delta_values[i] = calculate_Delta(as.vector(t(hidro_hist[[i]])))
  delta_values_tot[i] = calculate_Delta(as.vector(t(hinflow_list[[i]])))
}


data_longterm <- data.frame(data_longterm,KPSS_values_const,KPSS_values_const_tot,
                            delta_values,delta_values_tot,PV_names,nums_PV,PV_basin_name,hist_index) #KPSS_values_lin,KPSS_values_lin_tot
longterm_omitNan = na.omit(data_longterm)
nums_PV <- longterm_omitNan$nums_PV
PV_names <- longterm_omitNan$PV_names
PV_basin_name <- longterm_omitNan$PV_basin_name # Eliminate the names of the entries that equals NA in the other columns
table_relDis <- data.frame(matrix(ncol = nb_years_hist,nrow = nb_plants))
table_podres_relDist <- data.frame(matrix(ncol = 7 ,nrow = 0))
relDist_higher <- matrix(NA,nrow = nb_plants, ncol = nb_years_hist)
years_higher <- matrix(NA,nrow = nb_plants, ncol = nb_years_hist)
table_message <- data.frame(matrix(ncol = 4 ,nrow = nrow(table_podres_relDist)))

## Table to show all results ##
table_total <- data.frame(nums_PV,PV_names)
table_total$CV_mean <- round(longterm_omitNan$CV_mean_annual_tot, digits=2)
table_total$mean <- round(longterm_omitNan$mean_longterm_tot, digits=2)
table_total$kpss <- round(longterm_omitNan$KPSS_values_const_tot, digits=2)
table_total$trend_test <- paste(round(longterm_omitNan$delta_values_tot, digits=2)*100,"%")

table_incremental <- data.frame(nums_PV,PV_names)
table_incremental$CV_mean <- round(longterm_omitNan$CV_mean_annual, digits=2)
table_incremental$mean <- round(longterm_omitNan$mean_longterm, digits=2)
table_incremental$kpss <- round(longterm_omitNan$KPSS_values_const, digits=2)
table_incremental$trend_test <- paste(round(longterm_omitNan$delta_values, digits=2)*100,"%")

names_cols_table <- c(as.vector(dicTranslateCurrent['NUMBER']),
                        as.vector(dicTranslateCurrent['NAME']),
                        as.vector(dicTranslateCurrent['CVANNUALAVG']),
                        as.vector(dicTranslateCurrent['LONGTERMMEAN']),
                        as.vector(dicTranslateCurrent['KPSSCONSTTEST']),
                        as.vector(dicTranslateCurrent['TRENDTEST'])
                        )

names(table_total) <- names_cols_table
names(table_incremental) <- names_cols_table

## Warnings ##
k = 1
for (i in 1:nb_plants)
{
  for (j in 1:nb_years_hist_estim)
  {
    table_relDis[i,j] = (mean_hist_annual[i,j]-mean_longterm[i])/mean_longterm[i]
  }
}

line = 1
tol_CV = 1.2*quantile(CV_mean_annual,probs = .95 ,na.rm = TRUE)
tol_KPSS_const = 1.2*quantile(KPSS_values_const,probs = .95 ,na.rm = TRUE)
# tol_KPSS_lin = 1.2*quantile(KPSS_values_lin,probs = .95 ,na.rm = TRUE)
tol_ratio = 1.2*quantile(delta_values[is.finite(delta_values)],probs = .95 ,na.rm = TRUE)

for (i in 1:nb_plants)
{
  tol_relDist = max(abs(quantile(table_relDis[i,],probs = .95 ,na.rm = TRUE)),abs(quantile(table_relDis[i,],probs = .05 ,na.rm = TRUE)))
  
  # if(!is.na(CV_mean_annual[i]) && CV_mean_annual[i]>tol_CV)
  # {
  #   table_message[line,1] = nums_PV[i]
  #   table_message[line,2] = as.character(PV_names[i])
  #   table_message[line,3] = as.character(df[which(df$nums_PV == nums_PV[i]),3])
  #   table_message[line,4] = as.double(df[which(df$nums_PV == nums_PV[i]),2])
  #   table_message[line,5] = round(CV_mean_annual[i], digits = 2)
  #   table_message[line,6] = round(tol_CV, digits = 2)
  #   table_message[line,7] = paste0('<span style="color:red">',dicTranslateCurrent['MSGCVHIGH'],'</span>')
  #   line = line + 1
  # }
  if(!is.na(longterm_omitNan$KPSS_values_const[i]) && longterm_omitNan$KPSS_values_const[i]>tol_KPSS_const)
  {
    table_message[line,1] = nums_PV[i]
    table_message[line,2] = as.character(PV_names[i])
    table_message[line,3] = as.character(df[which(df$nums_PV == nums_PV[i]),3])
    table_message[line,4] = round(as.double(df[which(df$nums_PV == nums_PV[i]),2]),digits=0)
    table_message[line,5] = round(longterm_omitNan$KPSS_values_const[i], digits = 2)
    table_message[line,6] = round(tol_KPSS_const, digits = 2)
    # table_message[line,7] = paste0('<span style="color:red">',dicTranslateCurrent['MSGKPSSCONSTHIGH'],'</span>')
    line = line + 1
  }
  # if(!is.na(KPSS_values_lin[i]) && KPSS_values_lin[i]>tol_KPSS_lin)
  # {
  #   table_message[line,1] = nums_PV[i]
  #   table_message[line,2] = as.character(PV_names[i])
  #   table_message[line,3] = as.character(df[which(df$nums_PV == nums_PV[i]),3])
  #   table_message[line,4] = as.double(df[which(df$nums_PV == nums_PV[i]),2])
  #   table_message[line,5] = round(KPSS_values_lin[i], digits = 2)
  #   table_message[line,6] = round(tol_KPSS_lin, digits = 2)
  #   table_message[line,7] = paste0('<span style="color:red">',dicTranslateCurrent['MSGKPSSLINEARHIGH'],'</span>')
  #   line = line + 1
  # }
  # if(!is.na(delta_values[i]) && delta_values[i]>tol_ratio)
  # {
  #   table_message[line,1] = nums_PV[i]
  #   table_message[line,2] = as.character(PV_names[i])
  #   table_message[line,3] = as.character(df[which(df$nums_PV == nums_PV[i]),3])
  #   table_message[line,4] = as.double(df[which(df$nums_PV == nums_PV[i]),2])
  #   table_message[line,5] = round(delta_values[i]*100, digits = 2)
  #   table_message[line,6] = round(tol_ratio*100, digits = 2)
  #   table_message[line,7] = paste0('<span style="color:red">',dicTranslateCurrent['MSGRATIOHIGH'],'</span>')
  #   line = line + 1
  # }
}

names_options <- c(as.vector(dicTranslateCurrent['LONGTERMMEAN']),
                   as.vector(dicTranslateCurrent['CVANNUALAVG']),
                   as.vector(dicTranslateCurrent['KPSSCONSTTEST']),
                  #  as.vector(dicTranslateCurrent['KPSSLINEARTEST']),
                   as.vector(dicTranslateCurrent['TRENDTEST']))

filter_options = c(sort(as.character(PV_basin_name)))

names_cols_relDist <- c("Name","Num","CV","KPSS","Year", "Rel.Error", "Long-term mean")
names(table_podres_relDist)<- names_cols_relDist

names_cols_message <- c(as.vector(dicTranslateCurrent['NUMBER']),
                        as.vector(dicTranslateCurrent['NAME']),
                        as.vector(dicTranslateCurrent['SUBSYSTEM']),
                        as.vector(dicTranslateCurrent['POWER']),
                        as.vector(dicTranslateCurrent['VALUE']),
                        as.vector(dicTranslateCurrent['TOL'])
                        ) #as.vector(dicTranslateCurrent['WARN'])

names(table_message) <- names_cols_message

axis_vars = list(name = names_options, 
                 var = c("mean_longterm","CV_mean_annual","KPSS_values_const","delta_values")) #"KPSS_values_lin"
filter_vars = list(name = filter_options, 
                   var = c("PV_basin_name"))
axis_vars_tot = list(name = names_options, 
                     var = c("mean_longterm_tot","CV_mean_annual_tot","KPSS_values_const_tot",
                             "delta_values_tot")) #"KPSS_values_lin_tot"


##### Save and remove variables ######
save(longterm_omitNan,PV_basin_name,
     hidro_hist,hinflow_list,
     nb_stages,cv_title,cv_axis,years_hist,years_hist_estim,mean_hist_annual,mean_hist_annual_tot,
     nb_years_hist,nb_years_hist_estim,CV,CV_tot,CV_annual_heatmap,path_files,CV_annual,CV_annual_tot,
     data_longterm,KPSS_values_const,KPSS_values_const_tot,table_message,
     axis_vars,filter_vars,axis_vars_tot,table_incremental,table_total,
     first_plot,old_click,mean_longterm,mean_longterm_tot,delta_values,delta_values_tot,
     file = paste(path_files,"HydroCheck.RData",sep = "\\")) #KPSS_test_lin,KPSS_test_lin_tot

cat("\n\n ------- Calculation finished! -------\n\n\n")
write.table(1,check_path)
rm(list = ls(all = T))
