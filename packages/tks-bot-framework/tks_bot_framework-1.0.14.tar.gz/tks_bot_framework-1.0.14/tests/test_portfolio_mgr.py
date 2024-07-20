from datetime import datetime
from botframework.portfolio_mgr import PortfolioMgr
from botframework.trade_mgr import TradeMgr
from famodels.direction import Direction
from botframework.models.position_capacity import PositionCapacity
from botframework import botframework_utils
from tksessentials import utils
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path
import pytest
from pytest import approx
import yaml
from typing import List

@pytest.fixture(autouse=True)
def insert_test_data(mocker):
    print("Test Fixture up")
    # Patch the entire app_config.yaml
    path = Path(__file__).parent.parent.absolute().joinpath("tests/app_config.yaml")
    with open(path, 'r') as stream:
        try:
            algo_config=yaml.safe_load(stream)
            print(algo_config)
        except yaml.YAMLError as exc:
            print(exc)
    mocker.patch("tksessentials.utils.get_app_config", return_value=algo_config)
    yield # this is where the testing happens

def test_get_exchange():
    algo_cft = utils.get_app_config()
    assert algo_cft['exchange'] == 'BINANCE'

def test_get_market():
    algo_cft = utils.get_app_config()
    assert algo_cft['market'] == 'ETH-USDT'

def test_get_position_capacities():
    position_capacities = PortfolioMgr().get_position_capacities()
    assert position_capacities[0]['id'] == 0
    assert len(position_capacities) == 3

def test_get_position_capacity():
    p_c = PortfolioMgr().get_position_capacity(2)
    assert p_c['id'] == 2

@pytest.fixture
def mock_get_position_capacities(mocker):
    mocker.patch('botframework.portfolio_mgr.PortfolioMgr.get_position_capacities', return_value=[
        PositionCapacity(id=0, direction='long', take_profit=2, alternative_take_profit=None, stop_loss=2, alternative_stop_loss=None),
        PositionCapacity(id=1, direction='long', take_profit=2, alternative_take_profit=None, stop_loss=2, alternative_stop_loss=None),
        PositionCapacity(id=2, direction='short', take_profit=6, alternative_take_profit=None, stop_loss=7, alternative_stop_loss=None)
    ])

@pytest.mark.parametrize("direction, expected_ids", [
    (Direction.LONG, [0, 1]),
    (Direction.SHORT, [2])
])
def test_get_directional_position_capacities(mock_get_position_capacities, direction, expected_ids):
    pos_caps = PortfolioMgr().get_directional_position_capacities(direction)
    actual_ids = [pos.id for pos in pos_caps]
    assert actual_ids == expected_ids
    assert len(pos_caps) == len(expected_ids)

@pytest.fixture
def mock_get_position_capacities(mocker):
    mocker.patch('botframework.portfolio_mgr.PortfolioMgr.get_position_capacities', return_value=[
        PositionCapacity(id=0, direction='long', take_profit=2, alternative_take_profit=None, stop_loss=2, alternative_stop_loss=None),
        PositionCapacity(id=1, direction='long', take_profit=2, alternative_take_profit=None, stop_loss=2, alternative_stop_loss=None),
        PositionCapacity(id=2, direction='short', take_profit=6, alternative_take_profit=None, stop_loss=7, alternative_stop_loss=None)
    ])

@pytest.mark.asyncio
@patch('botframework.trade_mgr.TradeMgr.get_active_positions', new_callable=AsyncMock)
async def test_get_free_position_capacities_for_buys(mock_get_active_positions, mock_get_position_capacities):
    # Arrange.
    mock_get_active_positions.return_value = [0]
    portfolio_mgr = PortfolioMgr()

    # Act.
    free_positions = await portfolio_mgr.get_free_position_capacities_for_buys(
        "http://localhost:8088/query-stream", "mock_view", Direction.LONG
    )
    # Assert.
    assert len(free_positions) == 1
    assert free_positions[0].id == 1

@pytest.mark.asyncio
@patch('botframework.trade_mgr.TradeMgr.get_active_positions', new_callable=AsyncMock)
async def test_get_free_position_capacities_for_buys_short(mock_get_active_positions, mock_get_position_capacities):
    # Arrange.
    mock_get_active_positions.return_value = []
    portfolio_mgr = PortfolioMgr()
    # Act.
    free_positions = await portfolio_mgr.get_free_position_capacities_for_buys(
        "http://localhost:8088/query-stream", "mock_view", Direction.SHORT
    )
    # Assert.
    assert len(free_positions) == 1
    assert free_positions[0].id == 2

