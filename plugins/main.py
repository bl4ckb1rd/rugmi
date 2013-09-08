from rugmi.plugins.routing import application

if __name__ == '__main__':
    import sys
    for wrapper in wsgi_wrappers:
        application = wrapper(application)

    if len(sys.argv) == 2 and sys.argv[1] == "http":
        from wsgiref.simple_server import make_server
        srv = make_server('localhost', 8000, application)
        srv.serve_forever()
    else:
        from wsgiref.handlers import CGIHandler
        CGIHandler().run(application)
