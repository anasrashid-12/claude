from prometheus_fastapi_instrumentator import Instrumentator

def register_metrics(app):
    Instrumentator().instrument(app).expose(app)