@pytest.mark.asyncio
@patch('botframework.portfolio_mgr.PortfolioMgr.get_free_position_capacities_for_buys', new_callable=AsyncMock)
async def test_get_a_free_position_capacity_for_buys(mock_get_free_position_capacities_for_buys):
    # Arrange.
    mock_get_free_position_capacities_for_buys.return_value = [
        PositionCapacity(id=0, direction='long', take_profit=2, alternative_take_profit=None, stop_loss=2, alternative_stop_loss=None)
    ]
    portfolio_mgr = PortfolioMgr()
    # Act.
    free_position = await portfolio_mgr.get_a_free_position_capacity_for_buys(
        "http://localhost:8088/query-stream", "mock_view", Direction.LONG
    )
    # Assert.
    assert free_position is not None
    assert free_position.id == 0

@pytest.mark.asyncio
@patch('botframework.portfolio_mgr.PortfolioMgr.get_free_position_capacities_for_buys', new_callable=AsyncMock)
async def test_get_a_free_position_capacity_for_buys_none(mock_get_free_position_capacities_for_buys):
    # Arrange.
    mock_get_free_position_capacities_for_buys.return_value = []
    portfolio_mgr = PortfolioMgr()
    # Act.
    free_position = await portfolio_mgr.get_a_free_position_capacity_for_buys(
        "http://localhost:8088/query-stream", "mock_view", Direction.LONG
    )
    # Assert.
    assert free_position is None

@pytest.mark.asyncio
@pytest.mark.parametrize("direction, expected_percentage", [
    (Direction.LONG, 50),
    (Direction.SHORT, 100)
])
async def test_get_position_size_in_percentage(direction, expected_percentage):
    # Arrange and Act.
    position_size_in_percentage = await PortfolioMgr().get_position_size_in_percentage(direction)
    # Assert.
    assert position_size_in_percentage == expected_percentage

@pytest.mark.asyncio
@pytest.mark.parametrize("tp_sl_calculation, atr, expected_tp, expected_sl, expected_tp_alt, expected_sl_alt", [
    ("percentage", None, 110, 95, 115, 93),
    ("atr", 2, 120, 90, 130, 86)
])
@patch('botframework.portfolio_mgr.PortfolioMgr.get_position_capacity')
async def test_calculate_take_profit_stop_loss(mock_get_position_capacity, tp_sl_calculation, atr, expected_tp, expected_sl, expected_tp_alt, expected_sl_alt):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    portfolio_mgr.algo_cfg = {"TP_SL_calculation": tp_sl_calculation}
    mock_position_capacity = MagicMock()
    mock_position_capacity.take_profit = 10
    mock_position_capacity.stop_loss = 5
    mock_position_capacity.alternative_take_profit = 15
    mock_position_capacity.alternative_stop_loss = 7
    mock_get_position_capacity.return_value = mock_position_capacity
    close_price = 100
    pos_idx = 0
    # Act.
    tp_price, sl_price = await portfolio_mgr.calculate_take_profit_stop_loss(close_price, Direction.LONG, pos_idx, atr=atr)
    tp_price_alt, sl_price_alt = await portfolio_mgr.calculate_take_profit_stop_loss(close_price, Direction.LONG, pos_idx, atr=atr, alternative_profit_loss=True)
    # Assert.
    assert tp_price == pytest.approx(expected_tp, rel=1e-9)
    assert sl_price == pytest.approx(expected_sl, rel=1e-9)
    assert tp_price_alt == pytest.approx(expected_tp_alt, rel=1e-9)
    assert sl_price_alt == pytest.approx(expected_sl_alt, rel=1e-9)

