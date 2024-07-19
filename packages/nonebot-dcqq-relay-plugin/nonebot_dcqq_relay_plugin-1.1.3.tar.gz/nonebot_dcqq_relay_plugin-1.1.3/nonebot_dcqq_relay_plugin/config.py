from nonebot import get_plugin_config
from typing import List, Optional
from pydantic import BaseModel

class Config(BaseModel):
  data_dir: Optional[str] = None
  discord_guild: int;
  discord_channel: int;
  onebot_channel: int;

  class Config:
      extra = "ignore";

plugin_config = get_plugin_config(Config)