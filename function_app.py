import azure.functions as func
import logging
from geopy.geocoders import Nominatim
import json
import chinese_calendar as cc
from datetime import datetime, date, timedelta

# 创建 FunctionApp 实例通常不是必需的，除非您有特殊的配置需求
app = func.FunctionApp()

@app.route(route="zipcode", methods=['GET'], auth_level=func.AuthLevel.ANONYMOUS)
def zipcode(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for zipcode.')

    # 尝试从查询参数或请求体中获取邮政编码
    zipcode = req.params.get('zipcode')
    if not zipcode:
        try:
            req_body = req.get_json()
            zipcode = req_body.get('zipcode')
        except ValueError:
            pass

    if zipcode:
        # 使用 geopy 获取位置详情
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.geocode(zipcode)

        if location:
            # 准备 JSON 响应
            response = {
                "location": location.address,
                "longitude": location.longitude,
                "latitude": location.latitude
            }
            return func.HttpResponse(json.dumps(response), mimetype="application/json")
        else:
            return func.HttpResponse(f"未找到邮政编码: {zipcode} 的位置", status_code=404)
    else:
        return func.HttpResponse(
            "请在查询字符串或请求体中提供邮政编码。",
            status_code=400
        )

@app.route(route="holiday", methods=['GET'], auth_level=func.AuthLevel.ANONYMOUS)
def holiday(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for holiday.')

    try:
        # 从 GET 数据中解析日期
        req_body = req.get_json()
        date_str = req_body.get('date')
        date_obj = datetime.strptime(date_str, '%Y%m%d').date()

        # 检查日期是否为中国的节假日或工作日
        is_holiday = cc.is_holiday(date_obj)
        is_workday = cc.is_workday(date_obj)

        # 准备响应数据
        response_data = {
            "CNholiday": is_holiday,
            "NonCNHoliday": not is_holiday,
            "CNworkingday": is_workday,
            "description": ""
        }

        # 如果是节假日，则获取节假日描述
        if is_holiday:
            _, holiday_name = cc.get_holiday_detail(date_obj)
            response_data['description'] = f"中国国家节假日: {holiday_name}"
        else:
            response_data['description'] = "非中国国家节假日"

        return func.HttpResponse(
            json.dumps(response_data),
            mimetype="application/json",
            status_code=200
        )
    except ValueError as e:
        return func.HttpResponse(
            str(e),
            status_code=400
        )
    except Exception as e:
        return func.HttpResponse(
            "处理请求时出错",
            status_code=500
        )
    
@app.route(route="holidays", methods=['GET'], auth_level=func.AuthLevel.ANONYMOUS)
def holidays(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for holidays.')

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
            if cc.is_holiday(current_date):
                # 如果是节假日，则添加到列表中
                holidays_list.append(current_date.strftime('%Y-%m-%d'))
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
    except Exception as e:
        return func.HttpResponse(
            "处理请求时出错",
            status_code=500
        )