@pytest.mark.asyncio
@patch('botframework.trade_mgr.TradeMgr.get_latest_trade_data_by_pos_idx', new_callable=AsyncMock)
@patch('botframework.trade_mgr.TradeMgr.create_additional_entry_for_pos_idx', new_callable=AsyncMock)
async def test_check_for_position_closing_tp_long(mock_create_entry, mock_get_latest_trade_data):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    mock_get_latest_trade_data.return_value = [
        None, None, None, None, None, None, None, Direction.LONG, 110, 95
    ]
    ksqldb_query_url = "http://localhost:8088/query"
    topic_name = "mock_topic"
    view_name = "mock_view"
    pos_idx = 0
    close = 100
    high = 111
    low = 90
    # Act.
    await portfolio_mgr.check_for_position_closing(ksqldb_query_url, topic_name, view_name, pos_idx, close, high, low)
    # Assert.
    mock_create_entry.assert_called_once_with(
        ksqldb_query_url=ksqldb_query_url,
        topic_trade_name=topic_name,
        topic_trade_view=view_name,
        pos_idx=pos_idx,
        new_status_of_position='selling',
        tp_sl_reached=True
    )

@pytest.mark.asyncio
@patch('botframework.trade_mgr.TradeMgr.get_latest_trade_data_by_pos_idx', new_callable=AsyncMock)
@patch('botframework.trade_mgr.TradeMgr.create_additional_entry_for_pos_idx', new_callable=AsyncMock)
async def test_check_for_position_closing_sl_long(mock_create_entry, mock_get_latest_trade_data):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    mock_get_latest_trade_data.return_value = [
        None, None, None, None, None, None, None, Direction.LONG, 110, 95
    ]
    ksqldb_query_url = "http://localhost:8088/query"
    topic_name = "mock_topic"
    view_name = "mock_view"
    pos_idx = 0
    close = 100
    high = 105
    low = 94
    # Act.
    await portfolio_mgr.check_for_position_closing(ksqldb_query_url, topic_name, view_name, pos_idx, close, high, low)
    # Assert.
    mock_create_entry.assert_called_once_with(
        ksqldb_query_url=ksqldb_query_url,
        topic_trade_name=topic_name,
        topic_trade_view=view_name,
        pos_idx=pos_idx,
        new_status_of_position='selling',
        tp_sl_reached=True
    )

@pytest.mark.asyncio
@patch('botframework.trade_mgr.TradeMgr.get_latest_trade_data_by_pos_idx', new_callable=AsyncMock)
@patch('botframework.trade_mgr.TradeMgr.create_additional_entry_for_pos_idx', new_callable=AsyncMock)
async def test_check_for_position_closing_tp_short(mock_create_entry, mock_get_latest_trade_data):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    mock_get_latest_trade_data.return_value = [
        None, None, None, None, None, None, None, Direction.SHORT, 90, 105
    ]
    ksqldb_query_url = "http://localhost:8088/query"
    topic_name = "mock_topic"
    view_name = "mock_view"
    pos_idx = 0
    close = 100
    high = 95
    low = 89
    # Act.
    await portfolio_mgr.check_for_position_closing(ksqldb_query_url, topic_name, view_name, pos_idx, close, high, low)
    # Assert.
    mock_create_entry.assert_called_once_with(
        ksqldb_query_url=ksqldb_query_url,
        topic_trade_name=topic_name,
        topic_trade_view=view_name,
        pos_idx=pos_idx,
        new_status_of_position='selling',
        tp_sl_reached=True
    )

@pytest.mark.asyncio
@patch('botframework.trade_mgr.TradeMgr.get_latest_trade_data_by_pos_idx', new_callable=AsyncMock)
@patch('botframework.trade_mgr.TradeMgr.create_additional_entry_for_pos_idx', new_callable=AsyncMock)
async def test_check_for_position_closing_sl_short(mock_create_entry, mock_get_latest_trade_data):
    # Arrange.
    portfolio_mgr = PortfolioMgr()
    mock_get_latest_trade_data.return_value = [
        None, None, None, None, None, None, None, Direction.SHORT, 90, 105
    ]
    ksqldb_query_url = "http://localhost:8088/query"
    topic_name = "mock_topic"
    view_name = "mock_view"
    pos_idx = 0
    close = 100
    high = 106
    low = 100
    # Act.
    await portfolio_mgr.check_for_position_closing(ksqldb_query_url, topic_name, view_name, pos_idx, close, high, low)
    # Assert.
    mock_create_entry.assert_called_once_with(
        ksqldb_query_url=ksqldb_query_url,
        topic_trade_name=topic_name,
        topic_trade_view=view_name,
        pos_idx=pos_idx,
        new_status_of_position='selling',
        tp_sl_reached=True
    )