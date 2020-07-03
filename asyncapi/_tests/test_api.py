import asynctest
import pytest
from jsonschema import ValidationError

import asyncapi.exceptions


@pytest.fixture
def fake_api():
    return asyncapi.build_api('fake', operations_module='asyncapi._tests')


@pytest.fixture
def fake_api_no_operation(spec_dict):
    return asyncapi.build_api('fake')


@pytest.fixture
def fake_api_no_operation_id(spec_dict):
    spec_dict['channels']['fake']['subscribe'].pop('operationId')
    return asyncapi.build_api('fake')


def test_should_get_api(fake_api):
    assert fake_api.spec
    assert fake_api.operations


@pytest.mark.asyncio
async def test_should_publish_message(
    fake_api, fake_broadcast, message, mocker
):
    await fake_api.publish('fake', message)

    assert fake_broadcast.publish.call_args_list == [
        mocker.call(channel='fake', message=message)
    ]


@pytest.mark.asyncio
async def test_should_listen_message(
    fake_api, fake_broadcast, message, mocker
):
    fake_operation = asynctest.CoroutineMock()
    fake_api.operations[('fake', 'fake_operation')] = fake_operation
    await fake_api.listen('fake')

    assert fake_broadcast.subscribe.call_args_list == [
        mocker.call(channel='fake')
    ]
    assert fake_operation.call_args_list == [mocker.call(message)]


@pytest.mark.asyncio
async def test_should_not_publish_for_invalid_message(
    fake_api, invalid_message, mocker
):
    with pytest.raises(ValidationError) as exc_info:
        await fake_api.publish('fake', invalid_message)

    assert exc_info.value.instance == invalid_message['faked']


@pytest.mark.asyncio
async def test_should_not_publish_for_invalid_channel(
    fake_api, message, mocker
):
    with pytest.raises(asyncapi.exceptions.InvalidChannelError) as exc_info:
        await fake_api.publish('faked', message)

    assert exc_info.value.args == ('faked',)


@pytest.mark.asyncio
async def test_should_not_listen_for_invalid_message(
    fake_api, fake_broadcast, invalid_message, mocker, async_iterator
):
    fake_operation = asynctest.CoroutineMock()
    fake_api.operations[('fake', 'fake_operation')] = fake_operation
    fake_broadcast.subscribe.return_value = async_iterator(
        [mocker.MagicMock(message=invalid_message)]
    )

    with pytest.raises(ValidationError) as exc_info:
        await fake_api.listen('fake')

    assert exc_info.value.instance == invalid_message['faked']
    assert not fake_operation.called


@pytest.mark.asyncio
async def test_should_not_listen_for_invalid_channel(
    fake_api, message, mocker
):
    with pytest.raises(asyncapi.exceptions.InvalidChannelError) as exc_info:
        await fake_api.listen('faked')

    assert exc_info.value.args == ('faked',)


@pytest.mark.asyncio
async def test_should_not_listen_for_operation_error(
    fake_api_no_operation, message, mocker
):
    with pytest.raises(
        asyncapi.exceptions.OperationIdNotFoundError
    ) as exc_info:
        await fake_api_no_operation.listen('fake')

    assert exc_info.value.args == ('fake_operation',)


@pytest.mark.asyncio
async def test_should_not_listen_for_operation_id_error(
    fake_api_no_operation_id, message, mocker
):
    with pytest.raises(
        asyncapi.exceptions.ChannelOperationNotFoundError
    ) as exc_info:
        await fake_api_no_operation_id.listen('fake')

    assert exc_info.value.args == ('fake',)