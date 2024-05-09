import azure.functions as func
import logging
from geopy.geocoders import Nominatim
import json
from datetime import datetime, date, timedelta
import chinese_calendar as calendar

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="zipcode")
def zipcode(req: func.HttpRequest) -> func.HttpResponse:
    # ... 保持不变 ...

@app.route(route="holiday")
def holiday(req: func.HttpRequest) -> func.HttpResponse:
    # ... 保持不变 ...

@app.route(route="holidays")
def holidays(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # 解析请求中的年份
        request_json = req.get_json()
        year_str = request_json['year']
        year = int(year_str)

        # 获取年份的第一天和最后一天
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

        # 用于存储节假日日期的列表
        holidays_list = []

        # 遍历整个年份的日期
        current_date = start_date
        while current_date <= end_date:
            # 检查当前日期是否为法定节假日
            if calendar.is_holiday(current_date):
                # 如果是节假日，则添加到列表中
                holidays_list.append(current_date.strftime('%Y, %m, %d').replace(", ", ","))
            # 移动到下一天
            current_date += timedelta(days=1)

        # 构建响应数据
        response_data = {
            'year': year,
            'holidays': holidays_list
        }

        # 返回 JSON 响应
        return func.HttpResponse(json.dumps(response_data), mimetype="application/json")
    except ValueError as e:
        return func.HttpResponse(str(e), status_code=400)
