import re
import time
import redis
import threading
import numpy as np
import pytest

from .utils import redis_config_ctx
from blissdata.redis_engine.encoding.numeric import NumericStreamEncoder
from blissdata.redis_engine.stream import Stream, StreamingClient
from blissdata.redis_engine.exceptions import (
    EndOfStream,
    IndexNoMoreThereError,
    IndexNotYetThereError,
    NoWritePermission,
    UnknownEncodingError,
)


def stream_pair(data_store, dtype):
    # TODO use a context manager to seal the streams in case of error, so the sinks do not hang
    encoder = NumericStreamEncoder(dtype)
    model = data_store._stream_model(encoding=encoder.info())
    name = f"stream_{model.pk}"
    rw_stream = Stream.create(data_store, name, model, encoder)
    ro_stream = Stream.open(data_store, name, model)
    return rw_stream, ro_stream


def test_stream_key(data_store):
    model = data_store._stream_model(encoding={"type": "json"})
    stream = Stream.open(data_store, "my_stream", model)
    assert stream.name == "my_stream"
    assert re.match("^esrf:stream:[A-Z0-9]{26}$", stream.key)


@pytest.mark.parametrize("dtype", [int, float, np.uint32])
def test_stream_type(data_store, dtype):
    input = np.arange(1000, dtype=dtype)
    rw_stream, ro_stream = stream_pair(data_store, input.dtype)
    rw_stream.send(input)
    rw_stream.seal()
    output = ro_stream[:]
    assert input.dtype == output.dtype
    assert np.array_equal(input, output)


def test_stream_invalid_type(data_store):
    rw_stream, _ = stream_pair(data_store, np.int32)

    # invalid size
    with pytest.raises(TypeError):
        rw_stream.send(np.int16(5))

    # invalid kind
    with pytest.raises(TypeError):
        rw_stream.send(np.float32(5))


def test_stream_write_permission(data_store):
    input = np.arange(1000)
    rw_stream, ro_stream = stream_pair(data_store, input.dtype)
    rw_stream.send(input)
    rw_stream.seal()

    # both ro_stream and rw_stream can read
    assert np.array_equal(input, rw_stream[:])
    assert np.array_equal(input, ro_stream[:])

    # ro_stream can't send nor seal the stream
    with pytest.raises(NoWritePermission):
        ro_stream.send(input)
    with pytest.raises(NoWritePermission):
        ro_stream.seal()


def test_stream_unknown_encoding(data_store):
    model = data_store._stream_model(encoding={"type": "teapot"})
    with pytest.raises(UnknownEncodingError):
        Stream.create(data_store, "my_stream", model, None)


def test_multiple_calls_to_seal(data_store):
    input = np.arange(1000)
    rw_stream, _ = stream_pair(data_store, input.dtype)
    rw_stream.send(input)

    # make a second writing stream to test re-sealing from an unaware object
    external_writer = Stream.create(
        data_store, rw_stream.name, rw_stream._model, rw_stream._encoder
    )

    assert rw_stream.seal() == 1000
    assert rw_stream.seal() == 1000
    assert external_writer.seal() == 1000
    assert external_writer.seal() == 1000


def test_stream_chunk_slicing(data_store):
    data = np.arange(100)
    rw_stream, ro_stream = stream_pair(data_store, data.dtype)

    # produce chunks of different sizes
    rw_stream.send(data[0])  # 1
    rw_stream.send(data[1:3])  # 2
    rw_stream.send(data[3:6])  # 3
    rw_stream.send(data[6:10])  # 4
    rw_stream.send(data[10:20])  # 10
    rw_stream.send(data[20:50])  # 30
    rw_stream.send(data[50:])  # 50
    rw_stream.join()
    assert len(ro_stream) == 100

    assert np.array_equal(data[0], ro_stream[0])
    assert np.array_equal(data[42], ro_stream[42])
    assert np.array_equal(data[:10], ro_stream[:10])
    assert np.array_equal(data[20:30], ro_stream[20:30])
    assert np.array_equal(data[30:20], ro_stream[30:20])
    assert np.array_equal(data[0:10:3], ro_stream[0:10:3])

    data2 = np.arange(100, 200)

    # produce chunks of different sizes
    rw_stream.send(data2[0:50])  # 50
    rw_stream.send(data2[50:80])  # 30
    rw_stream.send(data2[80:90])  # 10
    rw_stream.send(data2[90:94])  # 4
    rw_stream.send(data2[94:97])  # 3
    rw_stream.send(data2[97:99])  # 2
    rw_stream.send(data2[99])  # 1

    rw_stream.seal()
    assert len(ro_stream) == 200

    assert np.array_equal(data2[0], ro_stream[100])
    assert np.array_equal(data2[-1], ro_stream[-1])
    assert np.array_equal(np.concatenate((data, data2)), ro_stream[:])
    assert np.array_equal(np.concatenate((data, data2))[50:150], ro_stream[50:150])


