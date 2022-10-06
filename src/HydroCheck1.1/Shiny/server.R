library(shinythemes)
library(shiny)
library(plotly)
library(shinyjs)
library(htmlwidgets)
library(DT)
library(RColorBrewer)
library(urca)

cat("----------------- SERVER.R File -----------------\n")
# options(warn=-1)

source("dictLoader.R")
dicTranslateCurrent <- dicTranslateCurrent

# Read inputs
path_files = commandArgs(trailingOnly = TRUE)

load(paste(path_files,"HydroCheck.RData",sep = "\\"))

server <- function(input,output,session)
{
  index_plot <- reactive({
    event.data <- event_data("plotly_click", source = "select")
    row_selected <- input$table_rows_selected[1]
    dataframe = dataframe()
    
    if(is.null(event.data) && first_plot == T)
    {
      pv_new_anal <<- which.max(longterm_omitNan$CV_mean_annual)
      pv_last_anal <<- pv_new_anal
      old_click <<- pv_new_anal
      first_plot <<- F
    }
    else
    {
      if(is.null(event.data) && first_plot == F)
      {
        pv_new_anal <<- pv_last_anal
      }
      else
      {
        if(event.data$curveNumber == 0)
          pv_new_anal <<- event.data$pointNumber+1
        pv_last_anal <<- pv_new_anal
        first_plot <<- F
      }
    }
    index_inputPV = grep(paste("^",input$PV_name,"$", sep = ""),longterm_omitNan$PV_names)
    index_withNan = grep(paste("^",dataframe$nums_PV[pv_new_anal],"$", sep = ""),longterm_omitNan$nums_PV)
    if(is.null(row_selected))
    {
      if(pv_new_anal == old_click)
      {
        index_plot = index_inputPV
        updateSelectInput(session = session,inputId = "PV_name",choices = sort(dataframe$PV_names),selected = longterm_omitNan$PV_names[index_plot])
        dataTableProxy('table') %>% selectRows(NULL)
      }
      else
      {
        index_plot = index_withNan
        updateSelectInput(session = session,inputId = "PV_name",choices = sort(dataframe$PV_names),selected = longterm_omitNan$PV_names[index_plot])
        old_click <<- pv_new_anal
      }
    }
    else
    {
      index_plot = which(table_message[row_selected,2] == longterm_omitNan$PV_names) # Comparing post name in table with dataframe
      updateSelectInput(session = session,inputId = "PV_name",choices = sort(dataframe$PV_names),selected = longterm_omitNan$PV_names[index_plot])
      dataTableProxy('table') %>% selectRows(NULL)
      updateTabsetPanel(session, "tabs_plts", selected = "hist_flw")
    }
    
    index_plot
  })
  
  observeEvent(input$size_check,{
    if(input$size_check == F)
    {
      disable("sizevar") 
    }
    else
    {
      enable("sizevar")
    }
  })
  
    observeEvent(input$all_basin,{
    if(input$all_basin == T)
    {
      disable("filters")
    }
    else
    {
      enable("filters")
    }
  })
  
  dataframe = reactive({
    if( input$all_basin == T){
	  dataframe = longterm_omitNan
	}
	else{
    dataframe = longterm_omitNan %>%
	  filter(PV_basin_name %in% input$filters)
	}
  })

  # observeEvent(input$por, {dicTranslateCurrent <- with(dict,setNames(pt, key))})
  # observeEvent(input$eng, {dicTranslateCurrent <- with(dict,setNames(en, key))})
  # observeEvent(input$esp, {dicTranslateCurrent <- with(dict,setNames(es, key))})
  
  output$pointsCV <- renderPlotly({
      color = "#434343"
      par(mar = c(4,4,1,1))
      
      xvar_name <- input$xvar
      yvar_name <- input$yvar
      colvar_name <- input$colvar
      sizevar_name <- input$sizevar
      
      pos_xvar = grep(paste("^",xvar_name,"$",sep = ""),axis_vars$name)
      pos_yvar = grep(paste("^",yvar_name,"$",sep = ""),axis_vars$name)
      pos_colvar = grep(paste("^",colvar_name,"$",sep = ""),axis_vars$name)
      pos_sizevar = grep(paste("^",sizevar_name,"$",sep = ""),axis_vars$name)
      
      dataframe = dataframe() # reactive variable
      
      if(input$Flow_type == "Incremental")
      {
        xvar = dataframe[[axis_vars$var[pos_xvar]]]
        yvar = dataframe[[axis_vars$var[pos_yvar]]]
        colvar = dataframe[[axis_vars$var[pos_colvar]]]
        sizevar = dataframe[[axis_vars$var[pos_sizevar]]]
        if (sizevar_name == "Trend test")
          sizevar = abs(sizevar)
        
        tick_x = ""
        tick_y = ""
        tick_col = ""
        if (xvar_name == dicTranslateCurrent['TRENDTEST'])
        {
          tick_x = "%"
        }
        if (yvar_name == dicTranslateCurrent['TRENDTEST'])
        {
          tick_y = "%"
        }
        if (colvar_name == dicTranslateCurrent['TRENDTEST'])
        {
          tick_col = "%"
        }
        scale_size = 15/(max(sizevar, na.rm = T))

        index_inputPV_noNan = grep(paste("^",input$PV_name,"$", sep = ""),dataframe$PV_names)
        
        if (input$size_check == F)
        {
          
          plot_ly(dataframe, x = ~xvar, y = ~yvar,type = "scatter", mode = "markers",
              marker = list(size = 11, opacity = 0.7, color = colvar, colorbar=list(title=colvar_name),colorscale='RdBu'),
              hoverinfo = 'text',
              text = ~paste("</br>",dicTranslateCurrent['STATION'],": ",dataframe$nums_PV," - ",dataframe$PV_names,
                            "</br>",dicTranslateCurrent['LONGTERMMEAN'],": ",round(dataframe$mean_longterm, digits = 2),"m3/s",
                            "</br>",dicTranslateCurrent['TEXTCV'],": ",round(dataframe$CV_mean_annual, digits = 2),
                            "</br>",dicTranslateCurrent['TEXTKPSSCONSTTOOLTIP'],": ",round(dataframe$KPSS_values_const,digits = 2),
                            "</br>",dicTranslateCurrent['TRENDTEST'],": ",round(100*dataframe$delta_values,digits = 0),"%"),
              source = "select") %>%
              add_trace(x = xvar[index_inputPV_noNan], y = yvar[index_inputPV_noNan],
                        marker = list( color = "rgba(0,0,0,0)",showscale = F,  size = 11,line = list(color = "rgb(0,255,0)", width = 2)),
                        hoverinfo = 'text', showlegend = F,
                        text = ~paste("</br>",dicTranslateCurrent['STATION'],": ",dataframe$nums_PV[index_inputPV_noNan]," - ",dataframe$PV_names[index_inputPV_noNan],
                                      "</br>",dicTranslateCurrent['LONGTERMMEAN'],": ",round(dataframe$mean_longterm[index_inputPV_noNan], digits = 2),"m3/s",
                                      "</br>",dicTranslateCurrent['TEXTCV'],": ",round(dataframe$CV_mean_annual[index_inputPV_noNan], digits = 2),
                                      "</br>",dicTranslateCurrent['TEXTKPSSCONSTTOOLTIP'],": ",round(dataframe$KPSS_values_const[index_inputPV_noNan],digits = 2),
                                      "</br>",dicTranslateCurrent['TRENDTEST'],": ",round(100*dataframe$delta_values[index_inputPV_noNan],digits = 0),"%")) %>%
              layout(xaxis = list(title = xvar_name, tickformat = tick_x),
                    yaxis = list(title = yvar_name, tickformat = tick_y))
        }
        else
        {
          plot_ly(dataframe, x = ~xvar, y = ~yvar,type = "scatter", mode = "markers",sizes = c(7,30),size = ~sizevar,
                  marker = list(sizemode = 'diameter',opacity = 0.7, line = list(width = 0.01), color = colvar, colorbar=list(title=colvar_name),colorscale='RdBu'),
                  hoverinfo = 'text', showlegend = F,
                  text = ~paste("</br>",dicTranslateCurrent['STATION'],": ",dataframe$nums_PV," - ",dataframe$PV_names,
                            "</br>",dicTranslateCurrent['LONGTERMMEAN'],": ",round(dataframe$mean_longterm, digits = 2),"m3/s",
                            "</br>",dicTranslateCurrent['TEXTCV'],": ",round(dataframe$CV_mean_annual, digits = 2),
                            "</br>",dicTranslateCurrent['TEXTKPSSCONSTTOOLTIP'],": ",round(dataframe$KPSS_values_const,digits = 2),
                            "</br>",dicTranslateCurrent['TRENDTEST'],": ",round(100*dataframe$delta_values,digits = 0),"%"),
                  source = "select") %>%
                  add_trace(x = xvar[index_inputPV_noNan], y = yvar[index_inputPV_noNan],size = sizevar[index_inputPV_noNan],
                            marker = list(color = "rgba(0,0,0,0)",showscale = F,line = list(color = "rgb(0,255,0)", width = 2),
                            hoverinfo = 'text', showlegend = F),
                            text = ~paste("</br>",dicTranslateCurrent['STATION'],": ",dataframe$nums_PV[index_inputPV_noNan]," - ",dataframe$PV_names[index_inputPV_noNan],
                                          "</br>",dicTranslateCurrent['LONGTERMMEAN'],": ",round(dataframe$mean_longterm[index_inputPV_noNan], digits = 2),"m3/s",
                                          "</br>",dicTranslateCurrent['TEXTCV'],": ",round(dataframe$CV_mean_annual[index_inputPV_noNan], digits = 2),
                                          "</br>",dicTranslateCurrent['TEXTKPSSCONSTTOOLTIP'],": ",round(dataframe$KPSS_values_const[index_inputPV_noNan],digits = 2),
                                          "</br>",dicTranslateCurrent['TRENDTEST'],": ",round(100*dataframe$delta_values[index_inputPV_noNan],digits = 0),"%")) %>%
            layout(xaxis = list(title = xvar_name, tickformat = tick_x),
                  yaxis = list(title = yvar_name, tickformat = tick_y))
        }
      }
      else
      {
        xvar = dataframe[[axis_vars_tot$var[pos_xvar]]]
        yvar = dataframe[[axis_vars_tot$var[pos_yvar]]]
        colvar = dataframe[[axis_vars_tot$var[pos_colvar]]]
        sizevar = dataframe[[axis_vars_tot$var[pos_sizevar]]]
        if (sizevar_name == "Trend test")
          sizevar = abs(sizevar)
        
        tick_x = ""
        tick_y = ""
        tick_col = ""
        if (xvar_name == dicTranslateCurrent['TRENDTEST'])
          tick_x = "%"
        if (yvar_name == dicTranslateCurrent['TRENDTEST'])
          tick_y = "%"
        if (colvar_name == dicTranslateCurrent['TRENDTEST'])
            tick_col = "%"
        scale_size = 15/(max(sizevar, na.rm = T))

        index_inputPV_noNan = grep(paste("^",input$PV_name,"$", sep = ""),dataframe$PV_names)
        
        if (input$size_check == F)
        {
          
          plot_ly(dataframe, x = ~xvar, y = ~yvar,type = "scatter", mode = "markers",
              marker = list(size = 11, opacity = 0.7, color = colvar, colorbar=list(title=colvar_name),colorscale='RdBu'),
              hoverinfo = 'text',
              text = ~paste("</br>",dicTranslateCurrent['STATION'],": ",dataframe$nums_PV," - ",dataframe$PV_names,
                            "</br>",dicTranslateCurrent['LONGTERMMEAN'],": ",round(dataframe$mean_longterm_tot, digits = 2),"m3/s",
                            "</br>",dicTranslateCurrent['TEXTCV'],": ",round(dataframe$CV_mean_annual_tot, digits = 2),
                            "</br>",dicTranslateCurrent['TEXTKPSSCONSTTOOLTIP'],": ",round(dataframe$KPSS_values_const_tot,digits = 2),
                            "</br>",dicTranslateCurrent['TRENDTEST'],": ",round(100*dataframe$delta_values_tot,digits = 0),"%"),
              source = "select") %>%
              add_trace(x = xvar[index_inputPV_noNan], y = yvar[index_inputPV_noNan],
                        marker = list( color = "rgba(0,0,0,0)",showscale = F,  size = 11,line = list(color = "rgb(0,255,0)", width = 2)),
                        hoverinfo = 'text', showlegend = F,
                        text = ~paste("</br>",dicTranslateCurrent['STATION'],": ",dataframe$nums_PV[index_inputPV_noNan]," - ",dataframe$PV_names[index_inputPV_noNan],
                                      "</br>",dicTranslateCurrent['LONGTERMMEAN'],": ",round(dataframe$mean_longterm_tot[index_inputPV_noNan], digits = 2),"m3/s",
                                      "</br>",dicTranslateCurrent['TEXTCV'],": ",round(dataframe$CV_mean_annual_tot[index_inputPV_noNan], digits = 2),
                                      "</br>",dicTranslateCurrent['TEXTKPSSCONSTTOOLTIP'],": ",round(dataframe$KPSS_values_const_tot[index_inputPV_noNan],digits = 2),
                                      "</br>",dicTranslateCurrent['TRENDTEST'],": ",round(100*dataframe$delta_values_tot[index_inputPV_noNan],digits = 0),"%")) %>%
              layout(xaxis = list(title = xvar_name, tickformat = tick_x),
                    yaxis = list(title = yvar_name, tickformat = tick_y))
        }
        else
        {
          plot_ly(dataframe, x = ~xvar, y = ~yvar,type = "scatter", mode = "markers",sizes = c(7,30),size = ~sizevar,
                  marker = list(sizemode = 'diameter',opacity = 0.7, line = list(width = 0.01), color = colvar, colorbar=list(title=colvar_name),colorscale='RdBu'),
                  hoverinfo = 'text', showlegend = F,
                  text = ~paste("</br>",dicTranslateCurrent['STATION'],": ",dataframe$nums_PV," - ",dataframe$PV_names,
                                "</br>",dicTranslateCurrent['LONGTERMMEAN'],": ",round(dataframe$mean_longterm_tot, digits = 2),"m3/s",
                                "</br>",dicTranslateCurrent['TEXTCV'],": ",round(dataframe$CV_mean_annual_tot, digits = 2),
                                "</br>",dicTranslateCurrent['TEXTKPSSCONSTTOOLTIP'],": ",round(dataframe$KPSS_values_const_tot,digits = 2),
                                "</br>",dicTranslateCurrent['TRENDTEST'],": ",round(100*dataframe$delta_values_tot,digits = 0),"%"),
                  source = "select") %>%
                  add_trace(x = xvar[index_inputPV_noNan], y = yvar[index_inputPV_noNan],size = sizevar[index_inputPV_noNan],
                            marker = list(color = "rgba(0,0,0,0)",showscale = F,line = list(color = "rgb(0,255,0)", width = 2),
                            hoverinfo = 'text', showlegend = F),
                            text = ~paste("</br>",dicTranslateCurrent['STATION'],": ",dataframe$nums_PV[index_inputPV_noNan]," - ",dataframe$PV_names[index_inputPV_noNan],
                                          "</br>",dicTranslateCurrent['LONGTERMMEAN'],": ",round(dataframe$mean_longterm_tot[index_inputPV_noNan], digits = 2),"m3/s",
                                          "</br>",dicTranslateCurrent['TEXTCV'],": ",round(dataframe$CV_mean_annual_tot[index_inputPV_noNan], digits = 2),
                                          "</br>",dicTranslateCurrent['TEXTKPSSCONSTTOOLTIP'],": ",round(dataframe$KPSS_values_const_tot[index_inputPV_noNan],digits = 2),
                                          "</br>",dicTranslateCurrent['TRENDTEST'],": ",round(100*dataframe$delta_values_tot[index_inputPV_noNan],digits = 0),"%")) %>%
            layout(xaxis = list(title = xvar_name, tickformat = tick_x),
                  yaxis = list(title = yvar_name, tickformat = tick_y))
        }
      }
      

    })
  
  output$flow_lineplot <- renderPlotly({
    color = "#434343"
    par(mar = c(4,4,1,1))
    
    index_plot = index_plot()
    years_timeseries = c()
    
    for(i in 1:length(years_hist_estim))
    {
      years_timeseries = c(years_timeseries,rep(years_hist_estim[i],nb_stages) + c(0:(nb_stages-1))/nb_stages)
    }
    
    if(input$Flow_type == "Incremental")
    {
      plot.new()
      plot_ly(x = years_timeseries, y = as.vector(t(hidro_hist[[longterm_omitNan$hist_index[index_plot]]])), trace = "scatter",mode = "lines",color = I("#434343"),
              hoverinfo = 'text',
              text = ~paste("</br>",dicTranslateCurrent['YEAR'],": ",round(years_timeseries, digits = 0),
                            "</br>",dicTranslateCurrent['INCRFLOW'],": ",round(as.vector(t(hidro_hist[[longterm_omitNan$hist_index[index_plot]]])), digits = 2))) %>%
                layout(title = paste(longterm_omitNan$PV_names[index_plot],longterm_omitNan$nums_PV[index_plot], sep = " - "), showlegend = FALSE,
                       xaxis = list(title = dicTranslateCurrent['YEAR'],showgrid = T),
                       yaxis = list (title = dicTranslateCurrent['INCREMENTALINFLOWUNIT']))
    }
    else
    {
      if(input$Flow_type == "Total")
        plot.new()
        plot_ly(x = years_timeseries, y = as.vector(t(hinflow_list[[longterm_omitNan$hist_index[index_plot]]])), trace = "scatter",mode = "lines",color = I("#434343"),
              hoverinfo = 'text',
              text = ~paste("</br>",dicTranslateCurrent['YEAR'],": ",round(years_timeseries, digits = 0),
                            "</br>",dicTranslateCurrent['TOTFLOW'],": ",round(as.vector(t(hinflow_list[[longterm_omitNan$hist_index[index_plot]]])), digits = 2))) %>%
        layout(title = paste(longterm_omitNan$PV_names[index_plot],longterm_omitNan$nums_PV[index_plot], sep = " - "), showlegend = FALSE,
               xaxis = list(title = dicTranslateCurrent['YEAR']),
               yaxis = list (title = dicTranslateCurrent['TOTALINFLOWUNIT']))
    }
  })

  output$mean_relDist <- renderPlotly({
    index_plot = index_plot()
    if(input$Flow_type == "Incremental")
    {
      plot_ly(x = years_hist_estim, y = mean_hist_annual[longterm_omitNan$hist_index[index_plot],], type = "bar", name = "Annual Avg.",
              hoverinfo = 'text',
              text = ~paste("</br>",dicTranslateCurrent['YEAR'],": ",round(years_hist_estim, digits = 0),
                            "</br>",dicTranslateCurrent['ANNUALAVGS'],": ",round(mean_hist_annual[longterm_omitNan$hist_index[index_plot],], digits = 2))) %>% 
        add_lines(y = rep(mean_longterm[longterm_omitNan$hist_index[index_plot]],nb_years_hist_estim), name = "Mean long-term (m3/s)",
                  hoverinfo = 'text',
                  text = ~paste("</br>Mean LT: ",round(rep(mean_longterm[longterm_omitNan$hist_index[index_plot]],nb_years_hist_estim), digits = 2))) %>%
        layout(title = paste(longterm_omitNan$PV_names[index_plot],longterm_omitNan$nums_PV[index_plot], sep = " - "), showlegend = FALSE,
               xaxis = list(title = dicTranslateCurrent['YEAR']),
               yaxis = list (title = dicTranslateCurrent['INCREMENTALINFLOWUNIT']))
    }
    else
    {
      plot_ly(x = years_hist_estim, y = mean_hist_annual_tot[longterm_omitNan$hist_index[index_plot],], type = "bar", name = "Annual Avg.",
              hoverinfo = 'text',
              text = ~paste("</br>",dicTranslateCurrent['YEAR'],": ",round(years_hist_estim, digits = 0),
                            "</br>",dicTranslateCurrent['ANNUALAVGS'],": ",round(mean_hist_annual_tot[longterm_omitNan$hist_index[index_plot],], digits = 2))) %>% 
        add_lines(y = rep(mean_longterm_tot[longterm_omitNan$hist_index[index_plot]], nb_years_hist_estim), name = "Mean long-term (m3/s)",
                  hoverinfo = 'text',
                  text = ~paste("</br>Mean LT: ",round(rep(mean_longterm_tot[longterm_omitNan$hist_index[index_plot]],nb_years_hist_estim), digits = 2))) %>%
        layout(title = paste(longterm_omitNan$PV_names[index_plot],longterm_omitNan$nums_PV[index_plot], sep = " - "), showlegend = FALSE,
               xaxis = list(title = dicTranslateCurrent['YEAR']),
               yaxis = list (title = dicTranslateCurrent['TOTALINFLOWUNIT']))
    }
  })
  
  output$cv_year <- renderPlotly({
    index_plot = index_plot()
    if(input$Flow_type == "Incremental")
    {
      plot_ly(x = years_hist_estim, y = CV_annual[longterm_omitNan$hist_index[index_plot],], type = "bar", name = "CV per Year",
              hoverinfo = 'text',
              text = ~paste("</br>",dicTranslateCurrent['YEAR'],": ",round(years_hist_estim, digits = 0),
                            "</br>",dicTranslateCurrent['TEXTCV'],": ",round(CV_annual[longterm_omitNan$hist_index[index_plot],], digits = 2))) %>% 
        add_lines(y = rep(mean(CV_annual[longterm_omitNan$hist_index[index_plot],]), nb_years_hist_estim), name = "Mean CV per year",
                  hoverinfo = 'text',
                  text = ~paste("</br>Mean LT: ",round(rep(mean(CV_annual[longterm_omitNan$hist_index[index_plot],]), nb_years_hist_estim), digits = 2))) %>%
        layout(title = paste(longterm_omitNan$PV_names[index_plot],longterm_omitNan$nums_PV[index_plot], sep = " - "), showlegend = FALSE,
               xaxis = list(title = dicTranslateCurrent['YEAR']),
               yaxis = list (title = dicTranslateCurrent['TEXTCV']))
    }
    else
    {
      plot_ly(x = years_hist_estim, y = CV_annual_tot[longterm_omitNan$hist_index[index_plot],], type = "bar", name = "CV per Year",
              hoverinfo = 'text',
              text = ~paste("</br>",dicTranslateCurrent['YEAR'],": ",round(years_hist_estim, digits = 0),
                            "</br>",dicTranslateCurrent['TEXTCV'],": ",round(CV_annual_tot[longterm_omitNan$hist_index[index_plot],], digits = 2))) %>% 
        add_lines(y = rep(mean(CV_annual_tot[longterm_omitNan$hist_index[index_plot],]), nb_years_hist_estim), name = "Mean CV per year",
                  hoverinfo = 'text',
                  text = ~paste("</br>Mean LT: ",round(rep(mean(CV_annual_tot[longterm_omitNan$hist_index[index_plot],]), nb_years_hist_estim), digits = 2))) %>%
        layout(title = paste(longterm_omitNan$PV_names[index_plot],longterm_omitNan$nums_PV[index_plot], sep = " - "), showlegend = FALSE,
               xaxis = list(title = dicTranslateCurrent['YEAR']),
               yaxis = list (title = dicTranslateCurrent['TEXTCV']))
    }
  })
  
  output$cv_stage <- renderPlotly({
    index_plot = index_plot()
    if(input$Flow_type == "Incremental")
    {
      plot_ly(x = c(1:nb_stages), y = CV[longterm_omitNan$hist_index[index_plot],], type = "bar", name = "CV per Stage",
              hoverinfo = 'text', 
              text = ~paste("</br>",cv_axis,": ",round(c(1:nb_stages), digits = 0),
                            "</br>",dicTranslateCurrent['TEXTCV'],": ",round(CV[longterm_omitNan$hist_index[index_plot],], digits = 2))) %>% 
        add_lines(y = rep(mean(CV[longterm_omitNan$hist_index[index_plot],]), nb_stages), name = "Mean CV per stage",
                  hoverinfo = 'text',
                  text = ~paste("</br>Mean LT: ",round(rep(mean(CV[longterm_omitNan$hist_index[index_plot],]), nb_stages), digits = 2))) %>%
        layout(title = paste(longterm_omitNan$PV_names[index_plot],longterm_omitNan$nums_PV[index_plot], sep = " - "), showlegend = FALSE,
               xaxis = list(title = cv_axis),
               yaxis = list (title = dicTranslateCurrent['TEXTCV']))
    }
    else
    {
      plot_ly(x = c(1:nb_stages), y = CV_tot[longterm_omitNan$hist_index[index_plot],], type = "bar", name = "CV per Stage",
              hoverinfo = 'text',
              text = ~paste("</br>",cv_axis,": ",round(c(1:nb_stages), digits = 0),
                            "</br>",dicTranslateCurrent['TEXTCV'],": ",round(CV_tot[longterm_omitNan$hist_index[index_plot],], digits = 2))) %>% 
        add_lines(y = rep(mean(CV_tot[longterm_omitNan$hist_index[index_plot],]), nb_stages), name = "Mean CV per stage",
                  hoverinfo = 'text',
                  text = ~paste("</br>Mean LT: ",round(rep(mean(CV_tot[longterm_omitNan$hist_index[index_plot],]), nb_stages), digits = 2))) %>%
        layout(title = paste(longterm_omitNan$PV_names[index_plot],longterm_omitNan$nums_PV[index_plot], sep = " - "), showlegend = FALSE,
               xaxis = list(title = cv_axis),
               yaxis = list (title = dicTranslateCurrent['TEXTCV']))
    }
  })
  
  output$Message <- renderText({
    index_inputPV = grep(paste("^",input$PV_name,"$", sep = ""),longterm_omitNan$PV_names)
    PV = longterm_omitNan$nums_PV[index_inputPV]
    paste(longterm_omitNan$PV_names[index_inputPV], PV, input$Flow_type, sep = " - ")
  })
  
  output$CV_message <- renderText({
    index_inputPV = grep(paste("^",input$PV_name,"$", sep = ""),longterm_omitNan$PV_names)
    # CV = round(data_longterm$CV_mean_annual[index_inputPV],digits = 2)
    # paste("CV: ",CV, sep = "")
    if(input$Flow_type == "Incremental")
      paste(dicTranslateCurrent['TEXTCV']," = ", round(longterm_omitNan$CV_mean_annual[index_inputPV],digits = 2),sep = "")
    else
      paste(dicTranslateCurrent['TEXTCV']," = ", round(longterm_omitNan$CV_mean_annual_tot[index_inputPV],digits = 2),sep = "")
  })
  
  output$mean_message <- renderText({
    index_inputPV = grep(paste("^",input$PV_name,"$", sep = ""),longterm_omitNan$PV_names)
    # mean = round(data_longterm$mean_longterm[index_inputPV],digits = 2)
    # paste("Long-term mean: ",mean, sep = "")
    if(input$Flow_type == "Incremental")
      paste(dicTranslateCurrent['LONGTERMMEAN']," = ", round(longterm_omitNan$mean_longterm[index_inputPV],digits = 2)," m3/s ",sep = "")
    else
      paste(dicTranslateCurrent['LONGTERMMEAN']," = ", round(longterm_omitNan$mean_longterm_tot[index_inputPV],digits = 2)," m3/s ",sep = "")
  })
  
  output$stat_test <- renderText({
    index_inputPV = grep(paste("^",input$PV_name,"$", sep = ""),longterm_omitNan$PV_names)
    # index_inputPV_noNan = grep(paste("^",input$PV_name,"$", sep = ""),dataframe$PV_names)
    if(input$Flow_type == "Incremental")
      # paste(dicTranslateCurrent['TEXTKPSSCONST']," = ", round(KPSS_values_const[[index_inputPV]],digits = 3),sep = "")
      paste(dicTranslateCurrent['TEXTKPSSCONST']," = ", round(longterm_omitNan$KPSS_values_const[[index_inputPV]],digits = 3),sep = "")
    else
      paste(dicTranslateCurrent['TEXTKPSSCONST']," = ", round(longterm_omitNan$KPSS_values_const_tot[[index_inputPV]],digits = 3),sep = "")
      
  })
  
  # output$stat_test_lin <- renderText({
  #   index_inputPV = grep(paste("^",input$PV_name,"$", sep = ""),longterm_omitNan$PV_names)
  #   if(input$Flow_type == "Incremental")
  #     paste(dicTranslateCurrent['TEXTKPSSLIN']," = ", round(KPSS_test_lin[[index_inputPV]]@teststat,digits = 3),sep = "")
  #   else
  #     paste(dicTranslateCurrent['TEXTKPSSLIN']," = ", round(KPSS_test_lin_tot[[index_inputPV]]@teststat,digits = 3),sep = "")

  # })
  
  output$ratio_test <- renderText({
    index_inputPV_noNAN = grep(paste("^",input$PV_name,"$", sep = ""),longterm_omitNan$PV_names)
    if(input$Flow_type == "Incremental")
      paste(dicTranslateCurrent['TEXTTREND']," = ", round(100*longterm_omitNan$delta_values[index_inputPV_noNAN],digits = 0),"%",sep = "")
    else
      paste(dicTranslateCurrent['TEXTTREND']," = ", round(100*longterm_omitNan$delta_values_tot[index_inputPV_noNAN],digits = 0),"%",sep = "")
  })
  
  output$table <- renderDataTable({
    index_plot = index_plot()
    datatable(table_message, escape = F, selection = "single",options = list(
        columnDefs = list(list(className = 'dt-center', targets = 1))))
  })

  output$table_res <- renderDataTable(server = FALSE,{
    index_plot = index_plot()
    if(input$Flow_type == "Incremental")
      datatable(table_incremental, escape = F, selection = "single",extensions = c("Buttons"), options = list(
        columnDefs = list(list(className = 'dt-center', targets = c(1,3,4,5,6))),dom = 'Bfrtip',
        buttons = list(
          list(extend = "csv", text = paste(dicTranslateCurrent['DOWNLOAD']), filename = "data",
               exportOptions = list(
                 modifier = list(page = "all")
               )))))
    else
      datatable(table_total, escape = F, selection = "single",extensions = c("Buttons"), options = list(
        columnDefs = list(list(className = 'dt-center', targets = c(1,3,4,5,6))),dom = 'Bfrtip',
        buttons = list(
          list(extend = "csv", text = paste(dicTranslateCurrent['DOWNLOAD']), filename = "data",
               exportOptions = list(
                 modifier = list(page = "all")
               )))))
  })
  
  # close the R session when Chrome closes
  session$onSessionEnded(function() { 
    stopApp()
    q("no") 
  })
}

# create Shiny object
#shinyApp(ui = ui, server = server)
