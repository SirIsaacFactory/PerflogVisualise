################################################################################
# Library
################################################################################
import os
import re

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker


################################################################################
# read_perflog
################################################################################
_TIMECOL = "Time"
def read_perflog(inputFile):
    # read csv file
    df = pd.read_csv(inputFile, encoding = "shift_jis", low_memory = False)

    # replace space with 0
    spRx = re.compile(r"^\ *$")
    delSp = lambda v:0 if spRx.match(v) is not None else v
    for col in df.select_dtypes(include=object).columns:
        df[col] = df[col].apply(delSp)

    # get servername
    svnRx1 = re.compile(r"^\\\\")
    svnRx2 = re.compile(r"\\.*")
    svname = svnRx2.sub("", svnRx1.sub("", df.columns[1]))
    
    # remove servername from columns
    svnRx = re.compile(r"\\\\[^\\]*\\")
    newCols = []
    
    for col in df.columns:
        newCol = svnRx.sub("", col)
        newCols.append(newCol)
    
    newCols[0] = _TIMECOL
    df.columns = newCols

    # change data type of time column
    timeRx = re.compile(r"\..*$")
    rmMillisec = lambda s:timeRx.sub("", s)
    df[_TIMECOL] = df["Time"].apply(rmMillisec)
    df[_TIMECOL] = pd.to_datetime(df[_TIMECOL], format = "%m/%d/%Y %H:%M:%S")

    return svname, df


################################################################################
# basicConfig for makeGraph
################################################################################
makeGraphByColName_basicConfig = {
    "Name": "Name",
    "resultDir": "result",
    "resultFile": "ResultFile",
    "dataset": [
        {
            "title": "Memory Usage",
            "xlabel": "Time",
            "ylabel": "Memory",
            "cols": [
                {
                    "x": "Time",
                    "y": "Memory\Available MBytes",
                    "label": "Memory\Available MBytes",
                }
            ],
            "x_data_point": 20
        },
        {
            "title": "CPU Usage",
            "xlabel": "Time",
            "ylabel": "Processor Time",
            "ylim": [0, 100],
            "cols": [
                {
                    "x": "Time",
                    "y": "Processor(_Total)\% User Time",
                    "label": "Processor(_Total)\% User Time",
                    "color": "Blue"
                },
                {
                    "x": "Time",
                    "y": "Processor(_Total)\% Processor Time",
                    "label": "Processor(_Total)\% Processor Time",
                    "color": "Red"
                }
            ]
        }

    ]
}

################################################################################
# makePerfGraph
################################################################################
_NA = "NA"
_NAME = "Name"
_TITLE = "title"
_RESULTDIR = "resultDir"
_RESULTFILE = "resultFile"
_DATASET = "dataset"
_GRAPH_WIDTH = "graph_width"
_GRAPH_HEIGHT = "graph_height"
_TITLE = "title"
_COLS = "cols"
_X = "x"
_Y = "y"
_X_DATA_POINT = "x_data_point"
_LABEL = "label"
_LINEWIDTH = "linewidth"
_COLOR = "color"
_XLABEL = "xlabel"
_YLABEL = "ylabel"
_XLIM = "xlim"
_YLIM = "ylim"

def makePerfGraph(config, data = ""):
    # define default variables
    default_x_data_piont = 40
    default_linewidth = 0.5
    default_color = "Blue"
    default_graph_width = 20
    default_graph_heigth = 15
    title_font_size = 20
    axis_font_size = 10

    #-----------------------------------
    # Check Input Data
    #-----------------------------------
    # Name of the Performance Data
    if _NAME not in config:
        raise ValueError(f'config dict does not include "[{_NAME}]".')
    Name = config[_NAME]

    # Performance Data
    if _DATASET not in config:
        raise ValueError(f'config dict does not include "[{_DATASET}]".')

    # Number of the graphs
    if _COLS in config[_DATASET]:
        raise ValueError(f'config dict does not include ["{_DATASET}"]["{_COLS}"].')
    graph_num = len(config[_DATASET])

    #-----------------------------------
    # Read Input Data
    #-----------------------------------
    if _RESULTDIR in config:
        resultDir = os.path.join(".", config[_RESULTDIR])
        if not os.path.isdir(resultDir):
            raise ValueError(f"result directory[{_RESULTDIR}] does not exist.")
    else:
        resultDir = _NA

    if _RESULTFILE in config:
        resultFile = config[_RESULTFILE]
    else:
        resultFile = _NA

    if _GRAPH_WIDTH in config:
        graph_width = config[_GRAPH_WIDTH]
    else:
        graph_width = default_graph_width
        
    if _GRAPH_HEIGHT in config:
        graph_height = config[_GRAPH_HEIGHT]
    else:
        graph_height = default_graph_heigth

    #-----------------------------------
    # Draw Performance Graph
    #-----------------------------------
    fig, ax = plt.subplots(nrows = graph_num, ncols = 1, figsize = (graph_width, graph_num * graph_height))

    i = -1
    for dataset in config[_DATASET]:
        i += 1
        if graph_num == 1:
            graph = ax
        else:
            graph = ax[i]
        
        if _TITLE in dataset:
            title = dataset[_TITLE]
        else:
            title = f"graph{i + 1:03}"

        if _X_DATA_POINT in dataset:
            x_data_point = dataset[_X_DATA_POINT]
        else:
            x_data_point = default_x_data_piont
        
        j = -1
        for cols in dataset[_COLS]:
            j += 1

            # Check X data is column name or data itself
            x = cols[_X]
            if type(x) == str:
                xdata = data[x].values
            else:
                xdata = x

            # Check Y data is column name or data itself
            y = cols[_Y]
            if type(y) == str:
                ydata = data[y].values
            else:
                ydata = y

            # Label of Y data
            label = cols[_LABEL]

            # Color of the graph
            if _COLOR in cols:
                color = cols[_COLOR]
            else:
                color = default_color

            # Linewidth of the graph
            if _LINEWIDTH in cols:
                linewidth = cols[_LINEWIDTH]
            else:
                linewidth = default_linewidth

            # Draw graph
            graph.plot(xdata, ydata, label = label, color = color, linewidth = linewidth)
            if (resultDir != _NA) and (resultFile != _NA):
                outpath = os.path.join(resultDir, f"{resultFile}_{i + 1:03}_{j + 1:03}.csv")
                pd.DataFrame(
                    data = {
                        dataset[_XLABEL]: xdata,
                        label: ydata
                    }
                ).to_csv(outpath, index = False)

        # Graph settings
        if _TITLE in dataset:
            graph.set_title(Name + ": " + title, fontsize = title_font_size)
        if _XLABEL in dataset:
            graph.set_xlabel(dataset[_XLABEL], fontsize = axis_font_size)
        if _YLABEL in dataset:
            graph.set_ylabel(dataset[_YLABEL], fontsize = axis_font_size)
        if _XLIM in dataset:
            graph.set_xlim(dataset[_XLIM][0], dataset[_XLIM][1])
        if _YLIM in dataset:
            graph.set_ylim(dataset[_YLIM][0], dataset[_YLIM][1])

        graph.legend()
        graph.grid(which = "major")
        graph.xaxis.set_major_formatter(mdates.DateFormatter("%y/%m/%d %H:%M"))
        graph.xaxis.set_major_locator(ticker.MaxNLocator(x_data_point))
        graph.tick_params(axis = "x", labelrotation = 90)

        if (resultDir != _NA) and (resultFile != _NA):
            outpath = os.path.join(resultDir, f"{resultFile}.pdf")
            fig.savefig(outpath)
    plt.show()



