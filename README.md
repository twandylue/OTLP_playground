# OTLP\_playground

My OpenTelemetry Playground. For learning and testing purposes. Tracing between multiple services.

In this case, `server1` would send a request to `server2`. Both servers are instrumented with OpenTelemetry.

## How to run

```console
$ python -m pip install -r requirements.txt
...(snip)
```

### On server 1

```consle
cd ./server1
$ python3 app.py
{'baggage': 'hello=world', 'traceparent': '00-ff6f8fe8c53cc958720b1c6ddc762cfa-1ba973510338c61f-01'}
127.0.0.1 - - [25/May/2024 05:36:45] "GET / HTTP/1.1" 200 -
{
    "name": "hello",
    "context": {
        "trace_id": "0xff6f8fe8c53cc958720b1c6ddc762cfa",
        "span_id": "0x1ba973510338c61f",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": null,
    "start_time": "2024-05-25T11:36:45.049766Z",
    "end_time": "2024-05-25T11:36:45.062631Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {},
    "events": [],
    "links": [],
    "resource": {
        "attributes": { "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.24.0",
            "service.name": "unknown_service"
        },
        "schema_url": ""
    }
}
```

### On server 2

This would output the log with WARNING level of the server 2 into `app.log` file.

```consle
cd ./server2
export ENV=DEV
$ python3 app.py
(...snip)
```

The log file would be created in the same directory.

### On client side

```console
$ curl http://localhost:8080/rolldice
Hell from API 1! Response from API 2: Hello from API 2!
```

## How to run the unit tests

```console
export ENV=TEST
$ pytest wsgi.py
(...snip)
```

## References

- [OpenTelemetry](https://opentelemetry.io/docs/languages/python/getting-started/)
- [Propagation](https://opentelemetry.io/docs/languages/js/propagation/)
