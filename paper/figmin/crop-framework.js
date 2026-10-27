// framework-crop.pdf: paper/fig/framework.pdf (figs/diagrams.py fig_framework) with its MediaBox cut to the drawing's
// vertical extent (gs -sDEVICE=bbox: y 11.214-106.190 pt of 108) plus 0.5 pt, full width kept so the drawing prints at
// the same scale. Usage: mutool run crop-framework.js <paper/fig/framework.pdf> framework-crop.pdf
var doc = Document.openDocument(scriptArgs[0]);
var page = doc.findPage(0);
var box = [0, 10.714, 484.56, 106.690];
page.put("MediaBox", box);
page.delete("CropBox");
doc.save(scriptArgs[1], "compress");
