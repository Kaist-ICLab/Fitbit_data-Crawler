import hashlib
from datetime import datetime, timedelta
import json
from concurrent.futures import ThreadPoolExecutor
from retriever import FitbitDataRetriever
import time
import pickle
import os


def _get_data(
        _fitbit: FitbitDataRetriever,
        _access_token: str,
        _refresh_token: str,
        _user_id: str,
        _user: str,
        _start_date: str,
        _end_date: str,
        _email: str,
        _pw: str
):
    datetime_start = datetime.strptime(_start_date, '%Y-%m-%d')
    datetime_end = datetime.strptime(_end_date, '%Y-%m-%d')
    n_days = (datetime_end - datetime_start).days + 1

    for t in range(n_days):
        date = datetime_end - timedelta(days=t)
        str_date = date.strftime("%Y-%m-%d")
        print(f"-- {t+1} / {n_days}: {str_date}")

        filename = f'./alldata/{_user}-{str_date}.json'
        if os.path.isfile(filename):# and is_ok(filename):
            print(f"done. ({uuid})")
            continue

        try:
            access_token_, refresh_token_, result = _fitbit.retrieve(
                access_token=_access_token,
                refresh_token=_refresh_token,
                user_id=_user_id,
                date=str_date,
                email=_email,
                pw=_pw
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(e)
            continue
        alg = hashlib.md5()
        alg.update(_user.encode())
        result['pid'] = alg.hexdigest()
        print(f"-- Retrieved: {_user}-{str_date}")

        with open(f'./alldata/{_user}-{str_date}.json', 'w') as f_:
            json.dump(result, f_, indent=2)

        token_info_ = dict()
        if os.path.isfile(token_path):
            with open(token_path, 'rb') as f_:
                token_info_ = pickle.load(f_)

        token_info_[_email] = (access_token_, refresh_token_, user_id)

        with open(token_path, 'wb') as f_:
            pickle.dump(token_info_, f_)


def is_ok(f_name):
    if not os.path.isfile(f_name):
        return False
    with open(f_name, 'r') as f_:
        content = json.load(f_)
        minLightAct = int(content.get("minutesLightlyActive").strip().strip('"'))
        minFairlyAct = int(content.get("minutesFairlyActive").strip().strip('"'))
        minVeryAct = int(content.get("minutesVeryActive").strip().strip('"'))
        actCal = int(content.get("activityCalories").strip().strip('"'))
        return minLightAct > 0 or minFairlyAct > 0 or minVeryAct > 0 or actCal > 0


if __name__ == '__main__':
    token_path = './token_info.pkl'
    accounts_path = './accounts.tsv'
    s_date_ = '2022-04-19' # 2020-02-05 ~ 2020-03-29
    e_date_ = '2022-05-20'
    debug_flag = True
    # check_file_path = f'./check-{e_date_}.txt'
    secret_file_path = './secret.txt'

    with open(secret_file_path, 'r') as f:
        client_id_ = f.readline().strip()
        client_secret_ = f.readline().strip()

    retriever = FitbitDataRetriever(
        selenium_path='./chromedriver.exe',
        client_id=client_id_,
        client_secret=client_secret_,
        callback='https://ic.kaist.ac.kr/fitbit',
        call_interval=15
    )

    email_pw = {}

    with open(accounts_path, 'r') as f:
        for line in f:
            id0, pw0 = line.strip().split()
            email_pw[id0] = pw0

    global token_info
    token_info = dict()
    if os.path.isfile(token_path):
        with open(token_path, 'rb') as f:
            token_info = pickle.load(f)

    executor = ThreadPoolExecutor(max_workers=8)

    for (email, pw) in email_pw.items():
        try:
            uuid = email.split("@")[0].split(".")[1]
            filename = f'./alldata/{uuid}-{e_date_}.json'
            
            if token_info.get(email):
                access_token, refresh_token, user_id = token_info.get(email)
            else:
                access_token, refresh_token, user_id = retriever.authorize(
                    email=email,
                    password=pw
                )
                token_info[email] = (access_token, refresh_token, user_id)

            if debug_flag:
                print(f"-- access_token: {access_token}")
                print(f"-- refresh_token: {refresh_token}")
                print(f"-- user_id: {user_id}")

            with open(token_path, 'wb') as f:
                pickle.dump(token_info, f)

            executor.submit(_get_data,
                            retriever,
                            access_token, refresh_token,
                            user_id, uuid,
                            s_date_, e_date_,
                            email, pw
                            )

            time.sleep(600)

        except Exception:
            import traceback
            traceback.print_exc()
            print(f'[ERROR] {email}')

    executor.shutdown(True)