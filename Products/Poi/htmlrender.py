# File: htmlrender.py
#
# GNU General Public Licence (GPL)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
__author__ = '''Rocky Burt <rocky@serverzen.com>'''
__docformat__ = 'plaintext'

__all__ = ('renderHTML', )

import reStructuredText as rst

htmlTemplate = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
      xml:lang="%(lang)s"
      lang="%(lang)s">

  <head>
     <meta http-equiv="Content-Type" content="text/html; charset=%(charset)s" />

    <style type="text/css" media="all">
<!--
BODY {
    font-size: 0.9em;
}

H4 {
    font-size: 1.2em;
    font-weight: bold;
}

DT {
    font-weight: bold;
}
-->
    </style>

  </head>


  <body>
%(body)s
  </body>
</html>
"""


def renderHTML(rstText, lang='en', charset='utf-8'):
    """Convert the given rST into a full XHTML transitional document.
    """

    ignored, warnings = rst.render(
        rstText, input_encoding=charset, output_encoding=charset)
    if len(warnings.messages) == 0:
        body = rst.HTML(
            rstText, input_encoding=charset, output_encoding=charset)
    else:
        # There are warnings, so we keep it simple.
        body = '<pre>%s</pre>' % rstText

    kwargs = {'lang': lang,
              'charset': charset,
              'body': body}

    return htmlTemplate % kwargs
