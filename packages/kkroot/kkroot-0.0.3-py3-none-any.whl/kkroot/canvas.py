def apply_ratio_canvas_style(c):
    """
    Split a TCanvas into two pads for the main plot and a ratio
    plot. The pads are sized correspondingly.
    """
    c.Clear()
    c.Divide(1,2)
    pad=c.cd(1)
    pad.SetPad(0.01,0.25,0.99,0.99)
    pad.SetBottomMargin(0)
    pad_ratio=c.cd(2)
    pad_ratio.SetBorderSize(0)
    pad_ratio.SetTopMargin(0)
    pad_ratio.SetBottomMargin(0.35)
    pad_ratio.SetPad(0.01,0.0,.99,0.25)
    pad_ratio.SetGridy()

    return pad,pad_ratio

def apply_ratio_axis_style(frame):
    """
    Apply correct font sizes to axes of `frame` to make the
    font legible with the use of `apply_ratio_axis_style`.

    Needs to be called with the drawn object.
    """
    frame.GetXaxis().SetTitleSize(0.17)
    frame.GetXaxis().SetTitleOffset(0.9)

    frame.GetYaxis().SetTitleSize(0.15)
    frame.GetYaxis().SetTitleOffset(0.45)

    frame.GetYaxis().SetNdivisions(5,2,1)

    frame.GetXaxis().SetLabelSize(0.15);
    frame.GetYaxis().SetLabelSize(0.15);
