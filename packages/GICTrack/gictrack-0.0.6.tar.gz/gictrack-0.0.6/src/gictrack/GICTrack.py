from PyQt6 import QtCore, QtWidgets, QtWebEngineCore, QtWebEngineWidgets
from PyQt6.QtCore import Qt, QTimer, QEvent, pyqtSignal
from PyQt6.QtWidgets import (QApplication, QComboBox,
        QGridLayout, QHBoxLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollArea,  QTableWidgetItem,
        QSlider, QSpinBox, QDoubleSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QFileDialog, QLineEdit, QStyledItemDelegate)
from PyQt6.QtGui import QPixmap, QFont, QPalette, QStandardItem, QFontMetrics
import sys
import statistics
from functools import partial # allow input of args into functions in connect
import numpy as np
import pandas as pd
import sqlite3
from dfply import X, group_by, summarize, summary_functions # R's dplyr equivalent
# Importing plot packages
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import scipy.io
# from plotnine import ggplot, aes, geom_line
# from matplotlib.figure import Figure
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os
from math import inf
import matplotlib.path as mpltPath # for points in polygon
from scipy import stats
from scipy.spatial import ConvexHull as chull # to identify border points
from scipy.spatial.distance import cdist, pdist, squareform # for distance between points
import multiprocessing as mp
# from pointpats import ripley, PointPattern
import matplotlib.pyplot as plt
import plotly.offline as po
import fnmatch # unix filename filtering
import math, time, h5py, copy, shutil
import plotly
from importlib.resources import files
            
class PlotlySchemeHandler(QtWebEngineCore.QWebEngineUrlSchemeHandler):
    def __init__(self, app):
        super().__init__(app)
        self.m_app = app

    def requestStarted(self, request):
        fig = self.m_app.fig_by_name()
        if isinstance(fig, go.Figure):
            raw_html = '<html><head><meta charset="utf-8" />'
            raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
            raw_html += "<body>"
            raw_html += po.plot(fig, include_plotlyjs=False, output_type="div")
            raw_html += "</body></html>"
            buf = QtCore.QBuffer(parent=self)
            request.destroyed.connect(buf.deleteLater)
            buf.open(QtCore.QIODevice.WriteOnly)
            buf.write(raw_html.encode())
            buf.seek(0)
            buf.close()
            request.reply(b"text/html", buf)
            return
        request.fail(QtWebEngineCore.QWebEngineUrlRequestJob.UrlNotFound)

class PlotlyApplication(QtCore.QObject):
    scheme = b"plotly"

    def __init__(self, parent=None):
        super().__init__(parent)
        scheme = QtWebEngineCore.QWebEngineUrlScheme(PlotlyApplication.scheme)
        QtWebEngineCore.QWebEngineUrlScheme.registerScheme(scheme)

    def init_handler(self, view, profile=None):
        self.view = view
        if profile is None:
            profile = QtWebEngineWidgets.QWebEngineView().page().profile().defaultProfile() #QWebEngineProfile.defaultProfile()
        handler = profile.urlSchemeHandler(PlotlyApplication.scheme)
        if handler is not None:
            profile.removeUrlSchemeHandler(handler)
        self.m_handler = PlotlySchemeHandler(self)
        profile.installUrlSchemeHandler(PlotlyApplication.scheme, self.m_handler)

    def fig_by_name(self):
        return self.view.fig

class CheckableComboBox(QComboBox):
    # Yoann Quenach de Quivillic on https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5
    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        # Make the lineedit the same color as QPushButton
        palette = QtWidgets.QApplication.instance().palette()
        # palette.setBrush(QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)

        # Use custom delegate
        self.setItemDelegate(CheckableComboBox.Delegate())

        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, object, event):

        if object == self.lineEdit():
            if event.type() == QEvent.Type.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if object == self.view().viewport():
            if event.type() == QEvent.Type.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.CheckState.Checked:
                    item.setCheckState(Qt.CheckState.Unchecked)
                else:
                    item.setCheckState(Qt.CheckState.Checked)
                return True
        return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        # Compute elided text (with "...")
        # metrics = QFontMetrics(self.lineEdit().font())
        # elidedText = metrics.elidedText(text, Qt.ElideRight, self.lineEdit().width())
        # self.lineEdit().setText(elidedText)
        self.lineEdit().setText(text)

    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(sorted(texts)):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                res.append(self.model().item(i).data())
        return res

    def checkAll(self):
        # Check all items in the list
        for i in range(self.model().rowCount()):
            self.model().item(i).setCheckState(Qt.CheckState.Checked)

    def uncheckAll(self):
        # Check all items in the list
        for i in range(self.model().rowCount()):
            self.model().item(i).setCheckState(Qt.CheckState.Unchecked)

class DStatistic(object):
    """
    Abstract Base Class for distance statistics.

    Parameters
    ----------
    name       : string
                 Name of the function. ("G", "F", "J", "K" or "L")

    Attributes
    ----------
    d          : array
                 The distance domain sequence.

    """
    def __init__(self, name):
        self.name = name

    def plot(self, qq=False):
        """
        Plot the distance function

        Parameters
        ----------
        qq: Boolean
            If False the statistic is plotted against distance. If Frue, the
            quantile-quantile plot is generated, observed vs. CSR.
        """

        # assuming mpl
        x = self.d
        if qq:
            plt.plot(self.ev, self._stat)
            plt.plot(self.ev, self.ev)
        else:
            plt.plot(x, self._stat, label='{}'.format(self.name))
            plt.ylabel("{}(d)".format(self.name))
            plt.xlabel('d')
            plt.plot(x, self.ev, label='CSR')
            plt.title("{} distance function".format(self.name))

class LoadingBarWindow(QWidget):
    def __init__(self):
        super(LoadingBarWindow, self).__init__()
        self.setWindowTitle("Progress")
        self.setStyle(QStyleFactory.create('Fusion'))
        self.createProgressBar()
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.progressBar)
        self.setLayout(mainLayout)

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(int(curVal + (maxVal - curVal) / 100))

    def createProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 10000)
        self.progressBar.setValue(0)

        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(10)

class produceJumpDistancePlot(QtCore.QThread):
    diffusionTrack2Par = pyqtSignal([object])
    diffusionTrack3Par = pyqtSignal([object])
    diffusionTrack2ParBox = pyqtSignal([object])
    diffusionTrack3ParBox = pyqtSignal([object])
    tableData = pyqtSignal([object])

    def __init__(self, model):
        super().__init__()
        self.model = model

    def run(self):
        data = self.model.getJumpDistanceData(self.selectionFile)
        mutList = list(set(data['mutation']))
        if len(self.selectionFile) > 1:
            # Multi file/conditions comparison
            dataLineChart = data.loc[data["jump_distance"] <= self.jumpDistanceConsidered,]
            dataMulti = dataLineChart >> group_by(X.mutation, X.jump_distance) >> summarize(sharedFrequency_mean = summary_functions.mean(X.sharedFrequency))
            twoParMultiFigure = px.line(dataMulti, x = "jump_distance", y = "sharedFrequency_mean", color = "mutation")
            self.diffusionTrack2Par.emit(twoParMultiFigure.to_html(include_plotlyjs='cdn'))

            dataMultiTrajSum = dataMulti >> group_by(X.mutation) >> summarize(totalFrequency = (X.sharedFrequency_mean.sum()))
            dataMulti['frequencyRatio'] = 0.0
            for n in range(len(mutList)):
                dataMulti.loc[dataMulti['mutation'] == dataMultiTrajSum['mutation'][n], 'frequencyRatio'] = dataMulti.loc[dataMulti['mutation'] == dataMultiTrajSum['mutation'][n], 'sharedFrequency_mean'] / dataMultiTrajSum.iloc[n, 1]
            threeParMultiFigure = px.line(dataMulti, x = "jump_distance", y = "frequencyRatio", color = "mutation")
            self.diffusionTrack3Par.emit(threeParMultiFigure.to_html(include_plotlyjs='cdn'))
        else:
            # Single file condition
            data = data.loc[data["jump_distance"] <= self.jumpDistanceConsidered,]
            twoParFigure = px.bar(data, x = "jump_distance", y = "sharedFrequency", color = "mutation", barmode = "group", labels = {"jump_distance": "Jump Distance (um)", "sharedFrequency": "Frequency"})
            for n in range(len(mutList)):
                twoParFigure.add_trace(px.line(data, x = "jump_distance", y = "twoParFrequency", color = "mutation", color_discrete_sequence = ["#EF553B"]).data[n])
                twoParFigure.add_trace(px.line(data, x = "jump_distance", y = "twoParD1Values", color = "mutation", color_discrete_sequence = ["#00CC96"]).data[n])
                twoParFigure.add_trace(px.line(data, x = "jump_distance", y = "twoParD2Values", color = "mutation", color_discrete_sequence = ["#AB63FA"]).data[n])
            twoParFigure.update_xaxes(range = [0, self.jumpDistanceConsidered])
            twoParFigure.update_traces(name = "Total", selector = dict(line_color="#EF553B"))
            twoParFigure.update_traces(name = "Diffusing", selector = dict(line_color="#00CC96"))
            twoParFigure.update_traces(name = "Bound", selector = dict(line_color="#AB63FA"))
            self.diffusionTrack2Par.emit(twoParFigure.to_html(include_plotlyjs='cdn'))

            threeParFigure = px.bar(data, x = "jump_distance", y = "sharedFrequency", color = "mutation", barmode = "group", labels = {"jump_distance": "Jump Distance (um)", "sharedFrequency": "Frequency"})
            for n in range(len(mutList)):
                threeParFigure.add_trace(px.line(data, x = "jump_distance", y = "threeParFrequency", color = "mutation", color_discrete_sequence = ["#EF553B"]).data[n])
                threeParFigure.add_trace(px.line(data, x = "jump_distance", y = "threeParD1Values", color = "mutation", color_discrete_sequence = ["#00CC96"]).data[n])
                threeParFigure.add_trace(px.line(data, x = "jump_distance", y = "threeParD2Values", color = "mutation", color_discrete_sequence = ["#AB63FA"]).data[n])
                threeParFigure.add_trace(px.line(data, x = "jump_distance", y = "threeParD3Values", color = "mutation", color_discrete_sequence = ["#FFA15A"]).data[n])
            threeParFigure.update_xaxes(range = [0, self.jumpDistanceConsidered])
            threeParFigure.update_traces(name = "Total", selector = dict(line_color="#EF553B"))
            threeParFigure.update_traces(name = "Diffusing", selector = dict(line_color="#00CC96"))
            threeParFigure.update_traces(name = "Mixed", selector = dict(line_color="#AB63FA"))
            threeParFigure.update_traces(name = "Bound", selector = dict(line_color="#FFA15A"))
            # plotly.io.write_image(threeParFigure, "Images/JumpDistance.svg")
            self.diffusionTrack3Par.emit(threeParFigure.to_html(include_plotlyjs='cdn'))

        # twoParFigure.update_layout(showlegend=False)
        twoParBoxData, threeParBoxData = self.model.getJumpDistanceBoxData(self.selectionFile)
        twoParBox = px.box(twoParBoxData, x = "fraction", y = "values", color = "mutation", points = "all", labels = {"fraction": "States", "values": "Fraction"}, hover_name = "filename")
        self.diffusionTrack2ParBox.emit(twoParBox.to_html(include_plotlyjs='cdn'))

        threeParBox = px.box(threeParBoxData, x = "fraction", y = "values", color = "mutation", points = "all", labels = {"fraction": "States", "values": "Fraction"}, hover_name = "filename")
        self.diffusionTrack3ParBox.emit(threeParBox.to_html(include_plotlyjs='cdn'))

        self.tableData.emit(data)

    def update(self, selectionFile, jumpDistanceConsidered):
        self.selectionFile = selectionFile
        self.jumpDistanceConsidered = jumpDistanceConsidered

class produceHeatMapPlot(QtCore.QThread):
    heatMapPlot = pyqtSignal([object])
    heatMapCummulativeTrajs = pyqtSignal([object])
    heatMapLiveTrajs = pyqtSignal([object])
    heatMapBurstLifetime = pyqtSignal([object])
    heatMapRipley = pyqtSignal([object])

    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view

    def run(self):
        data = self.model.getTrackFiles(self.selectionFile)
        # Get all data to plot outer region
        trajData = self.model.getHeatMapTraj(self.selectionFile, 0)
        trajData["duration"] = trajData["endTime"] - trajData["startTime"]
        trajData["meanXPixel"] = trajData["meanX"] / trajData["pixelSize"]
        trajData["meanYPixel"] = trajData["meanY"] / trajData["pixelSize"]

        trajCumData = trajData.groupby(["mutation", "startTime"]).agg(startTimeCount=("startTime", "count"), uniqueFilename = ("filename", "nunique"))
        trajCumData["Frequency"] = trajCumData["startTimeCount"] / trajCumData["uniqueFilename"]
        trajCumData.reset_index(inplace = True)
        # trajCumData = trajData >> group_by(X.mutation, X.startTime) >> summarize(Frequency = summary_functions.n(X.startTime) / summary_functions.n_distinct(X.filename))
        trajCumData["Cummulative Frequency"] = trajCumData.groupby("mutation")["Frequency"].transform(pd.Series.cumsum)
        trajLiveData = data.groupby(["mutation", "Frame"]).agg(frameCount = ("Frame", "count"), uniqueFilename = ("filename", "nunique"))
        trajLiveData["Frequency"] = trajLiveData["frameCount"] / trajLiveData["uniqueFilename"]
        trajLiveData.reset_index(inplace = True)

        if len(self.selectionFile) == 1:
            if os.path.exists(os.getcwd() + "/Data/h5-file/" + self.selectionFile[0] + ".h5"):
                dapiData = h5py.File(os.getcwd() + "/Data/h5-file/" + self.selectionFile[0] + ".h5", 'r')
                self.view.dapiData = dapiData

                tData = self.model.getHeatMapTrackData(self.selectionFile)
                tData.loc[:, "Frame"] = tData["Frame"] / tData["exposure_time"]
                tData.loc[:, "x"] = tData["x"] / tData["pixelSize"]
                tData.loc[:, "y"] = tData["y"] / tData["pixelSize"]
                self.view.tData = tData

                self.view.heatMapSlider.setMaximum(len(dapiData['data']) - 1)
                self.view.heatMapSlider.setValue(0)
                self.view.heatMapSlider.setDisabled(False)
                # Extract the first frame
                frame = 0
                X, Y = np.mgrid[0:len(dapiData['data'][frame]), 0:len(dapiData['data'][frame][0])]
                Z = np.zeros((len(dapiData['data'][frame]), len(dapiData['data'][frame][0])))
                hoverInfo = dapiData['data'][frame]
                surfaceData = [go.Surface(x = X, y = Y, z = Z, surfacecolor = dapiData['data'][frame], text = hoverInfo, hoverinfo = ['x + y + text'], opacity = 0.6, showscale = False)]
                xs = trajData['meanXPixel'].tolist()
                ys = trajData['meanYPixel'].tolist()
                zs = np.zeros(len(xs))
                scatterData = go.Scatter3d(x = xs, y = ys, z = zs, mode = 'markers', marker = dict(size = 5))
                layout = go.Layout(scene = dict(aspectmode = 'data'))
                figurePlot = go.Figure(data = surfaceData + [scatterData], layout = layout)
                figurePlot.update_layout(scene = dict(xaxis = dict(visible = False), yaxis = dict(visible = False), zaxis = dict(visible = False)),
                                         scene_camera = dict(up = dict(x = 0, y = 0, z = 1), eye = dict(x = 0, y = -0.001, z = max(len(dapiData['data'][frame]), len(dapiData['data'][frame][0]))/50)))
            else:
                figurePlot = px.density_heatmap(trajData, x = "meanX", y = "meanY", nbinsx = 16, nbinsy = 16, labels = {"mutation": "Condition"})
                self.view.heatMapSlider.setDisabled(True)
        else:
            figurePlot = px.density_heatmap(trajData, x = "meanX", y = "meanY", nbinsx = 16, nbinsy = 16, labels = {"mutation": "Condition"})
            self.view.heatMapSlider.setDisabled(True)
        # self.view.fig = figurePlot
        # url = QtCore.QUrl()
        # url.setScheme(PlotlyApplication.scheme.decode())
        # self.heatMapPlot.emit(url)
        self.heatMapPlot.emit(figurePlot.to_html(include_plotlyjs='cdn'))

        # f = h5py.File(os.getcwd() + "/Data/h5-file/" + self.selectionFile[0] + ".h5", 'r') 
        # f['data'][0]
        # X, Y = np.mgrid[0:len(f['data'][0]), 0:len(f['data'][0][0])]
        # Z = np.zeros((len(f['data'][0]), len(f['data'][0][0])))
        # hoverInfo = f['data'][0]
        # # figurePlot = go.Figure(data = go.Surface(x = X, y = Y, z = Z, surfacecolor = f['data'][0], text = hoverInfo, hoverinfo = ['x + y + text'], opacity = 0.6))
        # # figurePlot.update_layout(scene = dict(xaxis = dict(visible = False), yaxis = dict(visible = False), zaxis = dict(visible = False)),
        # #                          scene_camera = dict(up = dict(x = 0, y = 0, z = 1), eye = dict(x = 0, y = -0.001, z = 1.5)))
        # surfaceData = [go.Surface(x = X, y = Y, z = Z, surfacecolor = f['data'][0], text = hoverInfo, hoverinfo = ['x + y + text'], opacity = 0.6, showscale = False)]
        # xs = trajData['meanX'].tolist()
        # ys = trajData['meanY'].tolist()
        # zs = np.zeros(len(xs))
        # scatterData = go.Scatter3d(x = xs, y = ys, z = zs, mode = 'markers', marker = dict(size = 5))
        # layout = go.Layout(scene = dict(aspectmode = 'data'))
        # figurePlot = go.Figure(data = surfaceData + [scatterData], layout = layout)
        # figurePlot.update_layout(scene = dict(xaxis = dict(visible = False), yaxis = dict(visible = False), zaxis = dict(visible = False)),
        #                          scene_camera = dict(up = dict(x = 0, y = 0, z = 1), eye = dict(x = 0, y = -0.001, z = max(len(f['data'][0]), len(f['data'][0][0]))/50)))
        
        # figurePlot = px.density_heatmap(trajData, x = "meanX", y = "meanY", nbinsx = 16, nbinsy = 16, labels = {"mutation": "Condition"})
        figureCumTrajs = px.line(trajCumData, x = "startTime", y = "Cummulative Frequency", color = "mutation", labels = {"startTime": "Time (s)", "mutation": "Condition"})
        figureLiveTrajs = px.line(trajLiveData, x = "Frame", y = "Frequency", color = "mutation", labels = {"Frame": "Time (s)", "mutation": "Condition"})
        figureLifetime = px.histogram(trajData, x = "duration", color = "mutation", labels = {"duration": "Burst lifetime (s)", "mutation": "Condition"}).update_layout(yaxis_title = "Frequency")
        # self.heatMapPlot.emit(figurePlot.to_html(include_plotlyjs='cdn'))
        
        self.heatMapCummulativeTrajs.emit(figureCumTrajs.to_html(include_plotlyjs='cdn'))
        self.heatMapLiveTrajs.emit(figureLiveTrajs.to_html(include_plotlyjs='cdn'))
        self.heatMapBurstLifetime.emit(figureLifetime.to_html(include_plotlyjs='cdn'))

        self.view.heatMapLiveTrajsFigure = figureLiveTrajs

        rMax = 20 # 1.5
        dr = 1 # 0.1
        mutList = list(dict.fromkeys(trajData["mutation"]))
        pcData = pd.DataFrame()
        for n in range(len(mutList)):
            g = self.pairCorrelationFunction_2D(trajData.loc[trajData.loc[:, "mutation"] == mutList[n], "meanX"], trajData.loc[trajData.loc[:, "mutation"] == mutList[n], "meanY"], rMax, dr)
            pcData = pd.concat([pcData, pd.Series(g, name = mutList[n]).to_frame().transpose()])
        pcData["mutation"] = pcData.index
        pcData = pd.melt(pcData, id_vars = ["mutation"])
        figurePC = px.scatter(pcData, x = "variable", y = "value", color = "mutation", labels = {"value": "g(r)", "variable": "r(\u03BCm)", "mutation": "Condition"}) 
        self.heatMapRipley.emit(figurePC.to_html(include_plotlyjs='cdn'))

    def pairCorrelationFunction_2D(self, x, y, rMax, dr):
        numberDensity = 1
        r = np.arange(0, rMax + dr, dr)
        g = np.zeros([len(x), len(r) - 1])
        x, y = np.array(x), np.array(y)
        for n in range(len(x)):
            d = np.sqrt((x - x[n])**2 + (y - y[n])**2) 
            result, bins = np.histogram(d, bins=r)
            g[n, :] = result/numberDensity
        g_average = np.zeros(len(r) - 1)
        for n in range(len(r) - 1):
            g_average[n] = np.mean(g[:, n]) / (math.pi * (r[n + 1]**2 - r[n]**2))

        # counts, xBins, yBins = np.histogram2d(x0, y0, bins = (np.arange(0, max(x0), 1.5), np.arange(0, max(y0), 1.5)))
        # xCenters = (xBins[:-1] + xBins[1:]) / 2
        # yCenters = (yBins[:-1] + yBins[1:]) / 2
        # topCount = np.percentile(counts, 95) # find top 5%
        # countsInd = np.argwhere(counts > topCount)
        # for n in range(len(countsInd)):
        #     xC, yC = xCenters[countsInd[n, 0]], yCenters[countsInd[n, 1]]
        #     x, y = x0 - xC, y0 - yC
        #     rho = np.sqrt(x**2 + y**2)
        #     phi = np.arctan2(y, x)
        #     ind = rho.argsort()
        #     rho, phi = np.array(rho)[ind], np.array(phi)[ind]
        #     # r = np.arange(0, max(rho) + dr, dr)
        #     r = np.arange(0, rMax + dr, dr)
        #     rho = pd.DataFrame(rho)
        #     rho['bins'] = pd.cut(rho[0], r)
        #     bins = pd.cut(r, r)
        #     for n in range(len(bins)):
        #         rho.loc[rho['bins'] == bins[n], 'bin'] = n
                
        #     g = np.zeros(len(r) - 1)
        #     dg = np.zeros(len(r) - 1)
        #     for n in range(len(r) - 1):
        #         m = rho['bin'] == n
        #         n2 = sum(m)
        #         if n2 == 0:
        #             g[n], dg[n] = 0, 0
        #         else:
        #             g[n] = sum(phi[m]) / n2
        #             dg[n] = np.sqrt(sum(((phi - g[n])**2)[m])) / n2
        return g_average

    def update(self, selectionFile):
        self.selectionFile = selectionFile

class updateHeatMapPlot(QtCore.QThread):
    heatMapPlot = pyqtSignal([object])
    heatMapLiveTrajs = pyqtSignal([object])

    def __init__(self, view):
        super().__init__()
        self.view = view

    def run(self):
        dapiData = self.view.dapiData
        tData = self.view.tData

        X, Y = np.mgrid[0:len(dapiData['data'][self.frame]), 0:len(dapiData['data'][self.frame][0])]
        Z = np.zeros((len(dapiData['data'][self.frame]), len(dapiData['data'][self.frame][0])))
        hoverInfo = dapiData['data'][self.frame]
        surfaceData = [go.Surface(x = X, y = Y, z = Z, surfacecolor = dapiData['data'][self.frame], text = hoverInfo, hoverinfo = ['x + y + text'], opacity = 0.6, showscale = False)]
        trackInFrame = tData.loc[tData["Frame"] == self.frame + 1]
        xs = trackInFrame['x'].tolist()
        ys = trackInFrame['y'].tolist()
        zs = np.zeros(len(xs))
        scatterData = go.Scatter3d(x = xs, y = ys, z = zs, mode = 'markers', marker = dict(size = 5))
        layout = go.Layout(scene = dict(aspectmode = 'data'))
        figurePlot = go.Figure(data = surfaceData + [scatterData], layout = layout)
        figurePlot.update_layout(scene = dict(xaxis = dict(visible = False), yaxis = dict(visible = False), zaxis = dict(visible = False)),
                                              scene_camera = dict(up = dict(x = 0, y = 0, z = 1), eye = dict(x = 0, y = -0.001, z = max(len(dapiData['data'][self.frame]), len(dapiData['data'][self.frame][0]))/50)))
        self.view.fig = figurePlot
        # url = QtCore.QUrl()
        # url.setScheme(PlotlyApplication.scheme.decode())
        # self.heatMapPlot.emit(url)
        self.heatMapPlot.emit(figurePlot.to_html(include_plotlyjs='cdn'))

        # Plotting the grey line on the live trajectory plot to show the time of the DAPI plot
        figureLiveTrajs = copy.copy(self.view.heatMapLiveTrajsFigure)
        frameTime = self.frame * tData["exposure_time"][0]
        maxY = np.max([trace_data.y for trace_data in figureLiveTrajs.data])
        boundaryLine = pd.DataFrame({"x": [frameTime, frameTime], "y": [0, maxY]})
        figureLiveTrajs.add_trace(px.line(boundaryLine, x = "x", y = "y", line_dash_sequence = ["longdashdot"], color_discrete_sequence = ["#7F7F7F"]).data[0])
        self.heatMapLiveTrajs.emit(figureLiveTrajs.to_html(include_plotlyjs='cdn'))

    def update(self, frame):
        self.frame = frame

class produceAnglePlot(QtCore.QThread):
    mutHistSignal = pyqtSignal([object])
    trackAngleMut = pyqtSignal([object])
    trackAngleState = pyqtSignal([object])
    trackAngleBound = pyqtSignal([object])
    trackAngleDiffu = pyqtSignal([object])
    trackAngleBox = pyqtSignal([object])

    def __init__(self, model):
        super().__init__()
        self.model = model
    
    def run(self):
        data = self.model.getAngleData(self.selectionFile)
        dataTrack = self.model.getAngleTrackFiles(self.selectionFile)
        mutHist, stateHist, boundHist, diffuHist, trendPlot, boxPlot = self.model.produceAnglePlots(data, dataTrack, self.boundaryValue, self.selectionAngle, self.viewAllData)
        self.mutHistSignal.emit(mutHist)
        self.trackAngleMut.emit(mutHist.to_html(include_plotlyjs='cdn'))
        self.trackAngleState.emit(stateHist.to_html(include_plotlyjs='cdn'))
        self.trackAngleBound.emit(boundHist.to_html(include_plotlyjs='cdn'))
        self.trackAngleDiffu.emit(diffuHist.to_html(include_plotlyjs='cdn'))
        self.trackAngleBox.emit(boxPlot.to_html(include_plotlyjs='cdn'))

    def update(self, selectionFile, selectionAngle, angleRatio, boundaryValue, viewAllData):
        self.selectionFile = selectionFile
        self.selectionAngle = selectionAngle
        self.angleRatio = angleRatio
        self.boundaryValue = boundaryValue
        self.viewAllData = viewAllData

class ErrorMessageWindow(QWidget):
    def __init__(self, errorMessage):
        super().__init__()
        layout = QGridLayout()
        self.label = QLabel(errorMessage)
        layout.addWidget(self.label)
        self.setLayout(layout)
        # self.setWindowTitle("Files Failed Quality Control")

    def update(self, errorMessage):
        self.label.setText(errorMessage)

class ExportDatabaseWindow(QWidget):
    def __init__(self, dirPath):
        super().__init__()
        layout = QGridLayout()
        self.label = QLabel('Export database as:')
        self.name = QLineEdit()
        self.exportButton = QPushButton("Export Database")
        self.exportButton.setDefault(True)
        self.exportButton.pressed.connect(partial(self.exportDatabase, dirPath))
        layout.addWidget(self.label)
        layout.addWidget(self.name)
        layout.addWidget(self.exportButton)
        self.setLayout(layout)
        self.setWindowTitle("Export Database")

    def exportDatabase(self, dirPath):
        if self.name.text() == "":
            self.errorWindow = ErrorMessageWindow("Please enter valid name for the database.")
            self.errorWindow.show()
        else:
            shutil.copyfile('database.db', dirPath + '/' + self.name.text() + '.db')
            self.close()

class ImportDatabaseWindow(QWidget):
    def __init__(self, GICWindow, databasePath):
        super().__init__()
        self.GICWindow = GICWindow
        self.databasePath = databasePath[0]
        layout = QGridLayout()
        self.importLabel = QLabel('There are data in the dashboard at the moment, what do you want to do?')
        self.overwriteButton = QPushButton("Overwrite Database")
        self.overwriteButton.setDefault(True)
        self.appendButton = QPushButton("Combine Database")
        self.appendButton.setDefault(True)
        self.overwriteButton.pressed.connect(partial(self.importDatabaseChoice, "overwrite"))
        self.appendButton.pressed.connect(partial(self.importDatabaseChoice, "append"))
        layout.addWidget(self.importLabel, 0, 0)
        layout.addWidget(self.overwriteButton, 1, 0)
        layout.addWidget(self.appendButton, 1, 1)
        self.setLayout(layout)
        self.setWindowTitle("Database Import Options")

    def importDatabaseChoice(self, importChoice):
        if importChoice == "overwrite":
            os.remove("database.db")
            shutil.copyfile(self.databasePath, 'database.db')
        else:
            with sqlite3.connect(self.databasePath) as conn:
                dataFile = pd.read_sql_query("select * from FileList", conn)
                dataTraj = pd.read_sql_query("select * from TrajectoryList", conn)
                dataTrack = pd.read_sql_query("select * from TrackList", conn)
                dataJD = pd.read_sql_query("select * from JDList", conn)
                dataAngle = pd.read_sql_query("select * from AngleList", conn)
                try:
                    dataDwellTime = pd.read_sql_query("select * from DwellTimeData", conn)
                except:
                    dataDwellTime = 0
            with sqlite3.connect('database.db') as conn:
                dataFile.drop(columns = ["index"], inplace = True)
                dataTraj.drop(columns = ["index"], inplace = True)
                dataTrack.drop(columns = ["index"], inplace = True)
                dataJD.drop(columns = ["index"], inplace = True)
                dataAngle.drop(columns = ["index"], inplace = True)
                dataFile.to_sql('FileList', conn, if_exists="append")
                dataTraj.to_sql('TrajectoryList', conn, if_exists="append")
                dataTrack.to_sql('TrackList', conn, if_exists="append")
                dataJD.to_sql('JDList', conn, if_exists="append")
                dataAngle.to_sql('AngleList', conn, if_exists="append")
                if dataDwellTime != 0:
                    dataDwellTime.drop(columns = ["index"], inplace = True)
                    dataDwellTime.to_sql('DwellTimeData', conn, if_exists="append")
        self.GICWindow._loadExistingData()
        self.close()

