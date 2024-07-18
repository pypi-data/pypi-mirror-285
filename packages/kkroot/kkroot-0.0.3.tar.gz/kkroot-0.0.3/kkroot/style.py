"""
Helper functions for applying styles to plots from configurations.

Each `style` function takes at least two arguments. The first argument is the
object to be styled. The remaining arguments are properties that should be
applied as part of the styling. In most cases, they are direct maps to a `Set..`
function of the object. The argument can either be a string or the type expected
by the object functon. In case of string, automatic conversion is attempted.
"""

import ROOT

def style(obj, **kwargs):
    """
    Apply style to `obj` based on `kwargs`. This forwards all necessary style
    functions based on the inherted classes by `obj`.
    """
    if obj.InheritsFrom('TAttLine'):
        style_TAttLine(obj, **kwargs)

    if obj.InheritsFrom('TAttMarker'):
        style_TAttMarker(obj, **kwargs)

    if obj.InheritsFrom('THStack'):
        style_THStack(obj, **kwargs)

    if obj.InheritsFrom('TAxis'):
        style_TAxis(obj, **kwargs)

def style_TAttLine(obj, **kwargs):
    """
    Apply style to a TAttLine object. The following properties are supported:
     - `color` or `linecolor` -> `SetLineColor`
     - `linewidth` -> `SetLineWidth`
    """
    linecolor=None
    if 'color' in kwargs:
        linecolor=kwargs['color']
    if 'linecolor' in kwargs:
        linecolor=kwargs['linecolor']

    if linecolor is not None:
        if type(linecolor) is str:
            linecolor=getattr(ROOT, linecolor)
        obj.SetLineColor(linecolor)

    if 'linewidth' in kwargs:
        obj.SetLineWidth(kwargs['linewidth'])

def style_TAttMarker(obj, **kwargs):
    """
    Apply style to a TAttMarker object. The following properties are supported:
     - `color` or `markercolor` -> `SetMarkerColor`
    """
    markercolor=None
    if 'color' in kwargs:
        markercolor=kwargs['color']
    if 'markercolor' in kwargs:
        markercolor=kwargs['markercolor']

    if markercolor is not None:
        if type(markercolor) is str:
            markercolor=getattr(ROOT, markercolor)
        obj.SetmarkerColor(markercolor)

def style_THStack(obj, **kwargs):
    """
    Apply style to a THStack object. The following properties are supported:
     - `yaxis.min` -> `obj->SetMinimum`
     - `yaxis.max` -> `obj->SetMaximum`
     - `yaxis.*` -> `style_TAxis(**yaxis)`
    """
    if 'yaxis' in kwargs:
        yaxis=kwargs['yaxis']
        if 'min' in yaxis:
            obj.SetMinimum(yaxis['min'])
        if 'max' in yaxis:
            obj.SetMaximum(yaxis['max'])
        style_TAxis(obj.GetYaxis(), **yaxis)

def style_TAxis(obj, **kwargs):
    """
    Apply style to a TAxis object. The following properties are supported:
     - `title` -> `SetTitle`
    """
    if 'title' in kwargs:
        obj.SetTitle(kwargs['title'])
