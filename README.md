# OPTL_playground
OpenTelemetry Playground
=======
# OPTL\_playground

My OpenTelemetry Playground. For learning and testing purposes.

## How to run

### On server side

```consle
$ export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
opentelemetry-instrument \
    --traces_exporter console \
    --metrics_exporter console \
    --logs_exporter console \
    --service_name dice-server \
    flask run -p 8080
...(snip)
```

### On clinet side

```console
$ curl http://localhost:8080/rolldice
6
```

## References

- [OpenTelemetry](https://opentelemetry.io/docs/languages/python/getting-started/)
