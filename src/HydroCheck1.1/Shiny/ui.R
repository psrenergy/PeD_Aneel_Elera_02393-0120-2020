library(shinythemes)
library(shiny)
library(plotly)
library(shinyjs)
library(htmlwidgets)
library(DT)
library(RColorBrewer)
library(urca)

cat("----------------- UI.R File ---------------------\n")
options(warn=-1)

source("dictLoader.R")
dicTranslateCurrent <- dicTranslateCurrent

# Read inputs
path_files = commandArgs(trailingOnly = TRUE)

source("HydroCheck.R")

load(paste(path_files,"HydroCheck.RData",sep = "\\"))

ui <- fluidPage(
  navbarPage(
             title="HydroCheck 1.1",theme = shinytheme("flatly"),
             tabPanel(
               dicTranslateCurrent["VISUALIZATION"],
                      sidebarLayout(
                        sidebarPanel(
                          # actionButton("por", "Português"),
                          # actionButton("eng", "English"),
                          # actionButton("esp", "Español"),
                          # Select type of trend to plot
                          wellPanel(
                            selectInput(inputId = "Flow_type", label = strong(dicTranslateCurrent['FLOWTYPE']),
                                        choices = c("Incremental", "Total"),
                                        selected = "Incremental"),
                            checkboxInput("all_basin", dicTranslateCurrent['NOFILTER'], value = TRUE),
                            selectizeInput(inputId = "filters", dicTranslateCurrent['FILTERS'], choices = filter_vars$name, multiple = TRUE),
                            selectInput(inputId = "PV_name", label = strong(dicTranslateCurrent['GAUGINGSTATION']),
                                        choices = sort(longterm_omitNan$PV_names[sort(longterm_omitNan$CV_mean_annual, decreasing = TRUE, index.return = T)$ix])
                            )),
                          wellPanel(
                            selectInput("xvar", dicTranslateCurrent['XVAR'], axis_vars$name, selected = axis_vars$name[2]),
                            selectInput("yvar", dicTranslateCurrent['YVAR'], axis_vars$name, selected = axis_vars$name[4]),
                            selectInput("colvar", dicTranslateCurrent['COLORVAR'], axis_vars$name, selected = axis_vars$name[3]),
                            checkboxInput("size_check", dicTranslateCurrent['SIZESCALE']),
                            useShinyjs(),
                            disabled(selectInput("sizevar", dicTranslateCurrent['SIZESCALEVAR'], axis_vars$name, selected = axis_vars$name[1]))
                          ),
                          textOutput("Message"),
                          br(),
                          textOutput("CV_message"),
                          textOutput("mean_message"),
                          textOutput("stat_test"),
                          # textOutput("stat_test_lin"),
                          textOutput("ratio_test"),
                          br(),
                          tags$small(paste0(dicTranslateCurrent['DESCR_ABOUT']))
                          
                        ),
                        
                        # Output description 
                        mainPanel(
                          plotlyOutput(outputId = "pointsCV", width = "auto"),
                          br(),
                          tabsetPanel(type = "tabs", id = "tabs_plts",
                                      tabPanel(span(dicTranslateCurrent["HISTFLOWS"], title=dicTranslateCurrent["HISTFLOWSDESC"]),
                                               value = "hist_flw",
                                               br(),
                                               plotlyOutput(outputId = "flow_lineplot", width = "auto"
                                               )),
                                      tabPanel(span(dicTranslateCurrent["ANNUALAVGS"], title=dicTranslateCurrent["ANNUALAVGSDESC"]),
                                              br(),
                                              plotlyOutput(outputId = "mean_relDist", width = "auto")),
                                      tabPanel(span(dicTranslateCurrent["CVYEAR"],     title=dicTranslateCurrent["CVYEARDESC"]),
                                              br(),
                                              plotlyOutput(outputId = "cv_year", width = "auto")),
                                      tabPanel(span(cv_title,    title=dicTranslateCurrent["CVSTAGEDESC"]),
                                              br(),
                                              plotlyOutput(outputId = "cv_stage", width = "auto")),
                                      tabPanel(span(dicTranslateCurrent["WARN"],       title=dicTranslateCurrent["WARNDESC"]),
                                              tags$small(paste0(dicTranslateCurrent['DESCR_TABLE'])),
                                              br(),
                                              dataTableOutput("table")
                                              ),
                                      tabPanel(span(dicTranslateCurrent["RESULTS"],       title=dicTranslateCurrent["RESULTDESC"]),
                                              br(),
                                              dataTableOutput("table_res")
                                              ))
                        )
                      )
             ),
             tabPanel(dicTranslateCurrent['ABOUT'],
                      includeMarkdown(paste0('',dicTranslateCurrent['ABOUT_FILE'],''))
             ),
      tags$script(HTML("var header = $('.navbar > .container-fluid');
  header.append('<div style=\"float:right\"><img src=\"Logos.png\" alt=\"alt\" style=\"float:right;max-width:300px;height:auto;padding-top:8px;\"> </a>`</div>');
      console.log(header)")),
      tags$head(tags$link(rel = "shortcut icon", href = "hydro_check.ico"))
  ))