def test_stream_negative_index_sealed(data_store):
    data = np.arange(10)

    rw_stream, ro_stream = stream_pair(data_store, data.dtype)
    rw_stream.send(data[0:2])
    rw_stream.send(data[2])
    rw_stream.send(data[3:7])
    rw_stream.send(data[7:10])
    rw_stream.seal()
    assert len(ro_stream) == 10

    for i in range(-15, 15):
        if -10 <= i < 10:
            assert np.array_equal(data[i], ro_stream[i])
        else:
            with pytest.raises(IndexError):
                ro_stream[i]

    for i in range(-15, 15):
        for j in range(-15, 15):
            assert np.array_equal(data[i:j], ro_stream[i:j])


def test_stream_negative_index_unsealed(data_store):
    data = np.arange(10)

    rw_stream, ro_stream = stream_pair(data_store, data.dtype)
    rw_stream.send(data[0:2])
    rw_stream.send(data[2])
    rw_stream.send(data[3:7])
    rw_stream.send(data[7:10])
    rw_stream.join()
    assert len(ro_stream) == 10

    for i in range(-15, 15):
        if 0 <= i < 10:
            assert np.array_equal(data[i], ro_stream[i])
        else:
            with pytest.raises(IndexNotYetThereError):
                ro_stream[i]

    for i in range(-15, 15):
        for j in range(-15, 15):
            if i < 0 or j < 0:
                with pytest.raises(IndexNotYetThereError):
                    ro_stream[i:j]
            else:
                assert np.array_equal(data[i:j], ro_stream[i:j])

    for i in range(-15, 15):
        with pytest.raises(IndexNotYetThereError):
            ro_stream[i:]

    rw_stream.seal()


def test_stream_not_yet_there_index(data_store):
    # fixing issue https://gitlab.esrf.fr/bliss/bliss/-/issues/4389

    rw_stream, ro_stream = stream_pair(data_store, int)

    def send_soon():
        for i in range(1000):
            rw_stream.send(i)

    t = threading.Thread(target=send_soon)
    t.start()
    try:
        i = 0
        while i < 1000:
            try:
                ro_stream[i]
                i += 1
            except IndexNotYetThereError:
                # if the race condition exists, an IndexNoMoreThereError is
                # likely to be raised instead (not always).
                pass
    finally:
        rw_stream.seal()
        t.join()


############################################################################################
# STREAMING CLIENT


# def test_streaming_client_blocking_read(data_store):
#     one stream
#     two stream


# def test_streaming_client_timeout(data_store):
#     one stream
#     two stream
#
# client.read(block=False)
# client.read(block=True) # default
# client.read(timeout=-1)
# client.read(timeout=0)
# client.read(timeout=1)
#
# # client.read(count=0) # this is already default
# client.read(count=10)
# client.read(count=-1)
# client.read(count=-10)
#
# single bunch / multi bunch
# single stream / multi stream
#
#
# StreamingClient(read_from_origin)
# StreamingClient() # start immediately
# StreamingClient() # start after a while

# @pytest.mark.parametrize("wait_for_ack", [False]) # TODO discard to speed up and test sink separately ?


