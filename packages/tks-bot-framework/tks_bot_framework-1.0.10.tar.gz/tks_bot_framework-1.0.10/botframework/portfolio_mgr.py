from botframework import botframework_utils
from tksessentials import utils
from botframework.trade_mgr import TradeMgr
from famodels.direction import Direction
from botframework.models.position_capacity import PositionCapacity
from argparse import ArgumentError
from cmath import log
from ctypes.wintypes import SHORT
from pickle import NONE
import logging
from datetime import datetime
from typing import List
from pandas import DataFrame

logger = logging.getLogger('app')


class PortfolioMgr:
    """Portfolio Manager."""

    def __init__(self) -> None:
        # We are nesting the middleware JSONStorage (file storage) within the SerializationMiddleware        
        self.positions_capacities: List[PositionCapacity] = []
        self.algo_cfg = utils.get_app_config()

    def get_position_capacities(self, reload=True) -> List[PositionCapacity]:
        """Returns position capacity of the algo_config file. Set False to avoid 'reloading' from file."""
        if reload == False and self.positions_capacities != []:
            return self.positions_capacities

        """This will load the positions capacity directly from the file."""
        position_capacity = self.algo_cfg["position_capacities"]
        loaded_position_capacities: List[PositionCapacity] = []
        
        for pos_cap in position_capacity:
            pc:PositionCapacity = PositionCapacity( id=pos_cap["position_capacity"]["id"], 
                direction=pos_cap["position_capacity"]["direction"],
                take_profit=pos_cap["position_capacity"]["take_profit"],
                alternative_take_profit=pos_cap["position_capacity"]["alternative_take_profit"],
                stop_loss=pos_cap["position_capacity"]["stop_loss"],
                alternative_stop_loss=pos_cap["position_capacity"]["alternative_stop_loss"]
                )
            PositionCapacity()
            loaded_position_capacities.append(pc)        
        return loaded_position_capacities
    
    def get_position_capacity(self, pos_idx:int) -> PositionCapacity:
        all_position_capacities = self.get_position_capacities()
        for p_c in all_position_capacities:
            if p_c.id == pos_idx:
                return p_c

    def get_directional_position_capacities(self, direction:Direction) -> List[PositionCapacity]:
        """Returns the List of PositionCapacities for the specified direction (long/short)."""
        allowed_directional_positions:List[PositionCapacity] = []
        position_capacities:List[PositionCapacity] = self.get_position_capacities()
        for pos in position_capacities:
            if pos.direction == direction.value: #short or long
                allowed_directional_positions.append(pos)

        return allowed_directional_positions

    async def get_a_free_position_capacity_for_buys(self, ksqldb_query_url, view_name, direction:Direction) -> PositionCapacity:        
        """This method can only be called if we want to open a position. That is 'side' equals 'buy'; buy-long or buy-short. We always close all positions if 'side' equals 'sell'. 
        So, it returns any free long/short position capacity - or - None if all are occupied. Provide the direction with either long or short."""

        free_directional_position_capacities = await self.get_free_position_capacities_for_buys(ksqldb_query_url, view_name, direction)

        if len(free_directional_position_capacities) > 0:
            logger.info(f"The chosen free position is {free_directional_position_capacities[0].id}.")
            return free_directional_position_capacities[0]
        else:
            return None

    async def get_free_position_capacities_for_buys(self, ksqldb_query_url, view_name, direction:Direction) -> List[PositionCapacity]:
        strategy_id = utils.get_application_name()
        trade_mgr = TradeMgr()
        """Returns all free position capacities for buys."""
        if direction == None:
            raise ArgumentError("Failed to get a free position capacity. The direction is not passed.")
        if direction != Direction.LONG and direction != Direction.SHORT:
            raise ArgumentError(f"Failed to get a free position capacity. The direction passed is not valid: {direction}")
        # Fetch all position capacities of this direction (long/short)
        directional_position_capacities:List[PositionCapacity] = self.get_directional_position_capacities(direction)
        logger.info(f"We have {len(directional_position_capacities)} {direction}-position-capacities.")
         # Fetch active trades, which is a list of pos_idx integers
        active_trades: List[int] = await trade_mgr.get_active_positions(ksqldb_query_url, view_name, direction)
        logger.info(f"Currently there are {len(active_trades)} locally-registered active trades.")
        # Determine free directional position capacities
        free_directional_position_capacities: List[PositionCapacity] = [
            dir_pos_cap for dir_pos_cap in directional_position_capacities
            if dir_pos_cap.id not in active_trades
        ]
        logger.info("The currently available free position capacities (where there is no active trade) are: ")
        for free_trade in free_directional_position_capacities:
            logger.info(free_trade.id)

        return free_directional_position_capacities

    async def get_position_size_in_percentage(self, direction:Direction) -> float:
        """Returns the position size (in percentage of the total available amount), based on how many entries per direction are allowed."""
        # Divide the total available amount (i.e. 100%) by the number of position-capacities of a direction (long/short). If there is 2 long and 2 short position capacities, then divide by 2.
        total_position_capacities = len(self.get_directional_position_capacities(direction))
        position_size_in_percentage = 100 / total_position_capacities
        return position_size_in_percentage

    async def calculate_take_profit_stop_loss(self, close, direction:Direction, pos_idx, atr=None, alternative_profit_loss:bool=None):
        #Check if take profit and stop loss are calculated by percentage or by atr.
        # Calculate the take profit and stop loss price.
        take_profit = self.get_position_capacity(pos_idx).take_profit
        stop_loss = self.get_position_capacity(pos_idx).stop_loss
        alternative_take_profit = self.get_position_capacity(pos_idx).alternative_take_profit
        alternative_stop_loss = self.get_position_capacity(pos_idx).alternative_stop_loss
        if self.algo_cfg["TP_SL_calculation"] == "percentage":
            if direction == Direction.LONG:
                if alternative_profit_loss == None:
                    take_profit_price = close * (1 + take_profit/100)
                    stop_loss_price = close * (1 - stop_loss/100)
                else:
                    take_profit_price = close * (1 + alternative_take_profit/100)
                    stop_loss_price = close * (1 - alternative_stop_loss/100)
            elif direction == Direction.SHORT:
                if alternative_profit_loss == None:
                    take_profit_price = close * (1 - take_profit/100)
                    stop_loss_price = close * (1 + stop_loss/100)
                else:
                    take_profit_price = close * (1 - alternative_take_profit/100)
                    stop_loss_price = close * (1 + alternative_stop_loss/100)
        elif self.algo_cfg["TP_SL_calculation"] == "atr":
            if direction == Direction.LONG:
                if alternative_profit_loss == None:
                    take_profit_price = close + take_profit*atr
                    stop_loss_price = close - stop_loss*atr
                else:
                    take_profit_price = close + alternative_take_profit*atr
                    stop_loss_price = close - alternative_stop_loss*atr
            elif direction == Direction.SHORT:
                if alternative_profit_loss == None:
                    take_profit_price = close - take_profit*atr
                    stop_loss_price = close + stop_loss*atr
                else:
                    take_profit_price = close - alternative_take_profit*atr
                    stop_loss_price = close + alternative_stop_loss*atr

        return take_profit_price, stop_loss_price

    async def check_for_position_closing(self, ksqldb_query_url, topic_name, view_name, pos_idx, close, high, low):
        # Fetch the last entry for the provided pos_idx in the data base.
        # Check wether the take profit or stop loss price was hit during the last interval.
        # Check wether the position closing was already confirmed by freya alpha (and the trade is already marked as 'closed').
        # If not, we mark the trade as 'selling' and wait for the confirmation, then we mark the trade as 'closed'.
        new_status_of_position = 'selling'
        trade_mgr = TradeMgr()
        trade_data = await trade_mgr.get_latest_trade_data_by_pos_idx(ksqldb_query_url, view_name, pos_idx)
        direction = trade_data[7]
        tp = trade_data[8]
        sl = trade_data[9]
        if direction == Direction.LONG and high >= tp:
            logger.info(f"TP for position {pos_idx} was reached during the last interval - marking trade in data base as closed.")
            await trade_mgr.create_additional_entry_for_pos_idx(ksqldb_query_url=ksqldb_query_url, topic_trade_name=topic_name, topic_trade_view=view_name, pos_idx=pos_idx, new_status_of_position=new_status_of_position, tp_sl_reached=True)
        elif direction == Direction.LONG and low <= sl:
            logger.info(f"SL for position {pos_idx} was reached during the last interval - marking trade in data base as closed.")
            await trade_mgr.create_additional_entry_for_pos_idx(ksqldb_query_url=ksqldb_query_url, topic_trade_name=topic_name, topic_trade_view=view_name, pos_idx=pos_idx, new_status_of_position=new_status_of_position, tp_sl_reached=True)
        elif direction == Direction.SHORT and low <= tp:
            logger.info(f"TP for position {pos_idx} was reached during the last interval - marking trade in data base as closed.")
            await trade_mgr.create_additional_entry_for_pos_idx(ksqldb_query_url=ksqldb_query_url, topic_trade_name=topic_name, topic_trade_view=view_name, pos_idx=pos_idx, new_status_of_position=new_status_of_position, tp_sl_reached=True)
        elif direction == Direction.SHORT and high >= sl:
            logger.info(f"SL for position {pos_idx} was reached during the last interval - marking trade in data base as closed.")
            await trade_mgr.create_additional_entry_for_pos_idx(ksqldb_query_url=ksqldb_query_url, topic_trade_name=topic_name, topic_trade_view=view_name, pos_idx=pos_idx, new_status_of_position=new_status_of_position, tp_sl_reached=True)
        else:
            logger.info(f"Neither TP nor SL for position {pos_idx} reached during the last interval.")