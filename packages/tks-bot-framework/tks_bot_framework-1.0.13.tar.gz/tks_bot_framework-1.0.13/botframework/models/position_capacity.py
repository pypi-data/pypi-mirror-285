from typing import List, Set, Optional
from famodels.direction import Direction
from sqlmodel import Field, SQLModel

class PositionCapacity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)             
    direction: Direction # long, short        
    take_profit: float
    alternative_take_profit: float
    stop_loss: float
    alternative_stop_loss: float

    def __getitem__(self, key):
        return self.__dict__[key]   