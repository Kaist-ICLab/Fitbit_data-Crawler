import os
import json

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
    accounts_path = './accounts.csv'
    date_ = '2022-04-19' # 2022-04-19 ~ 2022-05-20
    check_file_path = f'./check-{date_}.txt'

    check_file = open(check_file_path, 'w')

    with open(accounts_path, 'r') as f:
        for line in f:
            email, _ = line.strip().split(',')
            user_id = email.split('@')[0].split('.')[1]
            filename = f'./data/{user_id}-{date_}.json'
            s = f"{user_id}:\t%sok" % ("" if is_ok(filename) else "not ")
            print(s)
            check_file.write(f"{s}\n")

    check_file.close()

