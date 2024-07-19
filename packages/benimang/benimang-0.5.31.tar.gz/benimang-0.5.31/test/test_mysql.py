# import pytest
# from beni.bmysql import MysqlDb


# @pytest.mark.asyncio
# async def test():
#     DB = MysqlDb(
#         host='114.132.242.93',
#         port=3306,
#         user='admin',
#         password='mydb@@709394',
#         db='test',
#     )
#     async with DB.getCursor() as cursor:
#         result = await cursor.getValue(int, 'SELECT COUNT(*) FROM product WHERE (product_id, change_date) IN (%s, %s)', (1, '1970-01-01'), (2, '1970-01-01'))
#     assert result == 2