@pytest.mark.parametrize(
    "count",
    [
        -100,
        -2,
        -1,
        0,
        1,
        2,
        100,
    ],
)
@pytest.mark.parametrize("block", [True, False])
@pytest.mark.parametrize("seal", [True, False])
@pytest.mark.parametrize(
    "batches",
    [
        [],  # empty
        [[0]],  # one
        [[0, 1, 2]],  # three
        [[0], [1, 2, 3]],  # one_three
        [[0, 1, 2], [3]],  # three_one
        [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9]],  # singles
        [[0, 1], [2, 3, 4, 5, 6, 7], [8], [9, 10], [11, 12, 13], [14, 15]],  # mixed
    ],
)
def test_streaming_client_batching(data_store, count, batches, seal, block):
    encoder = NumericStreamEncoder(np.int64)
    model = data_store._stream_model(encoding=encoder.info())
    stream = Stream.create(data_store, "test_stream", model, encoder)

    for batch in batches:
        stream.send(batch)
    if seal:
        stream.seal()
    stream.join()

    if count == 0:
        expected_batch = batches
    elif count < 0:
        expected_batch = batches[count:]
    else:
        expected_batch = batches[:count]

    if expected_batch:
        expected_data = np.concatenate(expected_batch)
    else:
        expected_data = np.array([], dtype=np.int64)

    client = StreamingClient([stream])
    if len(expected_data) == 0 and seal:
        output = {}
        with pytest.raises(EndOfStream):
            if block:
                output = client.read(timeout=0.001, count=count)
            else:
                output = client.read(block=False, count=count)
    else:
        if block:
            output = client.read(timeout=0.001, count=count)
        else:
            output = client.read(block=False, count=count)

    if batches:
        index, out = output[stream]
        assert index == expected_data[0]  # because values are the indexes
        assert np.array_equal(out, expected_data)
    else:
        assert output == {}


@pytest.fixture
def prepare_streams(data_store):
    streams_data = {
        "empty": [],
        "one": [[0]],
        "three": [[0, 1, 2]],
        "one_three": [[0], [1, 2, 3]],
        "three_one": [[0, 1, 2], [3]],
        "singles": [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9]],
        "mixed": [[0, 1], [2, 3, 4, 5, 6, 7], [8], [9, 10], [11, 12, 13], [14, 15]],
    }

    encoder = NumericStreamEncoder(np.int64)
    streams = {}
    for name, data in streams_data.items():
        model = data_store._stream_model(encoding=encoder.info())
        rw_stream = Stream.create(data_store, name, model, encoder)
        for batch in data:
            rw_stream.send(batch)
        rw_stream.join()
        streams[name] = Stream.open(data_store, name, model)
    return streams, streams_data


def test_streaming_client_read_from_origin(prepare_streams):
    streams, expected_data = prepare_streams
    client = StreamingClient(streams)
    output = client.read(block=False)
    named_output = {stream.name: data for stream, data in output.items()}
    for name, data in expected_data.items():
        if data:
            assert name in named_output
            first_index, dat = named_output[name]
            assert first_index == 0
            assert np.array_equal(dat, np.concatenate(expected_data[name]))
        else:
            assert name not in named_output


def test_streaming_client_read_from_now(prepare_streams):
    streams, expected_data = prepare_streams

    client = StreamingClient(streams)
    # skip existing data
    _ = client.read(block=False, count=-1)

    output = client.read(block=False)
    assert output == {}


@pytest.mark.parametrize("block", [True, False])
def test_streaming_client_block(data_store, block):
    rw_stream, ro_stream = stream_pair(data_store, np.int64)
    client = StreamingClient(streams={ro_stream.name: ro_stream})

    data = np.arange(100)

    def send_soon():
        time.sleep(0.5)
        rw_stream.send(data)

    t = threading.Thread(target=send_soon)
    t.start()
    output = client.read(block=block)
    t.join()

    if block:
        assert set(output.keys()) == {ro_stream}
        first_index, output_data = output[ro_stream]
        assert first_index == 0
        assert np.array_equal(data, output_data)
    else:
        assert output == {}


@pytest.mark.parametrize("timeout", [0.5, 2])
def test_streaming_client_timeout(data_store, timeout):
    rw_stream, ro_stream = stream_pair(data_store, np.int64)
    client = StreamingClient(streams={ro_stream.name: ro_stream})

    data = np.arange(100)

    def send_soon():
        time.sleep(1)
        rw_stream.send(data)

    t = threading.Thread(target=send_soon)
    t.start()
    output = client.read(timeout=timeout)
    t.join()

    if timeout > 1.0:
        assert set(output.keys()) == {ro_stream}
        first_index, output_data = output[ro_stream]
        assert first_index == 0
        assert np.array_equal(data, output_data)
    else:
        assert output == {}


