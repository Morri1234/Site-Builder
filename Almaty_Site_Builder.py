# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AlmatySiteBuilder
                                 A QGIS plugin
 Builds site area required based on factors specified in a Excel file
                              -------------------
        begin                : 2016-08-12
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Abhimanyu Acharya. Space Syntax Limited
        email                : a.acharya@spacesyntax.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from Almaty_Site_Builder_dialog import AlmatySiteBuilderDialog
import os.path
from qgis.core import *
from PyQt4.QtCore import *
import processing


class AlmatySiteBuilder:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'AlmatySiteBuilder_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = AlmatySiteBuilderDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&AlmatySiteBuilder')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'AlmatySiteBuilder')
        self.toolbar.setObjectName(u'AlmatySiteBuilder')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('AlmatySiteBuilder', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/AlmatySiteBuilder/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Almaty Site Builder'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&AlmatySiteBuilder'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        self.loadProject()
        self.getCoordinates()

    def loadProject(self):

        indir = 'P:/2334_Almaty_Visioning_Forum/2334C_New_City/2334_Design/For_Plugin'
        outdir = 'P:/2334_Almaty_Visioning_Forum/2334C_New_City/2334_Design/For_Plugin'
        for root, dirs, files in os.walk(indir):
            for file in files:
                if file.endswith('.csv'):
                    fullname = os.path.join(root, file).replace('\\', '/')
                    filename = os.path.splitext(os.path.basename(fullname))[0]
                    uri = 'file:///%s?crs=%s&delimiter=%s&xField=%s&yField=%s&decimal=%s' % (
                    fullname, 'EPSG:32643', ",", "x", "y", ".")
                    layer = QgsVectorLayer(uri, 'Site area coordinates', 'delimitedtext')
                    QgsVectorFileWriter.writeAsVectorFormat(layer, outdir + '/' + filename + '.shp', 'CP1250', None,
                                                            'ESRI Shapefile')

        path = outdir + '/' + filename + '.shp'
        filename = os.path.basename(path)
        location = os.path.abspath(path)
        input = self.iface.addVectorLayer(location, filename, "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(input)


    def getLegendLayerByName(self):
        layer = None
        for i in self.iface.legendInterface().layers():
            if i.name() == '2334C_New_City_Development_ scenarios_points.shp':
                layer = i
        return layer


    def getCoordinates(self):
        layer = self.getLegendLayerByName()
        features = layer.getFeatures()
        print features

        x = []
        y = []


        for feat in features:
            attrs = feat.attributes()
            x.append(attrs[0])
            y.append(attrs[1])

        print x
        print y

        point1 = QgsPoint(x[0],y[0])
        point2 = QgsPoint(x[1], y[1])
        point3 = QgsPoint(x[2], y[2])
        point4 = QgsPoint(x[3], y[3])

        destCRS = self.canvas.mapRenderer().destinationCrs()
        layer = QgsVectorLayer("LineString?crs=" + destCRS.toWkt(), 'Site Boundary', "memory")
        pr = layer.dataProvider()
        line = QgsFeature()
        line.setGeometry(QgsGeometry.fromPolyline([point1, point2]))

        line1 = QgsFeature()
        line1.setGeometry(QgsGeometry.fromPolyline([point1, point3]))

        line2 = QgsFeature()
        line2.setGeometry(QgsGeometry.fromPolyline([point2, point4]))

        line3 = QgsFeature()
        line3.setGeometry(QgsGeometry.fromPolyline([point3, point4]))

        pr.addFeatures([line])
        pr.addFeatures([line1])
        pr.addFeatures([line2])
        pr.addFeatures([line3])
        layer.updateExtents()
        QgsMapLayerRegistry.instance().addMapLayers([layer])



