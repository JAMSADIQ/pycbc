"""
This Module contains generic utility functions for creating plots within 
PyCBC. 
"""
import os.path, pycbc.version
import ConfigParser, HTMLParser
from xml.sax.saxutils import escape, unescape

escape_table = {
                '"': "&quot;",
                "'": "&apos;",
                }
unescape_table = {}
for k, v in escape_table.items():
    unescape_table[v] = k

class MetaParser(HTMLParser.HTMLParser):
    def __init__(self):
        self.metadata = {}

    def handle_starttag(self, tag, attrs):
        attr= {}
        for key, value in attrs:
            attr[key] = value
        if tag == 'div' and 'class' in attr and attr['class'] == 'pycbc-meta':
            self.metadata[attr['key']] = unescape(attr['value'], unescape_table)
        

def save_html_with_metadata(text, filename, fig_kwds, kwds):
    """ Save a html output to file with metadata """
    f = open(filename, 'w')
    f.write(text)
    for key, value in kwds:
        value = escape(value, escape_table)
        line = """<div class=pycbc-meta key="%s" value="%s"></div>\n""" % (str(key), value) 
    
def load_html_with_metadata(filename):
    """ Get metadata from html file """
    parser = MetaParser()
    parser.feed(open(filename, 'r').read())
    cp = ConfigParser.ConfigParser(parser.metadata)
    cp.add_section(os.path.basename(filename))
    return cp

def save_png_with_metadata(fig, filename, fig_kwds, kwds):
    """ Save a matplotlib figure to a png with metadata
    """
    from PIL import Image, PngImagePlugin
    fig.savefig(filename, **fig_kwds)
     
    im = Image.open(filename)
    meta = PngImagePlugin.PngInfo()
    
    for key in kwds:
        meta.add_text(str(key), str(kwds[key]))       
         
    im.save(filename, "png", pnginfo=meta)

def load_png_metadata(filename):
    from PIL import Image, PngImagePlugin
    data = Image.open(filename).info
    cp = ConfigParser.ConfigParser(data)
    cp.add_section(os.path.basename(filename))
    return cp
    
_metadata_saver = {'.png':save_png_with_metadata,
                   '.html':save_html_with_metadata,
                  }
_metadata_loader = {'.png':load_png_metadata,
                    '.html':load_html_metadata,
                   }

def save_fig_with_metadata(fig, filename, fig_kwds={}, **kwds):
    """ Save plot to file with metadata included. Kewords translate to metadata
    that is stored directly in the plot file. Limited format types available.
    
    Parameters
    ----------
    fig: matplotlib figure
        The matplotlib figure to save to the file
    filename: str
        Name of file to store the plot.
    """
    try:
        extension = os.path.splitext(filename)[1]
        kwds['version'] = pycbc.version.git_verbose_msg
        _metadata_saver[extension](fig, filename, fig_kwds, kwds)
    except KeyError:
        raise TypeError('Cannot save file %s with metadata, extension %s not ' 
                        'supported at this time' % (filename, extension))

def load_metadata_from_file(filename):
    """ Load the plot related metadata saved in a file
    
    Parameters
    ----------
    filename: str
        Name of file load metadata from.
        
    Returns
    -------
    cp: ConfigParser
        A configparser object containing the metadata
    """
    try:
        extension = os.path.splitext(filename)[1]
        return _metadata_loader[extension](filename)
    except KeyError:
        raise TypeError('Cannot read metadata from file %s, extension %s not ' 
                        'supported at this time' % (filename, extension))    