def test_streaming_client_block_exit(data_store):
    """StreamingClient.read(block=True) should return as soon as data arrives in any of its streams"""
    rw_streams = []
    ro_streams = []
    for i in range(3):
        rw_stream, ro_stream = stream_pair(data_store, np.int64)
        rw_streams.append(rw_stream)
        ro_streams.append(ro_stream)

    client = StreamingClient(streams={s.name: s for s in ro_streams})

    def send_soon():
        time.sleep(0.5)
        rw_streams[1].send([1, 2, 3])
        rw_streams[1].join()
        rw_streams[2].send([4, 5, 6])
        rw_streams[2].join()
        rw_streams[1].send([7, 8, 9])

    t = threading.Thread(target=send_soon)
    t.start()
    output = client.read()
    t.join()

    assert set(output.keys()) == {ro_streams[1]}
    first_index, output_data = output[ro_streams[1]]
    assert first_index == 0
    assert np.array_equal([1, 2, 3], output_data)

    for rw_stream in rw_streams:
        rw_stream.join()
    output = client.read()

    assert set(output.keys()) == {ro_streams[1], ro_streams[2]}
    first_index, output_data = output[ro_streams[1]]
    assert first_index == 3
    assert np.array_equal([7, 8, 9], output_data)
    first_index, output_data = output[ro_streams[2]]
    assert first_index == 0
    assert np.array_equal([4, 5, 6], output_data)


def test_streaming_client_sealed_stream(data_store):
    rw_stream, ro_stream = stream_pair(data_store, dtype=int)
    client = StreamingClient({"my_stream": ro_stream})

    rw_stream.send([1, 2, 3])
    client.read()
    rw_stream.seal()

    with pytest.raises(EndOfStream):
        client.read()
    assert not client._stream_ids
    assert ro_stream._seal is not None


def test_streaming_client_multi_bunch(data_store):
    nb_streams = 100

    rw_streams = []
    ro_streams = []
    for i in range(nb_streams):
        rw_stream, ro_stream = stream_pair(data_store, np.int64)
        rw_streams.append(rw_stream)
        ro_streams.append(ro_stream)

    client = StreamingClient(
        streams={f"my_stream{i}": ro_streams[i] for i in range(nb_streams)}
    )

    data = np.arange(2000)

    def send_soon():
        for slice_index in range(0, 2000, 100):
            for stream in rw_streams:
                stream.send(data[slice_index : slice_index + 100])

    t = threading.Thread(target=send_soon)
    t.start()
    all_data = {stream: np.empty(shape=(0), dtype=np.int64) for stream in ro_streams}
    while True:
        new_data = client.read(timeout=0.1)
        for stream, value in new_data.items():
            all_data[stream] = np.concatenate((all_data[stream], value[1]))
        if not new_data:
            break
    t.join()

    assert len(all_data) == nb_streams
    for stream_data in all_data.values():
        assert np.array_equal(stream_data, data)


def test_monitor_stream(data_store):
    rw_stream, ro_stream = stream_pair(data_store, dtype=int)
    client = StreamingClient({"my_stream": ro_stream})

    # read last batch (less than available)
    rw_stream.send(10)  # 0
    rw_stream.send([20, 21])  # 1, 2
    rw_stream.send([30, 31, 32])  # 3, 4, 5
    rw_stream.join()
    index, data = client.read(block=False, count=-1)[ro_stream]
    assert index == 3
    assert np.array_equal(data, [30, 31, 32])

    # read at most n last batches (exactly what's available)
    rw_stream.send([40, 41])  # 6, 7
    rw_stream.send([50, 51, 52])  # 8, 9, 10
    rw_stream.send(60)  # 11
    rw_stream.join()
    index, data = client.read(block=False, count=-3)[ro_stream]
    assert index == 6
    assert np.array_equal(data, [40, 41, 50, 51, 52, 60])

    # read at most m last batches (more than what's available)
    rw_stream.send(70)  # 12
    rw_stream.send(80)  # 13
    rw_stream.send([90, 91, 92])  # 14, 15, 16
    rw_stream.join()
    index, data = client.read(block=False, count=-7)[ro_stream]
    assert index == 12
    assert np.array_equal(data, [70, 80, 90, 91, 92])

    # read last batch, but there is nothing new
    assert client.read(block=False, count=-1) == {}

    # blocking read of at most n last batches (only one is returned)
    def send_soon():
        time.sleep(0.5)
        rw_stream.send(11)  # 17
        rw_stream.send(21)  # 18
        rw_stream.send(31)  # 19

    t = threading.Thread(target=send_soon)
    t.start()

    index, data = client.read(count=-10)[ro_stream]
    assert index == 17
    assert data == 11  # 11 unblock the client, 21 and 31 arrive after
    t.join()


def test_monitor_sealed_stream(data_store):
    rw_stream, ro_stream = stream_pair(data_store, dtype=int)
    client = StreamingClient({"my_stream": ro_stream})

    rw_stream.send([1, 2, 3])
    rw_stream.seal()

    index, data = client.read(count=-1)[ro_stream]
    assert index == 0
    assert np.array_equal(data, [1, 2, 3])


