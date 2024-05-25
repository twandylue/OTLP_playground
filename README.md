# OPTL\_playground

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
$ python3 server1.py
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

```consle
cd ./server2
$ python3 server2.py
Received headers: {'Host': 'localhost:5002', 'User-Agent': 'python-requests/2.32.2', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive', 'Baggage': 'hello=world', 'Traceparent': '00-ff6f8fe8c53cc958720b1c6ddc762cfa-1ba973510338c61f-01'}
Received context: {'current-span-7f6c34d0-62e3-4584-aed0-717044dfe423': NonRecordingSpan(SpanContext(trace_id=0xff6f8fe8c53cc958720b1c6ddc762cfa, span_id=0x1ba973510338c61f, trace_flags=0x01, trace_state=[], is_remote=True))}
Received context2: {'baggage-a4e0dff6-f6cd-4c2f-921e-4103abbaa52d': {'hello': 'world'}}
127.0.0.1 - - [25/May/2024 05:36:45] "GET / HTTP/1.1" 200 -
{
    "name": "api2_span",
    "context": {
        "trace_id": "0xff6f8fe8c53cc958720b1c6ddc762cfa",
        "span_id": "0xb6f3ef0370e3a2c1",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": "0x1ba973510338c61f",
    "start_time": "2024-05-25T11:36:45.061723Z",
    "end_time": "2024-05-25T11:36:45.061728Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {},
    "events": [],
    "links": [],
    "resource": {
        "attributes": {
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.24.0",
            "service.name": "unknown_service"
        },
        "schema_url": ""
    }
}
```

### On clinet side

```console
$ curl http://localhost:8080/rolldice
Hell from API 1! Response from API 2: Hello from API 2!
```

## References

- [OpenTelemetry](https://opentelemetry.io/docs/languages/python/getting-started/)
- [Propagation](https://opentelemetry.io/docs/languages/js/propagation/)
