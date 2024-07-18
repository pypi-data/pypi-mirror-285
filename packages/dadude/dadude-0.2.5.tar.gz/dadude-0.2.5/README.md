# dadude

Lakehouse management and orchestration tool.

## Status

- The ultimate target lakehouse is the unity catalog, which is to provide benefits from both `deltalake` and `iceberg`.
- To support writing data to the lakehouse, we currently use the `deltalake-rs` python bindings.
- For testing purposes, we use the `minio` instance at `http://192.168.18.206:9000`.