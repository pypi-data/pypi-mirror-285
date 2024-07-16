from pyqqq.utils.api_client import raise_for_status, send_request
from pyqqq.utils.logger import get_logger
import pyqqq.config as c

logger = get_logger("realtime")


def get_all_last_trades():
    """
    모든 종목의 최근 체결 정보를 반환합니다.

    Returns:
        list:
        - dict:
            - chetime (str): 체결시간
            - sign (str): 전일대비구분
            - change (int): 전일대비가격
            - drate (float): 전일대비등락율
            - price (int): 체결가
            - opentime (str): 시가시간
            - open (int): 시가
            - hightime (str): 고가시간
            - high (int): 고가
            - lowtime (str): 저가시간
            - low (int): 저가
            - cgubun (str): 체결구분
            - cvolume (int): 체결량
            - volume (int): 누적거래량
            - value (int): 누적거래대금(백만)
            - mdvolume (int): 매도체결수량
            - mdchecnt (int): 매도체결건수
            - msvolume (int): 매수체결수량
            - mschecnt (int): 매수체결건수
            - cpower (float): 체결강도
            - offerho (int): 매도호가
            - bidho (int): 매수호가
            - status (str): 장정보
            - jnilvolume (int): 전일동시간대거래량
            - shcode (str): 종목코드

    """

    r = send_request("GET", f"{c.PYQQQ_API_URL}/domestic-stock/trades")
    raise_for_status(r)

    data = r.json()
    result = [data[k] for k in data.keys()]

    return result
