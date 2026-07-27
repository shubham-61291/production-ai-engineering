from opentelemetry import trace

# Single tracer instance for the whole app
tracer = trace.get_tracer(__name__)
