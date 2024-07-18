import socket
from io import StringIO

import yaml

from src.apter import Apter


def create(config):
    return Apter(yaml.safe_load(StringIO(config)))


def test_dict_access():
    config = create("""
    simple: assignment
    """)
    assert config["simple"] == 'assignment'


def test_property_access():
    config = create("""
    simple: assignment
    """)
    assert config.simple == 'assignment'


def test_nested_mapping():
    config = create("""
    mapped:
        name1: amy
        name2: bob
        name3: carol
    """)
    assert config.mapped.name1 == 'amy'


def test_deep_nesting():
    config = create("""
    mapped:
        person:
            address: 1 True Way
    """)
    assert config.mapped.person.address == '1 True Way'


def test_interpolation():
    config = create("""
    mapped:
        person:
            address: 2 False Path
    primary:
        address: ${mapped.person.address}
    """)
    assert config.primary.address == '2 False Path'


def test_multi_reference_value():
    config = create("""
    mapped:
        person:
            name: Uly
            address: 3 Best Way
    primary:
        address: ${mapped.person.name} lives at ${mapped.person.address}
    """)
    assert config.primary.address == 'Uly lives at 3 Best Way'


def test_nested_reference():
    config = create("""
    base_dir: ./
    browser:
        base_dir: ${base_dir}browser/
        screenshot: ${browser.base_dir}screenshot.png
    """)
    assert config.browser.screenshot == './browser/screenshot.png'


def test_arbitrary_reference():
    config = create("""
    base_dir: ./
    browser:
        base_dir: ${base_dir}browser/
        screenshot: ${browser.base_dir}screenshot.png
    diagnostics:
        browser_screenshot: ${browser.screenshot}
    """)
    assert config.diagnostics.browser_screenshot == './browser/screenshot.png'


def test_list_reference():
    config = create("""
    base_dir: ./
    browser:
        base_dir: ${base_dir}browser/
        screenshot: ${browser.base_dir}screenshot.png
    directories:
        - ${base_dir}
        - ${browser.base_dir}
    """)
    assert config.directories == ['./', './browser/']


def test_lazy_referencing():
    config = create("""
    original: ./
    reference: ${original}subdirectory
    """)
    config.original = '/home/uly/'
    assert config.reference == '/home/uly/subdirectory'


def test_lazy_cross_referencing():
    config = create("""
    original: ./
    section:
        reference: ${original}subdirectory/
    addendum:
        subreference: ${section.reference}resubdir
    """)
    config.section.reference = '/home/uly/'
    assert config.addendum.subreference == '/home/uly/resubdir'


def test_add_new_mapping():
    config = create("""
    original: ./
    """)
    config.mapping = 'hippos'
    assert config.mapping == 'hippos'


def test_add_new_nested_mapping():
    config = create("""
    original: ./
    """)
    config.add_mapping('mapping.deep', 'hippos')
    assert config.mapping.deep == 'hippos'


def test_simple_merge():
    default_config = create("""
    env: system
    """)
    user_config = create("""
    env: user
    """)
    default_config.overlay(user_config)
    assert default_config.env == user_config.env


def test_merge_preserves_defaults():
    default_config = create("""
    env: system
    unmasked: true
    """)
    user_config = create("""
    env: user
    """)
    default_config.overlay(user_config)
    assert default_config.unmasked is True


def test_merge_map():
    default_config = create("""
    logging:
        level: info
    """)
    user_config = create("""
    logging:
        level: debug
    """)
    default_config.overlay(user_config)
    assert default_config.logging.level == 'debug'


def test_merge_map_preserves_defaults():
    default_config = create("""
    logging:
        level: info
        file: app.log
    """)
    user_config = create("""
    logging:
        level: debug
    """)
    default_config.overlay(user_config)
    assert default_config.logging.file == 'app.log'


def test_merge_list():
    default_config = create("""
    loggers:
        - file
    """)
    user_config = create("""
    loggers:
        - console
    """)
    default_config.overlay(user_config)
    assert default_config.loggers == ['console']


def test_merge_complex():
    default_config = create("""
    env: default
    working_dir: ./
    logging:
        console:
            format: (ts) [(level)] (msg)
            level: critical
        file:
            format: (ts) [(level)] (msg)
            level: debug
            path: ${working_dir}sense.log
    banking:
        login_url: https://wwws.bankinginstitution.net/login.event
        user_id: testacct@bankinginstitution.net
        capture: ~u ^https://wwws.bankinginstitution.net/app/getJsonData.*task=transactions
    browser:
        working_dir: ${working_dir}browser/
        screencap: ${browser.working_dir}most_recent.png
    diagnostics:
        base_dir: diagnostics/
        browser_screencap: ${browser.screencap}
    """)
    user_config = create("""
    env: tests
    logging:
        file:
            path: ${working_dir}tests.log
        console:
            level: debug
    mint:
        login_url: https://localhost:8888/login.event
        user_id: user
        capture: ~u ^http://localhost:8888/app/getJsonData.*task=transactions
    """)
    default_config.overlay(user_config)
    assert default_config.env == 'tests'
    assert default_config.logging.file.path == './tests.log'
    assert default_config.logging.console.level == 'debug'
    assert default_config.logging.console.format is not None


def test_support_default_value_on_missing_config():
    config = create("""
    original: ./
    """)
    assert config.get('unspecified', 5) == 5


def test_support_default_value_on_missing_nested_config():
    config = create("""
    original: ./
    """)
    assert config.get('nested.unspecified', 5) == 5


def test_blank_value_is_valid():
    config = create("""
    original: ./
    nested:
        unspecified:
    """)
    assert config.get('nested.unspecified', 5) is None


def test_can_get_from_absent_nested_element():
    config = create("""
    original: ./
    nested:
        unspecified:
    """)
    assert config.nested.get('count', 3) == 3


def test_can_get_from_nested_element():
    config = create("""
    original: ./
    nested:
        items: 30
    """)
    assert config.nested.get('items', 0) == 30


def test_can_get_programmatic_substitutions():
    config = create("""
    url: http://${ENV.hostname}/index.html
    """)
    assert config.url == 'http://{}/index.html'.format(socket.gethostname())
