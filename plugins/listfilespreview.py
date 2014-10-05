from rugmi.plugins.core import response, authenticate
from rugmi.plugins.config import store_path, url
from rugmi.plugins.routing import route
from rugmi.plugins.template import templated


@route("/list/filespreview")
@response
@templated
def indexlistpreview(environ, start_response):
    return """
    <form enctype="multipart/form-data" method="post" role="form">
      <div class="form-group">
        <p>Key: <input class="form-control" name="key" type="input"></p>
        <p><button type='submit' class='btn btn-primary'>Send</button></p>
      </div>
    </form>"""


@route("/list/filespreview", methods=["POST"])
@authenticate
@response
@templated
def listfilespreview(environ, start_response):
    files = os.listdir(store_path)
    files = (os.path.join(store_path, f) for f in files)
    files = filter(os.path.isfile, files)
    files = sorted(files, key=lambda x: os.path.getmtime(x), reverse=True)
    files = map(os.path.basename, files[:20])
    files = map(lambda s: s.decode("utf8"), files)

    html = '<div class="row">{rows}</div>{style}'
    row = '''
    <div class="col-sm-6 col-md-4 mymargin">
      <div class="thumbnail">
        <img src="{url}/{file}" alt="{file}">
        <div class="caption">
          <a href="{url}/{file}" class="btn btn-link" role="button">{file}</a>
        </div>
      </div>
    </div>
    '''

    style = '''
    <style>
    .thumbnail > img {
      min-width: 100px !important;
      min-height: 150px !important;
      max-width: 310px !important;
      max-height: 150px !important;
    }

    .btn-link, .btn-link:hover, .btn-link:focus, .btn-link:active {
      margin-right: auto !important;
      margin-left: auto !important;
      width: 100% !important;
    }

    .mymargin {
      margin-bottom: 10px !important;
    }
    </style>
    '''

    return html.format(style=style,
                       rows="".join(
                           [row.format(url=url, file=f) for f in files]))
