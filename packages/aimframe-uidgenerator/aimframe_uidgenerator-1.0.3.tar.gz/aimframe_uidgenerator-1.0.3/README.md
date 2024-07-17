# **uidgenerator-snowflakeid**

根据经典的雪花id算法，实现python的本地ip地址滚动映射到5+5位centerid和worerid，并解决时钟回拨问题。

> [!IMPORTANT]
>
> 使用方法
>
> ```
> from aimframe_uidgenerator.uidgenerator.usnowflake import USnowflake
> 
> def snowflakeid():
>  snowflake = USnowflake.Default()
>  return snowflake.NextId()
> ```
>
> 

