import json
import textwrap

import six

from .core import write_file_or_filename
from .headless import spec_to_image_mimebundle


HTML_TEMPLATE = {
'vega-lite': """
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/vega@{vega_version}"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-lite@{vegalite_version}"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@{vegaembed_version}"></script>
</head>
<body>
  <div id="vis"></div>
  <script type="text/javascript">
    var spec = {spec};
    var opt = {embed_opt};
    vegaEmbed("#vis", spec, opt);
  </script>
</body>
</html>
""",

'vega': """
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/vega@{vega_version}"></script>
  <script src="https://cdn.jsdelivr.net/npm/vega-embed@{vegaembed_version}"></script>
</head>
<body>
  <div id="vis"></div>
  <script type="text/javascript">
    var spec = {spec};
    var opt = {embed_opt};
    vegaEmbed("#vis", spec, opt);
  </script>
</body>
</html>
"""}


def savechart(chart, fp, format=None, mode=None,
              vegalite_version='2', vega_version='3', vegaembed_version='3',
              opt=None, json_kwds=None):
    """Save a chart to file in a variety of formats

    Supported formats are [json, html, png, svg]

    Parameters
    ----------
    chart : alt.Chart
        the chart instance to save
    fp : string filename or file-like object
        file in which to write the chart.
    format : string (optional)
        the format to write: one of ['json', 'html', 'png', 'eps'].
        If not specified, the format will be determined from the filename.
    mode : string (optional)
        Either 'vega' or 'vegalite'. If not specified, then infer the mode from
        the '$schema' property of the spec, or the ``opt`` dictionary.
        If it's not specified in either of those places, then use 'vegalite'.
    vega_version : string
        For html output, the version of vega.js to use
    vegalite_version : string
        For html output, the version of vegalite.js to use
    vegaembed_version : string
        For html output, the version of vegaembed.js to use
    opt : dict
        The vegaEmbed options dictionary. Default is {}
        (See https://github.com/vega/vega-embed for details)
    json_kwds : dict
        Additional keyword arguments are passed to the output method
        associated with the specified format.
    """
    if json_kwds is None:
        json_kwds = {}

    if opt is None:
        opt = {}

    if format is None:
        if isinstance(fp, six.string_types):
            format = fp.split('.')[-1]
        else:
            raise ValueError("must specify file format: "
                             "['png', 'eps', 'html', 'json']")
    spec = chart.to_dict()

    if mode is None:
        if 'mode' in opt:
            mode = opt['mode']
        elif '$schema' in spec:
            mode = spec['$schema'].split('/')[-2]
        else:
            mode = 'vega-lite'

    if mode not in ['vega', 'vega-lite']:
        raise ValueError("mode must be 'vega' or 'vega-lite', "
                         "not '{0}'".format(mode))

    if format == 'json':
        json_spec = json.dumps(spec, **json_kwds)
        write_file_or_filename(fp, json_spec, mode='w')
    elif format == 'html':
        template = HTML_TEMPLATE[mode]
        opt['mode'] = mode
        json_spec = json.dumps(spec, **json_kwds)
        spec_html = template.format(spec=json_spec,
                                    embed_opt=json.dumps(opt),
                                    vega_version=vega_version,
                                    vegalite_version=vegalite_version,
                                    vegaembed_version=vegaembed_version)
        write_file_or_filename(fp, spec_html, mode='w')
    elif format in ['png', 'svg']:
        mimebundle = spec_to_image_mimebundle(spec, format=format, mode=mode,
                                              vega_version=vega_version,
                                              vegalite_version=vegalite_version,
                                              vegaembed_version=vegaembed_version)
        if format == 'png':
            write_file_or_filename(fp, mimebundle['image/png'], mode='wb')
        else:
            write_file_or_filename(fp, mimebundle['image/svg+xml'], mode='w')
    else:
        raise ValueError("unrecognized format: '{0}'".format(format))