def test_monitor_sealed_stream_no_new_available(data_store):
    rw_stream, ro_stream = stream_pair(data_store, dtype=int)
    client = StreamingClient({"my_stream": ro_stream})

    rw_stream.send([1, 2, 3])
    client.read(count=-1)
    rw_stream.seal()

    with pytest.raises(EndOfStream):
        client.read(count=-1)


def test_monitor_sealed_stream_no_data_at_all(data_store):
    rw_stream, ro_stream = stream_pair(data_store, dtype=int)
    client = StreamingClient({"my_stream": ro_stream})

    rw_stream.seal()
    with pytest.raises(EndOfStream):
        client.read(count=-1)


def test_monitor_sealed_stream_during_read(data_store):
    rw_stream, ro_stream = stream_pair(data_store, dtype=int)
    client = StreamingClient({"my_stream": ro_stream})

    def seal_soon():
        time.sleep(0.5)
        rw_stream.seal()

    t = threading.Thread(target=seal_soon)
    t.start()

    with pytest.raises(EndOfStream):
        client.read(count=-1)
    t.join()


def test_streaming_client_discontinuity(data_store):
    encoder = NumericStreamEncoder(np.int64)
    model = data_store._stream_model(encoding=encoder.info())
    stream = Stream.create(data_store, "test_stream", model, encoder)
    client = StreamingClient([stream])

    stream.send([0, 1, 2, 3])
    stream.join()
    _ = client.read()

    # break the internal index before writing again
    stream._write_index += 1

    stream.send([4, 5, 6, 7])
    stream.join()

    with pytest.raises(IndexNoMoreThereError):
        _ = client.read()


@pytest.mark.timeout(20)
def test_out_of_memory_send(redis_url, data_store):
    with redis_config_ctx(
        redis_url,
        redis_config={
            "maxmemory": "20MB",
            "maxmemory-policy": "noeviction",
        },
    ):
        encoder = NumericStreamEncoder(dtype=float, shape=(64,))
        model = data_store._stream_model(encoding=encoder.info())
        stream = Stream.create(data_store, "test_stream", model, encoder)

        with pytest.raises(redis.exceptions.ResponseError):
            # send too much data for Redis
            for i in range(40000):
                stream.send(np.empty((64,)))
            # If the sink puts commands in the socket fast enough, errors from Redis may
            # have not been received yet. In that case, let's wait a bit an send again.
            while True:
                time.sleep(0.01)
                stream.send(np.empty((64,)))


@pytest.mark.timeout(20)
def test_out_of_memory_join(redis_url, data_store):
    with redis_config_ctx(
        redis_url,
        redis_config={
            "maxmemory": "128MB",
            "maxmemory-policy": "noeviction",
        },
    ):
        encoder = NumericStreamEncoder(dtype=float, shape=(64,))
        model = data_store._stream_model(encoding=encoder.info())
        stream = Stream.create(data_store, "test_stream", model, encoder)

        # send ALMOST too much data for Redis
        while data_store._redis.info()["used_memory"] < 100 * 2**20:  # ~100MB
            stream.send(
                np.empty(
                    (
                        10000,
                        64,
                    )
                )
            )
            stream.join()

        # Overload Redis in one go, so the error can only be raised later (in the join())
        stream.send(np.empty((100000, 64)))
        with pytest.raises(redis.exceptions.ResponseError):
            stream.join()


@pytest.mark.timeout(20)
def test_out_of_memory_seal(redis_url, data_store):
    with redis_config_ctx(
        redis_url,
        redis_config={
            "maxmemory": "128MB",
            "maxmemory-policy": "noeviction",
        },
    ):
        encoder = NumericStreamEncoder(dtype=float, shape=(64,))
        model = data_store._stream_model(encoding=encoder.info())
        stream = Stream.create(data_store, "test_stream", model, encoder)

        # send ALMOST too much data for Redis
        while data_store._redis.info()["used_memory"] < 100 * 2**20:  # ~100MB
            stream.send(
                np.empty(
                    (
                        10000,
                        64,
                    )
                )
            )
            stream.join()

        # Overload Redis in one go, so the error can only be raised later (in the seal())
        stream.send(np.empty((100000, 64)))
        with pytest.raises(redis.exceptions.ResponseError):
            stream.seal()
