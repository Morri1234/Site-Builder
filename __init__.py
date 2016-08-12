# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AlmatySiteBuilder
                                 A QGIS plugin
 Builds site area required based on factors specified in a Excel file
                             -------------------
        begin                : 2016-08-12
        copyright            : (C) 2016 by Abhimanyu Acharya. Space Syntax Limited
        email                : a.acharya@spacesyntax.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load AlmatySiteBuilder class from file AlmatySiteBuilder.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Almaty_Site_Builder import AlmatySiteBuilder
    return AlmatySiteBuilder(iface)