class PopUpThread(QtCore.QThread):
    def __init__(self, UI, errorMessage):
        super().__init__()
        self.UI = UI
        self.errorMessage = errorMessage
    
    def __del__(self):
        self.wait()

    def run(self):
        self.UI.window = ErrorMessageWindow(self.errorMessage)
        self.UI.window.show()

class Controller:
    def __init__(self, model, view):
        self._model = model
        self._view = view
        self._buttonResponse()
        self._loadExistingData()
        # Creating a thread for jump distance plots
        self.produceJumpDistanceFigure = produceJumpDistancePlot(self._model)
        # Prepare to receive signals from the jump distance plot and link the signals to appropriate plots/figures
        self.produceJumpDistanceFigure.diffusionTrack2Par.connect(self._view.diffusionTrack2Par_browser.setHtml)
        self.produceJumpDistanceFigure.diffusionTrack3Par.connect(self._view.diffusionTrack3Par_browser.setHtml)
        self.produceJumpDistanceFigure.diffusionTrack2ParBox.connect(self._view.diffusionTrack2ParBox_browser.setHtml)
        self.produceJumpDistanceFigure.diffusionTrack3ParBox.connect(self._view.diffusionTrack3ParBox_browser.setHtml)
        self.produceJumpDistanceFigure.tableData.connect(self.jumpDistanceTableUpdate)

        self.produceAngleFigure = produceAnglePlot(self._model)
        self.produceAngleFigure.trackAngleMut.connect(self._view.trackAngleMut_browser.setHtml)
        self.produceAngleFigure.trackAngleState.connect(self._view.trackAngleState_browser.setHtml)
        self.produceAngleFigure.trackAngleBound.connect(self._view.trackAngleBound_browser.setHtml)
        self.produceAngleFigure.trackAngleDiffu.connect(self._view.trackAngleDiffu_browser.setHtml)
        self.produceAngleFigure.trackAngleBox.connect(self._view.trackAngleBox_browser.setHtml)

        self.produceHeatMapFigure = produceHeatMapPlot(self._model, self._view)
        self.produceHeatMapFigure.heatMapPlot.connect(self._view.heatMapPlot.setHtml)
        # self.produceHeatMapFigure.heatMapPlot.connect(self._view.heatMapPlot.load)
        self.produceHeatMapFigure.heatMapCummulativeTrajs.connect(self._view.heatMapCummulativeTrajs.setHtml)
        self.produceHeatMapFigure.heatMapLiveTrajs.connect(self._view.heatMapLiveTrajs.setHtml)
        self.produceHeatMapFigure.heatMapBurstLifetime.connect(self._view.heatMapBurstLifetime.setHtml)
        self.produceHeatMapFigure.heatMapRipley.connect(self._view.heatMapRipley.setHtml)

        self.heatMapSliderUpdate = updateHeatMapPlot(self._view)
        self.heatMapSliderUpdate.heatMapPlot.connect(self._view.heatMapPlot.load)
        self.heatMapSliderUpdate.heatMapLiveTrajs.connect(self._view.heatMapLiveTrajs.setHtml)
        # self._view.trajectoryPlotTab.layout.count()
        # self._view.trajectoryPlotTab.layout.itemAt(1).widget().setValue(0)
        # self._view.trajectoryPlotTab.layout.itemAtPosition(0,0)

        # Plots download
        self.produceAngleFigure.mutHistSignal.connect(self.saveSVG)
        self._view.trackAngleMut_browser.page().profile().downloadRequested.connect(self.savePlot)

    def saveSVG(self, plot):
        plotly.io.write_image(plot, "Images/plot.svg")
        return
    
    def savePlot(self, download):
        # https://stackoverflow.com/questions/62545804/issue-about-plotly-when-clicked-the-download-plot-icon-within-pyqt5-qwebenginevi
        # save_file_name_dialog is a function to show the windows file window
        # image_path = save_file_name_dialog(self, "Choose your file", "Png files (*.png)")
        # if path:
            # download.setPath(image_path)
            # download.accept()
        download.setPath("Images/newplot.png")
        download.accept()
        return

    def uploadFileButton(self, fileType):
        if not os.path.exists(os.path.realpath(os.getcwd() +"/Data")):
            os.mkdir(os.path.realpath(os.getcwd() +"/Data"))
        if not os.path.exists(os.path.realpath(os.getcwd() +"/Data/" + "fast-raw")):
            os.mkdir(os.path.realpath(os.getcwd() +"/Data/" + "fast-raw"))
        if not os.path.exists(os.path.realpath(os.getcwd() +"/Data/" + "fast-tif")):
            os.mkdir(os.path.realpath(os.getcwd() +"/Data/" + "fast-tif"))
        if not os.path.exists(os.path.realpath(os.getcwd() +"/Data/" + "h5-file")):
            os.mkdir(os.path.realpath(os.getcwd() +"/Data/" + "h5-file"))
        selectionFile = self._view.comboFileList.currentData()
        if selectionFile == []:
            selectionFile = [self._view.comboFileList.itemText(i) for i in range(self._view.comboFileList.count())]
        if selectionFile != []:
            1 # TODO: gives warning about adding data to existing database
        if fileType == "raw_files":
            files = QFileDialog.getOpenFileNames(self._view, "Choose File", os.getcwd(), 'Images (*.tif)')
        else:
            files = QFileDialog.getOpenFileNames(self._view, "Choose File", os.getcwd(), 'MATLAB Files (*.mat)')
        if os.path.exists(os.path.realpath(os.getcwd()) + "/Data/fast-raw/" "rejectedFiles.mat"):
            os.remove(os.path.realpath(os.getcwd()) + "/Data/fast-raw/" "rejectedFiles.mat")
        if files[1] != "":
            temp = files[0][0].split("/")
            input_path = temp[0] + "/"
            for n in range(len(temp) - 2):
                input_path += temp[n+1] + "/"
            file_names = np.zeros((len(files[0]),), dtype=object)
            for n in range(len(files[0])):
                file_names[n] = files[0][n].split("/")[-1][:-4]
            if self._view.acquisitionRateFast.isChecked():
                acquisition_rate = "fast"
            elif self._view.acquisitionRateSlow.isChecked():
                acquisition_rate = "slow"
            if self._view.analysisTypePercentage.isChecked():
                analysis_type = "percentage"
            elif self._view.analysisTypeNumber.isChecked():
                analysis_type = "number"
            exposureTime = self._view.exposureTimeBox.value() / 1000
            pixelSize = self._view.pixelSize.value()
            impars = {"PixelSize": self._view.pixelSize.value(),
                      "psf_scale": self._view.psfScaling.value(),
                      "wvlnth": float(self._view.emissionWavelengthBox.value()),
                      "iNA": float(self._view.detectionObjectiveNA.value()),
                      "psfStd": self._view.psfScaling.value() * 0.55 * (self._view.emissionWavelengthBox.value() / 1000) / self._view.detectionObjectiveNA.value() / 1.17 / 2 / self._view.pixelSize.value(),
                      "FrameRate": float(self._view.exposureTimeBox.value() / 1000),
                      "FrameSize": float(self._view.exposureTimeBox.value() / 1000)
                     }
            locpars = {"wn": float(self._view.detectionBox.value()),
                       "errorRate": float(self._view.localizationErrorBox.value()),
                       "dfltnLoops": float(self._view.deflationLoopsNumberBox.value()),
                       "minInt": float(self._view.minIntensity.value()),
                       "maxOptimIter": float(self._view.maxIteration.value()),
                       "termTol": float(self._view.terminationTolerance.value()),
                       "isRadiusTol": self._view.radiusTolerance.isChecked(),
                       "radiusTol": float(self._view.radiusToleranceValue.value()),
                       "posTol": float(self._view.positionTolerance.value()),
                       "optim": [float(self._view.maxIteration.value()), float(self._view.terminationTolerance.value()), float(self._view.radiusTolerance.isChecked()), float(self._view.radiusToleranceValue.value()), float(self._view.positionTolerance.value())],
                       "isThreshLocPrec": self._view.threshLocPrec.isChecked(),
                       "minLoc": float(self._view.minLoc.value()),
                       "maxLoc": inf,
                       "isThreshSNR": self._view.threshSNR.isChecked(),
                       "minSNR": float(self._view.minSNR.value()),
                       "maxSNR": inf,
                       "isThreshDensity": self._view.threshDensity.isChecked()
                      }
            if self._view.maxLoc.value() > 0:
                locpars.update({"maxLoc": float(self._view.maxLoc.value())})
            if self._view.maxSNRIter.value() > 0:
                locpars.update({"maxSNR": float(self._view.maxSNRIter.value())})
            trackpars = {"trackStart": float(self._view.trackStart.value()),
                         "trackEnd": inf,
                         "Dmax": float(self._view.diffusionConstantMaxBox.value()),
                         "searchExpFac": float(self._view.exponentialFactorSearch.value()),
                         "statWin": float(self._view.statWin.value()),
                         "maxComp": float(self._view.compMax.value()),
                         "maxOffTime": float(self._view.gapsAllowedBox.value()),
                         "intLawWeight": float(self._view.intLawWeight.value()),
                         "diffLawWeight": float(self._view.difLawWeight.value())
                        }
            if self._view.trackEnd.value() > 0:
                locpars.update({"trackEnd": float(self._view.trackEnd.value())})
            uploadParameters = pd.DataFrame({"impars": impars, "locpars": locpars, "trackpars": trackpars,
                                             "bleach_rate": self._view.bleachRate.value(), "traj_length": self._view.trajectoryLengthBox.value(),
                                             "min_traj": self._view.minTrajectoryNumberBox.value(), "clip_factor": self._view.clipFactorBox.value(),
                                             "tol": self._view.toleranceBox.value()})
            scipy.io.savemat("tifupload.mat", {"input_path": input_path,
                                               "output_path": os.getcwd() + "/Data/fast-tif/",
                                               "output_path_further_processing": os.getcwd() + "/Data/fast-raw/",
                                               "file_names": file_names,
                                               "acquisition_rate": acquisition_rate,
                                               "analysis_type": analysis_type,
                                               "bleach_rate": self._view.bleachRate.value(),
                                               "impars": impars,
                                               "locpars": locpars,
                                               "trackpars": trackpars,
                                               "traj_length": self._view.trajectoryLengthBox.value(),
                                               "min_traj": self._view.minTrajectoryNumberBox.value(),
                                               "clip_factor": self._view.clipFactorBox.value(),
                                               "tol": self._view.toleranceBox.value(),
                                               "runParallel": self._view.parallelization.isChecked(),
                                               "ExposureTime": float(self._view.exposureTimeBox.value()),
                                               "numCores": self._view.parallelizationCores.value()
                                              }
                            )
            if sys.platform == "win32":
                # Windows
                if fileType == "raw_files":
                    # os.system("matlab.exe -wait -nodesktop -nosplash -r \"run([pwd, '../SPT_LocAndTrack/fastSPT_JF549_TIFF_Diffusion.m']); exit(1)\"")
                    os.system("matlab.exe -wait -nodesktop -nosplash -r \"matLoc = \'" + os.getcwd() + "\'; run(\'" + str(self._view.libDir.joinpath("SPT_LocAndTrack/fastSPT_JF549_TIFF_Diffusion.m")) + "\'); exit(1)\"")
                elif fileType == "post_files":
                    # os.system("matlab.exe -wait -nodesktop -nosplash -r \"run([pwd, '../SPT_LocAndTrack/UploadExistingData.m']); exit(1)\"")
                    os.system("matlab.exe -wait -nodesktop -nosplash -r \"matLoc = \'" + os.getcwd() + "\'; run(\'" + str(self._view.libDir.joinpath("SPT_LocAndTrack/UploadExistingData.m")) + "\'); exit(1)\"")
            elif sys.platform == "darwin":
                # MacOS
                MATLAB_Versions = [matlab for matlab in os.listdir("/Applications/") if fnmatch.fnmatch(matlab, "MATLAB_*.app")]
                if len(MATLAB_Versions) == 0:
                    # MATLAB Not Installed
                    errorMessage = ErrorMessageWindow("No Installation of MATLAB Found.")
                    errorMessage.show()
                else:
                    MATLAB_To_Run = "/Applications/" + MATLAB_Versions[-1] + "/bin/matlab"
                    if fileType == "raw_files":
                        # os.system(MATLAB_To_Run + " -wait -nodesktop -nosplash -r \"run([pwd, '/SPT_LocAndTrack/fastSPT_JF549_TIFF_Diffusion.m']); exit(1)\"")
                        os.system(MATLAB_To_Run + " -wait -nodesktop -nosplash -r \"matLoc = \'" + os.getcwd() + "\'; run(\'" + str(self._view.libDir.joinpath("SPT_LocAndTrack/fastSPT_JF549_TIFF_Diffusion.m")) + "\'); exit(1)\"")
                    elif fileType == "post_files":
                        # os.system(MATLAB_To_Run + " -wait -nodesktop -nosplash -r \"run([pwd, '/SPT_LocAndTrack/UploadExistingData.m']); exit(1)\"")
                        os.system(MATLAB_To_Run + " -wait -nodesktop -nosplash -r \"matLoc = \'" + os.getcwd() + "\'; run(\'" + str(self._view.libDir.joinpath("SPT_LocAndTrack/UploadExistingData.m")) + "\'); exit(1)\"")
            # load new file_names and potentially display file_names that have been removed
            if (fileType == "raw_files") or (fileType == "post_files"):
                filenames = scipy.io.loadmat(os.path.realpath(os.getcwd()) + "/Data/fast-raw/" "acceptedFiles.mat")
                filenames = [file[0][:] for file in filenames['Filenames'][0]] # the [:] is to account for dtype <U31
                rejectedFiles = scipy.io.loadmat(os.path.realpath(os.getcwd()) + "/Data/fast-raw/" "rejectedFiles.mat")
                if len(rejectedFiles['rejectedFiles']) > 0:
                    rejectedFiles = [file[0][:] for file in rejectedFiles['rejectedFiles'][0]] # the [:] is to account for dtype <U31
                    self.errorMessage = ErrorMessageWindow("The following file(s) did not meet your Quality Control and has been removed from analysis:\n" + '\n'.join(rejectedFiles))
                    self.errorMessage.show()

                    # self.thread = QtCore.QThread()
                    # self.errorMessage.moveToThread(self.thread)
                    # self.thread.started.connect(partial(self.errorMessage.update, "a"))
                    # self.errorMessage = PopUpThread(self._view, "The following file(s) did not meet your Quality Control and has been removed from analysis:\n" + '\n'.join(filenames))
                    # self.errorMessage.start() #TODO: Thread this
            else:
                filenames = file_names
            dataFile, dataTraj, dataTrack, dataJD, dataAngle, dataDwellTime = self._model.processUploadedFileToDatabase(filenames, acquisition_rate, exposureTime, pixelSize, uploadParameters) # file_names is all files, including rejected files
            if len(dataFile) > 0:
                with sqlite3.connect('database.db') as conn:
                    dataFile.to_sql('FileList', conn, if_exists="append")
                    dataTraj.to_sql('TrajectoryList', conn, if_exists="append")
                    dataTrack.to_sql('TrackList', conn, if_exists="append")
                    dataJD.to_sql('JDList', conn, if_exists="append")
                    dataAngle.to_sql('AngleList', conn, if_exists="append")
                    if len(dataDwellTime) > 0:
                        dataDwellTime.to_sql('DwellTimeData', conn, if_exists="append") # TODO: Make a new table for dwell time data
                    textData = pd.DataFrame({"text": self._view.textEdit.toPlainText()}, index = [0])
                    textData.to_sql('Settings', conn, if_exists="replace")
                self._loadExistingData()

    # File Selection Tabs
    def comboMutationUpdate(self):
        data = self._model.updateMutationFilelist(self._view.comboAcquisitionRate.currentData())
        self._view.comboMutation.model().clear()
        self._view.comboMutation.addItems(set(data['mutation']))
        self._view.comboMutation.updateText()
        self._view.comboFileList.model().clear()
        self._view.comboFileList.addItems(set(data['filename']))
        self._view.comboFileList.updateText()
        # Ticking all files
        self._view.comboMutation.checkAll()

    def comboFileListUpdate(self):
        data = self._model.updateFilelist(self._view.comboAcquisitionRate.currentData(), self._view.comboMutation.currentData())
        self._view.comboFileList.model().clear()
        self._view.comboFileList.addItems(set(data['filename']))
        self._view.comboFileList.updateText()
        # Ticking all files
        self._view.comboFileList.checkAll()

    def sidebarFileList(self):
        data = self._model.getSelectedFiles(self._view.comboAcquisitionRate.currentData(), self._view.comboMutation.currentData(), self._view.comboFileList.currentData(), "FileList")
        return data

    def unselectAllFiles(self):
        # TODO: Disable the calculation while unticking or untick all at once instead of bringing user back to homepage
        # Brings user back to home page to prevent it compute as it untick
        self._view.tabs.setCurrentIndex(0)
        # Unticking all files
        self._view.comboFileList.uncheckAll()

    def deleteFiles(self):
        selectionFile = self._view.comboFileList.currentData()
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                data = pd.read_sql_query(f"SELECT TrackList.trajID FROM TrackList INNER JOIN TrajectoryList ON TrackList.trajID = TrajectoryList.trajID AND TrajectoryList.filename IN {tuple(selectionFile)}", conn)
                trajIDs = tuple(pd.unique(data.trajID))
                conn.execute(f"DELETE FROM TrackList WHERE TrackList.trajID IN {trajIDs}")
                conn.execute(f"DELETE FROM TrajectoryList WHERE TrajectoryList.filename IN {tuple(selectionFile)}")
                conn.execute(f"DELETE FROM JDList WHERE JDList.filename IN {tuple(selectionFile)}")
                conn.execute(f"DELETE FROM DwellTimeData WHERE DwellTimeData.filename IN {tuple(selectionFile)}")
                conn.execute(f"DELETE FROM FileList WHERE FileList.filename IN {tuple(selectionFile)}")
            else:
                data = pd.read_sql_query(f"SELECT TrackList.trajID FROM TrackList INNER JOIN TrajectoryList ON TrackList.trajID = TrajectoryList.trajID AND TrajectoryList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
                trajIDs = tuple(pd.unique(data.trajID))
                conn.execute(f"DELETE FROM TrackList WHERE TrackList.trajID IN {trajIDs}")
                conn.execute("DELETE FROM TrajectoryList WHERE TrajectoryList.filename = ?", (selectionFile[0],))
                conn.execute("DELETE FROM JDList WHERE JDList.filename = ?", (selectionFile[0],))
                conn.execute("DELETE FROM DwellTimeData WHERE DwellTimeData.filename = ?", (selectionFile[0],))
                conn.execute("DELETE FROM FileList WHERE FileList.filename = ?", (selectionFile[0],))
        self._loadExistingData()
        return

    # Plotting
    def plotTrajectory(self, *args):
        trajNumber = int(self._view.trajNumberBox.text())
        jumpNumber = int(self._view.jumpNumberDrawBox.text())
        trajLength = int(self._view.minTrajLength.text())
        selectionFile = self._view.comboFileList.currentData()
        if len(selectionFile) > 1:
            self._view.trajectory_browser.setHtml("")
        else:
            data = self._model.getTrackFiles(selectionFile)
            if (trajNumber > 0) and (jumpNumber > 0) and (trajLength > 0):
                df = self._model.plotTrajectory_data(trajLength, trajNumber, jumpNumber, data)

            # if self._view.trajTabTrajGroupButton.isChecked():
            #     figure = px.line(df, x = "x", y = "y", color = "trajID")
            # elif self._view.trajTabSpeedGroupButton.isChecked():
            #     1
                figure = px.line(df, x = "x", y = "y", color = "trajID", labels = {"x": "X (\u03BCm)", "y": "Y (\u03BCm)"})
                figure.layout.update(showlegend = False)
                self._view.trajectory_browser.setHtml(figure.to_html(include_plotlyjs='cdn'))

    def trajectoryData(self):
        selectionFile = self._view.comboFileList.currentData()
        try:
            data = self._model.getTrajectoryDataFiles(selectionFile)
            boxData = data >> group_by(X.filename, X.mutation) >> summarize(TrajNumber = summary_functions.n_distinct(X.trajID))
            boxFigure = px.box(boxData, y = "TrajNumber", color = "mutation", points = "all", hover_name = "filename", labels = {"mutation": "Condition"})
            densityData = data >> group_by(X.filename, X.mutation) >> summarize(TrajNumber = summary_functions.n_distinct(X.trajID), CellArea = summary_functions.mean(X.pixelSize)** 2 * summary_functions.mean(X.cellSize))
            densityData["TrajDensity"] = densityData.loc[:, "TrajNumber"] / densityData.loc[:, "CellArea"]
            densityFigure = px.box(densityData, y = "TrajDensity", color = "mutation", points = "all", hover_name = "filename", labels = {"TrajDensity": "Trajectories per Area (um^2)", "mutation": "Condition"})
            # boxFigure = self._model.add_pvalue_annotation(boxFigure, boxData, "mutation", ["WT", "WT-Cy"], "TrajNumber", [1.00, 1.01])
            self._view.trajectoryNumberBox_browser.setHtml(boxFigure.to_html(include_plotlyjs='cdn'))
            self._view.trajectoryDensityBox_browser.setHtml(densityFigure.to_html(include_plotlyjs='cdn'))
        except:
            pass

    def diffusionPlotUpdate(self):
        try:
            selectionFile = self._view.comboFileList.currentData()
            if self._view.diffusionErrorVariation.isChecked() == True:
                errorView = 0
            elif self._view.diffusionErrorSTD.isChecked() == True:
                errorView = 1
            else:
                errorView = 2
            data = self._model.getTrajectoryFiles(selectionFile)
            if self._view.boundaryComputation.currentText() == "Formula":
                boundaryValue = np.log10(data.loc[0, "pixelSize"]**2 / (4 * 4 * data.loc[0, "exposure_time"]))
            else:
                boundaryValue = self._view.boundaryRawValue.value()
            figure, pieFigure = self._model.produceDiffusionData(data, self._view.diffusionBinSize.value(), self._view.diffusionLowerLimit.value(), self._view.diffusionUpperLimit.value(), errorView, boundaryValue) 
            # plotly.io.write_image(pieFigure, "Images/DiffusionPieFigure.svg")
            self._view.diffusion_browser.setHtml(figure.to_html(include_plotlyjs='cdn'))
            self._view.diffusionFraction_browser.setHtml(pieFigure.to_html(include_plotlyjs='cdn'))
            self._view.diffusionFraction_browser.setMinimumHeight(400 * len(list(set(data["mutation"]))))
        except:
            self._view.diffusion_browser.setHtml("")
            self._view.diffusionFraction_browser.setHtml("")

    def jumpDistancePlotUpdate(self):
        self._view.diffusionTrack2Par_browser.setHtml(self._view.loadingHtml)
        self._view.diffusionTrack3Par_browser.setHtml(self._view.loadingHtml)
        self._view.diffusionTrack2ParBox_browser.setHtml(self._view.loadingHtml)
        self._view.diffusionTrack3ParBox_browser.setHtml(self._view.loadingHtml)
        selectionFile = self._view.comboFileList.currentData()
        if selectionFile == []:
            return
        # data = self._model.getJumpDistanceData(selectionFile)
        self.produceJumpDistanceFigure.terminate()
        self.produceJumpDistanceFigure.update(selectionFile, self._view.jumpDistanceConsidered.value())
        self.produceJumpDistanceFigure.start()
    
    def jumpDistanceTableUpdate(self, data):
        # Set table
        mutNumber = len(list(set(data["mutation"])))
        mutList = list(set(data["mutation"]))
        mutList.sort()
        self._view.twoParTable.setColumnCount(mutNumber)
        self._view.twoParTable.setHorizontalHeaderLabels(mutList)
        self._view.twoParTable.setRowCount(5)
        self._view.twoParTable.setVerticalHeaderLabels(["n", "D1 (μm²/s)", "D2 (μm²/s)", "Bound Fraction", "SSR"])
        for n in range(mutNumber):
            subData = data.loc[data.loc[:, "mutation"] == mutList[n],]
            self._view.twoParTable.setItem(0, n, QTableWidgetItem(str(round(sum(list(set(subData["twoParN"]))), 2)) + " +/- " + str(round(sum(list(set(subData["twoPardN"]))), 2))))
            self._view.twoParTable.setItem(1, n, QTableWidgetItem(str(round(np.mean(list(set(subData["twoParD1"]))), 2)) + " +/- " + str(round(np.mean(list(set(subData["twoPardD1"]))), 2))))
            self._view.twoParTable.setItem(2, n, QTableWidgetItem(str(round(np.mean(list(set(subData["twoParD2"]))), 2)) + " +/- " + str(round(np.mean(list(set(subData["twoPardD2"]))), 2))))
            self._view.twoParTable.setItem(3, n, QTableWidgetItem(str(round(np.mean(list(set(subData["twoParf1"]))), 2)) + " +/- " + str(round(np.mean(list(set(subData["twoPardf1"]))), 2))))
            self._view.twoParTable.setItem(4, n, QTableWidgetItem(str(round(np.mean(list(set(subData["twoParSSR"]))), 2))))
     
        self._view.threeParTable.setColumnCount(mutNumber)
        self._view.threeParTable.setHorizontalHeaderLabels(mutList)
        self._view.threeParTable.setRowCount(7)
        self._view.threeParTable.setVerticalHeaderLabels(["n", "D1 (μm²/s)", "D2 (μm²/s)", "D3 (μm²/s)", "Bound Fraction", "Mixed Fraction", "SSR"])
        for n in range(mutNumber):
            subData = data.loc[data.loc[:, "mutation"] == mutList[n],]
            self._view.threeParTable.setItem(0, n, QTableWidgetItem(str(round(sum(list(set(subData["threeParN"]))), 2)) + " +/- " + str(round(np.sum(list(set(subData["threePardN"]))), 2))))
            self._view.threeParTable.setItem(1, n, QTableWidgetItem(str(round(np.mean(list(set(subData["threeParD1"]))), 2)) + " +/- " + str(round(np.mean(list(set(subData["threePardD1"]))), 2))))
            self._view.threeParTable.setItem(2, n, QTableWidgetItem(str(round(np.mean(list(set(subData["threeParD2"]))), 2)) + " +/- " + str(round(np.mean(list(set(subData["threePardD2"]))), 2))))
            self._view.threeParTable.setItem(3, n, QTableWidgetItem(str(round(np.mean(list(set(subData["threeParD3"]))), 2)) + " +/- " + str(round(np.mean(list(set(subData["threePardD3"]))), 2))))
            self._view.threeParTable.setItem(4, n, QTableWidgetItem(str(round(np.mean(list(set(subData["threeParf1"]))), 2)) + " +/- " + str(round(np.mean(list(set(subData["threePardf1"]))), 2))))
            self._view.threeParTable.setItem(5, n, QTableWidgetItem(str(round(np.mean(list(set(subData["threeParf2"]))), 2)) + " +/- " + str(round(np.mean(list(set(subData["threePardf2"]))), 2))))
            self._view.threeParTable.setItem(6, n, QTableWidgetItem(str(round(np.mean(list(set(subData["threeParSSR"]))), 2))))

    def jumpDistanceDataSave(self):
        selectionFile = self._view.comboFileList.currentData()
        if selectionFile == []:
            return
        # data = self._model.getJumpDistanceData(selectionFile) #TODO:
        twoParBoxData, threeParBoxData = self._model.getJumpDistanceBoxData(selectionFile)
        twoParBoxData.to_csv("Two_Parameter_Fit.csv")
        threeParBoxData.to_csv("Three_Parameter_Fit.csv")

    def anglePlot(self):
        self._view.trackAngleMut_browser.setHtml(self._view.loadingHtml)
        self._view.trackAngleState_browser.setHtml(self._view.loadingHtml)
        self._view.trackAngleBound_browser.setHtml(self._view.loadingHtml)
        self._view.trackAngleDiffu_browser.setHtml(self._view.loadingHtml)
        self._view.trackAngleBox_browser.setHtml(self._view.loadingHtml)
        selectionFile = self._view.comboFileList.currentData()
        if selectionFile == []:
            return
        allMutation = [self._view.comboMutation.itemText(i) for i in range(self._view.comboMutation.count())]
        allFile = [self._view.comboFileList.itemText(i) for i in range(self._view.comboFileList.count())]
        if (((self._view.comboMutation.currentData() == []) or (self._view.comboMutation.currentData() == allMutation)) and (allFile == selectionFile)):
            viewAllData = True
        else:
            viewAllData = False
        selectionAngle = self._view.angleSelection.currentData()
        if selectionAngle == []:
            selectionAngle = [self._view.angleSelection.itemText(i) for i in range(self._view.angleSelection.count())]
        angleRatio = self._view.angleRatio
        boundaryValue = self._view.boundaryValueAngle.value()
        # data = self._model.getAngleData(selectionFile)
        # dataTrack = self._model.getAngleTrackFiles(selectionFile)
        # mutHist, stateHist, boundHist, diffuHist, trendPlot, boxPlot = self._model.produceAnglePlots(data, dataTrack, boundaryValue, selectionAngle, viewAllData)
        self.produceAngleFigure.terminate()
        self.produceAngleFigure.update(selectionFile, selectionAngle, angleRatio, boundaryValue, viewAllData)
        self.produceAngleFigure.start()

        # self._view.fig = trendPlot # TODO: Temporary fix by setting a figure to view scene so it can be captured by the url generator.
        # url = QtCore.QUrl()
        # url.setScheme(PlotlyApplication.scheme.decode())
        # self._view.trackAngleBox_browser.load(url)       

    def dOTMapUpdate(self):
        selectionFile = self._view.comboFileList.currentData()
        if selectionFile == []:
            return
        dOTRegions = [float(i) for i in self._view.dOTRegionArea.text().split(",")]
        # data = self._model.getDOTFiles(selectionFile)
        # tableData, boxData, figure = self._model.getDOTData(data, dOTRegions, self._view.dOTMinTrajLength.value())

        # Angle data
        dataAngle = self._model.getDOTAngleData(selectionFile)
        tableData, boxData, figure = self._model.produceDOTAngleData(dataAngle, dOTRegions, self._view.dOTMinTrajLength.value(), self._view.dOTAngleMaxAC.value())

        # Set table
        self._view.dOTTable.setColumnCount(5)
        self._view.dOTTable.setHorizontalHeaderLabels(["Region", "Number of Data", "Max Length", "Mean Length", "Median Length"])
        self._view.dOTTable.setRowCount(len(dOTRegions) + 1)
        for n in range(len(tableData)):
            self._view.dOTTable.setItem(n, 0, QTableWidgetItem(str(tableData["Region"][n])))
            self._view.dOTTable.setItem(n, 1, QTableWidgetItem(str(tableData["number"][n])))
            self._view.dOTTable.setItem(n, 2, QTableWidgetItem(str(tableData["max"][n])))
            self._view.dOTTable.setItem(n, 3, QTableWidgetItem(str(round(tableData["mean"][n], 2))))
            self._view.dOTTable.setItem(n, 4, QTableWidgetItem(str(tableData["median"][n])))

        # Plot the final figure
        if len(selectionFile) > 1:
            self._view.dOTMapBrowser.setHtml("")
        else:
            self._view.dOTMapBrowser.setHtml(figure.to_html(include_plotlyjs='cdn'))

        # Plot the box plot
        if self._view.dOTTrajChoiceMax.isChecked() == True:
            dOTTrajChoice = "max"
        elif self._view.dOTTrajChoiceMean.isChecked() == True:
            dOTTrajChoice = "mean"
        else:
            dOTTrajChoice = "median"
        if self._view.dOTDataPointChoice.isChecked() == True:
            dOTTrajPoints = "all"
        else:
            dOTTrajPoints = "outliers"
        boxFigure = px.box(boxData, x = "Region", y = dOTTrajChoice, color = "mutation", points = dOTTrajPoints, labels = {"mean": "Mean Trajectory Length (s)", "max": "Max Trajectory Length (s)", "median": "Median Trajectory Length (s)", "mutation": "Condition"}, hover_name = "filename")
        self._view.dOTBoxPlotBrowser.setHtml(boxFigure.to_html(include_plotlyjs='cdn'))
 
    def heatMapUpdate(self):
        self._view.heatMapPlot.setHtml(self._view.loadingHtml)
        self._view.heatMapCummulativeTrajs.setHtml(self._view.loadingHtml)
        self._view.heatMapLiveTrajs.setHtml(self._view.loadingHtml)
        self._view.heatMapBurstLifetime.setHtml(self._view.loadingHtml)
        self._view.heatMapRipley.setHtml(self._view.loadingHtml)
        selectionFile = self._view.comboFileList.currentData()
        if selectionFile == []:
            return

        self.produceHeatMapFigure.terminate()
        self.produceHeatMapFigure.update(selectionFile)
        self.produceHeatMapFigure.start()

    def heatMapUpdateFrame(self):
        self.heatMapSliderUpdate.terminate()
        self.heatMapSliderUpdate.update(self._view.heatMapSlider.value())
        self.heatMapSliderUpdate.run()

    def dwellTimeUpdate(self):
        selectionFile = self._view.comboFileList.currentData()
        if selectionFile == []:
            return
        boxFigure, densityFigure, pieFigure = self._model.produceDwellTimeFigures(selectionFile)
        plotly.io.write_image(pieFigure, "Images/DwellPieFigure.svg")
        if boxFigure != [None]:
            self._view.dwellBox_browser.setHtml(boxFigure.to_html(include_plotlyjs='cdn'))
            self._view.dwellDensity_browser.setHtml(densityFigure.to_html(include_plotlyjs='cdn'))
            self._view.dwellPie_browser.setHtml(pieFigure.to_html(include_plotlyjs='cdn'))
        else:
            self._view.dwellBox_browser.setHtml("")
            self._view.dwellDensity_browser.setHtml("")
            self._view.dwellPie_browser.setHtml("")

    def chromatinTabUpdate(self):
        selectionFile = self._view.comboFileList.currentData()
        if selectionFile == []:
            return
        data = self._model.getChromatinData(selectionFile)
        fastData = data.loc[data.loc[:, "acquisition_rate"] == "fast", ]
        fastData = data
        fastData.loc[:, "AC"] = np.log2((fastData.loc[:, "A1"] + fastData.loc[:, "A2"] + fastData.loc[:, "A3"]).div(fastData.loc[:, "A16"] + fastData.loc[:, "A17"] + fastData.loc[:, "A18"]))
        fastData = fastData[~fastData.isin([np.nan, np.inf, -np.inf]).any(1)]
        # fastData.replace(np.inf, 2, inplace = True)
        # fastData.replace(-np.inf, -2, inplace = True)

        boundaryD = self._view.diffusionBoundary.value()
        boundIndex = fastData.groupby(["mutation", "filename", "trajID"]).apply(lambda fastData, x, boundaryD: np.mean(fastData[x]) <= boundaryD, "D", boundaryD).reset_index().loc[:, 0] == True
        diffuIndex = fastData.groupby(["mutation", "filename", "trajID"]).apply(lambda fastData, x, boundaryD: np.mean(fastData[x]) > boundaryD, "D", boundaryD).reset_index().loc[:, 0] == True
        trajBG = fastData.groupby(["mutation", "filename", "trajID"]).apply(lambda fastData, x: np.round(np.mean(fastData[x])), "bgRegion").reset_index()
        # Number of traj in each bgRegion
        trajCount = fastData.groupby(["mutation", "filename", "trajID"]).apply(lambda fastData, x: np.round(np.mean(fastData[x])), "bgRegion").reset_index().groupby(["mutation", "filename", 0]).count().reset_index()
        trajCount.rename(columns = {0 : "bgRegion"}, inplace = True)
        trajNumFig = px.box(trajCount, x = "bgRegion", y = "trajID", color = "mutation", points = "all", labels = {"bgRegion": "Background Intensity", "trajID": "Number of Trajectories"}, hover_name = "filename", title = "Trajectories Number by Region")
        # Number of bound traj in each bgRegion
        trajBound = fastData.groupby(["mutation", "filename", "trajID"]).apply(lambda fastData, x: np.round(np.mean(fastData[x])), "bgRegion").reset_index().loc[boundIndex, :].groupby(["mutation", "filename", 0]).count().reset_index()
        trajBound.rename(columns = {0: "bgRegion"}, inplace = True)
        bn2bgFig = px.box(trajBound, x = "bgRegion", y = "trajID", color = "mutation", points = "all", labels = {"trajID": "Number of Trajectories"}, hover_name = "filename", title = "Bound Trajectories Number by Region")
        # Number of mobile traj in each bgRegion
        trajDiffu = fastData.groupby(["mutation", "filename", "trajID"]).apply(lambda fastData, x: np.round(np.mean(fastData[x])), "bgRegion").reset_index().loc[diffuIndex, :].groupby(["mutation", "filename", 0]).count().reset_index()
        trajDiffu.rename(columns = {0: "bgRegion"}, inplace = True)
        df2bgFig = px.box(trajDiffu, x = "bgRegion", y = "trajID", color = "mutation", points = "all", labels = {"trajID": "Number of Trajectories"}, hover_name = "filename", title = "Mobile Trajectories Number by Region")
        # Mean of all trajectories' AC in each cell is used to plot box plot
        trajAC = fastData.groupby(["mutation", "filename", "trajID"]).apply(lambda fastData, x: np.mean(fastData[x]), "AC").reset_index()
        trajAC.loc[:, "bgRegion"] = trajBG.loc[:, 0] # AC of each trajectory in each bgRegion
        fileAC = trajAC.groupby(["mutation", "filename", "bgRegion"]).apply(lambda trajAC, x: np.mean(trajAC[x]), 0).reset_index()
        fileAC.rename(columns = {0: "AC"}, inplace = True)
        ac2bgFig = px.box(fileAC, x = "bgRegion", y = "AC", color = "mutation", points = "all", labels = {"bgRegion": "Background Intensity", "AC": "Asymmetry Coefficient"}, hover_name = "filename", title = "Asymmetry Coefficient with respect to Background Intensity Region")
        # Percentage of bound traj in each region
        trajCount.loc[:, "trajID"].div(trajBound.loc[:, "trajID"])

        # fig = px.box(trajCount, x = 0, y = "trajID", color = "mutation", points = "all", labels = {"trajID": "Number of Trajectories"}, hover_name = "filename", title = "Trajectories Number by Region")
        self._view.chromatinAC_browser.setHtml(ac2bgFig.to_html(include_plotlyjs='cdn'))
        self._view.chromatinTraj_browser.setHtml(trajNumFig.to_html(include_plotlyjs='cdn'))
        self._view.chromatinFast_browser.setHtml(df2bgFig.to_html(include_plotlyjs='cdn'))
        self._view.chromatinSlow_browser.setHtml(bn2bgFig.to_html(include_plotlyjs='cdn'))
        
        # fig = go.Figure(go.Sunburst(
        #     labels = [" ", "Low Intensity", "Short Dwell (l)", "Long Dwell (l)", "Mid Intensity", "Short Dwell (m)", "Long Dwell (m)", "High Intensity", "Short Dwell (h)", "Long Dwell (h)"],
        #     parents = ["", " ", "Low Intensity", "Low Intensity", " ", "Mid Intensity", "Mid Intensity", " ", "High Intensity", "High Intensity"],
        #     values = [0, 0, lIntFinal[0], lIntFinal[1], 0, mIntFinal[0], mIntFinal[1], 0, hIntFinal[0], hIntFinal[1]]
        # ))
        # fig.show()["filename", "trajID"]).agg({"D": np.mean}).reset_index()
            # subData.groupby(["filename", "trajID"]).apply(lambda subData, A1, A2: subData[A1] + subData[A2], "A1", "A2").reset_index()
            # fileList = list(dict.fromkeys(subData.loc[:, "filename"]))
            # for m in range(len(fileList)):
            #     fileData = subData.loc[subData.loc[:, "filename"] == fileList[m], ]
            #     # vectorised
            #     fileData.groupby("trajID").agg({"D": [np.mean]})
                
            #     # for loop
            #     trajList = list(dict.fromkeys(fileData.loc[:, "trajID"]))
            #     for p in range(len(trajList)):
            #         p

        # fastData.groupby("bgRegion").size().reset_index(name = "Counts")

        # slowData = 1
        # # Check whether the traj cross regions
        # fastData.groupby(["mutation", "filename", "trajID"]).bgRegion.nunique().eq(1)

        # mutList = list(dict.fromkeys(fastData.loc[:, "mutation"]))
        # for n in range(len(mutList)):
        #     subData = fastData.loc[fastData.loc[:, "mutation"] == mutList[n], ]
        return
    
    # Data Saving
    def angleDataSave(self):
        selectionFile = self._view.comboFileList.currentData()
        if selectionFile == []:
            return
        selectionAngle = self._view.angleSelection.currentData()
        if selectionAngle == []:
            selectionAngle = [self._view.angleSelection.itemText(i) for i in range(self._view.angleSelection.count())]
        angleRatio = self._view.angleRatio
        data = self._model.getAngleData(selectionFile)
        boundaryValue = self._view.boundaryValueAngle.value()
        boxData = self._model.produceAngleData(data, boundaryValue, selectionAngle)
        boxData.to_csv("AngleData.csv")

    def dwellTimeDataSave(self):
        selectionFile = self._view.comboFileList.currentData()
        if selectionFile == []:
            return
        dwellData, processedDensityData, figureData = self._model.produceDwellTimeData(selectionFile)
        dwellData.to_csv("DwellData.csv")
        processedDensityData.to_csv("DensityDwellData.csv")
        figureData.to_csv("FractionDwellData.csv")

    def fractionExport(self):
        try:
            selectionFile = self._view.comboFileList.currentData()
            if self._view.diffusionErrorVariation.isChecked() == True:
                errorView = 0
            elif self._view.diffusionErrorSTD.isChecked() == True:
                errorView = 1
            else:
                errorView = 2
            data = self._model.getTrajectoryFiles(selectionFile)
            if self._view.boundaryComputation.currentText() == "Formula":
                boundaryValue = np.log10(data.loc[0, "pixelSize"]**2 / (4 * 4 * data.loc[0, "exposure_time"]))
            else:
                boundaryValue = self._view.boundaryRawValue.value()
            plotData, pieData = self._model.produceDiffusionExportData(data, self._view.diffusionBinSize.value(), self._view.diffusionLowerLimit.value(), self._view.diffusionUpperLimit.value(), errorView, boundaryValue) 
            plotData.to_csv("msdDiffusion.csv")
            pieData.to_csv("msdDiffusionFraction.csv")
        except:
            pass

    def tabsUpdate(self):
        tabIndex = self._view.tabs.currentIndex()
        # self._view.tabs.tabText(self._view.tabs.currentIndex()) <- use string instead of index?
        if tabIndex == 1:
            if self._view.trajectory_tab.currentIndex() == 0: # Trajectory Plot
                self.plotTrajectory()
            elif self._view.trajectory_tab.currentIndex() == 1: # Trajectory Data
                self.trajectoryData()
        elif tabIndex == 2:
            if self._view.diffusionTabs.currentIndex() == 0: # Diffusion Plot
                self.diffusionPlotUpdate()
            elif self._view.diffusionTabs.currentIndex() == 1:
                self.jumpDistancePlotUpdate()
        elif tabIndex == 3: # Angle
            self.anglePlot()
        elif tabIndex == 4: # Distribution of Tracks
            self.dOTMapUpdate()
        elif tabIndex == 5: # Heat map
            self.heatMapUpdate()
        elif tabIndex == 6: # Dwell time
            self.dwellTimeUpdate()
        elif tabIndex == 7: # Chromatin tab
            self.chromatinTabUpdate()

    def exportingDatabase(self):
        dirPath = QFileDialog.getExistingDirectory(self._view, "Select Directory")
        self.exportDatabaseWindow = ExportDatabaseWindow(dirPath)
        self.exportDatabaseWindow.show()
    
    def importingDatabase(self):
        databasePath = QFileDialog.getOpenFileName(self._view, "Select Database To Import", os.getcwd(), 'Database (*.db)')
        selectionFile = self._view.comboFileList.currentData()
        if selectionFile == []:
            selectionFile = [self._view.comboFileList.itemText(i) for i in range(self._view.comboFileList.count())]
        if selectionFile != []:
            self.importDatabaseWindow = ImportDatabaseWindow(self, databasePath)
            self.importDatabaseWindow.show()
        else:
            shutil.copyfile(self.databasePath, 'database.db')
            self._loadExistingData()

    def _buttonResponse(self):
        self._view.comboAcquisitionRate.model().dataChanged.connect(self.comboMutationUpdate)
        self._view.comboMutation.model().dataChanged.connect(self.comboFileListUpdate)
        # self._view.comboFileList.model().dataChanged.connect(self.sidebarFileList)
        self._view.tabs.currentChanged.connect(self.tabsUpdate)
        self._view.trajectory_tab.currentChanged.connect(self.tabsUpdate)
        self._view.diffusionTabs.currentChanged.connect(self.tabsUpdate)
        
        self._view.comboAcquisitionRate.model().dataChanged.connect(self.tabsUpdate)
        self._view.comboMutation.model().dataChanged.connect(self.tabsUpdate)
        self._view.comboFileList.model().dataChanged.connect(self.tabsUpdate)
        self._view.unselectAllFiles.pressed.connect(self.unselectAllFiles)
        self._view.deleteFile.pressed.connect(self.deleteFiles)

        self._view.exportDatabase.pressed.connect(self.exportingDatabase)
        self._view.importDatabase.pressed.connect(self.importingDatabase)

        # Trajectory Plot
        self._view.trajNumberBox.textChanged.connect(self.plotTrajectory) # or valueChanged
        self._view.jumpNumberDrawBox.textChanged.connect(self.plotTrajectory)
        self._view.minTrajLength.textChanged.connect(self.plotTrajectory)
        self._view.jumpDistanceToCSV.clicked.connect(self.jumpDistanceDataSave)
        self._view.fractionExportButton.clicked.connect(self.fractionExport)
        # self._view.trajTabTrajGroupButton.clicked.connect(self.plotTrajectory)

        # Diffusion Plot Interactive
        self._view.diffusionBinSize.valueChanged.connect(self.diffusionPlotUpdate)
        self._view.diffusionLowerLimit.valueChanged.connect(self.diffusionPlotUpdate)
        self._view.diffusionUpperLimit.valueChanged.connect(self.diffusionPlotUpdate)
        self._view.diffusionErrorVariation.clicked.connect(self.diffusionPlotUpdate)
        self._view.diffusionErrorSTD.clicked.connect(self.diffusionPlotUpdate)
        self._view.diffusionErrorSEM.clicked.connect(self.diffusionPlotUpdate)
        self._view.boundaryComputation.currentTextChanged.connect(self.diffusionPlotUpdate)
        self._view.boundaryRawValue.valueChanged.connect(self.diffusionPlotUpdate)
        
        # Track Diffusion Plot Interactive
        self._view.jumpDistanceConsidered.valueChanged.connect(self.jumpDistancePlotUpdate)

        # Angle Plot Interactive
        self._view.boundaryValueAngle.valueChanged.connect(self.anglePlot)
        self._view.angleToCSV.clicked.connect(self.angleDataSave)

        # Distribution of Tracks Interactive
        self._view.dOTAngleMaxAC.valueChanged.connect(self.dOTMapUpdate)
        self._view.dOTTrajChoiceMax.clicked.connect(self.dOTMapUpdate)
        self._view.dOTTrajChoiceMean.clicked.connect(self.dOTMapUpdate)
        self._view.dOTTrajChoiceMedian.clicked.connect(self.dOTMapUpdate)
        self._view.dOTDataPointChoice.toggled.connect(self.dOTMapUpdate)
        self._view.dOTMinTrajLength.valueChanged.connect(self.dOTMapUpdate)
        self._view.dOTButton.clicked.connect(self.dOTMapUpdate)

        # Heatmap tab
        self._view.heatMapSlider.valueChanged.connect(self.heatMapUpdateFrame)

        # Dwell time tab
        self._view.dwellTimeExportButton.clicked.connect(self.dwellTimeDataSave)

        # Upload tab
        self._view.acquisitionRateFast.clicked.connect(partial(self.loadUploadPreset, "fast"))
        self._view.acquisitionRateSlow.clicked.connect(partial(self.loadUploadPreset, "slow"))
        self._view.uploadFileButton.pressed.connect(partial(self.uploadFileButton, "raw_files"))
        self._view.uploadPostFileButton.pressed.connect(partial(self.uploadFileButton, "post_files"))

        # Chromatin tab
        self._view.diffusionBoundary.valueChanged.connect(self.chromatinTabUpdate)
    
    # Start-up
    def loadUploadPreset(self, presetType):
        # Store current values
        try:
            len(self._view.uploadSettings)
        except:
            self._view.uploadSettings = pd.DataFrame()
        if presetType == "fast":
            storingPreset = "slow"
        else:
            storingPreset = "fast"
        self._view.uploadSettings.loc[0, "coreNum"] = str(self._view.parallelizationCores.value())
        self._view.uploadSettings.loc[0, "bleachRate"] = str(self._view.bleachRate.value())
        self._view.uploadSettings.loc[0, storingPreset + "AnalysisType"] = str(int(self._view.analysisTypeNumber.isChecked()))
        self._view.uploadSettings.loc[0, storingPreset + "ClipFactor"] = str(self._view.clipFactorBox.value())
        self._view.uploadSettings.loc[0, storingPreset + "TrajLength"] = str(self._view.trajectoryLengthBox.value())
        self._view.uploadSettings.loc[0, storingPreset + "MinTrajNum"] = str(self._view.minTrajectoryNumberBox.value())
        self._view.uploadSettings.loc[0, storingPreset + "Tolerance"] = str(self._view.toleranceBox.value())
        self._view.uploadSettings.loc[0, storingPreset + "LocError"] = str(self._view.localizationErrorBox.value())
        self._view.uploadSettings.loc[0, storingPreset + "EmmWave"] = str(self._view.emissionWavelengthBox.value())
        self._view.uploadSettings.loc[0, storingPreset + "ExposureTime"] = str(self._view.exposureTimeBox.value())
        self._view.uploadSettings.loc[0, storingPreset + "DflLoop"] = str(self._view.deflationLoopsNumberBox.value())
        self._view.uploadSettings.loc[0, storingPreset + "DMax"] = str(self._view.diffusionConstantMaxBox.value())
        self._view.uploadSettings.loc[0, storingPreset + "Gaps"] = str(self._view.gapsAllowedBox.value())
        self._view.uploadSettings.loc[0, storingPreset + "PxSize"] = str(self._view.pixelSize.value())
        self._view.uploadSettings.loc[0, storingPreset + "PSFScaling"] = str(self._view.psfScaling.value())
        self._view.uploadSettings.loc[0, storingPreset + "NA"] = str(self._view.detectionObjectiveNA.value())
        self._view.uploadSettings.loc[0, storingPreset + "DetectionBox"] = str(self._view.detectionBox.value())
        self._view.uploadSettings.loc[0, storingPreset + "MaxIter"] = str(self._view.maxIteration.value())
        self._view.uploadSettings.loc[0, storingPreset + "TermTol"] = str(self._view.terminationTolerance.value())
        self._view.uploadSettings.loc[0, storingPreset + "RadTol"] = str(self._view.radiusToleranceValue.value())
        self._view.uploadSettings.loc[0, storingPreset + "PosTol"] = str(self._view.positionTolerance.value())
        self._view.uploadSettings.loc[0, storingPreset + "MinLoc"] = str(self._view.minLoc.value())
        self._view.uploadSettings.loc[0, storingPreset + "MaxLoc"] = str(self._view.maxLoc.value())
        self._view.uploadSettings.loc[0, storingPreset + "PosTol"] = str(self._view.positionTolerance.value())
        self._view.uploadSettings.loc[0, storingPreset + "MinSNR"] = str(self._view.minSNR.value())
        self._view.uploadSettings.loc[0, storingPreset + "MaxSNRIter"] = str(self._view.maxSNRIter.value())
        self._view.uploadSettings.loc[0, storingPreset + "TrackStart"] = str(self._view.trackStart.value())
        self._view.uploadSettings.loc[0, storingPreset + "TrackEnd"] = str(self._view.trackEnd.value())
        self._view.uploadSettings.loc[0, storingPreset + "ExpFS"] = str(self._view.exponentialFactorSearch.value())
        self._view.uploadSettings.loc[0, storingPreset + "StatWin"] = str(self._view.statWin.value())
        self._view.uploadSettings.loc[0, storingPreset + "CompMax"] = str(self._view.compMax.value())
        self._view.uploadSettings.loc[0, storingPreset + "IntLaw"] = str(self._view.intLawWeight.value())
        self._view.uploadSettings.loc[0, storingPreset + "DifLaw"] = str(self._view.difLawWeight.value())
        if os.path.exists("Settings.txt"):
            try:
                len(self._view.uploadSettings)
            except:
                with open("Settings.txt") as f:
                    lines = f.readlines()
                self._view.uploadSettings = pd.DataFrame()
                for line in lines:
                    self._view.uploadSettings.loc[0, line.split(": ")[0]] = line.split(": ")[1][0:-1]
        if presetType + "AnalysisType" in self._view.uploadSettings:
            if self._view.uploadSettings.loc[0, presetType + "AnalysisType"] == "1":
                self._view.analysisTypeNumber.setChecked(True)
            else:
                self._view.analysisTypePercentage.setChecked(True)
            self._view.clipFactorBox.setValue(int(self._view.uploadSettings.loc[0, presetType + "ClipFactor"]))
            self._view.trajectoryLengthBox.setValue(int(self._view.uploadSettings.loc[0, presetType + "TrajLength"]))
            self._view.minTrajectoryNumberBox.setValue(int(self._view.uploadSettings.loc[0, presetType + "MinTrajNum"]))
            self._view.toleranceBox.setValue(int(self._view.uploadSettings.loc[0, presetType + "Tolerance"]))
            self._view.localizationErrorBox.setValue(float(self._view.uploadSettings.loc[0, presetType + "LocError"]))
            self._view.emissionWavelengthBox.setValue(int(self._view.uploadSettings.loc[0, presetType + "EmmWave"]))
            self._view.exposureTimeBox.setValue(float(self._view.uploadSettings.loc[0, presetType + "ExposureTime"]))
            self._view.deflationLoopsNumberBox.setValue(int(self._view.uploadSettings.loc[0, presetType + "DflLoop"]))
            self._view.diffusionConstantMaxBox.setValue(float(self._view.uploadSettings.loc[0, presetType + "DMax"]))
            self._view.gapsAllowedBox.setValue(int(self._view.uploadSettings.loc[0, presetType + "Gaps"]))
            self._view.pixelSize.setValue(float(self._view.uploadSettings.loc[0, presetType + "PxSize"]))
            self._view.psfScaling.setValue(float(self._view.uploadSettings.loc[0, presetType + "PSFScaling"]))
            self._view.detectionObjectiveNA.setValue(float(self._view.uploadSettings.loc[0, presetType + "NA"]))
            self._view.detectionBox.setValue(int(self._view.uploadSettings.loc[0, presetType + "DetectionBox"]))
            self._view.maxIteration.setValue(int(self._view.uploadSettings.loc[0, presetType + "MaxIter"]))
            self._view.terminationTolerance.setValue(int(self._view.uploadSettings.loc[0, presetType + "TermTol"]))
            self._view.radiusToleranceValue.setValue(int(self._view.uploadSettings.loc[0, presetType + "RadTol"]))
            self._view.positionTolerance.setValue(float(self._view.uploadSettings.loc[0, presetType + "PosTol"]))
            self._view.minLoc.setValue(int(self._view.uploadSettings.loc[0, presetType + "MinLoc"]))
            self._view.maxLoc.setValue(int(self._view.uploadSettings.loc[0, presetType + "MaxLoc"]))
            self._view.positionTolerance.setValue(float(self._view.uploadSettings.loc[0, presetType + "PosTol"]))
            self._view.minSNR.setValue(int(self._view.uploadSettings.loc[0, presetType + "MinSNR"]))
            self._view.maxSNRIter.setValue(int(self._view.uploadSettings.loc[0, presetType + "MaxSNRIter"]))
            self._view.trackStart.setValue(int(self._view.uploadSettings.loc[0, presetType + "TrackStart"]))
            self._view.trackEnd.setValue(int(self._view.uploadSettings.loc[0, presetType + "TrackEnd"]))
            self._view.exponentialFactorSearch.setValue(float(self._view.uploadSettings.loc[0, presetType + "ExpFS"]))
            self._view.statWin.setValue(int(self._view.uploadSettings.loc[0, presetType + "StatWin"]))
            self._view.compMax.setValue(int(self._view.uploadSettings.loc[0, presetType + "CompMax"]))
            self._view.intLawWeight.setValue(float(self._view.uploadSettings.loc[0, presetType + "IntLaw"]))
            self._view.difLawWeight.setValue(float(self._view.uploadSettings.loc[0, presetType + "DifLaw"]))
            self._view.parallelizationCores.setValue(int(self._view.uploadSettings.loc[0, "coreNum"]))
            self._view.bleachRate.setValue(float(self._view.uploadSettings.loc[0, "bleachRate"]))

    def _loadExistingData(self):
        # Remove previous data to prevent repeats after data upload
        self._view.comboAcquisitionRate.model().clear()
        self._view.comboMutation.model().clear()
        self._view.comboFileList.model().clear()
        self._view.angleSelection.model().clear()

        # Get data from database
        with sqlite3.connect('database.db') as conn:
            try:
                # data = pd.read_sql_query("select * from TrackList", conn)
                df = pd.read_sql_query("select * from FileList", conn)
                self._view.textEdit.setText(pd.read_sql_query("select text from Settings", conn).loc[0, "text"])
                if len(df) > 0:
                    dataExist = True
                else:
                    dataExist = False
            except:
                dataExist = False
                
        if dataExist == True:
            # Adding data from database to selection
            acquisitionRate = set(df['acquisition_rate'])
            self._view.comboAcquisitionRate.addItems(acquisitionRate)
            mutation = set(df['mutation'])
            self._view.comboMutation.addItems(mutation)
            # filename = df['filename']
            filename = df['filename'].sort_values()
            self._view.comboFileList.addItems(filename)
            angleList = pd.DataFrame({"0 - 10": "",
                                      "10 - 20": "",
                                      "20 - 30": "",
                                      "30 - 40": "",
                                      "40 - 50": "",
                                      "50 - 60": "",
                                      "60 - 70": "",
                                      "70 - 80": "",
                                      "80 - 90": "",
                                      "90 - 100": "",
                                      "100 - 110": "",
                                      "110 - 120": "",
                                      "120 - 130": "",
                                      "130 - 140": "",
                                      "140 - 150": "",
                                      "150 - 160": "",
                                      "160 - 170": "",
                                      "170 - 180": ""},
                                      index = [0])
            self._view.angleSelection.addItems(angleList)

            # Clearing the names in the box
            self._view.comboAcquisitionRate.updateText()
            self._view.comboMutation.updateText()
            self._view.comboFileList.updateText()
            self._view.angleSelection.updateText()

            self._view.comboAcquisitionRate.checkAll()
            self._view.comboMutation.checkAll()
            self._view.comboFileList.checkAll()

            if os.path.exists("Settings.txt"):
                try:
                    len(self._view.uploadSettings)
                except:
                    with open("Settings.txt") as f:
                        lines = f.readlines()
                    self._view.uploadSettings = pd.DataFrame()
                    for line in lines:
                        self._view.uploadSettings.loc[0, line.split(": ")[0]] = line.split(": ")[1][0:-1]
                    if self._view.uploadSettings.loc[0, "fastAnalysisType"] == "1":
                        self._view.analysisTypeNumber.setChecked(True)
                    else:
                        self._view.analysisTypePercentage.setChecked(True)
                    self._view.clipFactorBox.setValue(int(self._view.uploadSettings.loc[0, "fastClipFactor"]))
                    self._view.trajectoryLengthBox.setValue(int(self._view.uploadSettings.loc[0, "fastTrajLength"]))
                    self._view.minTrajectoryNumberBox.setValue(int(self._view.uploadSettings.loc[0, "fastMinTrajNum"]))
                    self._view.toleranceBox.setValue(int(self._view.uploadSettings.loc[0, "fastTolerance"]))
                    self._view.localizationErrorBox.setValue(float(self._view.uploadSettings.loc[0, "fastLocError"]))
                    self._view.emissionWavelengthBox.setValue(int(self._view.uploadSettings.loc[0, "fastEmmWave"]))
                    self._view.exposureTimeBox.setValue(float(self._view.uploadSettings.loc[0, "fastExposureTime"]))
                    self._view.deflationLoopsNumberBox.setValue(int(self._view.uploadSettings.loc[0, "fastDflLoop"]))
                    self._view.diffusionConstantMaxBox.setValue(float(self._view.uploadSettings.loc[0, "fastDMax"]))
                    self._view.gapsAllowedBox.setValue(int(self._view.uploadSettings.loc[0, "fastGaps"]))
                    self._view.pixelSize.setValue(float(self._view.uploadSettings.loc[0, "fastPxSize"]))
                    self._view.psfScaling.setValue(float(self._view.uploadSettings.loc[0, "fastPSFScaling"]))
                    self._view.detectionObjectiveNA.setValue(float(self._view.uploadSettings.loc[0, "fastNA"]))
                    self._view.detectionBox.setValue(int(self._view.uploadSettings.loc[0, "fastDetectionBox"]))
                    self._view.maxIteration.setValue(int(self._view.uploadSettings.loc[0, "fastMaxIter"]))
                    self._view.terminationTolerance.setValue(int(self._view.uploadSettings.loc[0, "fastTermTol"]))
                    self._view.radiusToleranceValue.setValue(int(self._view.uploadSettings.loc[0, "fastRadTol"]))
                    self._view.positionTolerance.setValue(float(self._view.uploadSettings.loc[0, "fastPosTol"]))
                    self._view.minLoc.setValue(int(self._view.uploadSettings.loc[0, "fastMinLoc"]))
                    self._view.maxLoc.setValue(int(self._view.uploadSettings.loc[0, "fastMaxLoc"]))
                    self._view.positionTolerance.setValue(float(self._view.uploadSettings.loc[0, "fastPosTol"]))
                    self._view.minSNR.setValue(int(self._view.uploadSettings.loc[0, "fastMinSNR"]))
                    self._view.maxSNRIter.setValue(int(self._view.uploadSettings.loc[0, "fastMaxSNRIter"]))
                    self._view.trackStart.setValue(int(self._view.uploadSettings.loc[0, "fastTrackStart"]))
                    self._view.trackEnd.setValue(int(self._view.uploadSettings.loc[0, "fastTrackEnd"]))
                    self._view.exponentialFactorSearch.setValue(float(self._view.uploadSettings.loc[0, "fastExpFS"]))
                    self._view.statWin.setValue(int(self._view.uploadSettings.loc[0, "fastStatWin"]))
                    self._view.compMax.setValue(int(self._view.uploadSettings.loc[0, "fastCompMax"]))
                    self._view.intLawWeight.setValue(float(self._view.uploadSettings.loc[0, "fastIntLaw"]))
                    self._view.difLawWeight.setValue(float(self._view.uploadSettings.loc[0, "fastDifLaw"]))
                    self._view.parallelizationCores.setValue(int(self._view.uploadSettings.loc[0, "coreNum"]))
                    self._view.bleachRate.setValue(float(self._view.uploadSettings.loc[0, "bleachRate"]))
    
class Model:
    def __init__(self):
        pass

    # Upload
    @staticmethod
    def processUploadedFileToDatabaseParallel(arg):
        file_name, acquisition_rate, exposureTime, pixelSize, uploadParameters= arg
        dataDir = os.path.realpath(os.getcwd()) + "/Data/fast-tif/"
        
        mutation = file_name.split("_")[0]
        data = scipy.io.loadmat(dataDir + file_name + "_dataTrack.mat")
        dataTrack = pd.DataFrame({"trajID": [file_name + f"_{m}" for m in data['dataTrack'][:, 0].astype(int)],
                                  "Frame": data['dataTrack'][:, 1].astype(float),
                                  "x": data['dataTrack'][:, 2].astype(float),
                                  "y": data['dataTrack'][:, 3].astype(float),
                                  "msd": data['dataTrack'][:, 4].astype(float),
                                  "distance": data['dataTrack'][:, 5].astype(float),
                                  "angle": data['dataTrack'][:, 6].astype(float),
                                  "bgIntensity": data['dataTrack'][:, 7].astype(float),
                                  "bgRegion": data['dataTrack'][:, 8].astype(float)
                                 }
                                )
        trajIDs = list(set(dataTrack["trajID"].to_numpy().astype(str)))
        distances = pd.DataFrame(data = [])
        for m in range(len(trajIDs)):
            dataSubset = dataTrack.loc[dataTrack["trajID"] == trajIDs[m]]
            points = dataSubset.to_numpy()[:, (2,3)].astype(float)
            # hull = chull(points)
            # hullpoints = points[hull.vertices, :]
            # hdist = cdist(hullpoints, hullpoints, metric='euclidean')
            hdist = cdist(points, points, metric='euclidean')
            distances = pd.concat([distances, pd.DataFrame({"meanX": dataSubset['x'].mean(), "meanY": dataSubset['y'].mean(), "maxDistance": hdist.max(), "meanDistance": hdist[0,:][1:].mean(), "medianDistance": np.median(hdist[0,:][1:])}, index = [m])], axis = 0)
        data = scipy.io.loadmat(dataDir + file_name + "_dataTraj.mat")
        dataTraj = pd.DataFrame({"filename": [file_name] * len(data['dataTraj'][:, 0]),
                                 "trajID": [file_name + f"_{m}" for m in data['dataTraj'][:, 1].astype(int)],
                                 "traj_length": data['dataTraj'][:, 2].astype(int),
                                 "msd": data['dataTraj'][:, 3].astype(float),
                                 "D": data['dataTraj'][:, 4].astype(float),
                                 "startTime": data['dataTraj'][:, 5].astype(float),
                                 "endTime": data['dataTraj'][:, 6].astype(float),
                                 "meanX": distances["meanX"],
                                 "meanY": distances["meanY"],
                                 "maxDistance": distances["maxDistance"],
                                 "meanDistance": distances["meanDistance"],
                                 "medianDistance": distances["medianDistance"]
                                }
                               )
        data = scipy.io.loadmat(dataDir + file_name + "_CMPFitPar.mat")
        twoCMPData = scipy.io.loadmat(dataDir + file_name + "_2CMPFit.mat")
        threeCMPData = scipy.io.loadmat(dataDir + file_name + "_3CMPFit.mat")
        dataJD = pd.DataFrame({"filename": [file_name] * len(data['FJH'][:, 0]),
                               "jump_distance": data["FJH"][:, 0],
                               "sharedFrequency": data["FJH"][:, 1],
                               "twoParFrequency": data["FJH"][:, 3],
                               "threeParFrequency": data["FJH"][:, 4],
                               "twoParD1Values": twoCMPData["twoCMPFit"][:, 0],
                               "twoParD2Values": twoCMPData["twoCMPFit"][:, 1],
                               "threeParD1Values": threeCMPData["threeCMPFit"][:, 0],
                               "threeParD2Values": threeCMPData["threeCMPFit"][:, 1],
                               "threeParD3Values": threeCMPData["threeCMPFit"][:, 2]
                              }
                             )
        data = scipy.io.loadmat(dataDir + file_name + "_FitPar.mat")
        data = pd.DataFrame(data["FitPar"])
        data.replace(np.nan, 0, inplace = True)
        dataFile = pd.DataFrame(data = {"filename": file_name,
                                        "mutation": mutation,
                                        "acquisition_rate": acquisition_rate,
                                        "exposure_time": exposureTime,
                                        "pixelSize": pixelSize,
                                        "cellSize": np.nan,
                                        "psfScale": uploadParameters.loc["psf_scale", "impars"], "wvlnth": uploadParameters.loc["wvlnth", "impars"],
                                        "iNA": uploadParameters.loc["iNA", "impars"], "psfStd": uploadParameters.loc["psfStd", "impars"],
                                        "wn": uploadParameters.loc["wn", "locpars"], "errorRate": uploadParameters.loc["errorRate", "locpars"],
                                        "dfltnLoops": uploadParameters.loc["dfltnLoops", "locpars"], "minInt": uploadParameters.loc["minInt", "locpars"],
                                        "optim_MaxIter": uploadParameters.loc["optim", "locpars"][0],
                                        "optim_termTol": uploadParameters.loc["optim", "locpars"][1],
                                        "optim_isRadTol": uploadParameters.loc["optim", "locpars"][2],
                                        "optim_radTol": uploadParameters.loc["optim", "locpars"][3],
                                        "optim_posTol": uploadParameters.loc["optim", "locpars"][4],
                                        "isThreshLocPrec": uploadParameters.loc["isThreshLocPrec", "locpars"], "minLoc": uploadParameters.loc["minLoc", "locpars"],
                                        "maxLoc": uploadParameters.loc["maxLoc", "locpars"], "isThreshSNR": uploadParameters.loc["isThreshSNR", "locpars"],
                                        "minSNR": uploadParameters.loc["minSNR", "locpars"], "maxSNR": uploadParameters.loc["maxSNR", "locpars"],
                                        "isThreshDensity": uploadParameters.loc["isThreshDensity", "locpars"],
                                        "trackStart": uploadParameters.loc["trackStart", "trackpars"], "trackEnd": uploadParameters.loc["trackEnd", "trackpars"],
                                        "Dmax": uploadParameters.loc["Dmax", "trackpars"], "searchExpFac": uploadParameters.loc["searchExpFac", "trackpars"],
                                        "statWin": uploadParameters.loc["statWin", "trackpars"], "maxComp": uploadParameters.loc["maxComp", "trackpars"],
                                        "maxOffTime": uploadParameters.loc["maxOffTime", "trackpars"], "intLawWeight": uploadParameters.loc["intLawWeight", "trackpars"],
                                        "diffLawWeight": uploadParameters.loc["diffLawWeight", "trackpars"],
                                        "bleach_rate": uploadParameters.loc["PixelSize", "bleach_rate"], "traj_length": uploadParameters.loc["PixelSize", "traj_length"],
                                        "min_traj": uploadParameters.loc["PixelSize", "min_traj"], "clip_factor": uploadParameters.loc["PixelSize", "clip_factor"],
                                        "tol": uploadParameters.loc["PixelSize", "tol"],
                                        "twoParN": data.iloc[0, 3],
                                        "twoPardN": data.iloc[1, 3],
                                        "twoParD1": data.iloc[0, 4],
                                        "twoPardD1": data.iloc[1, 4],
                                        "twoParD2": data.iloc[0, 5],
                                        "twoPardD2": data.iloc[1, 5],
                                        "twoParf1": data.iloc[0, 6],
                                        "twoPardf1": data.iloc[1, 6],
                                        "twoParSSR": data.iloc[0, 7],
                                        "threeParN": data.iloc[0, 8],
                                        "threePardN": data.iloc[1, 8],
                                        "threeParD1": data.iloc[0, 9],
                                        "threePardD1": data.iloc[1, 9],
                                        "threeParD2": data.iloc[0, 10],
                                        "threePardD2": data.iloc[1, 10],
                                        "threeParD3": data.iloc[0, 11],
                                        "threePardD3": data.iloc[1, 11],
                                        "threeParf1": data.iloc[0, 12],
                                        "threePardf1": data.iloc[1, 12],
                                        "threeParf2": data.iloc[0, 13],
                                        "threePardf2": data.iloc[1, 13],
                                        "threeParSSR": data.iloc[0, 14]
                                       }, index = [0]
                               )
        if os.path.exists(dataDir + file_name + "_cellData.mat"):
            data = scipy.io.loadmat(dataDir + file_name + "_cellData.mat")
            dataFile.loc[0, "cellSize"] = data["cellData"][0][0]
        data = scipy.io.loadmat(dataDir + file_name + "_dataAngle.mat")
        dataAngle = pd.DataFrame(data = {"filename": file_name,
                                         "trajID": [file_name + f"_{m}" for m in data['dataAngle'][:, 0].astype(int)],
                                         "A1": [m for m in data['dataAngle'][:, 1].astype(int)],
                                         "A2": [m for m in data['dataAngle'][:, 2].astype(int)],
                                         "A3": [m for m in data['dataAngle'][:, 3].astype(int)],
                                         "A4": [m for m in data['dataAngle'][:, 4].astype(int)],
                                         "A5": [m for m in data['dataAngle'][:, 5].astype(int)],
                                         "A6": [m for m in data['dataAngle'][:, 6].astype(int)],
                                         "A7": [m for m in data['dataAngle'][:, 7].astype(int)],
                                         "A8": [m for m in data['dataAngle'][:, 8].astype(int)],
                                         "A9": [m for m in data['dataAngle'][:, 9].astype(int)],
                                         "A10": [m for m in data['dataAngle'][:, 10].astype(int)],
                                         "A11": [m for m in data['dataAngle'][:, 11].astype(int)],
                                         "A12": [m for m in data['dataAngle'][:, 12].astype(int)],
                                         "A13": [m for m in data['dataAngle'][:, 13].astype(int)],
                                         "A14": [m for m in data['dataAngle'][:, 14].astype(int)],
                                         "A15": [m for m in data['dataAngle'][:, 15].astype(int)],
                                         "A16": [m for m in data['dataAngle'][:, 16].astype(int)],
                                         "A17": [m for m in data['dataAngle'][:, 17].astype(int)],
                                         "A18": [m for m in data['dataAngle'][:, 18].astype(int)]
                                        })
        if acquisition_rate == "fast":
            return dataFile, dataTraj, dataTrack, dataJD, dataAngle
        else:
            if os.path.exists(dataDir + file_name + "_dwellTime.mat"):
                data = scipy.io.loadmat(dataDir + file_name + "_dwellTime.mat")
                dataDwellTime = pd.DataFrame(data = {"filename": file_name,
                                                    "R1": data["dwellTimeData"][0][0], # TODO: Make a new table for dwell time data
                                                    "R2": data["dwellTimeData"][0][1],
                                                    "F": data["dwellTimeData"][0][2]
                                                    }, index = [0]
                                            )
            else:
                dataDwellTime = pd.DataFrame()
            return dataFile, dataTraj, dataTrack, dataJD, dataAngle, dataDwellTime

    def processUploadedFileToDatabase(self, file_names, acquisition_rate, exposureTime, pixelSize, uploadParameters):
        mpPool = mp.Pool(mp.cpu_count())
        # data = [mpPool.apply(self.processUploadedFileToDatabaseParallel, args = (file_names[n], acquisition_rate, exposureTime)) for n in range(len(file_names))]
        data = mpPool.map(self.processUploadedFileToDatabaseParallel, ((file_names[n], acquisition_rate, exposureTime, pixelSize, uploadParameters) for n in range(len(file_names))))
        mpPool.close()

        dataFile = pd.DataFrame(data = [])
        dataTraj = pd.DataFrame(data = [])
        dataTrack = pd.DataFrame(data = [])
        dataJD = pd.DataFrame(data = [])
        dataAngle = pd.DataFrame(data = [])
        dataDwellTime = pd.DataFrame(data = [])
        if acquisition_rate == "fast":
            for n in range(len(data)):
                dataFile = pd.concat([dataFile, data[n][0]], axis = 0)
                dataTraj = pd.concat([dataTraj, data[n][1]], axis = 0)
                dataTrack = pd.concat([dataTrack, data[n][2]], axis = 0)
                dataJD = pd.concat([dataJD, data[n][3]], axis = 0)
                dataAngle = pd.concat([dataAngle, data[n][4]], axis = 0)
        else:
            for n in range(len(data)):
                dataFile = pd.concat([dataFile, data[n][0]], axis = 0)
                dataTraj = pd.concat([dataTraj, data[n][1]], axis = 0)
                dataTrack = pd.concat([dataTrack, data[n][2]], axis = 0)
                dataJD = pd.concat([dataJD, data[n][3]], axis = 0)
                dataAngle = pd.concat([dataAngle, data[n][4]], axis = 0)
                dataDwellTime = pd.concat([dataDwellTime, data[n][5]], axis = 0)
        return dataFile, dataTraj, dataTrack, dataJD, dataAngle, dataDwellTime

    # File selection
    def updateMutationFilelist(self, selectionRate):
        if selectionRate == []:
            data = pd.DataFrame({"filename": [], "mutation": []})
        else:
            with sqlite3.connect('database.db') as conn:
                if len(selectionRate) > 1:
                    data = pd.read_sql_query(f"select * from FileList where acquisition_rate IN {tuple(selectionRate)}", conn)
                else:
                    data = pd.read_sql_query("select * from FileList where acquisition_rate = :selectionRate", conn, params = {"selectionRate": selectionRate[0]})
        return data

    def updateFilelist(self, selectionRate, selectionMutation):
        if selectionMutation == []:
            data = pd.DataFrame({"filename": [], "mutation": []})
        else:
            with sqlite3.connect('database.db') as conn:
                if len(selectionRate) > 1:
                    if len(selectionMutation) > 1:
                        data = pd.read_sql_query(f"select * from FileList where acquisition_rate IN {tuple(selectionRate)} AND mutation IN {tuple(selectionMutation)}", conn)
                    else:
                        data = pd.read_sql_query(f"select * from FileList where acquisition_rate IN {tuple(selectionRate)} AND mutation = :selectionMutation", conn, params = {"selectionMutation": selectionMutation[0]})
                else:
                    if len(selectionMutation) > 1:
                        data = pd.read_sql_query(f"select * from FileList where acquisition_rate = :selectionRate AND mutation IN {tuple(selectionMutation)}", conn, params = {"selectionRate": selectionRate[0]})
                    else:
                        data = pd.read_sql_query("select * from FileList where acquisition_rate = :selectionRate AND mutation = :selectionMutation", conn, params = {"selectionRate": selectionRate[0], "selectionMutation": selectionMutation[0]})
        return data

    def getSelectedFiles(self, selectionRate, selectionMutation, selectionFile, table):
        with sqlite3.connect('database.db') as conn:
            if len(selectionRate) > 1:
                if len(selectionMutation) > 1:
                    if len(selectionFile) > 1:
                        data = pd.read_sql_query(f"select * from {table} where acquisition_rate IN {tuple(selectionRate)} AND mutation IN {tuple(selectionMutation)} AND filename IN {tuple(selectionFile)}", conn)
                    else:
                        data = pd.read_sql_query(f"select * from {table} where acquisition_rate IN {tuple(selectionRate)} AND mutation IN {tuple(selectionMutation)} AND filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
                else:
                    if len(selectionFile) > 1:
                        data = pd.read_sql_query(f"select * from {table} where acquisition_rate IN {tuple(selectionRate)} AND mutation = :selectionMutation AND filename IN {tuple(selectionFile)}", conn, params = {"selectionMutation": selectionMutation[0]})
                    else:
                        data = pd.read_sql_query(f"select * from {table} where acquisition_rate IN {tuple(selectionRate)} AND mutation = :selectionMutation AND filename = :selectionFile", conn, params = {"selectionMutation": selectionMutation[0], "selectionFile": selectionFile[0]})
            else:
                if len(selectionMutation) > 1:
                    if len(selectionFile) > 1:
                        data = pd.read_sql_query(f"select * from {table} where acquisition_rate = :selectionRate AND mutation IN {tuple(selectionMutation)} AND filename IN {tuple(selectionFile)}", conn, params = {"selectionRate": selectionRate[0]})
                    else:
                        data = pd.read_sql_query(f"select * from {table} where acquisition_rate = :selectionRate AND mutation IN {tuple(selectionMutation)} AND filename = :selectionFile", conn, params = {"selectionRate": selectionRate[0], "selectionFile": selectionFile[0]})
                else:
                    if len(selectionFile) > 1:
                        data = pd.read_sql_query(f"select * from {table} where acquisition_rate = :selectionRate AND mutation = :selectionMutation AND filename IN {tuple(selectionFile)}", conn, params = {"selectionRate": selectionRate[0], "selectionMutation": selectionMutation[0]})
                    else:
                        data = pd.read_sql_query(f"select * from {table} where acquisition_rate = :selectionRate AND mutation = :selectionMutation AND filename = :selectionFile", conn, params = {"selectionRate": selectionRate[0], "selectionMutation": selectionMutation[0], "selectionFile": selectionFile[0]})
        return data

    # Statistics feature
    def add_pvalue_annotation(self, fig, df, x_values, x_marks, y_mark, y_range, symbol=''):
        """
        Adding statistics annotation to figure.
        Arguments:
        fig: The figure you want to add statistical annotation to.
        df: The dataframe that used to plot the figure.
        x_values: The column name that is used on the x-axis of the figure.
        x_marks: The two x values on the figure that want to be marked or adding statistics to.
        y_mark: The values used for y axis in figure.
        y_range: The height of the annotation, in papper units.
        """
        if (len(x_marks) > 0) and (len(y_mark) > 0):
            pvalue = stats.ttest_ind(
                df.loc[df[x_values]==x_marks[0], y_mark],
                df.loc[df[x_values]==x_marks[1], y_mark])[1]
        elif len(y_mark) > 0:
            pvalue = stats.ttest_ind(
                df.loc[:, y_mark],
                df.loc[:, y_mark])[1]
        else:
            pvalue = stats.ttest_ind(
                df.loc[df[x_values]==x_marks[0],],
                df.loc[df[x_values]==x_marks[1],])[1]
        # print(pvalue)
        if pvalue >= 0.05:
            symbol = 'ns'
        if pvalue < 0.05:
            symbol = '*'
        fig.add_shape(type="line",
            xref="x", yref="paper",
            x0=x_marks[0], y0=y_range[0], x1=x_marks[0], y1=y_range[1],
            line=dict(
                color="black",
                width=2,
            )
        )
        fig.add_shape(type="line",
            xref="x", yref="paper",
            x0=x_marks[0], y0=y_range[1], x1=x_marks[1], y1=y_range[1],
            line=dict(
                color="black",
                width=2,
            )
        )
        fig.add_shape(type="line",
            xref="x", yref="paper",
            x0=x_marks[1], y0=y_range[1], x1=x_marks[1], y1=y_range[0],
            line=dict(
                color="black",
                width=2,
            )
        )
        ## add text at the correct x, y coordinates
        ## for bars, there is a direct mapping from the bar number to 0, 1, 2...
        bar_xcoord_map = {x: idx for idx, x in enumerate(list(dict.fromkeys(df[x_values])))}
        fig.add_annotation(dict(font=dict(color="black",size=14),
            x=(bar_xcoord_map[x_marks[0]] + bar_xcoord_map[x_marks[1]])/2,
            y=y_range[1]*1.03,
            showarrow=False,
            text=symbol,
            textangle=0,
            xref="x",
            yref="paper"
        ))
        return fig

    # Reading database
    def getTrajectoryFiles(self, selectionFile):
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.exposure_time, FileList.pixelSize, TrajectoryList.traj_length, TrajectoryList.msd, TrajectoryList.D from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename WHERE FileList.filename IN {tuple(selectionFile)}", conn)
            else:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.exposure_time, FileList.pixelSize, TrajectoryList.traj_length, TrajectoryList.msd, TrajectoryList.D from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename WHERE FileList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
        return data

    def getTrajectoryDataFiles(self, selectionFile):
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.pixelSize, FileList.cellSize, TrajectoryList.trajID, TrajectoryList.traj_length from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename WHERE FileList.filename IN {tuple(selectionFile)}", conn)
            else:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.pixelSize, FileList.cellSize, TrajectoryList.trajID, TrajectoryList.traj_length from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename WHERE FileList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
        return data

    def getAngleTrackFiles(self, selectionFile):
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, TrajectoryList.trajID, TrajectoryList.traj_length, TrajectoryList.D, TrackList.Frame, TrackList.x, TrackList.y, TrackList.distance, TrackList.angle from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename INNER JOIN TrackList ON TrajectoryList.trajID = TrackList.trajID WHERE FileList.filename IN {tuple(selectionFile)}", conn)
            else:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, TrajectoryList.trajID, TrajectoryList.traj_length, TrajectoryList.D, TrackList.Frame, TrackList.x, TrackList.y, TrackList.distance, TrackList.angle from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename INNER JOIN TrackList ON TrajectoryList.trajID = TrackList.trajID WHERE FileList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
        return data

    def plotTrajectory_data(self, trajLength, trajNumber, jumpNumber, data):
        mutations = set(data["mutation"])
        mutations = list(mutations)
        df = pd.DataFrame()
        for n in range(len(mutations)):
            dataSubset = data.loc[data["mutation"] == mutations[n]]
            files = set(dataSubset["filename"])
            files = list(files)
            for m in range(len(files)):
                dataSubSubset = dataSubset.loc[dataSubset["filename"] == files[m]]
                trajs = set(dataSubSubset["trajID"])
                trajs = list(trajs)
                if trajNumber > len(trajs):
                    trajToPlot = len(trajs)
                else:
                    trajToPlot = trajNumber
                for i in range(trajToPlot):
                    dataOfInterest = dataSubSubset.loc[dataSubSubset["trajID"] == trajs[i]]
                    if len(dataOfInterest) > trajLength:
                        if jumpNumber > len(dataOfInterest):
                            temp = dataOfInterest.head(len(dataOfInterest))
                        else:
                            temp = dataOfInterest.head(jumpNumber)
                        df = pd.concat([df, temp], axis = 0)
        return df

    def getJumpDistanceData(self, selectionFile):
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                data = pd.read_sql_query(f"select FileList.*, JDList.jump_distance, JDList.sharedFrequency, JDList.twoParFrequency, JDList.threeParFrequency, JDList.twoParD1Values, JDList.twoParD2Values, JDList.threeParD1Values, JDList.threeParD2Values, JDList.threeParD3Values from FileList INNER JOIN JDList ON FileList.filename = JDList.filename WHERE FileList.filename IN {tuple(selectionFile)}", conn)
            else:
                data = pd.read_sql_query(f"select FileList.*, JDList.jump_distance, JDList.sharedFrequency, JDList.twoParFrequency, JDList.threeParFrequency, JDList.twoParD1Values, JDList.twoParD2Values, JDList.threeParD1Values, JDList.threeParD2Values, JDList.threeParD3Values from FileList INNER JOIN JDList ON FileList.filename = JDList.filename WHERE FileList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
        return data

    def getJumpDistanceBoxData(self, selectionFile):
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                data = pd.read_sql_query(f"select FileList.* from FileList WHERE FileList.filename IN {tuple(selectionFile)}", conn)
            else:
                data = pd.read_sql_query(f"select FileList.* from FileList WHERE FileList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
        twoParBoxData = pd.DataFrame()
        threeParBoxData = pd.DataFrame()
        for n in range(len(data.index)):
            twoParTemp = pd.DataFrame({"filename": data["filename"][n],
                                       "mutation": data["mutation"][n],
                                       "fraction": ["Bound", "Diffusing"],
                                       "values": [data["twoParf1"][n], 1 - data["twoParf1"][n]]
                                       }
                                     )
            threeParTemp = pd.DataFrame({"filename": data["filename"][n],
                                         "mutation": data["mutation"][n],
                                         "fraction": ["Bound", "Mixed", "Diffusing"],
                                         "values": [data["threeParf1"][n], data["threeParf2"][n], 1 - data["threeParf1"][n] - data["threeParf2"][n]]
                                         }
                                       )
            twoParBoxData = pd.concat([twoParBoxData, twoParTemp], axis = 0)
            threeParBoxData = pd.concat([threeParBoxData, threeParTemp], axis = 0)
        return twoParBoxData, threeParBoxData

    def getAngleData(self, selectionFile):
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.exposure_time, TrajectoryList.trajID, TrajectoryList.D, TrajectoryList.traj_length, TrajectoryList.maxDistance, AngleList.A1, AngleList.A2, AngleList.A3, AngleList.A4, AngleList.A5, AngleList.A6, AngleList.A7, AngleList.A8, AngleList.A9, AngleList.A10, AngleList.A11, AngleList.A12, AngleList.A13, AngleList.A14, AngleList.A15, AngleList.A16, AngleList.A17, AngleList.A18 from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename INNER JOIN AngleList ON TrajectoryList.trajID = AngleList.trajID WHERE FileList.filename IN {tuple(selectionFile)}", conn)
            else:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.exposure_time, TrajectoryList.trajID, TrajectoryList.D, TrajectoryList.traj_length, TrajectoryList.maxDistance, AngleList.A1, AngleList.A2, AngleList.A3, AngleList.A4, AngleList.A5, AngleList.A6, AngleList.A7, AngleList.A8, AngleList.A9, AngleList.A10, AngleList.A11, AngleList.A12, AngleList.A13, AngleList.A14, AngleList.A15, AngleList.A16, AngleList.A17, AngleList.A18  from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename INNER JOIN AngleList ON TrajectoryList.trajID = AngleList.trajID WHERE FileList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
        return data

    def getDOTFiles(self, selectionFile):
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                # data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.exposure_time, TrajectoryList.traj_length, TrajectoryList.meanX, TrajectoryList.meanY, TrajectoryList.maxDistance, TrajectoryList.meanDistance, TrajectoryList.medianDistance from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename WHERE FileList.filename IN {tuple(selectionFile)} AND TrajectoryList.traj_length > :minTrajLength", conn, params = {"minTrajLength": minTrajLength})
                data = pd.read_sql_query(f"select FileList.filename, FileList.acquisition_rate, FileList.mutation, FileList.exposure_time, TrajectoryList.traj_length, TrajectoryList.meanX, TrajectoryList.meanY, TrajectoryList.maxDistance, TrajectoryList.meanDistance, TrajectoryList.medianDistance from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename WHERE FileList.filename IN {tuple(selectionFile)}", conn)
            else:
                # data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.exposure_time, TrajectoryList.traj_length, TrajectoryList.meanX, TrajectoryList.meanY, TrajectoryList.maxDistance, TrajectoryList.meanDistance, TrajectoryList.medianDistance from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename WHERE FileList.filename = :selectionFile AND TrajectoryList.traj_length > :minTrajLength", conn, params = {"selectionFile": selectionFile[0], "minTrajLength": minTrajLength})
                data = pd.read_sql_query(f"select FileList.filename, FileList.acquisition_rate, FileList.mutation, FileList.exposure_time, TrajectoryList.traj_length, TrajectoryList.meanX, TrajectoryList.meanY, TrajectoryList.maxDistance, TrajectoryList.meanDistance, TrajectoryList.medianDistance from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename WHERE FileList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]}) 
        # data = data.loc[data.exposure_time * data.traj_length > minTrajLength,]
        return data

    def getDOTAngleData(self, selectionFile):
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                data = pd.read_sql_query(f"select FileList.filename, FileList.acquisition_rate, FileList.mutation, FileList.exposure_time, TrajectoryList.trajID, TrajectoryList.D, TrajectoryList.traj_length, TrajectoryList.meanX, TrajectoryList.meanY, TrajectoryList.maxDistance, TrajectoryList.meanDistance, TrajectoryList.medianDistance, AngleList.A1, AngleList.A2, AngleList.A3, AngleList.A4, AngleList.A5, AngleList.A6, AngleList.A7, AngleList.A8, AngleList.A9, AngleList.A10, AngleList.A11, AngleList.A12, AngleList.A13, AngleList.A14, AngleList.A15, AngleList.A16, AngleList.A17, AngleList.A18 from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename INNER JOIN AngleList ON TrajectoryList.trajID = AngleList.trajID WHERE FileList.filename IN {tuple(selectionFile)}", conn)
            else:
                data = pd.read_sql_query(f"select FileList.filename, FileList.acquisition_rate, FileList.mutation, FileList.exposure_time, TrajectoryList.trajID, TrajectoryList.D, TrajectoryList.traj_length, TrajectoryList.meanX, TrajectoryList.meanY, TrajectoryList.maxDistance, TrajectoryList.meanDistance, TrajectoryList.medianDistance, AngleList.A1, AngleList.A2, AngleList.A3, AngleList.A4, AngleList.A5, AngleList.A6, AngleList.A7, AngleList.A8, AngleList.A9, AngleList.A10, AngleList.A11, AngleList.A12, AngleList.A13, AngleList.A14, AngleList.A15, AngleList.A16, AngleList.A17, AngleList.A18  from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename INNER JOIN AngleList ON TrajectoryList.trajID = AngleList.trajID WHERE FileList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
        return data

    def getHeatMapTraj(self, selectionFile, minTrajLength):
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.pixelSize, TrajectoryList.traj_length, TrajectoryList.startTime, TrajectoryList.endTime, TrajectoryList.meanX, TrajectoryList.meanY from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename WHERE FileList.filename IN {tuple(selectionFile)} AND TrajectoryList.traj_length > :minTrajLength", conn, params = {"minTrajLength": minTrajLength})
            else:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.pixelSize, TrajectoryList.traj_length, TrajectoryList.startTime, TrajectoryList.endTime, TrajectoryList.meanX, TrajectoryList.meanY from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename WHERE FileList.filename = :selectionFile AND TrajectoryList.traj_length > :minTrajLength", conn, params = {"selectionFile": selectionFile[0], "minTrajLength": minTrajLength})
        return data

    def getTrackFiles(self, selectionFile):
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, TrajectoryList.trajID, TrajectoryList.traj_length, TrackList.Frame, TrackList.x, TrackList.y from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename INNER JOIN TrackList ON TrajectoryList.trajID = TrackList.trajID WHERE FileList.filename IN {tuple(selectionFile)}", conn)
            else:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, TrajectoryList.trajID, TrajectoryList.traj_length, TrackList.Frame, TrackList.x, TrackList.y from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename INNER JOIN TrackList ON TrajectoryList.trajID = TrackList.trajID WHERE FileList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
        return data

    def getHeatMapTrackData(self, selectionFile):
        # Get tracks data for the DAPI background plot in Heat Map tab
        with sqlite3.connect('database.db') as conn:
            data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.exposure_time, FileList.pixelSize, TrajectoryList.trajID, TrajectoryList.traj_length, TrackList.Frame, TrackList.x, TrackList.y from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename INNER JOIN TrackList ON TrajectoryList.trajID = TrackList.trajID WHERE FileList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
        return data

    def getDwellTimeDensityData(self, selectionFile):
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.exposure_time, FileList.pixelSize, FileList.cellSize, TrajectoryList.trajID, TrajectoryList.traj_length from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename WHERE FileList.filename IN {tuple(selectionFile)}", conn)
            else:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.exposure_time, FileList.pixelSize, FileList.cellSize, TrajectoryList.trajID, TrajectoryList.traj_length from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename WHERE FileList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
        return data

    def getChromatinData(self, selectionFile):
        with sqlite3.connect('database.db') as conn:
            if len(selectionFile) > 1:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.acquisition_rate, FileList.twoParD1, FileList.twoParD2, FileList.threeParD1, FileList.threeParD2, FileList.threeParD3, TrajectoryList.trajID, TrajectoryList.traj_length, TrajectoryList.D, TrajectoryList.maxDistance, TrackList.Frame, TrackList.x, TrackList.y, TrackList.distance, TrackList.bgIntensity, TrackList.bgRegion, AngleList.A1, AngleList.A2, AngleList.A3, AngleList.A4, AngleList.A5, AngleList.A6, AngleList.A7, AngleList.A8, AngleList.A9, AngleList.A10, AngleList.A11, AngleList.A12, AngleList.A13, AngleList.A14, AngleList.A15, AngleList.A16, AngleList.A17, AngleList.A18 from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename INNER JOIN TrackList ON TrajectoryList.trajID = TrackList.trajID INNER JOIN AngleList ON TrackList.trajID = AngleList.trajID WHERE FileList.filename IN {tuple(selectionFile)}", conn)
            else:
                data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.acquisition_rate, FileList.twoParD1, FileList.twoParD2, FileList.threeParD1, FileList.threeParD2, FileList.threeParD3, TrajectoryList.trajID, TrajectoryList.traj_length, TrajectoryList.D, TrajectoryList.maxDistance, TrackList.Frame, TrackList.x, TrackList.y, TrackList.distance, TrackList.bgIntensity, TrackList.bgRegion, AngleList.A1, AngleList.A2, AngleList.A3, AngleList.A4, AngleList.A5, AngleList.A6, AngleList.A7, AngleList.A8, AngleList.A9, AngleList.A10, AngleList.A11, AngleList.A12, AngleList.A13, AngleList.A14, AngleList.A15, AngleList.A16, AngleList.A17, AngleList.A18 from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename INNER JOIN TrackList ON TrajectoryList.trajID = TrackList.trajID INNER JOIN AngleList ON TrackList.trajID = AngleList.trajID WHERE FileList.filename = :selectionFile", conn, params = {"selectionFile": selectionFile[0]})
        return data

    # Plotting
    def produceDiffusionData(self, data, binSize, lowerLimit, upperLimit, errorView, boundaryValue):
        mutations = set(data["mutation"])
        mutations = list(mutations)
        plotData = pd.DataFrame(data = [])
        data = data.loc[data.D > lowerLimit,]
        data = data.loc[data.D < upperLimit,]
        pieData = data >> group_by(X.mutation) >> summarize(BoundFraction = (X.D < boundaryValue).sum() / summary_functions.n(X.D), UnboundFraction = (X.D >= boundaryValue).sum() / summary_functions.n(X.D)) 
        for n in range(len(mutations)):
            dataSubset = data.loc[data["mutation"] == mutations[n]]
            files = set(dataSubset["filename"])
            files = list(files)
            errorData = pd.DataFrame(data = [])
            for m in range(len(files)):
                dataSubSubset = dataSubset.loc[dataSubset["filename"] == files[m]]
                a, binEdges = np.histogram(dataSubSubset['D'], bins = binSize, range = (lowerLimit, upperLimit))
                errorData = pd.concat([pd.DataFrame({f"{files[m]}": a / len(dataSubSubset['D'])}), errorData], axis = 1)
            a, binEdges = np.histogram(dataSubset['D'], bins = binSize, range = (lowerLimit, upperLimit))
            binCenters = 0.5 * (binEdges[:-1] + binEdges[1:])
            if errorView == 0: # data variation
                temp = pd.DataFrame({"x": binCenters, "y": a / len(dataSubset['D']), "error": errorData.max(axis = 1) - errorData.min(axis = 1), "error_minus": (a / len(dataSubset['D'])) - errorData.min(axis = 1), "mutation": [mutations[n]] * binSize})
            elif errorView == 1: # STD
                temp = pd.DataFrame({"x": binCenters, "y": a / len(dataSubset['D']), "error": errorData.std(axis = 1), "mutation": [mutations[n]] * binSize})
            else: # Standard Error of Mean
                temp = pd.DataFrame({"x": binCenters, "y": a / len(dataSubset['D']), "error": errorData.sem(axis = 1), "mutation": [mutations[n]] * binSize})
            plotData = pd.concat([plotData, temp], axis = 0)
            plotData.sort_values(by = ["mutation", "x"], inplace = True)
        if errorView == 0:
            figure = px.line(plotData, x = "x", y = "y", error_y = "error", error_y_minus = "error_minus", color = "mutation", labels = {"x": "Log10(D(um^2/s))", "y": "Normalized Frequency", "mutation": "Condition"})
        else:
            figure = px.line(plotData, x = "x", y = "y", error_y = "error", color = "mutation", labels = {"x": "Log10(D(um^2/s))", "y": "Normalized Frequency", "mutation": "Condition"})
        boundaryLine = pd.DataFrame({"x": [boundaryValue, boundaryValue], "y": [0, max(plotData["y"] + plotData["error"])]})
        figure.add_trace(px.line(boundaryLine, x = "x", y = "y", line_dash_sequence = ["longdashdot"], color_discrete_sequence = ["#7F7F7F"]).data[0])
        figure.update_layout(font = dict(size = 18))
        pieFigure = make_subplots(rows = pieData.shape[0], cols = 1, specs=[[{"type": "domain"}]] * pieData.shape[0])
        for n in range(pieData.shape[0]):
            figureData = pd.DataFrame({"Condition": ["Bound", "Unbound"], 
                                       "Fraction": [pieData.iloc[n, 1], 1.0 - pieData.iloc[n, 1]]
                                      }
                                     )
            figureData.sort_values(by = ["Condition"], inplace = True)
            pieFigure.add_trace(go.Pie(labels = figureData["Condition"], values = figureData["Fraction"], title = pieData["mutation"][n], sort = False), row = n + 1, col = 1)
        pieFigure.update_layout(font = dict(size = 18))
        # plotly.io.write_image(figure, "Images/DiffusionCoefficient.svg")
        plotly.io.write_image(pieFigure, "Images/PieDiffusionCoefficient.svg")
        return figure, pieFigure

    def produceAnglePlots(self, data, dataTrack, boundaryValue, selectionAngle, viewAllData):
        if viewAllData != True:
            with sqlite3.connect('database.db') as conn:
                allData = pd.read_sql_query(f"select FileList.filename, FileList.mutation, FileList.exposure_time, TrajectoryList.trajID, TrajectoryList.D, TrajectoryList.traj_length, TrajectoryList.maxDistance, AngleList.A1, AngleList.A2, AngleList.A3, AngleList.A4, AngleList.A5, AngleList.A6, AngleList.A7, AngleList.A8, AngleList.A9, AngleList.A10, AngleList.A11, AngleList.A12, AngleList.A13, AngleList.A14, AngleList.A15, AngleList.A16, AngleList.A17, AngleList.A18 from FileList INNER JOIN TrajectoryList ON FileList.filename = TrajectoryList.filename INNER JOIN AngleList ON TrajectoryList.trajID = AngleList.trajID", conn)
            mutData = allData >> group_by(X.mutation) >> summarize(A1 = X.A1.sum() / summary_functions.n_distinct(X.filename),
                                                                   A2 = X.A2.sum() / summary_functions.n_distinct(X.filename),
                                                                   A3 = X.A3.sum() / summary_functions.n_distinct(X.filename),
                                                                   A4 = X.A4.sum() / summary_functions.n_distinct(X.filename),
                                                                   A5 = X.A5.sum() / summary_functions.n_distinct(X.filename),
                                                                   A6 = X.A6.sum() / summary_functions.n_distinct(X.filename),
                                                                   A7 = X.A7.sum() / summary_functions.n_distinct(X.filename),
                                                                   A8 = X.A8.sum() / summary_functions.n_distinct(X.filename),
                                                                   A9 = X.A9.sum() / summary_functions.n_distinct(X.filename),
                                                                   A10 = X.A10.sum() / summary_functions.n_distinct(X.filename),
                                                                   A11 = X.A11.sum() / summary_functions.n_distinct(X.filename),
                                                                   A12 = X.A12.sum() / summary_functions.n_distinct(X.filename),
                                                                   A13 = X.A13.sum() / summary_functions.n_distinct(X.filename),
                                                                   A14 = X.A14.sum() / summary_functions.n_distinct(X.filename),
                                                                   A15 = X.A15.sum() / summary_functions.n_distinct(X.filename),
                                                                   A16 = X.A16.sum() / summary_functions.n_distinct(X.filename),
                                                                   A17 = X.A17.sum() / summary_functions.n_distinct(X.filename),
                                                                   A18 = X.A18.sum() / summary_functions.n_distinct(X.filename)
                                                           )
            mutData = mutData.rename(columns = {"A1": "0 - 10",
                                                "A2": "10 - 20",
                                                "A3": "20 - 30",
                                                "A4": "30 - 40",
                                                "A5": "40 - 50",
                                                "A6": "50 - 60",
                                                "A7": "60 - 70",
                                                "A8": "70 - 80",
                                                "A9": "80 - 90",
                                                "A10": "90 - 100",
                                                "A11": "100 - 110",
                                                "A12": "110 - 120",
                                                "A13": "120 - 130",
                                                "A14": "130 - 140",
                                                "A15": "140 - 150",
                                                "A16": "150 - 160",
                                                "A17": "160 - 170",
                                                "A18": "170 - 180"})
            mutData["Base"] = 0
            mutData.loc[:, 1:19] = mutData.iloc[:, 1:19].divide(mutData.sum(1, numeric_only = True), axis = 0)
            mutData = mutData.melt(id_vars = ["mutation", "Base"], var_name = "Theta", value_name = "Counts")
            mutHist = px.bar_polar(mutData, r = "Counts", theta = "Theta", color = "mutation", base = "Base", start_angle = 0, direction = "counterclockwise", labels = {"mutation": "Condition"}, title = "Condition")
            max_r = round(np.max([trace_data.r for trace_data in mutHist.data]), 1)
        # trajIDs = list(dict.fromkeys(dataTrack['trajID']))
        # for n in range(len(trajIDs)):
        #     dataTrack.loc[dataTrack["trajID"] == trajIDs[n], "distance"] = squareform(pdist(dataTrack.loc[dataTrack["trajID"] == trajIDs[n], ["x", "y"]]))[0, ]
        mutData = data >> group_by(X.mutation) >> summarize(A1 = X.A1.sum() / summary_functions.n_distinct(X.filename),
                                                            A2 = X.A2.sum() / summary_functions.n_distinct(X.filename),
                                                            A3 = X.A3.sum() / summary_functions.n_distinct(X.filename),
                                                            A4 = X.A4.sum() / summary_functions.n_distinct(X.filename),
                                                            A5 = X.A5.sum() / summary_functions.n_distinct(X.filename),
                                                            A6 = X.A6.sum() / summary_functions.n_distinct(X.filename),
                                                            A7 = X.A7.sum() / summary_functions.n_distinct(X.filename),
                                                            A8 = X.A8.sum() / summary_functions.n_distinct(X.filename),
                                                            A9 = X.A9.sum() / summary_functions.n_distinct(X.filename),
                                                            A10 = X.A10.sum() / summary_functions.n_distinct(X.filename),
                                                            A11 = X.A11.sum() / summary_functions.n_distinct(X.filename),
                                                            A12 = X.A12.sum() / summary_functions.n_distinct(X.filename),
                                                            A13 = X.A13.sum() / summary_functions.n_distinct(X.filename),
                                                            A14 = X.A14.sum() / summary_functions.n_distinct(X.filename),
                                                            A15 = X.A15.sum() / summary_functions.n_distinct(X.filename),
                                                            A16 = X.A16.sum() / summary_functions.n_distinct(X.filename),
                                                            A17 = X.A17.sum() / summary_functions.n_distinct(X.filename),
                                                            A18 = X.A18.sum() / summary_functions.n_distinct(X.filename)
                                                           )
        mutData = mutData.rename(columns = {"A1": "0 - 10",
                                            "A2": "10 - 20",
                                            "A3": "20 - 30",
                                            "A4": "30 - 40",
                                            "A5": "40 - 50",
                                            "A6": "50 - 60",
                                            "A7": "60 - 70",
                                            "A8": "70 - 80",
                                            "A9": "80 - 90",
                                            "A10": "90 - 100",
                                            "A11": "100 - 110",
                                            "A12": "110 - 120",
                                            "A13": "120 - 130",
                                            "A14": "130 - 140",
                                            "A15": "140 - 150",
                                            "A16": "150 - 160",
                                            "A17": "160 - 170",
                                            "A18": "170 - 180"})
        mutData["Base"] = 0
        mutData.iloc[:, 1:19] = mutData.iloc[:, 1:19].divide(mutData.sum(1, numeric_only = True), axis = 0)
        # Duplicating data for full circle
        mutData.loc[:, "180 - 190"] = mutData.loc[:, "170 - 180"]
        mutData.loc[:, "190 - 200"] = mutData.loc[:, "160 - 170"]
        mutData.loc[:, "200 - 210"] = mutData.loc[:, "150 - 160"]
        mutData.loc[:, "210 - 220"] = mutData.loc[:, "140 - 150"]
        mutData.loc[:, "220 - 230"] = mutData.loc[:, "130 - 140"]
        mutData.loc[:, "230 - 240"] = mutData.loc[:, "120 - 130"]
        mutData.loc[:, "240 - 250"] = mutData.loc[:, "110 - 120"]
        mutData.loc[:, "250 - 260"] = mutData.loc[:, "100 - 110"]
        mutData.loc[:, "260 - 270"] = mutData.loc[:, "90 - 100"]
        mutData.loc[:, "270 - 280"] = mutData.loc[:, "80 - 90"]
        mutData.loc[:, "280 - 290"] = mutData.loc[:, "70 - 80"]
        mutData.loc[:, "290 - 300"] = mutData.loc[:, "60 - 70"]
        mutData.loc[:, "300 - 310"] = mutData.loc[:, "50 - 60"]
        mutData.loc[:, "310 - 320"] = mutData.loc[:, "40 - 50"]
        mutData.loc[:, "320 - 330"] = mutData.loc[:, "30 - 40"]
        mutData.loc[:, "330 - 340"] = mutData.loc[:, "20 - 30"]
        mutData.loc[:, "340 - 350"] = mutData.loc[:, "10 - 20"]
        mutData.loc[:, "350 - 360"] = mutData.loc[:, "0 - 10"]
        mutData = mutData.melt(id_vars = ["mutation", "Base"], var_name = "Theta", value_name = "Counts")
        if viewAllData == True:
            mutHist = px.bar_polar(mutData, r = "Counts", theta = "Theta", color = "mutation", base = "Base", start_angle = 5, direction = "counterclockwise", labels = {"mutation": "Condition"}, title = "Condition") # range_r = [0, 0.1]
        else:
            mutHist = px.bar_polar(mutData, r = "Counts", theta = "Theta", color = "mutation", base = "Base", start_angle = 5, direction = "counterclockwise", labels = {"mutation": "Condition"}, title = "Condition", range_r = [0, max_r])
        mutHist.update_traces(opacity = 0.6)
        mutHist.update_polars(angularaxis_ticklabelstep = 2)

        boundData = data.loc[data.D <= boundaryValue,]
        diffuData = data.loc[data.D > boundaryValue,]
        boundTData = boundData >> summarize(A1 = X.A1.sum() / summary_functions.n_distinct(X.filename),
                                            A2 = X.A2.sum() / summary_functions.n_distinct(X.filename),
                                            A3 = X.A3.sum() / summary_functions.n_distinct(X.filename),
                                            A4 = X.A4.sum() / summary_functions.n_distinct(X.filename),
                                            A5 = X.A5.sum() / summary_functions.n_distinct(X.filename),
                                            A6 = X.A6.sum() / summary_functions.n_distinct(X.filename),
                                            A7 = X.A7.sum() / summary_functions.n_distinct(X.filename),
                                            A8 = X.A8.sum() / summary_functions.n_distinct(X.filename),
                                            A9 = X.A9.sum() / summary_functions.n_distinct(X.filename),
                                            A10 = X.A10.sum() / summary_functions.n_distinct(X.filename),
                                            A11 = X.A11.sum() / summary_functions.n_distinct(X.filename),
                                            A12 = X.A12.sum() / summary_functions.n_distinct(X.filename),
                                            A13 = X.A13.sum() / summary_functions.n_distinct(X.filename),
                                            A14 = X.A14.sum() / summary_functions.n_distinct(X.filename),
                                            A15 = X.A15.sum() / summary_functions.n_distinct(X.filename),
                                            A16 = X.A16.sum() / summary_functions.n_distinct(X.filename),
                                            A17 = X.A17.sum() / summary_functions.n_distinct(X.filename),
                                            A18 = X.A18.sum() / summary_functions.n_distinct(X.filename)
                                           )
        diffuTData = diffuData >> summarize(A1 = X.A1.sum() / summary_functions.n_distinct(X.filename),
                                            A2 = X.A2.sum() / summary_functions.n_distinct(X.filename),
                                            A3 = X.A3.sum() / summary_functions.n_distinct(X.filename),
                                            A4 = X.A4.sum() / summary_functions.n_distinct(X.filename),
                                            A5 = X.A5.sum() / summary_functions.n_distinct(X.filename),
                                            A6 = X.A6.sum() / summary_functions.n_distinct(X.filename),
                                            A7 = X.A7.sum() / summary_functions.n_distinct(X.filename),
                                            A8 = X.A8.sum() / summary_functions.n_distinct(X.filename),
                                            A9 = X.A9.sum() / summary_functions.n_distinct(X.filename),
                                            A10 = X.A10.sum() / summary_functions.n_distinct(X.filename),
                                            A11 = X.A11.sum() / summary_functions.n_distinct(X.filename),
                                            A12 = X.A12.sum() / summary_functions.n_distinct(X.filename),
                                            A13 = X.A13.sum() / summary_functions.n_distinct(X.filename),
                                            A14 = X.A14.sum() / summary_functions.n_distinct(X.filename),
                                            A15 = X.A15.sum() / summary_functions.n_distinct(X.filename),
                                            A16 = X.A16.sum() / summary_functions.n_distinct(X.filename),
                                            A17 = X.A17.sum() / summary_functions.n_distinct(X.filename),
                                            A18 = X.A18.sum() / summary_functions.n_distinct(X.filename)
                                           )
        boundTData.loc[:, "State"] = "Bound"
        boundTData.loc[:, "Base"] = 0
        diffuTData.loc[:, "State"] = "Diffusing"
        diffuTData.loc[:, "Base"] = 0
        stateData = pd.concat([boundTData, diffuTData]) # boundData.append(diffuData)
        stateData = stateData.rename(columns = {"A1": "0 - 10",
                                                "A2": "10 - 20",
                                                "A3": "20 - 30",
                                                "A4": "30 - 40",
                                                "A5": "40 - 50",
                                                "A6": "50 - 60",
                                                "A7": "60 - 70",
                                                "A8": "70 - 80",
                                                "A9": "80 - 90",
                                                "A10": "90 - 100",
                                                "A11": "100 - 110",
                                                "A12": "110 - 120",
                                                "A13": "120 - 130",
                                                "A14": "130 - 140",
                                                "A15": "140 - 150",
                                                "A16": "150 - 160",
                                                "A17": "160 - 170",
                                                "A18": "170 - 180"})
        stateData.iloc[:, 0:18] = stateData.iloc[:, 0:18].divide(stateData.sum(1, numeric_only = True), axis = 0)
        stateData.loc[:, "180 - 190"] = stateData.loc[:, "170 - 180"]
        stateData.loc[:, "190 - 200"] = stateData.loc[:, "160 - 170"]
        stateData.loc[:, "200 - 210"] = stateData.loc[:, "150 - 160"]
        stateData.loc[:, "210 - 220"] = stateData.loc[:, "140 - 150"]
        stateData.loc[:, "220 - 230"] = stateData.loc[:, "130 - 140"]
        stateData.loc[:, "230 - 240"] = stateData.loc[:, "120 - 130"]
        stateData.loc[:, "240 - 250"] = stateData.loc[:, "110 - 120"]
        stateData.loc[:, "250 - 260"] = stateData.loc[:, "100 - 110"]
        stateData.loc[:, "260 - 270"] = stateData.loc[:, "90 - 100"]
        stateData.loc[:, "270 - 280"] = stateData.loc[:, "80 - 90"]
        stateData.loc[:, "280 - 290"] = stateData.loc[:, "70 - 80"]
        stateData.loc[:, "290 - 300"] = stateData.loc[:, "60 - 70"]
        stateData.loc[:, "300 - 310"] = stateData.loc[:, "50 - 60"]
        stateData.loc[:, "310 - 320"] = stateData.loc[:, "40 - 50"]
        stateData.loc[:, "320 - 330"] = stateData.loc[:, "30 - 40"]
        stateData.loc[:, "330 - 340"] = stateData.loc[:, "20 - 30"]
        stateData.loc[:, "340 - 350"] = stateData.loc[:, "10 - 20"]
        stateData.loc[:, "350 - 360"] = stateData.loc[:, "0 - 10"]
        stateData = stateData.melt(id_vars = ["State", "Base"], var_name = "Theta", value_name = "Counts")
        stateHist = px.bar_polar(stateData, r = "Counts", theta = "Theta", color = "State", base = "Base", start_angle = 0, direction = "counterclockwise", title = "State")
        stateHist.update_traces(opacity = 0.6)

        boundData = boundData >> group_by(X.mutation) >> summarize(A1 = X.A1.sum() / summary_functions.n_distinct(X.filename),
                                                                   A2 = X.A2.sum() / summary_functions.n_distinct(X.filename),
                                                                   A3 = X.A3.sum() / summary_functions.n_distinct(X.filename),
                                                                   A4 = X.A4.sum() / summary_functions.n_distinct(X.filename),
                                                                   A5 = X.A5.sum() / summary_functions.n_distinct(X.filename),
                                                                   A6 = X.A6.sum() / summary_functions.n_distinct(X.filename),
                                                                   A7 = X.A7.sum() / summary_functions.n_distinct(X.filename),
                                                                   A8 = X.A8.sum() / summary_functions.n_distinct(X.filename),
                                                                   A9 = X.A9.sum() / summary_functions.n_distinct(X.filename),
                                                                   A10 = X.A10.sum() / summary_functions.n_distinct(X.filename),
                                                                   A11 = X.A11.sum() / summary_functions.n_distinct(X.filename),
                                                                   A12 = X.A12.sum() / summary_functions.n_distinct(X.filename),
                                                                   A13 = X.A13.sum() / summary_functions.n_distinct(X.filename),
                                                                   A14 = X.A14.sum() / summary_functions.n_distinct(X.filename),
                                                                   A15 = X.A15.sum() / summary_functions.n_distinct(X.filename),
                                                                   A16 = X.A16.sum() / summary_functions.n_distinct(X.filename),
                                                                   A17 = X.A17.sum() / summary_functions.n_distinct(X.filename),
                                                                   A18 = X.A18.sum() / summary_functions.n_distinct(X.filename)
                                                                  )
        diffuData = diffuData >> group_by(X.mutation) >> summarize(A1 = X.A1.sum() / summary_functions.n_distinct(X.filename),
                                                                   A2 = X.A2.sum() / summary_functions.n_distinct(X.filename),
                                                                   A3 = X.A3.sum() / summary_functions.n_distinct(X.filename),
                                                                   A4 = X.A4.sum() / summary_functions.n_distinct(X.filename),
                                                                   A5 = X.A5.sum() / summary_functions.n_distinct(X.filename),
                                                                   A6 = X.A6.sum() / summary_functions.n_distinct(X.filename),
                                                                   A7 = X.A7.sum() / summary_functions.n_distinct(X.filename),
                                                                   A8 = X.A8.sum() / summary_functions.n_distinct(X.filename),
                                                                   A9 = X.A9.sum() / summary_functions.n_distinct(X.filename),
                                                                   A10 = X.A10.sum() / summary_functions.n_distinct(X.filename),
                                                                   A11 = X.A11.sum() / summary_functions.n_distinct(X.filename),
                                                                   A12 = X.A12.sum() / summary_functions.n_distinct(X.filename),
                                                                   A13 = X.A13.sum() / summary_functions.n_distinct(X.filename),
                                                                   A14 = X.A14.sum() / summary_functions.n_distinct(X.filename),
                                                                   A15 = X.A15.sum() / summary_functions.n_distinct(X.filename),
                                                                   A16 = X.A16.sum() / summary_functions.n_distinct(X.filename),
                                                                   A17 = X.A17.sum() / summary_functions.n_distinct(X.filename),
                                                                   A18 = X.A18.sum() / summary_functions.n_distinct(X.filename)
                                                                  )
        boundData = boundData.rename(columns = {"A1": "0 - 10",
                                                "A2": "10 - 20",
                                                "A3": "20 - 30",
                                                "A4": "30 - 40",
                                                "A5": "40 - 50",
                                                "A6": "50 - 60",
                                                "A7": "60 - 70",
                                                "A8": "70 - 80",
                                                "A9": "80 - 90",
                                                "A10": "90 - 100",
                                                "A11": "100 - 110",
                                                "A12": "110 - 120",
                                                "A13": "120 - 130",
                                                "A14": "130 - 140",
                                                "A15": "140 - 150",
                                                "A16": "150 - 160",
                                                "A17": "160 - 170",
                                                "A18": "170 - 180"})
        boundData["Base"] = 0
        boundData.iloc[:, 1:19] = boundData.iloc[:, 1:19].divide(boundData.sum(1, numeric_only = True), axis = 0)
        boundData = boundData.melt(id_vars = ["mutation", "Base"], var_name = "Theta", value_name = "Counts")
        boundHist = px.bar_polar(boundData, r = "Counts", theta = "Theta", color = "mutation", base = "Base", start_angle = 5, direction = "counterclockwise", title = "Bound")
        boundHist.update_traces(opacity = 0.6)

        diffuData = diffuData.rename(columns = {"A1": "0 - 10",
                                                "A2": "10 - 20",
                                                "A3": "20 - 30",
                                                "A4": "30 - 40",
                                                "A5": "40 - 50",
                                                "A6": "50 - 60",
                                                "A7": "60 - 70",
                                                "A8": "70 - 80",
                                                "A9": "80 - 90",
                                                "A10": "90 - 100",
                                                "A11": "100 - 110",
                                                "A12": "110 - 120",
                                                "A13": "120 - 130",
                                                "A14": "130 - 140",
                                                "A15": "140 - 150",
                                                "A16": "150 - 160",
                                                "A17": "160 - 170",
                                                "A18": "170 - 180"})
        diffuData["Base"] = 0
        diffuData.iloc[:, 1:19] = diffuData.iloc[:, 1:19].divide(diffuData.sum(1, numeric_only = True), axis = 0)
        diffuData = diffuData.melt(id_vars = ["mutation", "Base"], var_name = "Theta", value_name = "Counts")
        diffuHist = px.bar_polar(diffuData, r = "Counts", theta = "Theta", color = "mutation", base = "Base", start_angle = 0, direction = "counterclockwise", title = "Diffusing")
        diffuHist.update_traces(opacity = 0.6)

        data["Ratio"] = np.log2((data["A1"] + data["A2"] + data["A3"]).div(data["A16"] + data["A17"] + data["A18"]))
        trendPlot = px.scatter(data, x = "D", y = "Ratio", color = "mutation", labels = {"Ratio": "Asymmetry Coefficient", "D": "Log10(D(um^2/s))", "mutation": "Condition"})
        trendPlot.update_traces(opacity = 0.6)

        dataSubset = data.loc[data.loc[:, 'D'] <= boundaryValue, ]
        forwardBound = dataSubset.loc[dataSubset.loc[:, "Ratio"] > 0,]
        backwardBound = dataSubset.loc[dataSubset.loc[:, "Ratio"] < 0,]
        dataSubset = data.loc[data.loc[:, 'D'] > boundaryValue, ]
        forwardDiffu = dataSubset.loc[dataSubset.loc[:, "Ratio"] > 0,]
        backwardDiffu = dataSubset.loc[dataSubset.loc[:, "Ratio"] < 0,]

        # forwardBound["State"] = "Forward Bound"
        # backwardBound["State"] = "Backward Bound"
        # forwardDiffu["State"] = "Forward Diffusing"
        # backwardDiffu["State"] = "Backward Diffusing"
        # forwardBound["State"] = "Forward"
        # backwardBound["State"] = "Backward"
        # forwardDiffu["State"] = "Forward"
        # backwardDiffu["State"] = "Backward"
        forwardBound.loc[:, "State"] = "1"
        backwardBound.loc[:, "State"] = "1"
        forwardDiffu.loc[:, "State"] = "1"
        backwardDiffu.loc[:, "State"] = "1"
        boxData = pd.concat([forwardBound, backwardBound, forwardDiffu, backwardDiffu])
        # boxPlot = px.box(boxData, x = "State", y = "Ratio", color = "mutation", points = "all", labels = {"Ratio": "Asymmetry Ratio"}) 

        # Average AC in each cells that lasted a certain duration each condition (using trajectories)
        boxData = boxData.loc[~boxData.isin([np.nan, np.inf, -np.inf]).any(axis = 1)]
        # boxData.replace([np.inf, -np.inf], 0, inplace = True) #TODO: How to deal with inf and nan?
        lengthData = boxData.copy()
        lengthData['duration'] = lengthData['exposure_time'] * lengthData['traj_length']
        meanET = lengthData["exposure_time"].mean()
        lengthData['bins'] = pd.cut(lengthData['duration'], [meanET, 2 * meanET, 3 * meanET, 4 * meanET, 5 * meanET, 6 * meanET, 7 * meanET, 8 * meanET, 9 * meanET, 10 * meanET]) #[0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20])
        lengthData.drop(lengthData.index[lengthData['bins'].isnull(),], inplace = True)
        for n in range(len(pd.unique(lengthData['bins']))):
            lengthData.loc[lengthData['bins'] == pd.unique(lengthData['bins'])[n], 'bin'] = n * meanET #0.02

        lengthData = lengthData >> group_by(X.filename, X.mutation, X.bin) >> summarize(Ratio = summary_functions.mean(X.Ratio))
        boundHist = px.box(lengthData, x = "bin", y = "Ratio", color = "mutation", points = "all", labels = {"Ratio": "Asymmetry Ratio", "bin": "Trajectory Duration (s)", "mutation": "Condition"}, hover_name = "filename", title = "Lifetime") 

        # distanceData = boxData.copy()
        # distanceData['bins'] = pd.cut(distanceData['maxDistance'], [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
        # distanceData.drop(distanceData.index[distanceData['bins'].isnull(),], inplace = True)
        # for n in range(len(pd.unique(distanceData['bins']))):
        #     distanceData.loc[distanceData['bins'] == pd.unique(distanceData['bins'])[n], 'bin'] = n

        # distanceData = distanceData >> group_by(X.filename, X.mutation, X.bin) >> summarize(Ratio = summary_functions.mean(X.Ratio))
        # diffuHist = px.box(distanceData, x = "bin", y = "Ratio", color = "mutation", points = "all", labels = {"Ratio": "Asymmetry Ratio"}, hover_name = "filename", title = "Translocation")

        # Average AC in each cells that travelled a certain distance each condition (using tracks)
        # mutList = list(dict.fromkeys(dataTrack["mutation"]))
        # transDist = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        # mutAC = pd.DataFrame()
        # for n in range(len(mutList)):
        #     subData = dataTrack.loc[dataTrack.loc[:, "mutation"] == mutList[n], ]
        #     temp = pd.DataFrame({"mutation": [mutList[n]] * len(transDist), "translocation": transDist})
        #     for m in range(len(transDist) - 1):
        #         try:
        #             temp.loc[m, "Ratio"] = np.log2(sum(subData.loc[(subData["distance"] >= transDist[m]) & (subData["distance"] < transDist[m + 1]), "angle"] <= (30 * math.pi / 180)) / sum(subData.loc[(subData["distance"] >= transDist[m]) & (subData["distance"] < transDist[m + 1]), "angle"] >= (150 * math.pi / 180)))
        #         except:
        #             temp.loc[m, "Ratio"] = 0
        #     # temp.drop(len(transDist) - 1, inplace = True)
        #     temp.drop(0, inplace = True)
        #     mutAC = pd.concat([mutAC, temp], ignore_index = True)
        # diffuHist = px.box(mutAC, x = "translocation", y = "Ratio", color = "mutation", points = "all", labels = {"Ratio": "Asymmetry Ratio", "translocation": "Translocation (nm)", "mutation": "Condition"}, title = "Translocation")

        # Average AC in each cells that travelled a certain distance each condition (using tracks) with error bar
        mutList = list(dict.fromkeys(dataTrack["mutation"]))
        transDist = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        binSize = 10
        lowerLimit = 0.0
        upperLimit = 1.0
        errorView = 1
        plotData = pd.DataFrame()
        for n in range(len(mutList)):
            subData = dataTrack.loc[dataTrack.loc[:, "mutation"] == mutList[n], ]
            files = list(dict.fromkeys(subData["filename"]))
            errorData = pd.DataFrame(data = [])
            for m in range(len(files)):
                dataSubset = subData.loc[subData["filename"] == files[m]]
                dataRatio = pd.DataFrame({"mutation": [mutList[n]] * len(transDist), "translocation": transDist})
                for k in range(len(transDist) - 1):
                    try:
                        dataRatio.loc[k, "Ratio"] = np.log2(sum(dataSubset.loc[(dataSubset["distance"] >= transDist[k]) & (dataSubset["distance"] < transDist[k + 1]), "angle"] <= (30 * math.pi / 180)) / sum(subData.loc[(subData["distance"] >= transDist[m]) & (subData["distance"] < transDist[m + 1]), "angle"] >= (150 * math.pi / 180)))
                    except:
                        dataRatio.loc[k, "Ratio"] = 0
                # dataRatio.drop(0, inplace = True)
                a, binEdges = np.histogram(dataRatio['Ratio'], bins = binSize, range = (lowerLimit, upperLimit))
                errorData = pd.concat([pd.DataFrame({f"{files[m]}": dataRatio.loc[0:(binSize - 1), "Ratio"]}), errorData], axis = 1)
            binCenters = 0.5 * (binEdges[:-1] + binEdges[1:])
            if errorView == 0: # data variation
                temp = pd.DataFrame({"x": binCenters, "y": errorData.mean(axis = 1), "error": errorData.max(axis = 1) - errorData.min(axis = 1), "error_minus": errorData.mean(axis = 1) - errorData.min(axis = 1), "mutation": [mutList[n]] * binSize})
            elif errorView == 1: # STD
                temp = pd.DataFrame({"x": binCenters, "y": errorData.mean(axis = 1), "error": errorData.std(axis = 1), "mutation": [mutList[n]] * binSize})
            else: # Standard Error of Mean
                temp = pd.DataFrame({"x": binCenters, "y": errorData.mean(axis = 1), "error": errorData.sem(axis = 1), "mutation": [mutList[n]] * binSize})
            plotData = pd.concat([plotData, temp], axis = 0)
        if errorView == 0:
            diffuHist = px.line(plotData, x = "x", y = "y", error_y = "error", error_y_minus = "error_minus", color = "mutation", labels = {"x": "Translocation (nm)", "y": "Asymmetry Ratio", "mutation": "Condition"})
        else:
            diffuHist = px.line(plotData, x = "x", y = "y", error_y = "error", color = "mutation", labels = {"x": "Translocation (nm)", "y": "Asymmetry Ratio", "mutation": "Condition"})
            
        # Average AC in each cell in each condition
        boxData = boxData >> group_by(X.filename, X.mutation, X.State) >> summarize(Ratio = summary_functions.mean(X.Ratio))
        boxData = boxData.sort_values(by = ["mutation"])
        boxPlot = px.box(boxData, x = "State", y = "Ratio", color = "mutation", points = "all", labels = {"Ratio": "Asymmetry Ratio", "mutation": "Condition"}, hover_name = "filename") 
        return mutHist, stateHist, boundHist, diffuHist, trendPlot, boxPlot

    def produceAngleData(self, data, boundaryValue, selectionAngle):
        data["Ratio"] = np.log2((data["A1"] + data["A2"] + data["A3"]).div(data["A16"] + data["A17"] + data["A18"]))

        dataSubset = data.loc[data.loc[:, 'D'] <= boundaryValue, ]
        forwardBound = dataSubset.loc[dataSubset.loc[:, "Ratio"] > 0,]
        backwardBound = dataSubset.loc[dataSubset.loc[:, "Ratio"] < 0,]
        dataSubset = data.loc[data.loc[:, 'D'] > boundaryValue, ]
        forwardDiffu = dataSubset.loc[dataSubset.loc[:, "Ratio"] > 0,]
        backwardDiffu = dataSubset.loc[dataSubset.loc[:, "Ratio"] < 0,]

        # forwardBound["State"] = "Forward Bound"
        # backwardBound["State"] = "Backward Bound"
        # forwardDiffu["State"] = "Forward Diffusing"
        # backwardDiffu["State"] = "Backward Diffusing"
        # forwardBound["State"] = "Forward"
        # backwardBound["State"] = "Backward"
        # forwardDiffu["State"] = "Forward"
        # backwardDiffu["State"] = "Backward"
        forwardBound["State"] = "1"
        backwardBound["State"] = "1"
        forwardDiffu["State"] = "1"
        backwardDiffu["State"] = "1"
        boxData = pd.concat([forwardBound, backwardBound, forwardDiffu, backwardDiffu])
        # boxPlot = px.box(boxData, x = "State", y = "Ratio", color = "mutation", points = "all", labels = {"Ratio": "Asymmetry Ratio"}) 

        boxData.replace([np.inf, -np.inf], 0, inplace = True)
        boxData = boxData >> group_by(X.filename, X.mutation, X.State) >> summarize(Ratio = summary_functions.mean(X.Ratio))
        boxData = boxData.sort_values(by = ["mutation"])
        return boxData

    def getDOTData(self, data, dOTRegions, minTrajLength):
        coord = data[["meanX", "meanY"]].to_numpy().astype(float)
        temp = chull(coord) # TODO: Do for each cell or condition?
        boundaryRegionPoints = np.append(temp.vertices, temp.vertices[0]) # list(set(temp.vertices)) # list(set([i for row in temp.simplices for i in row]))
        boundaryRegion = np.array(coord[boundaryRegionPoints, :]) #outside most points
        centerPoint = np.mean(boundaryRegion, axis = 0)
        data = data.assign(traj_duration = data["exposure_time"] * data["traj_length"])

        # In theory, I could just replace the data and coord with the selectedData and selectedCoord, they're already used in defining the region
        selectedData = data.loc[data.traj_duration > minTrajLength,]
        selectedCoord = selectedData[["meanX", "meanY"]].to_numpy().astype(float)
        figure = px.scatter(selectedData, x = "meanX", y = "meanY", color = "traj_duration", size = "maxDistance", labels = {"meanX": "X (\u03BCm)", "meanY": "Y (\u03BCm)"})

        # First row of data
        newBoundaryRegion = ((boundaryRegion - centerPoint) * dOTRegions[0]) + centerPoint
        boundaryRegionDF = pd.DataFrame({"x": newBoundaryRegion[:, 0], "y": newBoundaryRegion[:, 1]})
        figure.add_trace(px.line(boundaryRegionDF, x = "x", y = "y").data[0])
        polygon = mpltPath.Path(newBoundaryRegion)
        pointsWithinPolygon = polygon.contains_points(selectedCoord)
        # Prepare dataframe
        plotData = selectedData.loc[pointsWithinPolygon]
        plotData["Region"] = [str(dOTRegions[0])] * len(plotData) # produce error of try to use .iloc, safe to ignore
        for n in range(1, len(dOTRegions)):
            # Drawing the border
            nextBoundaryRegion = ((boundaryRegion - centerPoint) * dOTRegions[n]) + centerPoint
            nextBoundaryRegionDF = pd.DataFrame({"x": nextBoundaryRegion[:, 0], "y": nextBoundaryRegion[:, 1]})
            figure.add_trace(px.line(nextBoundaryRegionDF, x = "x", y = "y").data[0])
            # Computing the values
            nextPolygon = mpltPath.Path(nextBoundaryRegion)
            pointsWithinNextPolygon = nextPolygon.contains_points(selectedCoord)

            temp = selectedData.iloc[pointsWithinNextPolygon].merge(selectedData.iloc[pointsWithinPolygon], how = "outer", indicator = True).loc[lambda x : x['_merge']=='left_only']
            temp["Region"] = [str(dOTRegions[n])] * len(temp)
            plotData = pd.concat([plotData, temp], axis = 0)

            # Prepare for next loop
            pointsWithinPolygon = pointsWithinNextPolygon
        # Final row of table
        boundaryRegionDF = pd.DataFrame({"x": boundaryRegion[:, 0], "y": boundaryRegion[:, 1]})
        figure.add_trace(px.line(boundaryRegionDF, x = "x", y = "y").data[0])

        temp = selectedData.merge(selectedData.iloc[pointsWithinPolygon], how = "outer", indicator = True).loc[lambda x : x['_merge']=='left_only']
        temp["Region"] = ["1.0"] * len(temp)
        plotData = pd.concat([plotData, temp], axis = 0)

        tableData = plotData >> group_by(X.Region) >> summarize(number = summary_functions.n(X.traj_duration), max = X.traj_duration.max(), mean = X.traj_duration.mean(), median = X.traj_duration.median())
        boxData = (plotData >> group_by(X.filename, X.acquisition_rate, X.mutation, X.Region) >> summarize(max = X.traj_duration.max(), mean = X.traj_duration.mean(), median = X.traj_duration.median()))
        boxData["mutation"] = boxData["acquisition_rate"] + "-" + boxData["mutation"]
        boxData = boxData.sort_values(by=['Region'])
        return tableData, boxData, figure

    def produceDOTAngleData(self, data, dOTRegions, minTrajLength, maxAC):
        # Normalization
        # data = data >> summarize(A1 = X.A1.sum() / summary_functions.n_distinct(X.filename),
        #                          A2 = X.A2.sum() / summary_functions.n_distinct(X.filename),
        #                          A3 = X.A3.sum() / summary_functions.n_distinct(X.filename),
        #                          A4 = X.A4.sum() / summary_functions.n_distinct(X.filename),
        #                          A5 = X.A5.sum() / summary_functions.n_distinct(X.filename),
        #                          A6 = X.A6.sum() / summary_functions.n_distinct(X.filename),
        #                          A7 = X.A7.sum() / summary_functions.n_distinct(X.filename),
        #                          A8 = X.A8.sum() / summary_functions.n_distinct(X.filename),
        #                          A9 = X.A9.sum() / summary_functions.n_distinct(X.filename),
        #                          A10 = X.A10.sum() / summary_functions.n_distinct(X.filename),
        #                          A11 = X.A11.sum() / summary_functions.n_distinct(X.filename),
        #                          A12 = X.A12.sum() / summary_functions.n_distinct(X.filename),
        #                          A13 = X.A13.sum() / summary_functions.n_distinct(X.filename),
        #                          A14 = X.A14.sum() / summary_functions.n_distinct(X.filename),
        #                          A15 = X.A15.sum() / summary_functions.n_distinct(X.filename),
        #                          A16 = X.A16.sum() / summary_functions.n_distinct(X.filename),
        #                          A17 = X.A17.sum() / summary_functions.n_distinct(X.filename),
        #                          A18 = X.A18.sum() / summary_functions.n_distinct(X.filename)
        #                         )
        data["Ratio"] = np.log2((data["A1"] + data["A2"] + data["A3"]).div(data["A16"] + data["A17"] + data["A18"]))
        data.replace([np.inf, -np.inf], 0, inplace = True)
        data = data.assign(traj_duration = data["exposure_time"] * data["traj_length"])
        # Remove the data that are lesser than required trajectory length
        filteredData = data.loc[data.traj_duration > minTrajLength,]
        filteredData.reset_index(inplace = True)
        filteredData = filteredData.loc[filteredData.Ratio < maxAC,] # adding the ability to filter by angle AC
        filteredData.reset_index(inplace = True)

        # Create a new dataframe to store all the data
        regionsLabel = dOTRegions.copy()
        regionsLabel.append(1.0)
        # Convert the label to string to force the ticks mark in the box figure later
        regionsLabel = [str(n) for n in regionsLabel]
        finalData = pd.DataFrame({"filename": list(dict.fromkeys(filteredData["filename"])), "mutation": [file.split("_")[0] for file in list(dict.fromkeys(filteredData["filename"]))], "Region": [regionsLabel] * len(list(dict.fromkeys(filteredData["filename"]))), "number": 0, "max": 0, "mean": 0, "median": 0}).explode("Region")

        mutList = list(dict.fromkeys(filteredData["mutation"]))
        for n in range(len(mutList)):
            cellList = list(dict.fromkeys(filteredData.loc[filteredData["mutation"] == mutList[n], "filename"]))
            for m in range(len(cellList)):
                selectedData = filteredData.loc[filteredData["filename"] == cellList[m], ]
                # coord = selectedData.loc[selectedData["filename"] == cellList[m], ["meanX", "meanY"]].to_numpy().astype(float)
                # dataCell use ALL the trajectories of the file (to get the nucleus shape without filter yet)
                dataCell = data.loc[data["filename"] == cellList[m], ]
                coord = dataCell[["meanX", "meanY"]].to_numpy().astype(float)
                temp = chull(coord)
                # Add the first data point back to the last data point to ensure a full circle
                boundaryRegionPoints = np.append(temp.vertices, temp.vertices[0])
                # Get the coordinates of the outside most points
                boundaryRegion = np.array(coord[boundaryRegionPoints, :])
                # Calculate the mean of all the outside points to be used as center point
                centerPoint = np.mean(boundaryRegion, axis = 0)
                # Prepare the DoT figure
                figure = px.scatter(selectedData, x = "meanX", y = "meanY", color = "traj_duration", size = "maxDistance", labels = {"meanX": "X (\u03BCm)", "meanY": "Y (\u03BCm)"})

                newBoundaryRegion = ((boundaryRegion - centerPoint) * dOTRegions[0]) + centerPoint
                boundaryRegionDF = pd.DataFrame({"x": newBoundaryRegion[:, 0], "y": newBoundaryRegion[:, 1]})
                figure.add_trace(px.line(boundaryRegionDF, x = "x", y = "y").data[0])
                polygon = mpltPath.Path(newBoundaryRegion)
                # Only count the trajectories of those are pass the QC/filter (minimum trajectory length and AC)
                selectedCoord = selectedData[["meanX", "meanY"]].to_numpy().astype(float)
                pointsWithinPolygon = polygon.contains_points(selectedCoord)

                plotData = selectedData.loc[pointsWithinPolygon]
                # Assign region data to the data frame
                # plotData["Region"] = [str(dOTRegions[0])] * len(plotData) # Produce error of try to use .iloc
                plotData = plotData.assign(Region = str(dOTRegions[0]))
                for p in range(1, len(dOTRegions)):
                    # Drawing the border
                    nextBoundaryRegion = ((boundaryRegion - centerPoint) * dOTRegions[p]) + centerPoint
                    nextBoundaryRegionDF = pd.DataFrame({"x": nextBoundaryRegion[:, 0], "y": nextBoundaryRegion[:, 1]})
                    figure.add_trace(px.line(nextBoundaryRegionDF, x = "x", y = "y").data[0])
                    # Computing the values
                    nextPolygon = mpltPath.Path(nextBoundaryRegion)
                    pointsWithinNextPolygon = nextPolygon.contains_points(selectedCoord)

                    temp = selectedData.iloc[pointsWithinNextPolygon].merge(selectedData.iloc[pointsWithinPolygon], how = "outer", indicator = True).loc[lambda x : x['_merge']=='left_only']
                    temp["Region"] = [str(dOTRegions[p])] * len(temp)
                    plotData = pd.concat([plotData, temp], axis = 0)

                    # Prepare for next loop
                    pointsWithinPolygon = pointsWithinNextPolygon
                # Final row of table
                boundaryRegionDF = pd.DataFrame({"x": boundaryRegion[:, 0], "y": boundaryRegion[:, 1]})
                figure.add_trace(px.line(boundaryRegionDF, x = "x", y = "y").data[0])

                temp = selectedData.merge(selectedData.iloc[pointsWithinPolygon], how = "outer", indicator = True).loc[lambda x : x['_merge']=='left_only']
                temp["Region"] = ["1.0"] * len(temp)
                plotData = pd.concat([plotData, temp], axis = 0)
                plotDataGroup = plotData.groupby("Region")["traj_duration"]
                if len(plotDataGroup.count()) == len(regionsLabel):
                    finalData.loc[finalData["filename"] == cellList[m], "number"] = plotDataGroup.count().to_list()
                    finalData.loc[finalData["filename"] == cellList[m], "max"] = plotDataGroup.max().to_list()
                    finalData.loc[finalData["filename"] == cellList[m], "mean"] = plotDataGroup.mean().to_list()
                    finalData.loc[finalData["filename"] == cellList[m], "median"] = plotDataGroup.median().to_list()
                else:
                    # To account for situation where there's no data in certain regions
                    regionsWithData = plotDataGroup.count().index.to_list()
                    numberData = plotDataGroup.count().to_list()
                    maxData = plotDataGroup.max().to_list()
                    meanData = plotDataGroup.mean().to_list()
                    medianData = plotDataGroup.median().to_list()
                    dataSlot = 0
                    for p in range(len(regionsLabel)):
                        regionInterested = regionsLabel[p]
                        if regionInterested in regionsWithData:
                            finalData.loc[(finalData["filename"] == cellList[m]) & (finalData["Region"] == regionInterested), "number"] = numberData[dataSlot]
                            finalData.loc[(finalData["filename"] == cellList[m]) & (finalData["Region"] == regionInterested), "max"] = maxData[dataSlot]
                            finalData.loc[(finalData["filename"] == cellList[m]) & (finalData["Region"] == regionInterested), "mean"] = meanData[dataSlot]
                            finalData.loc[(finalData["filename"] == cellList[m]) & (finalData["Region"] == regionInterested), "median"] = medianData[dataSlot]
                            dataSlot += 1
        
        # coord = data[["meanX", "meanY"]].to_numpy().astype(float)
        # temp = chull(coord) # TODO: Do for each cell or condition?
        # boundaryRegionPoints = np.append(temp.vertices, temp.vertices[0]) # list(set(temp.vertices)) # list(set([i for row in temp.simplices for i in row]))
        # boundaryRegion = np.array(coord[boundaryRegionPoints, :]) #outside most points
        # centerPoint = np.mean(boundaryRegion, axis = 0)
        # data = data.assign(traj_duration = data["exposure_time"] * data["traj_length"])

        # # In theory, I could just replace the data and coord with the selectedData and selectedCoord, they're already used in defining the region
        # selectedData = data.loc[data.traj_duration > minTrajLength,]
        # selectedData.reset_index(inplace = True)
        # selectedData = selectedData.loc[selectedData.Ratio < maxAC,] # adding the ability to filter by angle AC
        # selectedCoord = selectedData[["meanX", "meanY"]].to_numpy().astype(float)
        # figure = px.scatter(selectedData, x = "meanX", y = "meanY", color = "traj_duration", size = "maxDistance", labels = {"meanX": "X (\u03BCm)", "meanY": "Y (\u03BCm)"})

        # # First row of data
        # newBoundaryRegion = ((boundaryRegion - centerPoint) * dOTRegions[0]) + centerPoint
        # boundaryRegionDF = pd.DataFrame({"x": newBoundaryRegion[:, 0], "y": newBoundaryRegion[:, 1]})
        # figure.add_trace(px.line(boundaryRegionDF, x = "x", y = "y").data[0])
        # polygon = mpltPath.Path(newBoundaryRegion)
        # pointsWithinPolygon = polygon.contains_points(selectedCoord)
        # Prepare dataframe
        # plotData = selectedData.loc[pointsWithinPolygon]
        # plotData["Region"] = [str(dOTRegions[0])] * len(plotData) # produce error of try to use .iloc, safe to ignore
        # for n in range(1, len(dOTRegions)):
        #     # Drawing the border
        #     nextBoundaryRegion = ((boundaryRegion - centerPoint) * dOTRegions[n]) + centerPoint
        #     nextBoundaryRegionDF = pd.DataFrame({"x": nextBoundaryRegion[:, 0], "y": nextBoundaryRegion[:, 1]})
        #     figure.add_trace(px.line(nextBoundaryRegionDF, x = "x", y = "y").data[0])
        #     # Computing the values
        #     nextPolygon = mpltPath.Path(nextBoundaryRegion)
        #     pointsWithinNextPolygon = nextPolygon.contains_points(selectedCoord)

        #     temp = selectedData.iloc[pointsWithinNextPolygon].merge(selectedData.iloc[pointsWithinPolygon], how = "outer", indicator = True).loc[lambda x : x['_merge']=='left_only']
        #     temp["Region"] = [str(dOTRegions[n])] * len(temp)
        #     plotData = pd.concat([plotData, temp], axis = 0)

        #     # Prepare for next loop
        #     pointsWithinPolygon = pointsWithinNextPolygon
        # # Final row of table
        # boundaryRegionDF = pd.DataFrame({"x": boundaryRegion[:, 0], "y": boundaryRegion[:, 1]})
        # figure.add_trace(px.line(boundaryRegionDF, x = "x", y = "y").data[0])

        # temp = selectedData.merge(selectedData.iloc[pointsWithinPolygon], how = "outer", indicator = True).loc[lambda x : x['_merge']=='left_only']
        # temp["Region"] = ["1.0"] * len(temp)
        # plotData = pd.concat([plotData, temp], axis = 0)

        # tableData = plotData >> group_by(X.Region) >> summarize(number = summary_functions.n(X.traj_duration), max = X.traj_duration.max(), mean = X.traj_duration.mean(), median = X.traj_duration.median())
        # boxData = (plotData >> group_by(X.filename, X.acquisition_rate, X.mutation, X.Region) >> summarize(max = X.traj_duration.max(), mean = X.traj_duration.mean(), median = X.traj_duration.median()))
        tableData = pd.DataFrame({"number": finalData.groupby("Region")["number"].sum(), "max": finalData.groupby("Region")["max"].max(), "mean": finalData.groupby("Region")["mean"].mean(), "median": finalData.groupby("Region")["median"].median()})
        tableData.reset_index(inplace = True)
        boxData = finalData
        # boxData["mutation"] = boxData["acquisition_rate"] + "-" + boxData["mutation"]
        boxData = boxData.sort_values(by=['Region'])
        return tableData, boxData, figure

    def produceDwellTimeFigures(self, selectionFile):
        # filter out to only slow acquisition data first
        try:
            with sqlite3.connect('database.db') as conn: #TODO : Filter out filename with slow acquisition time first and then search the database with the slow acquisition filename only
                if len(selectionFile) > 1:
                    data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, DwellTimeData.R1, DwellTimeData.R2, DwellTimeData.F from FileList INNER JOIN DwellTimeData ON FileList.filename = DwellTimeData.filename WHERE FileList.filename IN {tuple(selectionFile)} AND acquisition_rate = 'slow'", conn)
                else:
                    data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, DwellTimeData.R1, DwellTimeData.R2, DwellTimeData.F from FileList INNER JOIN DwellTimeData ON FileList.filename = DwellTimeData.filename WHERE FileList.filename = :selectionFile AND acquisition_rate = 'slow'", conn, params = {"selectionFile": selectionFile[0]})
            if len(data.index) > 0:
                dwellData = pd.DataFrame()
                for n in range(len(data.index)):
                    dwellDataTemp = pd.DataFrame({"filename": data["filename"][n],
                                                "mutation": data["mutation"][n],
                                                "R": ["Long", "Short"],
                                                "rTime": [data["R1"][n], data["R2"][n]],
                                                "Fraction": [data["F"][n], 1 - data["F"][n]]
                                               }
                                              )
                    dwellData = pd.concat([dwellData, dwellDataTemp], axis = 0)
                dwellData.sort_values(by = ["mutation"], inplace = True)
                boxFigure = px.box(dwellData, x = "R", y = "rTime", color = "mutation", points = "all", labels = {"R": "Dwell-Time Types", "rTime": "Dwell-Time (s)", "mutation": "Condition"}, hover_name = "filename")
                
                densityData = self.getDwellTimeDensityData(selectionFile)
                # Convert traj_length to seconds
                densityData.loc[:, "traj_length"] = densityData.loc[:, "exposure_time"] * densityData.loc[:, "traj_length"]
                processedDensityData = data.copy()
                fileList = list(set(data.loc[:, "filename"]))
                for file in fileList:
                    trajNumber = len(densityData.loc[densityData.loc[:, "filename"] == file, "traj_length"] > data.loc[data.loc[:, "filename"] == file, "R1"].to_list()[0])
                    cellArea = densityData.loc[densityData.loc[:, "filename"] == file, "pixelSize"]**2 * densityData.loc[densityData.loc[:, "filename"] == file, "cellSize"]
                    processedDensityData.loc[processedDensityData.loc[:, "filename"] == file, "Density"] = trajNumber / cellArea.mean()
                processedDensityData.sort_values(by = ["mutation"], inplace = True)
                densityFigure = px.box(processedDensityData, y = "Density", color = "mutation", points = "all", hover_name = "filename", title = "Long Dwell Time Trajectories Density", labels = {"Density": "Trajectories per Area (um^2)", "mutation": "Condition"})

                pieData = data >> group_by(X.mutation) >> summarize(Long = X.F.mean(), Short = (1 - X.F.mean()))
                pieData.sort_values(by = ["mutation"], inplace = True)
                pieFigure = make_subplots(rows = pieData.shape[0], cols = 1, specs=[[{"type": "domain"}]] * pieData.shape[0])
                for n in range(pieData.shape[0]):
                    figureData = pd.DataFrame({"Condition": ["Long", "Short"], 
                                               "Fraction": [pieData["Long"][n], pieData["Short"][n]]
                                              }
                                             )
                    figureData.sort_values(by = ["Condition"], inplace = True)
                    pieFigure.add_trace(go.Pie(labels = figureData["Condition"], values = figureData["Fraction"], title = pieData["mutation"][n], sort = False), row = n + 1, col = 1)
                pieFigure.update_layout(font = dict(size = 18))
                pieFigure.update_traces(marker = dict(colors = ['black', 'grey']))
            else:
                boxFigure = [None]
                densityFigure = [None]
                pieFigure = [None]
        except:
            boxFigure = [None]
            densityFigure = [None]
            pieFigure = [None]
        return boxFigure, densityFigure, pieFigure

    # Data saving
    def produceDiffusionExportData(self, data, binSize, lowerLimit, upperLimit, errorView, boundaryValue):
        mutations = set(data["mutation"])
        mutations = list(mutations)
        plotData = pd.DataFrame(data = [])
        data = data.loc[data.D > lowerLimit,]
        data = data.loc[data.D < upperLimit,]
        pieData = data >> group_by(X.mutation) >> summarize(BoundFraction = (X.D < boundaryValue).sum() / summary_functions.n(X.D), UnboundFraction = (X.D >= boundaryValue).sum() / summary_functions.n(X.D)) 
        for n in range(len(mutations)):
            dataSubset = data.loc[data["mutation"] == mutations[n]]
            files = set(dataSubset["filename"])
            files = list(files)
            errorData = pd.DataFrame(data = [])
            for m in range(len(files)):
                dataSubSubset = dataSubset.loc[dataSubset["filename"] == files[m]]
                a, binEdges = np.histogram(dataSubSubset['D'], bins = binSize, range = (lowerLimit, upperLimit))
                errorData = pd.concat([pd.DataFrame({f"{files[m]}": a / len(dataSubSubset['D'])}), errorData], axis = 1)
            a, binEdges = np.histogram(dataSubset['D'], bins = binSize, range = (lowerLimit, upperLimit))
            binCenters = 0.5 * (binEdges[:-1] + binEdges[1:])
            if errorView == 0: # data variation
                temp = pd.DataFrame({"x": binCenters, "y": a / len(dataSubset['D']), "error": errorData.max(axis = 1) - errorData.min(axis = 1), "error_minus": (a / len(dataSubset['D'])) - errorData.min(axis = 1), "mutation": [mutations[n]] * binSize})
            elif errorView == 1: # STD
                temp = pd.DataFrame({"x": binCenters, "y": a / len(dataSubset['D']), "error": errorData.std(axis = 1), "mutation": [mutations[n]] * binSize})
            else: # Standard Error of Mean
                temp = pd.DataFrame({"x": binCenters, "y": a / len(dataSubset['D']), "error": errorData.sem(axis = 1), "mutation": [mutations[n]] * binSize})
            plotData = pd.concat([plotData, temp], axis = 0)
            plotData.sort_values(by = ["mutation", "x"], inplace = True)
        return plotData, pieData

    def produceDwellTimeData(self, selectionFile):
        # filter out to only slow acquisition data first
        try:
            with sqlite3.connect('database.db') as conn: #TODO : Filter out filename with slow acquisition time first and then search the database with the slow acquisition filename only
                if len(selectionFile) > 1:
                    data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, DwellTimeData.R1, DwellTimeData.R2, DwellTimeData.F from FileList INNER JOIN DwellTimeData ON FileList.filename = DwellTimeData.filename WHERE FileList.filename IN {tuple(selectionFile)} AND acquisition_rate = 'slow'", conn)
                else:
                    data = pd.read_sql_query(f"select FileList.filename, FileList.mutation, DwellTimeData.R1, DwellTimeData.R2, DwellTimeData.F from FileList INNER JOIN DwellTimeData ON FileList.filename = DwellTimeData.filename WHERE FileList.filename = :selectionFile AND acquisition_rate = 'slow'", conn, params = {"selectionFile": selectionFile[0]})
            if len(data.index) > 0:
                dwellData = pd.DataFrame()
                for n in range(len(data.index)):
                    dwellDataTemp = pd.DataFrame({"filename": data["filename"][n],
                                                "mutation": data["mutation"][n],
                                                "R": ["Long", "Short"],
                                                "rTime": [data["R1"][n], data["R2"][n]],
                                                "Fraction": [data["F"][n], 1 - data["F"][n]]
                                               }
                                              )
                    dwellData = pd.concat([dwellData, dwellDataTemp], axis = 0)
                boxFigure = px.box(dwellData, x = "R", y = "rTime", color = "mutation", points = "all", labels = {"R": "Dwell-Time Types", "rTime": "Dwell-Time (s)", "mutation": "Condition"}, hover_name = "filename")
                
                densityData = self.getDwellTimeDensityData(selectionFile)
                # Convert traj_length to seconds
                densityData.loc[:, "traj_length"] = densityData.loc[:, "exposure_time"] * densityData.loc[:, "traj_length"]
                processedDensityData = data.copy()
                fileList = list(set(data.loc[:, "filename"]))
                for file in fileList:
                    trajNumber = len(densityData.loc[densityData.loc[:, "filename"] == file, "traj_length"] > data.loc[data.loc[:, "filename"] == file, "R1"].to_list()[0])
                    cellArea = densityData.loc[densityData.loc[:, "filename"] == file, "pixelSize"]**2 * densityData.loc[densityData.loc[:, "filename"] == file, "cellSize"]
                    processedDensityData.loc[processedDensityData.loc[:, "filename"] == file, "Density"] = trajNumber / cellArea.mean()
                densityFigure = px.box(processedDensityData, y = "Density", color = "mutation", points = "all", hover_name = "filename", title = "Long Dwell Time Trajectories Density", labels = {"Density": "Trajectories per Area (um^2)", "mutation": "Condition"})

                pieData = data >> group_by(X.mutation) >> summarize(Long = X.F.mean(), Short = (1 - X.F.mean()))
                pieFigure = make_subplots(rows = pieData.shape[0], cols = 1, specs=[[{"type": "domain"}]] * pieData.shape[0])
                for n in range(pieData.shape[0]):
                    figureData = pd.DataFrame({"Condition": ["Long", "Short"], 
                                               "Fraction": [pieData["Long"][n], pieData["Short"][n]]
                                              }
                                             )
                    figureData.sort_values(by = ["Condition"], inplace = True)
                    pieFigure.add_trace(go.Pie(labels = figureData["Condition"], values = figureData["Fraction"], title = pieData["mutation"][n], sort = False), row = n + 1, col = 1)
                pieFigure.update_layout(font = dict(size = 18))
                pieFigure.update_traces(marker = dict(colors = ['black', 'grey']))
            else:
                dwellData = [None]
                processedDensityData = [None]
                figureData = [None]
        except:
            dwellData = [None]
            processedDensityData = [None]
            figureData = [None]
        return dwellData, processedDensityData, figureData

class GICDashboard(QWidget):
    def __init__(self):
        # super(GICDashboard, self).__init__(parent)
        super().__init__()

        # Pre-allocate arrays to save upload settings
        self.fastSettings = []
        self.slowSettings = []

        # Creating minimize and maximize buttons for the dashboard window
        self.originalPalette = QApplication.palette()
        # self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        # self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        # Defining loading view for Figures
        self.loadingHtml = '<center><span class="pp">Loading</span></center>'

        self.libDir = files("gictrack")
        # Input logo images
        logoCI = QLabel(self)
        pixmap = QPixmap(str(files("gictrack").joinpath("Centenary_Institute_logo.png")))
        # pixmap = QPixmap("Centenary_Institute_logo.png")
        logoCI.setPixmap(pixmap.scaled(200, 120))
        logoGIC = QLabel(self)
        pixmap = QPixmap(str(files("gictrack").joinpath("GIC.png")))
        # pixmap = QPixmap("GIC.png")
        logoGIC.setPixmap(pixmap.scaled(200, 120))

        # Input Dashboard Title
        dashboardTitle = QLabel("Transcription Factor Analysis Dashboard")
        dashboardTitle.setFont(QFont("Arial", 24))

        # Generate tabs, file selection and note widgets
        self.create_tabs()
        self.createDataSelectionPanel()
        self.exportDatabase = QPushButton("Export Database")
        self.exportDatabase.setDefault(True)
        self.importDatabase = QPushButton("Import Database")
        self.importDatabase.setDefault(True)
        self.textEdit = QTextEdit()

        # Creating the upper end of the dashboard
        topLayout = QHBoxLayout()
        topLayout.addStretch()
        topLayout.addWidget(logoCI)
        topLayout.addWidget(dashboardTitle)
        topLayout.addWidget(logoGIC)
        topLayout.addStretch()

        # Creating the left hand side and main body of the dashboard
        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 3) # y, x, y-span, x-span
        mainLayout.addWidget(self.dataSelectionPanel, 1, 0)
        mainLayout.addWidget(self.exportDatabase, 3, 0)
        mainLayout.addWidget(self.importDatabase, 4, 0)
        mainLayout.addWidget(self.tabsPage, 1, 1, 4, 3)
        mainLayout.addWidget(self.textEdit, 2, 0)
        mainLayout.setRowStretch(1, 1) # stretching which row, by how much
        mainLayout.setRowStretch(2, 1)
        mainLayout.setRowStretch(3, 1)
        mainLayout.setRowStretch(4, 1)
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 2)
        mainLayout.setColumnStretch(2, 2)
        self.setLayout(mainLayout)

        self.setWindowTitle("Genome Imaging Centre Dashboard")
        self.changeStyle('Fusion')

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        QApplication.setPalette(QApplication.style().standardPalette())

    def closeEvent(self, event):
        with sqlite3.connect('database.db') as conn:
            textData = pd.DataFrame({"text": self.textEdit.toPlainText()}, index = [0])
            textData.to_sql('Settings', conn, if_exists="replace")
        # with open('Notes.txt', 'w') as f:
        #     f.write(self.textEdit.toPlainText())
        try:
            len(self.uploadSettings)
        except:
            self.uploadSettings = pd.DataFrame()
        if self.acquisitionRateFast.isChecked():
            presetType = "fast"
        else:
            presetType = "slow"
        self.uploadSettings.loc[0, "coreNum"] = str(self.parallelizationCores.value())
        self.uploadSettings.loc[0, "bleachRate"] = str(self.bleachRate.value())
        self.uploadSettings.loc[0, presetType + "AnalysisType"] = str(int(self.analysisTypeNumber.isChecked()))
        self.uploadSettings.loc[0, presetType + "ClipFactor"] = str(self.clipFactorBox.value())
        self.uploadSettings.loc[0, presetType + "TrajLength"] = str(self.trajectoryLengthBox.value())
        self.uploadSettings.loc[0, presetType + "MinTrajNum"] = str(self.minTrajectoryNumberBox.value())
        self.uploadSettings.loc[0, presetType + "Tolerance"] = str(self.toleranceBox.value())
        self.uploadSettings.loc[0, presetType + "LocError"] = str(self.localizationErrorBox.value())
        self.uploadSettings.loc[0, presetType + "EmmWave"] = str(self.emissionWavelengthBox.value())
        self.uploadSettings.loc[0, presetType + "ExposureTime"] = str(self.exposureTimeBox.value())
        self.uploadSettings.loc[0, presetType + "DflLoop"] = str(self.deflationLoopsNumberBox.value())
        self.uploadSettings.loc[0, presetType + "DMax"] = str(self.diffusionConstantMaxBox.value())
        self.uploadSettings.loc[0, presetType + "Gaps"] = str(self.gapsAllowedBox.value())
        self.uploadSettings.loc[0, presetType + "PxSize"] = str(self.pixelSize.value())
        self.uploadSettings.loc[0, presetType + "PSFScaling"] = str(self.psfScaling.value())
        self.uploadSettings.loc[0, presetType + "NA"] = str(self.detectionObjectiveNA.value())
        self.uploadSettings.loc[0, presetType + "DetectionBox"] = str(self.detectionBox.value())
        self.uploadSettings.loc[0, presetType + "MaxIter"] = str(self.maxIteration.value())
        self.uploadSettings.loc[0, presetType + "TermTol"] = str(self.terminationTolerance.value())
        self.uploadSettings.loc[0, presetType + "RadTol"] = str(self.radiusToleranceValue.value())
        self.uploadSettings.loc[0, presetType + "PosTol"] = str(self.positionTolerance.value())
        self.uploadSettings.loc[0, presetType + "MinLoc"] = str(self.minLoc.value())
        self.uploadSettings.loc[0, presetType + "MaxLoc"] = str(self.maxLoc.value())
        self.uploadSettings.loc[0, presetType + "PosTol"] = str(self.positionTolerance.value())
        self.uploadSettings.loc[0, presetType + "MinSNR"] = str(self.minSNR.value())
        self.uploadSettings.loc[0, presetType + "MaxSNRIter"] = str(self.maxSNRIter.value())
        self.uploadSettings.loc[0, presetType + "TrackStart"] = str(self.trackStart.value())
        self.uploadSettings.loc[0, presetType + "TrackEnd"] = str(self.trackEnd.value())
        self.uploadSettings.loc[0, presetType + "ExpFS"] = str(self.exponentialFactorSearch.value())
        self.uploadSettings.loc[0, presetType + "StatWin"] = str(self.statWin.value())
        self.uploadSettings.loc[0, presetType + "CompMax"] = str(self.compMax.value())
        self.uploadSettings.loc[0, presetType + "IntLaw"] = str(self.intLawWeight.value())
        self.uploadSettings.loc[0, presetType + "DifLaw"] = str(self.difLawWeight.value())
        with open('Settings.txt', 'w') as f:
            for col in self.uploadSettings:
                f.write(col + ": " + self.uploadSettings.loc[0, col] + "\n")

    def create_tabs(self):
        # Create tabs
        self.tabsPage = QScrollArea(widgetResizable = True)
        self.tabs = QTabWidget()
        self.tabs.setMinimumSize(1800, 900)
        self.tabsPage.setWidget(self.tabs)

        self.home_tab = QWidget()
        self.trajectory_tab = QTabWidget()
        self.diffusionTabs = QTabWidget()
        self.trackAngleTab = QTabWidget()
        self.trajectoryCharacteristicsTabs = QTabWidget()
        self.distributionOfTrackTab = QWidget()
        self.heatMapTab = QWidget()
        self.dwellTab = QWidget()
        self.chromatinTab = QWidget()
        self.uploadTab = QWidget()

        # Add tabs to tabs
        self.tabs.addTab(self.home_tab, "&Home")
        self.tabs.addTab(self.trajectory_tab, "&Trajectory")
        self.tabs.addTab(self.diffusionTabs, "&Diffusion Plots")
        self.tabs.addTab(self.trackAngleTab, "&Angle Plots")
        ## TODO:
        #self.tabs.addTab(self.trajectoryCharacteristicsTabs, "Tra&jectory Characteristics")
        self.tabs.addTab(self.distributionOfTrackTab, "D&istribution of Tracks")
        self.tabs.addTab(self.heatMapTab, "&Heat Map")
        self.tabs.addTab(self.dwellTab, "Dwe&ll Time")
        self.tabs.addTab(self.chromatinTab, "&Chromatin")
        self.tabs.addTab(self.uploadTab, "&Upload")

        # Create the first tab
        self.home_tab.layout = QGridLayout(self)
        self.home_tab.setLayout(self.home_tab.layout)

        welcomeText = QLabel()
        welcomeText.setText("Welcome to the Transcription Factor Analysis dashboard!")
        welcomeText.setFont(QFont("Arial", 20))
        aboutLabel = QLabel()
        aboutLabel.setText("About")
        aboutLabel.setFont(QFont("Arial", 16))
        aboutText = QLabel()
        aboutText.setText("This app is designed for the spatial and temporal analysis of fluorescently tagged transcription factors within cell nuclei.")
        aboutText.setFont(QFont("Arial", 12))
        aboutText.setWordWrap(True)
        gsLabel = QLabel()
        gsLabel.setText("Getting started")
        gsLabel.setFont(QFont("Arial", 16))
        gsText = QLabel()
        gsText.setText("Please head to the app's GitHub repository and download the PDF documentation to get started and analyse your data.")
        gsText.setFont(QFont("Arial", 12))
        gsText.setWordWrap(True)
        gicLabel = QLabel()
        gicLabel.setText("Genome Imaging Centre")
        gicLabel.setFont(QFont("Arial", 16))
        gicText = QLabel()
        gicText.setText("This dashboard was built by the Genome Imaging Centre, a Core Research Facility of the Centenary Institute.")
        gicText.setFont(QFont("Arial", 12))
        gicText.setWordWrap(True)
        citaLabel = QLabel()
        citaLabel.setText("Citation")
        citaLabel.setFont(QFont("Arial", 16))
        citaText = QLabel()
        citaText.setText("Previously published algorithms, analysis, and scripts that are utilized in the dashboard can be found below: <br>\n" +
                          "<br> \n" +
                          "<u>Localization and Tracking:</u> <br>\n" +
                          "D. M. McSwiggen et al. (2019) Evidence for DNA-mediated nuclear compartmentalization distinct from phase separation. eLife. 8:e47098. <br>\n" +
                          "A. Sergé et al. (2008) Dynamic multiple-target tracing to probe spatiotemporal cartography of cell membranes. Nature methods, 5(8):687. <br>\n" +
                          "<br>\n" +
                          "<u>MSD-Based Diffusion Plot:</u> <br>\n" +
                          "J. Chen et al. (2014) Single-molecule dynamics of enhanceosome assembly in embryonic stem cells. Cell. 156(6):1274 - 1285. <br>\n" +
                          "<br>\n" + 
                          "<u>Jump Distance Plot:</u> <br>\n" +
                          "D. Mazza et al. (2013) Monitoring dynamic binding of chromatin proteins in vivo by single-molecule tracking. Methods Mol Biol. 1042:117-37. <br>\n" +
                          "<br>\n" +
                          "<u>Angle Plots:</u> <br>\n" +
                          "I. Izeddin et. al. (2014), Single-molecule tracking in live cells reveals distinct target-search strategies of transcription factors in the nucleus. eLife. 3:e02230. <br>\n" +
                          "<br>\n" +
                          "<u>Heat Map:</u> <br>\n" +
                          "J. O. Andrews et al. (2018) qSR: a quantitative super-resolution analysis tool reveals the cell-cycle dependent organization of RNA Polymerase I in live human cells. Sci Rep. 7424 (2018). +<br>\n" +
                          "<br>\n" +
                          "<u>Dwell Time:</u> <br>\n" +
                          "A.J. McCann et al. (2021) A dominant-negative SOX18 mutant disrupts multiple regulatory layers essential to transcription factor activity. Nucleic Acids Res. 49(19):10931-10955." +
                          "Developed by Zhe Liu in Janelia Research Campus")
        # citaText.setTextFormat(Qt.RichText)
        citaText.setFont(QFont("Arial", 12))
        citaText.setWordWrap(True)

        self.home_tab.layout.addWidget(welcomeText)
        self.home_tab.layout.addWidget(aboutLabel)
        self.home_tab.layout.addWidget(aboutText)
        self.home_tab.layout.addWidget(gsLabel)
        self.home_tab.layout.addWidget(gsText)
        self.home_tab.layout.addWidget(gicLabel)
        self.home_tab.layout.addWidget(gicText)
        self.home_tab.layout.addWidget(citaLabel)
        self.home_tab.layout.addWidget(citaText)

        # Trajectory tab
        self.trajectoryPlotTab = QWidget()
        self.trajectoryDataTab = QWidget()

        self.trajectory_tab.addTab(self.trajectoryPlotTab, "&Plot")
        self.trajectory_tab.addTab(self.trajectoryDataTab, "Detai&ls")

        # Trajectory plot sub tab
        self.trajectoryPlotTab.layout = QGridLayout(self)
        self.trajectoryPlotTab.setLayout(self.trajectoryPlotTab.layout)

        self.trajectory_browser = QtWebEngineWidgets.QWebEngineView(self)

        trajNumber = QLabel()
        trajNumber.setText("Number of Trajectory:")
        self.trajNumberBox = QSpinBox()
        self.trajNumberBox.setMaximum(99999)
        self.trajNumberBox.setValue(100)
        self.trajNumberBox.setMaximumWidth(200)
        jumpNumberDraw = QLabel()
        jumpNumberDraw.setText("Jumps To Draw:")
        self.jumpNumberDrawBox = QSpinBox()
        self.jumpNumberDrawBox.setValue(5)
        minTrajLength = QLabel()
        minTrajLength.setText("Minimum Trajectory Length Considered:")
        self.minTrajLength = QSpinBox()
        self.minTrajLength.setValue(5)

        trajectoryGrouping = QLabel()
        trajectoryGrouping.setText("Group Trajectory By:")
        self.trajTabTrajGroupButton = QRadioButton("Trajectory")
        self.trajTabSpeedGroupButton = QRadioButton("Speed")
        self.trajTabTrajGroupButton.setChecked(True)

        self.trajectoryPlotTab.layout.addWidget(trajNumber, 0, 0, 1, 1)
        self.trajectoryPlotTab.layout.addWidget(self.trajNumberBox, 1, 0, 1, 1)
        self.trajectoryPlotTab.layout.addWidget(jumpNumberDraw, 2, 0, 1, 1)
        self.trajectoryPlotTab.layout.addWidget(self.jumpNumberDrawBox, 3, 0, 1, 1)
        self.trajectoryPlotTab.layout.addWidget(minTrajLength, 4, 0, 1, 1)
        self.trajectoryPlotTab.layout.addWidget(self.minTrajLength, 5, 0, 1, 1)
        # self.trajectory_tab.layout.addWidget(trajectoryGrouping, 6, 0)
        # self.trajectory_tab.layout.addWidget(self.trajTabTrajGroupButton, 7, 0)
        # self.trajectory_tab.layout.addWidget(self.trajTabSpeedGroupButton, 8, 0)
        self.trajectoryPlotTab.layout.addWidget(self.trajectory_browser, 0, 1, 10, 3)

        self.trajectoryPlotTab.layout.setColumnStretch(0, 5)
        self.trajectoryPlotTab.layout.setColumnStretch(1, 1)
        self.trajectoryPlotTab.layout.setColumnStretch(2, 2)

        # Trajectory data tab
        self.trajectoryDataTab.layout = QGridLayout(self)
        self.trajectoryDataTab.setLayout(self.trajectoryDataTab.layout)

        self.trajectoryNumberBox_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.trajectoryDensityBox_browser = QtWebEngineWidgets.QWebEngineView(self)

        self.trajectoryDataTab.layout.addWidget(self.trajectoryNumberBox_browser, 0, 0, 1, 1)
        self.trajectoryDataTab.layout.addWidget(self.trajectoryDensityBox_browser, 0, 1, 1, 1)

        # Diffusion tab
        self.diffusionTrajectoryTab = QWidget()
        self.diffusionTrackTab = QWidget()

        self.diffusionTabs.addTab(self.diffusionTrajectoryTab, "&Trajectory")
        self.diffusionTabs.addTab(self.diffusionTrackTab, "Tra&ck")

        # Trajectory diffusion sub tab
        self.diffusionTrajectoryTab.layout = QGridLayout(self)
        self.diffusionTrajectoryTab.setLayout(self.diffusionTrajectoryTab.layout)

        self.diffusionTrajectoryTabLeftSideBar = QVBoxLayout(self.diffusionTrajectoryTab)
        self.diffusionTrajectoryTabPlots = QGridLayout(self.diffusionTrajectoryTab)

        self.diffusionTrajectoryTab.layout.addLayout(self.diffusionTrajectoryTabLeftSideBar, 0, 0, 1, 1)
        self.diffusionTrajectoryTab.layout.addLayout(self.diffusionTrajectoryTabPlots, 0, 1, 1, 5)

        diffusionBinSize = QLabel()
        diffusionBinSize.setText("Number of Bins:")
        self.diffusionBinSize = QSpinBox()
        self.diffusionBinSize.setValue(20)

        diffusionLowerLimit = QLabel()
        diffusionLowerLimit.setText("Lower Limit For Plot:")
        self.diffusionLowerLimit = QSpinBox()
        self.diffusionLowerLimit.setMinimum(-10)
        self.diffusionLowerLimit.setValue(-4)
        diffusionUpperLimit = QLabel()
        diffusionUpperLimit.setText("Upper Limit For Plot:")
        self.diffusionUpperLimit = QSpinBox()
        self.diffusionUpperLimit.setValue(6) #TODO: change back to 2

        boundaryValue = QLabel()
        boundaryValue.setText("Boundary Computation:")
        self.boundaryComputation = QComboBox()
        self.boundaryComputation.addItems(["Formula", "Raw Value"])
        self.boundaryRawValue = QDoubleSpinBox()
        self.boundaryRawValue.setMinimum(-99.99)
        self.boundaryRawValue.setValue(-0.5)

        diffusionErrorBar = QLabel()
        diffusionErrorBar.setText("Errorbar Type:")
        self.diffusionErrorVariation = QRadioButton("Data Variation")
        self.diffusionErrorSTD = QRadioButton("Standard Deviation")
        self.diffusionErrorSEM = QRadioButton("Standard Error of Mean")
        self.diffusionErrorSTD.setChecked(True)

        self.fractionExportButton = QPushButton("Boundary Export")

        self.diffusion_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.diffusion_browser.setMinimumWidth(900)
        self.diffusionFraction_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.diffusionFraction_browser.setMinimumHeight(1200)

        self.diffusionPieRegion = QScrollArea(widgetResizable = True)
        self.diffusionPieRegion.setWidget(self.diffusionFraction_browser)
        self.diffusionPieRegion.setMaximumWidth(600)

        self.diffusionTrajectoryTabLeftSideBar.addWidget(diffusionBinSize)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(self.diffusionBinSize)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(diffusionLowerLimit)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(self.diffusionLowerLimit)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(diffusionUpperLimit)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(self.diffusionUpperLimit)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(boundaryValue)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(self.boundaryComputation)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(self.boundaryRawValue)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(diffusionErrorBar)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(self.diffusionErrorVariation)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(self.diffusionErrorSTD)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(self.diffusionErrorSEM)
        self.diffusionTrajectoryTabLeftSideBar.addWidget(self.fractionExportButton)
        self.diffusionTrajectoryTabPlots.addWidget(self.diffusion_browser, 0, 0, 3, 3)
        self.diffusionTrajectoryTabPlots.addWidget(self.diffusionPieRegion, 0, 4)

        # Track diffusion sub tab
        self.diffusionTrackTab.layout = QGridLayout(self)
        self.diffusionTrackTab.setLayout(self.diffusionTrackTab.layout)
        self.jumpDistanceToCSV = QPushButton("Export Data")

        twoParLabel = QLabel()
        twoParLabel.setText("2 Parameters Fit:")
        twoParLabel.setFont(QFont("Arial", 16))
        self.diffusionTrack2Par_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.diffusionTrack2ParBox_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.diffusionTrack2ParBox_browser.setMinimumSize(900, 200)
        self.twoParTable = QTableWidget(self)

        threeParLabel = QLabel()
        threeParLabel.setText("3 Parameters Fit:")
        threeParLabel.setFont(QFont("Arial", 16))
        self.diffusionTrack3Par_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.diffusionTrack3ParBox_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.diffusionTrack3ParBox_browser.setMinimumSize(900, 200)
        self.threeParTable = QTableWidget(self)

        jumpDistanceLabel = QLabel()
        jumpDistanceLabel.setText("Jump Distance To Plot:")
        self.jumpDistanceConsidered = QDoubleSpinBox()
        self.jumpDistanceConsidered.setValue(0.5)

        self.diffusionTrackTab.layout.addWidget(twoParLabel, 0, 0)
        self.diffusionTrackTab.layout.addWidget(self.jumpDistanceToCSV, 0, 2)
        self.diffusionTrackTab.layout.addWidget(self.diffusionTrack2Par_browser, 1, 0, 14, 2)
        self.diffusionTrackTab.layout.addWidget(self.diffusionTrack2ParBox_browser, 1, 2, 10, 4)
        self.diffusionTrackTab.layout.addWidget(self.twoParTable, 11, 2, 4, 4)

        self.diffusionTrackTab.layout.addWidget(threeParLabel, 15, 0)
        self.diffusionTrackTab.layout.addWidget(self.diffusionTrack3Par_browser, 16, 0, 14, 2)
        self.diffusionTrackTab.layout.addWidget(self.diffusionTrack3ParBox_browser, 16, 2, 10, 4)
        self.diffusionTrackTab.layout.addWidget(self.threeParTable, 26, 2, 4, 4)

        self.diffusionTrackTab.layout.addWidget(jumpDistanceLabel, 30, 2, 1, 2)
        self.diffusionTrackTab.layout.addWidget(self.jumpDistanceConsidered, 30, 4, 1, 2)

        # Angle tab
        self.trackAngleTab.layout = QGridLayout(self)
        self.trackAngleTab.setLayout(self.trackAngleTab.layout)

        self.trackAngleMut_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.trackAngleMut_browser.setMinimumSize(400, 400)
        self.trackAngleState_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.trackAngleState_browser.setMinimumSize(400, 400)
        self.trackAngleBound_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.trackAngleBound_browser.setMinimumSize(400, 400)
        self.trackAngleDiffu_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.trackAngleDiffu_browser.setMinimumSize(400, 400)
        self.trackAngleBox_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.trackAngleBox_browser.setMinimumSize(400, 400)

        self.angleGroupBox = QGroupBox("Angle Parameters")

        angleSelectionText = QLabel()
        angleSelectionText.setText("Angles of Interest:")
        self.angleSelection = CheckableComboBox()
        angleRatioText = QLabel()
        angleRatioText.setText("Ratio:")
        self.angleRatio = QDoubleSpinBox()
        self.angleRatio.setMaximum(100)
        self.angleRatio.setMinimum(0)
        self.angleRatio.setValue(50)

        angleGroupBoxLayout = QVBoxLayout()
        angleGroupBoxLayout.addWidget(angleSelectionText)
        angleGroupBoxLayout.addWidget(self.angleSelection)
        angleGroupBoxLayout.addWidget(angleRatioText)
        angleGroupBoxLayout.addWidget(self.angleRatio)
        self.angleGroupBox.setLayout(angleGroupBoxLayout)  

        boundaryValueText = QLabel()
        boundaryValueText.setText("Boundary Computation:")
        self.boundaryValueAngle = QDoubleSpinBox()
        self.boundaryValueAngle.setMinimum(-99.99)
        self.boundaryValueAngle.setValue(-0.5)
        self.angleToCSV = QPushButton("Export Data")

        self.trackAngleTab.layout.addWidget(self.trackAngleMut_browser, 0, 0, 1, 1)
        self.trackAngleTab.layout.addWidget(self.trackAngleState_browser, 1, 0, 1, 1)
        self.trackAngleTab.layout.addWidget(self.trackAngleBound_browser, 0, 1, 1, 1)
        self.trackAngleTab.layout.addWidget(self.trackAngleDiffu_browser, 1, 1, 1, 1)
        self.trackAngleTab.layout.addWidget(self.trackAngleBox_browser, 0, 2, 1, 1)
        self.trackAngleTab.layout.addWidget(self.angleGroupBox, 1, 2, 1, 1)
        self.trackAngleTab.layout.addWidget(boundaryValueText, 2, 0, 1, 1)
        self.trackAngleTab.layout.addWidget(self.boundaryValueAngle, 2, 1, 1, 1)
        self.trackAngleTab.layout.addWidget(self.angleToCSV, 2, 2, 1, 1)

        # Trajectory characteristics tab
        self.trajCharLifetimeTab = QWidget()
        self.trajCharAveDistanceTab = QWidget()
        self.trajCharTotDistanceTab = QWidget()

        self.trajectoryCharacteristicsTabs.addTab(self.trajCharLifetimeTab, "&Lifetime")
        self.trajectoryCharacteristicsTabs.addTab(self.trajCharAveDistanceTab, "A&verage Distance")
        self.trajectoryCharacteristicsTabs.addTab(self.trajCharTotDistanceTab, "&Total Distance")

        # Lifetime trajectory characterteristics sub tab
        self.trajCharLifetimeTab.layout = QGridLayout(self)
        self.trajCharLifetimeTab.setLayout(self.trajCharLifetimeTab.layout)

        # Average distance trajectory characterteristics sub tab
        self.trajCharAveDistanceTab.layout = QGridLayout(self)
        self.trajCharAveDistanceTab.setLayout(self.trajCharAveDistanceTab.layout)

        # Total distance trajectory characterteristics sub tab
        self.trajCharTotDistanceTab.layout = QGridLayout(self)
        self.trajCharTotDistanceTab.setLayout(self.trajCharTotDistanceTab.layout)

        # Distribution of tracks tab
        self.distributionOfTrackTab.layout = QGridLayout(self)
        self.distributionOfTrackTab.setLayout(self.distributionOfTrackTab.layout)

        self.dOTBoxPlotBrowser = QtWebEngineWidgets.QWebEngineView(self)
        dOTAngleAC = QLabel()
        dOTAngleAC.setText("Maximum Allowed Asymmetry Ratio:")
        self.dOTAngleMaxAC = QDoubleSpinBox()
        self.dOTAngleMaxAC.setMinimum(-np.inf)
        self.dOTAngleMaxAC.setMaximum(np.inf)
        self.dOTAngleMaxAC.setValue(np.inf)
        dOTTrajChoice = QLabel()
        dOTTrajChoice.setText("Trajectory Length:")
        self.dOTTrajChoiceMax = QRadioButton("Max")
        self.dOTTrajChoiceMean = QRadioButton("Mean")
        self.dOTTrajChoiceMedian = QRadioButton("Median")
        self.dOTTrajChoiceMean.setChecked(True)
        self.dOTDataPointChoice = QPushButton("Show Data Points")
        self.dOTDataPointChoice.setCheckable(True)
        self.dOTDataPointChoice.setChecked(True)

        self.dOTMapBrowser = QtWebEngineWidgets.QWebEngineView(self)

        self.dOTTable = QTableWidget(self)

        dOTMinTrajLength = QLabel()
        dOTMinTrajLength.setText("Minimum Seconds of Trajectory Length:")
        self.dOTMinTrajLength = QDoubleSpinBox()
        self.dOTMinTrajLength.setMinimum(0.00)
        self.dOTMinTrajLength.setMaximum(999.99)
        self.dOTMinTrajLength.setValue(0)
        dOTRegionArea = QLabel()
        dOTRegionArea.setText("Regions Area:")
        self.dOTRegionArea = QLineEdit()
        self.dOTRegionArea.setText("0.4, 0.8")
        self.dOTButton = QPushButton("Update")

        self.distributionOfTrackTab.layout.addWidget(self.dOTMapBrowser, 0, 0, 6, 1)
        self.distributionOfTrackTab.layout.addWidget(self.dOTBoxPlotBrowser, 0, 1, 1, 2)
        self.distributionOfTrackTab.layout.addWidget(self.dOTTable, 1, 1, 7, 1) #5, 1)
        self.distributionOfTrackTab.layout.addWidget(dOTAngleAC, 1, 2)
        self.distributionOfTrackTab.layout.addWidget(self.dOTAngleMaxAC, 2, 2)
        self.distributionOfTrackTab.layout.addWidget(dOTTrajChoice, 3, 2) #1, 2)
        self.distributionOfTrackTab.layout.addWidget(self.dOTTrajChoiceMax, 4, 2) #2, 2)
        self.distributionOfTrackTab.layout.addWidget(self.dOTTrajChoiceMean, 5, 2) #3, 2)
        self.distributionOfTrackTab.layout.addWidget(self.dOTTrajChoiceMedian, 6, 2) #5, 2)
        self.distributionOfTrackTab.layout.addWidget(self.dOTDataPointChoice, 7, 2)#5, 2)
        self.distributionOfTrackTab.layout.addWidget(dOTMinTrajLength, 8, 0) #6, 0)
        self.distributionOfTrackTab.layout.addWidget(self.dOTMinTrajLength, 9, 0) #7, 0)
        self.distributionOfTrackTab.layout.addWidget(dOTRegionArea, 8, 1) #6, 1)
        self.distributionOfTrackTab.layout.addWidget(self.dOTRegionArea, 9, 1) #7, 1)
        self.distributionOfTrackTab.layout.addWidget(self.dOTButton, 8, 2, 2, 1) #6, 2, 2, 1)
        self.distributionOfTrackTab.layout.setRowStretch(0, 5)
        self.distributionOfTrackTab.layout.setColumnStretch(0, 3)
        self.distributionOfTrackTab.layout.setColumnStretch(1, 3)
        self.distributionOfTrackTab.layout.setColumnStretch(2, 1)

        # Heat map tab
        self.heatMapTab.layout = QGridLayout(self)
        self.heatMapTab.setLayout(self.heatMapTab.layout)

        self.heatMapPlot = QtWebEngineWidgets.QWebEngineView(self)
        self.heatMapCummulativeTrajs = QtWebEngineWidgets.QWebEngineView(self)
        self.heatMapCummulativeTrajs.setMinimumWidth(600)
        self.heatMapLiveTrajs = QtWebEngineWidgets.QWebEngineView(self)
        self.heatMapBurstLifetime = QtWebEngineWidgets.QWebEngineView(self)
        self.heatMapRipley = QtWebEngineWidgets.QWebEngineView(self)

        self.heatMapSlider = QSlider(Qt.Orientation.Horizontal)
        self.heatMapSlider.setMaximum(100)
        self.heatMapSlider.setMinimum(0)
        self.heatMapSlider.setSingleStep(1)
        self.heatMapSlider.setValue(0)
        self.heatMapSlider.setDisabled(True)

        self.heatMapTab.layout.addWidget(self.heatMapPlot, 0, 0, 2, 1)
        self.heatMapTab.layout.addWidget(self.heatMapSlider, 2, 0)
        self.heatMapTab.layout.addWidget(self.heatMapCummulativeTrajs, 0, 1)
        self.heatMapTab.layout.addWidget(self.heatMapLiveTrajs, 1, 1, 2, 1)
        self.heatMapTab.layout.addWidget(self.heatMapBurstLifetime, 3, 0)
        self.heatMapTab.layout.addWidget(self.heatMapRipley, 3, 1)

        # Dwell time tab
        self.dwellTab.layout = QGridLayout(self)
        self.dwellTab.setLayout(self.dwellTab.layout)

        self.dwellBox_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.dwellBox_browser.setMinimumWidth(900)
        self.dwellDensity_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.dwellPie_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.dwellPie_browser.setMinimumHeight(1200)

        self.dwellPieRegion = QScrollArea(widgetResizable = True)
        self.dwellPieRegion.setWidget(self.dwellPie_browser)
        self.dwellPieRegion.setMaximumWidth(600)

        self.dwellTimeExportButton = QPushButton("Export Data", default = False, autoDefault = False)

        self.dwellTab.layout.addWidget(self.dwellBox_browser, 0, 0, 1, 1)
        self.dwellTab.layout.addWidget(self.dwellDensity_browser, 1, 0, 1, 1)
        self.dwellTab.layout.addWidget(self.dwellPieRegion, 0, 1, 2, 1)
        self.dwellTab.layout.addWidget(self.dwellTimeExportButton, 2, 0, 1, 2)

        # Chromatin tab
        self.chromatinTab.layout = QGridLayout(self)
        self.chromatinTab.setLayout(self.chromatinTab.layout)

        self.chromatinAC_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.chromatinAC_browser.setMinimumSize(400, 400)
        self.chromatinTraj_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.chromatinTraj_browser.setMinimumSize(400, 400)
        self.chromatinFast_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.chromatinFast_browser.setMinimumSize(400, 400)
        self.chromatinSlow_browser = QtWebEngineWidgets.QWebEngineView(self)
        self.chromatinSlow_browser.setMinimumSize(400, 400)

        self.diffusionBoundary = QDoubleSpinBox()
        self.diffusionBoundary.setMinimum(-99.99)
        self.diffusionBoundary.setMaximum(99.99)
        self.diffusionBoundary.setValue(0)
        self.diffusionBoundary.setMaximumWidth(200)
        yAxisText = QLabel()
        yAxisText.setText("")
        self.yAxisSelection = QComboBox()

        self.chromatinTab.layout.addWidget(self.diffusionBoundary, 1, 0, 1, 1)
        self.chromatinTab.layout.addWidget(yAxisText, 2, 0, 1, 1)
        self.chromatinTab.layout.addWidget(self.yAxisSelection, 3, 0, 1, 1)
        self.chromatinTab.layout.addWidget(self.chromatinAC_browser, 0, 1, 1, 1)
        self.chromatinTab.layout.addWidget(self.chromatinTraj_browser, 1, 1, 1, 1)
        self.chromatinTab.layout.addWidget(self.chromatinFast_browser, 0, 2, 1, 1)
        self.chromatinTab.layout.addWidget(self.chromatinSlow_browser, 1, 2, 1, 1)

        # self.chromatinTab.layout.setColumnStretch(0, 5)
        # self.chromatinTab.layout.setColumnStretch(1, 1)

        # Upload tab
        self.uploadTab.layout = QGridLayout(self)
        self.uploadTab.setLayout(self.uploadTab.layout)

        acquisitionRate = QLabel()
        acquisitionRate.setText("Acquisition Rate:")
        acquisitionRate.setToolTip("Select whether the analysis will be carried out using a pre-defined number of tracks from the trajectory or a percentage of the total trajectory.")
        self.acquisitionRateFast = QRadioButton("Fast")
        self.acquisitionRateSlow = QRadioButton("Slow")
        self.acquisitionRateFast.setChecked(True)

        parallelization = QLabel()
        parallelization.setText("Make Use of Multi-Core/Parallelization:")
        parallelization.setToolTip("Make use of multi-cores architecture, needs to ensure you have the MATLAB multicore processing toolbox.")
        self.parallelization = QPushButton("Yes")
        self.parallelization.setCheckable(True)
        self.parallelization.setChecked(True)

        parallelizationCores = QLabel()
        parallelizationCores.setText("Number of Cores to Use:")
        parallelizationCores.setToolTip("If parallelization is on, define the number of cores (not thread) to use.")
        self.parallelizationCores = QSpinBox()
        self.parallelizationCores.setValue(16)
        # self.parallelization.clicked.connect(parallelizationCores.setDisabled)
        # self.parallelization.clicked.connect(self.parallelizationCores.setDisabled)

        bleachRate = QLabel()
        bleachRate.setText("Bleach Rate:")
        self.bleachRate = QDoubleSpinBox()
        self.bleachRate.setMinimum(0.00)
        self.bleachRate.setMaximum(100.00)
        self.bleachRate.setValue(0.00)

        self.createParametersGroupBox()
        self.createImagingGroupBox()
        self.createLocalizationGroupBox()
        self.createTrackingGroupBox()

        self.uploadFileButton = QPushButton("Upload &Files")
        self.uploadFileButton.setDefault(True)
        self.uploadPostFileButton = QPushButton("Upload Post-Processe&d Files")
        self.uploadPostFileButton.setDefault(True)

        self.uploadTab.layout.addWidget(acquisitionRate, 0, 0)
        self.uploadTab.layout.addWidget(self.acquisitionRateFast, 1, 0)
        self.uploadTab.layout.addWidget(self.acquisitionRateSlow, 2, 0)
        self.uploadTab.layout.addWidget(parallelization, 0, 1)
        self.uploadTab.layout.addWidget(self.parallelization, 1, 1)
        self.uploadTab.layout.addWidget(parallelizationCores, 0, 2)
        self.uploadTab.layout.addWidget(self.parallelizationCores, 1, 2)
        self.uploadTab.layout.addWidget(bleachRate, 2, 1)
        self.uploadTab.layout.addWidget(self.bleachRate, 2, 2)
        self.uploadTab.layout.addWidget(self.parametersGroupBox, 3, 0, 2, 1)
        self.uploadTab.layout.addWidget(self.localizationGroupBox, 3, 1, 2, 1)
        self.uploadTab.layout.addWidget(self.trackingGroupBox, 3, 2, 1, 1)
        self.uploadTab.layout.addWidget(self.imagingGroupBox, 4, 2, 1, 1)

        self.uploadTab.layout.addWidget(self.uploadFileButton, 5, 0, 1, 2)
        self.uploadTab.layout.addWidget(self.uploadPostFileButton, 5, 2, 1, 1)

    def createParametersGroupBox(self):
        self.parametersGroupBox = QGroupBox("Generic Parameters")
        self.parametersGroupBox.layout = QVBoxLayout()

        analysisType = QLabel()
        analysisType.setText("Analysis Type:")
        analysisType.setToolTip("Select whether the analysis will be carried out using a pre-defined number of tracks from the trajectory or a percentage of the total trajectory.")
        self.analysisTypePercentage = QRadioButton("Percentage")
        self.analysisTypeNumber = QRadioButton("Number")
        self.analysisTypeNumber.setChecked(True)

        clipFactor = QLabel()
        clipFactor.setText("Clip Factor:")
        clipFactor.setToolTip("Decide the number of tracks in a trajectory to be used for the 'number' analysis. Otherwise, choose the percentage of tracks to be used, with 1 being all of the tracks in a trajectory.")
        self.clipFactorBox = QSpinBox()
        self.clipFactorBox.setMaximum(100)
        self.clipFactorBox.setValue(4)

        trajectoryLength = QLabel()
        trajectoryLength.setText("Trajectory Length:")
        trajectoryLength.setToolTip("Length of trajectory to keep (trajectory appear with less than this number of frame will be discarded).")
        self.trajectoryLengthBox = QSpinBox()
        self.trajectoryLengthBox.setValue(7)

        minTrajectoryNumber = QLabel()
        minTrajectoryNumber.setText("Minimum Number of Trajectory:")
        minTrajectoryNumber.setToolTip("Minimum trajectories in a file to be accepted into the analysis.")
        self.minTrajectoryNumberBox = QSpinBox()
        self.minTrajectoryNumberBox.setMaximum(9999)
        self.minTrajectoryNumberBox.setValue(1000)

        tolerance = QLabel()
        tolerance.setText("Tolerance:")
        tolerance.setToolTip("Number of decimals to be kept during analysis.")
        self.toleranceBox = QSpinBox()
        self.toleranceBox.setValue(12)

        localizationError = QLabel()
        localizationError.setText("Localization Error:")
        localizationError.setToolTip("Localization Error: -6 <- 10^-6.")
        self.localizationErrorBox = QDoubleSpinBox()
        self.localizationErrorBox.setMinimum(-99.99)
        self.localizationErrorBox.setValue(-6.5)

        emissionWavelength = QLabel()
        emissionWavelength.setText("Emission Wavelength:")
        emissionWavelength.setToolTip("Wavelength in nm consider emission max and filter cutoff.")
        self.emissionWavelengthBox = QSpinBox()
        self.emissionWavelengthBox.setMaximum(9999)
        self.emissionWavelengthBox.setValue(580)

        exposureTime = QLabel()
        exposureTime.setText("Exposure Time:")
        exposureTime.setToolTip("Exposure time in milliseconds.")
        self.exposureTimeBox = QDoubleSpinBox()
        self.exposureTimeBox.setMaximum(1000)
        self.exposureTimeBox.setValue(20)

        deflationLoopsNumber = QLabel()
        deflationLoopsNumber.setText("Number of Deflation Loops:")
        deflationLoopsNumber.setToolTip("Generally keep this to 0 if you need deflation loops, you are imaging at too high a density.")
        self.deflationLoopsNumberBox = QSpinBox()
        self.deflationLoopsNumberBox.setValue(0)

        diffusionConstantMax = QLabel()
        diffusionConstantMax.setText("Maximum Expected Diffusion Constant::")
        diffusionConstantMax.setToolTip("The maximal expected diffusion constant caused by Brownian motion in um^2/s.")
        self.diffusionConstantMaxBox = QDoubleSpinBox()
        self.diffusionConstantMaxBox.setMaximum(99)
        self.diffusionConstantMaxBox.setMinimum(0)
        self.diffusionConstantMaxBox.setValue(3)

        gapsAllowed = QLabel()
        gapsAllowed.setText("Number of Gaps Allowed:")
        gapsAllowed.setToolTip("The number of gaps allowed in trajectories (1 being trajectories must exist in both frame n and frame n+1).")
        self.gapsAllowedBox = QSpinBox()
        self.gapsAllowedBox.setValue(1)

        self.parametersGroupBox.layout.addWidget(analysisType)
        self.parametersGroupBox.layout.addWidget(self.analysisTypePercentage)
        self.parametersGroupBox.layout.addWidget(self.analysisTypeNumber)
        self.parametersGroupBox.layout.addWidget(clipFactor)
        self.parametersGroupBox.layout.addWidget(self.clipFactorBox)
        self.parametersGroupBox.layout.addWidget(trajectoryLength)
        self.parametersGroupBox.layout.addWidget(self.trajectoryLengthBox)
        self.parametersGroupBox.layout.addWidget(minTrajectoryNumber)
        self.parametersGroupBox.layout.addWidget(self.minTrajectoryNumberBox)
        self.parametersGroupBox.layout.addWidget(tolerance)
        self.parametersGroupBox.layout.addWidget(self.toleranceBox)
        self.parametersGroupBox.layout.addWidget(localizationError)
        self.parametersGroupBox.layout.addWidget(self.localizationErrorBox)
        self.parametersGroupBox.layout.addWidget(emissionWavelength)
        self.parametersGroupBox.layout.addWidget(self.emissionWavelengthBox)
        self.parametersGroupBox.layout.addWidget(exposureTime)
        self.parametersGroupBox.layout.addWidget(self.exposureTimeBox)
        self.parametersGroupBox.layout.addWidget(deflationLoopsNumber)
        self.parametersGroupBox.layout.addWidget(self.deflationLoopsNumberBox)
        self.parametersGroupBox.layout.addWidget(diffusionConstantMax)
        self.parametersGroupBox.layout.addWidget(self.diffusionConstantMaxBox)
        self.parametersGroupBox.layout.addWidget(gapsAllowed)
        self.parametersGroupBox.layout.addWidget(self.gapsAllowedBox)
        self.parametersGroupBox.setLayout(self.parametersGroupBox.layout)

    def createImagingGroupBox(self):
        self.imagingGroupBox = QGroupBox("Imaging Parameters")
        self.imagingGroupBox.layout = QVBoxLayout()
        
        pixelSize = QLabel()
        pixelSize.setText("Pixel Size:")
        pixelSize.setToolTip("um per pixel.")
        self.pixelSize = QDoubleSpinBox()
        self.pixelSize.setDecimals(3)
        self.pixelSize.setValue(0.130)

        psfScaling = QLabel()
        psfScaling.setText("PSF Scaling:")
        psfScaling.setToolTip("Point spread function value of the microscope.")
        self.psfScaling = QDoubleSpinBox()
        self.psfScaling.setDecimals(3)
        self.psfScaling.setValue(1.350)

        detectionObjectiveNA = QLabel()
        detectionObjectiveNA.setText("NA of Detection Objective:")
        detectionObjectiveNA.setToolTip("NA of detection objective (the microscope lens).")
        self.detectionObjectiveNA = QDoubleSpinBox()
        self.detectionObjectiveNA.setValue(1.49)

        self.imagingGroupBox.layout.addWidget(pixelSize)
        self.imagingGroupBox.layout.addWidget(self.pixelSize)
        self.imagingGroupBox.layout.addWidget(psfScaling)
        self.imagingGroupBox.layout.addWidget(self.psfScaling)
        self.imagingGroupBox.layout.addWidget(detectionObjectiveNA)
        self.imagingGroupBox.layout.addWidget(self.detectionObjectiveNA)
        self.imagingGroupBox.setLayout(self.imagingGroupBox.layout)

    def createLocalizationGroupBox(self):
        self.localizationGroupBox = QGroupBox("Localization Parameters")
        self.localizationGroupBox.layout = QVBoxLayout()

        detectionBox = QLabel()
        detectionBox.setText("Detection Box:")
        detectionBox.setToolTip("Spatial sliding window width used for particle detection (in pixels).")
        self.detectionBox = QSpinBox()
        self.detectionBox.setValue(9)

        minIntensity = QLabel()
        minIntensity.setText("Minimum Intensity:")
        minIntensity.setToolTip("Minimum intensity to be classified as a point.")
        self.minIntensity = QSpinBox()
        self.minIntensity.setMaximum(99999)

        maxIteration = QLabel()
        maxIteration.setText("Maximum Number of Iterations:")
        maxIteration.setToolTip("The maximum number of iteration allowed during localization optimization.")
        self.maxIteration = QSpinBox()
        self.maxIteration.setValue(50)

        terminationTolerance = QLabel()
        terminationTolerance.setText("Termination Tolerance:")
        terminationTolerance.setToolTip("The termination tolerance (the value is 10 to the power of the input value). If the variation of x and y coordinates is lesser than this, the iteration will stop.")
        self.terminationTolerance = QSpinBox()
        self.terminationTolerance.setMinimum(-99)
        self.terminationTolerance.setValue(-2)

        self.radiusTolerance = QPushButton("Radius Tolerance")
        self.radiusTolerance.setCheckable(True)
        radiusTolerance = QLabel()
        radiusTolerance.setText("Radius Tolerance:")
        radiusTolerance.setToolTip("The Gaussian radius tolerance (in percentage) with respect to 'point spread function deviation' (psfStd).")
        radiusTolerance.setEnabled(False)
        self.radiusToleranceValue = QSpinBox()
        self.radiusToleranceValue.setValue(50)
        self.radiusToleranceValue.setEnabled(False)
        positionTolerance = QLabel()
        positionTolerance.setText("Position Tolerance:")
        positionTolerance.setToolTip("The tolerance for the x and y coordinates of the point detected during the localization (in pixels).")
        positionTolerance.setEnabled(False)
        self.positionTolerance = QDoubleSpinBox()
        self.positionTolerance.setValue(1.5)
        self.positionTolerance.setEnabled(False)
        self.radiusTolerance.toggled.connect(radiusTolerance.setEnabled)
        self.radiusTolerance.toggled.connect(self.radiusToleranceValue.setEnabled)
        self.radiusTolerance.toggled.connect(positionTolerance.setEnabled)
        self.radiusTolerance.toggled.connect(self.positionTolerance.setEnabled)

        self.threshLocPrec = QPushButton("Thresh Loc Prec")
        self.threshLocPrec.setCheckable(True)
        minLoc = QLabel()
        minLoc.setText("Minimum Loc:")
        minLoc.setToolTip("Minimum Loc. \nCurrently not being used.")
        minLoc.setEnabled(False)
        self.minLoc = QSpinBox()
        self.minLoc.setEnabled(False)
        maxLoc = QLabel()
        maxLoc.setText("Maximum Loc:")
        maxLoc.setToolTip("Maximum Loc, leave zero for infinity. \nCurrently not being used.")
        maxLoc.setEnabled(False)
        self.maxLoc = QSpinBox()
        self.maxLoc.setEnabled(False)
        self.threshLocPrec.toggled.connect(minLoc.setEnabled)
        self.threshLocPrec.toggled.connect(self.minLoc.setEnabled)
        self.threshLocPrec.toggled.connect(maxLoc.setEnabled)
        self.threshLocPrec.toggled.connect(self.maxLoc.setEnabled)

        self.threshSNR = QPushButton("Thresh SNR")
        self.threshSNR.setCheckable(True)
        minSNR = QLabel()
        minSNR.setText("Minimum SNR:")
        minSNR.setToolTip("Minimum SNR. \nCurrently not being used.")
        minSNR.setEnabled(False)
        self.minSNR = QSpinBox()
        self.minSNR.setEnabled(False)
        maxSNRIter = QLabel()
        maxSNRIter.setText("Max Number of Iterations for Thresh SNR:")
        maxSNRIter.setToolTip("Maximum SNR, leave zero for infinity. \nCurrently not being used.")
        maxSNRIter.setEnabled(False)
        self.maxSNRIter = QSpinBox()
        self.maxSNRIter.setEnabled(False)
        self.threshSNR.toggled.connect(minSNR.setEnabled)
        self.threshSNR.toggled.connect(self.minSNR.setEnabled)
        self.threshSNR.toggled.connect(maxSNRIter.setEnabled)
        self.threshSNR.toggled.connect(self.maxSNRIter.setEnabled)

        self.threshDensity = QPushButton("Thresh Density")
        self.threshDensity.setCheckable(True)

        self.localizationGroupBox.layout.addWidget(detectionBox)
        self.localizationGroupBox.layout.addWidget(self.detectionBox)
        self.localizationGroupBox.layout.addWidget(minIntensity)
        self.localizationGroupBox.layout.addWidget(self.minIntensity)
        self.localizationGroupBox.layout.addWidget(maxIteration)
        self.localizationGroupBox.layout.addWidget(self.maxIteration)
        self.localizationGroupBox.layout.addWidget(terminationTolerance)
        self.localizationGroupBox.layout.addWidget(self.terminationTolerance)
        self.localizationGroupBox.layout.addWidget(self.radiusTolerance)
        self.localizationGroupBox.layout.addWidget(radiusTolerance)
        self.localizationGroupBox.layout.addWidget(self.radiusToleranceValue)
        self.localizationGroupBox.layout.addWidget(positionTolerance)
        self.localizationGroupBox.layout.addWidget(self.positionTolerance)
        self.localizationGroupBox.layout.addWidget(self.threshLocPrec)
        self.localizationGroupBox.layout.addWidget(minLoc)
        self.localizationGroupBox.layout.addWidget(self.minLoc)
        self.localizationGroupBox.layout.addWidget(maxLoc)
        self.localizationGroupBox.layout.addWidget(self.maxLoc)
        self.localizationGroupBox.layout.addWidget(self.threshSNR)
        self.localizationGroupBox.layout.addWidget(minSNR)
        self.localizationGroupBox.layout.addWidget(self.minSNR)
        self.localizationGroupBox.layout.addWidget(maxSNRIter)
        self.localizationGroupBox.layout.addWidget(self.maxSNRIter)
        self.localizationGroupBox.layout.addWidget(self.threshDensity)
        self.localizationGroupBox.setLayout(self.localizationGroupBox.layout)

    def createTrackingGroupBox(self):
        self.trackingGroupBox = QGroupBox("Tracking Parameters")
        self.trackingGroupBox.layout = QVBoxLayout()

        trackStart = QLabel()
        trackStart.setText("Track Start:")
        trackStart.setToolTip("Track start. Currently not being used.")
        self.trackStart = QSpinBox()
        self.trackStart.setValue(1)

        trackEnd = QLabel()
        trackEnd.setText("Track End:")
        trackEnd.setToolTip("Track end, leave zero for infinity. Currently not being used.")
        self.trackEnd = QSpinBox()

        exponentialFactorSearch = QLabel()
        exponentialFactorSearch.setText("Search Exponential Factor:")
        exponentialFactorSearch.setToolTip("Search exploration factor, a multiplicative factor to the maximum amount a point can move.")
        self.exponentialFactorSearch = QDoubleSpinBox()
        self.exponentialFactorSearch.setValue(1.2)

        statWin = QLabel()
        statWin.setText("Stat Win:")
        statWin.setToolTip("Number of frames data to be used in computing trajectories data.")
        self.statWin = QSpinBox()
        self.statWin.setValue(10)

        compMax = QLabel()
        compMax.setText("Maximum Comp:")
        compMax.setToolTip("Maximum number of trajectories a point can belong to (during trajectories forming stage).")
        self.compMax = QSpinBox()
        self.compMax.setValue(5)

        intLawWeight = QLabel()
        intLawWeight.setText("Int Law Weight:")
        intLawWeight.setToolTip("The intensity probability law weighting, value ranges from 0 to 1.0, with 1.0 accounting for intensity staying on and 0 accounting for blinking state. \nThe reconnection procedure take into account the point's intensity, diffusion and blinking.")
        self.intLawWeight = QDoubleSpinBox()
        self.intLawWeight.setValue(0.9)

        difLawWeight = QLabel()
        difLawWeight.setText("Diff Law Weight:")
        difLawWeight.setToolTip("The diffusion probability law weighting, value ranges from 0 to 1.0, with 1.0 accounting for local diffusion (based on estimated standard deviation of diffusion based on 'statWin' number of past frames information) and 0 accounting for free diffusion. \nThe reconnection procedure take into account the point's intensity, diffusion and blinking, a value of 0.9 with emphasizes on local behaviour while allowing the possibility of a sudden increase towards free diffusion.")
        self.difLawWeight = QDoubleSpinBox()
        self.difLawWeight.setValue(0.5)

        self.trackingGroupBox.layout.addWidget(trackStart)
        self.trackingGroupBox.layout.addWidget(self.trackStart)
        self.trackingGroupBox.layout.addWidget(trackEnd)
        self.trackingGroupBox.layout.addWidget(self.trackEnd)
        self.trackingGroupBox.layout.addWidget(exponentialFactorSearch)
        self.trackingGroupBox.layout.addWidget(self.exponentialFactorSearch)
        self.trackingGroupBox.layout.addWidget(statWin)
        self.trackingGroupBox.layout.addWidget(self.statWin)
        self.trackingGroupBox.layout.addWidget(compMax)
        self.trackingGroupBox.layout.addWidget(self.compMax)
        self.trackingGroupBox.layout.addWidget(intLawWeight)
        self.trackingGroupBox.layout.addWidget(self.intLawWeight)
        self.trackingGroupBox.layout.addWidget(difLawWeight)
        self.trackingGroupBox.layout.addWidget(self.difLawWeight)
        self.trackingGroupBox.setLayout(self.trackingGroupBox.layout)

    def createDataSelectionPanel(self):
        self.dataSelectionPanel = QGroupBox("Data Selection")

        acquisitionRateSelection = QLabel()
        acquisitionRateSelection.setText("Acquisition Rate:")
        self.comboAcquisitionRate = CheckableComboBox()
        mutationSelection = QLabel()
        mutationSelection.setText("Mutation(s):")
        self.comboMutation = CheckableComboBox()
        fileSelection = QLabel()
        fileSelection.setText("File(s):")
        self.comboFileList = CheckableComboBox()
        self.unselectAllFiles = QPushButton("Unselect All Files", default = False, autoDefault = False)
        self.deleteFile = QPushButton("Delete Selected Files", default = False, autoDefault = False)

        layout = QVBoxLayout()
        layout.addWidget(acquisitionRateSelection)
        layout.addWidget(self.comboAcquisitionRate)
        layout.addWidget(mutationSelection)
        layout.addWidget(self.comboMutation)
        layout.addWidget(fileSelection)
        layout.addWidget(self.comboFileList)
        layout.addStretch(1)
        layout.addWidget(self.unselectAllFiles)
        layout.addWidget(self.deleteFile)
        self.dataSelectionPanel.setLayout(layout)    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # plotly_app = PlotlyApplication()
    dashboard = GICDashboard()
    # plotly_app.init_handler(dashboard)
    dashboard.showMaximized()
    controller = Controller(model=Model(), view=dashboard)
    sys.exit(app.exec())