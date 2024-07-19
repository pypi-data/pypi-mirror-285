from typing import cast
import pytest

from idac_sdk import IDACRequestSync, IDACControllerSync, IDACAuthType, IDACRequestType, SessionData
from idac_sdk.errors import SessionDataFileNotFoundError

from xml.parsers.expat import ExpatError

longrun = pytest.mark.skipif("not config.getoption('longrun')")


@pytest.fixture(scope="session")
def test_dev_controller():
    return IDACControllerSync(auth_type=IDACAuthType.NONE)


@pytest.mark.parametrize(
    "session_xml_path, initial_data, test_props",
    [
        (False, {"location": "test.location"}, None),
        (
            "good_session.xml",
            {"recipeName": "nop_v1"},
            {"datacenter": "LON", "id": "551495"},
        ),
    ],
)
def test_session_data_ok(test_data_path, session_xml_path, initial_data, test_props):
    if session_xml_path:
        file = f"{test_data_path}/{session_xml_path}"
    else:
        file = session_xml_path

    sd = SessionData(session_xml_path=file, initial_data=initial_data)
    assert isinstance(sd, SessionData)
    if isinstance(initial_data, dict):
        for k, v in initial_data.items():
            assert sd.has(k), f"Prop {k} not set on SessionData"
            assert sd.get(k) == v, f"Value of prop {k} is different"

    if isinstance(test_props, dict):
        for k, v in test_props.items():
            assert sd.has(k), f"Prop {k} not set on SessionData"
            assert sd.get(k) == v, f"Value of prop {k} is different"


@pytest.mark.parametrize(
    "session_xml_path, initial_data, expected",
    [
        ("bad_session.xml", None, ExpatError),
        ("non_existent.xml", None, SessionDataFileNotFoundError),
    ],
)
def test_session_data_error(test_data_path, session_xml_path, initial_data, expected):
    if session_xml_path:
        file = f"{test_data_path}/{session_xml_path}"
    else:
        file = session_xml_path

    with pytest.raises(expected):
        sd = SessionData(session_xml_path=file, initial_data=initial_data)
        assert isinstance(sd, SessionData)


def test_empty_request():
    p = IDACRequestSync(session_data=SessionData(session_xml_path=False))
    assert isinstance(p, IDACRequestSync)


@pytest.mark.parametrize(
    "session_xml_path, initial_data, request_type",
    [
        pytest.param(
            False,
            {"recipeName": "nop-v1", "recipePath": "common/", "owner": "sdk_test"},
            IDACRequestType.SIMPLE,
            marks=pytest.mark.dependency(name="test_recipe_1"),
        ),
        pytest.param(
            False,
            {
                "recipeName": "hello-world",
                "recipePath": "common/",
                "owner": "sdk_test",
                "datacenter": "lon",
            },
            IDACRequestType.STATELESS,
            marks=pytest.mark.dependency(name="test_recipe_2"),
        ),
    ],
)
def test_recipe(
    request, test_data_path, test_dev_controller, session_xml_path, initial_data, request_type
):
    if session_xml_path:
        file = f"{test_data_path}/{session_xml_path}"
    else:
        file = session_xml_path

    sd = SessionData(initial_data=initial_data, session_xml_path=file)
    req = IDACRequestSync(session_data=sd, controller=test_dev_controller)

    state, redirect = req.create(request_type=request_type)
    assert state.request and state.request.uuid
    request.config.cache.set(f"created_uuid_{sd.get('recipeName')}", state.request.uuid)
    request.config.cache.set(f"redirect_{sd.get('recipeName')}", redirect)
    assert True


@pytest.mark.dependency(depends=["test_recipe_1"])
def test_get_state(request, test_dev_controller):
    req = IDACRequestSync(
        uuid=request.config.cache.get("created_uuid_nop-v1", None),
        controller=test_dev_controller,
        session_data=SessionData(session_xml_path=False),
    )

    state = req.get_state()
    assert state.status


@pytest.mark.dependency(depends=["test_recipe_1"])
def test_extend(request, test_dev_controller):
    req = IDACRequestSync(
        uuid=request.config.cache.get("created_uuid_nop-v1", None),
        controller=test_dev_controller,
        session_data=SessionData(session_xml_path=False),
    )

    req.extend(60)
    assert True


@pytest.mark.dependency(depends=["test_recipe_1"])
def test_cleanup(request, test_dev_controller):
    req = IDACRequestSync(
        uuid=request.config.cache.get("created_uuid_nop-v1", None),
        controller=test_dev_controller,
        session_data=SessionData(session_xml_path=False),
    )

    req.cleanup()
    assert True


@pytest.mark.dependency(depends=["test_recipe_2"])
def test_redirection(request):
    redirect = request.config.cache.get("redirect_hello-world", None)
    uuid = request.config.cache.get("created_uuid_hello-world", None)
    assert isinstance(redirect, str)
    assert uuid in redirect


@pytest.mark.dependency(depends=["test_recipe_2", "test_redirection"])
def test_cleanup_hello_world(request, test_dev_controller):
    req = IDACRequestSync(
        uuid=request.config.cache.get("created_uuid_hello-world", None),
        controller=test_dev_controller,
        session_data=SessionData(session_xml_path=False),
    )

    st = req.wait_for_status(wanted_state=["executed"], max_attempts=5, interval=5)
    assert st and st.status == "executed"

    req.cleanup()
    assert True


@longrun
@pytest.mark.parametrize(
    "session_xml_path, initial_data, request_type, amount",
    [
        pytest.param(
            False,
            {"recipeName": "nop-v1", "recipePath": "common/", "owner": "sdk_test"},
            IDACRequestType.SIMPLE,
            10,
            marks=pytest.mark.dependency(name="test_multiple_1"),
        ),
    ],
)
def test_multiple(
    request,
    test_data_path,
    test_dev_controller,
    session_xml_path,
    initial_data,
    request_type,
    amount,
):
    if session_xml_path:
        file = f"{test_data_path}/{session_xml_path}"
    else:
        file = session_xml_path

    request.config.cache.set(f"multi_amount", amount)

    for idx in range(0, amount):
        cast(dict, initial_data).update({"demo": f"Multi test, request #{idx}"})
        sd = SessionData(initial_data=initial_data, session_xml_path=file)
        req = IDACRequestSync(session_data=sd, controller=test_dev_controller)

        state, redirect = req.create(request_type=request_type)
        assert state.request and state.request.uuid
        request.config.cache.set(f"created_uuid_{idx}_{sd.get('recipeName')}", state.request.uuid)


@longrun
@pytest.mark.dependency(depends=["test_multiple_1"])
def test_multi_awaits(request, test_dev_controller):
    amount = request.config.cache.get("multi_amount", None)

    for idx in range(0, amount):
        uu = request.config.cache.get(f"created_uuid_{idx}_nop-v1", None)
        assert uu
        req = IDACRequestSync(
            uuid=uu,
            controller=test_dev_controller,
            session_data=SessionData(session_xml_path=False),
        )

        st = req.wait_for_status(wanted_state=["executed"], max_attempts=5, interval=5)
        assert st and st.status == "executed"
