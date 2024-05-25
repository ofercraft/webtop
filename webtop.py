import requests

# -- coding: utf-8 --
#!/usr/bin/python
from datetime import datetime, timezone, timedelta, date
import random
import math
import requests
import json
import time
import certifi
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()


cookies = ""
student_id = ""

def get_cookies():
    global cookies
    HOST = "https://webtop.smartschool.co.il/"
    r = requests.get(HOST, verify=False)
    return r.cookies
def get_cookies2():
    global cookies
    HOST = "https://webtop.smartschool.co.il/"
    r1 = requests.get(HOST, verify=False)

    HOST = "https://webtop.smartschool.co.il/account/login?stateUrl=U2FsdGVkX1%2BpSRA%2BLzZGFHzt6Vw8IU%2FuAJB5TTZmqO8%3D"
    r2 = requests.get(HOST, cookies=r1.cookies, verify=False)

    return r2.cookies

def main(username: str, password: str, display: bool = False):
    cookies = get_cookies()
    print(username, password)
    data = encrypt_string_to_server(f"{username}0")

    url = "https://webtopserver.smartschool.co.il/server/api/user/LoginByUserNameAndPassword"
    # data = {
    #     "Data": "NU4M8WVf+/5Uuy1lLs35u6fJhxjME9AGN/KbwlbSoUIUZLsSh6DO3MYfQBtwpWkg",
    #     "UserName": "AHYC52",0
    #     "Password": "Neches90210",
    # }
    data = {
        "Data": data, #also: qdMHqjQ5doKkcPsCzdCYzV1k139sAmI/1CBYNTs4+lhO7g6KEnJGXFnB6Z3/eNwv
        "UserName": username,
        "Password": password,
        "deviceDataJson": '{"isMobile":true,"isTablet":false,"isDesktop":false,"getDeviceType":"Mobile","os":"Android","osVersion":"6.0","browser":"Chrome","browserVersion":"122.0.0.0","browserMajorVersion":122,"screen_resolution":"1232 x 840","cookies":true,"userAgent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"}'

    }
    response = requests.post(url, json=data, cookies=cookies, verify=False)
    if display:
        print(response.json())
    student_id=response.json()["data"]["userId"]
    print(student_id)
    # url = "https://webtopserver.smartschool.co.il/server/api/dashboard/GetHomeWork"
    # data = {
    # "id": "PY0anAW1Gtn3RWi/7YyBjn51E+zNJ35ZO1wnEAb8/V4=",
    # "ClassCode": 7,
    # "ClassNumber": 6
    # }
    #
    # response = requests.post(url, json=data, cookies=response.cookies, verify=False)
    # print(response.json())
    #
    cookies = response.cookies
    return cookies, student_id, response.json()
def check_account(username: str, password: str, display: bool = False):
    cookies = get_cookies()
    data = encrypt_string_to_server(username + "0")

    url = "https://webtopserver.smartschool.co.il/server/api/user/LoginByUserNameAndPassword"

    data = {
        "Data": data,
        "UserName": username,
        "Password": password,
        "deviceDataJson": '{"isMobile":true,"isTablet":false,"isDesktop":false,"getDeviceType":"Mobile","os":"Android","osVersion":"6.0","browser":"Chrome","browserVersion":"122.0.0.0","browserMajorVersion":122,"screen_resolution":"1232 x 840","cookies":true,"userAgent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"}'

    }
    response = requests.post(url, json=data, cookies=cookies, verify=False)
    try:
        return response.json()["status"]
    except:
        return False

def main_tamar():
    cookies = get_cookies2()
    print(cookies)
    url = "https://webtopserver.smartschool.co.il/server/api/user/LoginMoe"
    # data = {
    #     "Data": "NU4M8WVf+/5Uuy1lLs35u6fJhxjME9AGN/KbwlbSoUIUZLsSh6DO3MYfQBtwpWkg",
    #     "UserName": "AHYC52",
    #     "Password": "Neches90210",
    # }
    data = {
    "rememberMe": "",
    "key": "ym25gEIyClDJUUfbIgpqsc1n/YYmO7uaZbJKK6A5qYlpP8iq7PK5V15znP6gvdOSwk P eRuBKgcCsn4wxJ5aHaBs/8DhtPlQlL/b1zSJaeb8 yR8t20uRWv/rDGhkl/sdfyB66mFGkWnOkURbHEHA==",

}
    response = requests.post(url, json=data, cookies=cookies, verify=False)
    print(response.json())
    #student_id=response.json()["data"]["userId"]

    # url = "https://webtopserver.smartschool.co.il/server/api/dashboard/GetHomeWork"
    # data = {
    # "id": "PY0anAW1Gtn3RWi/7YyBjn51E+zNJ35ZO1wnEAb8/V4=",
    # "ClassCode": 7,
    # "ClassNumber": 6
    # }
    #
    # response = requests.post(url, json=data, cookies=response.cookies, verify=False)
    # print(response.json())
    #
    cookies = response.cookies
    return cookies, student_id


def get_messages(cookies, student_id=None):
    url = "https://webtopserver.smartschool.co.il/server/api/messageBox/GetMessagesInbox"
    data = {
        "PageId": 1,
        "LabelId": 0,
        "SearchQuery": "",
    }

    response = requests.post(url, json=data, cookies=cookies, verify=False)
    #print(response.json())

    for message in response.json()["data"]:
        #print(message)
        url = "https://webtopserver.smartschool.co.il/server/api/messageBox/GetMessagesInboxData"
        data = {
            "MessageId": message['messageId'],
            "FilterId": 0,
            "IsInbox": True
        }

        response = requests.post(url, json=data, cookies=cookies, verify=False)
        print(f"{message['student_F_name']} {message['student_L_name']}: {message['subject']}")
        soup = BeautifulSoup(response.json()["data"]["messageData"]["messageContent"], "lxml")
        text = soup.get_text().replace("\n\n\n\n", "\n").replace("\n\n\n", "\n").replace("\n\n", "\n")
        print(text)


def lesson_events(cookies, student_id):
    url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilDiciplineEvents"
    data = {
  "studentID": student_id,
  "moduleID": 11
}
    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)

    #print(response.json())
    data = response.json()["data"]

    current_type = ""
    events = {}
    for item in data["diciplineEvents"]:
        #print(item)
        if item["eventType"]!=current_type:
            current_type = item["eventType"]
            events[item["eventType"]]=[{"type": item["eventType"], "date": item["eventDate"], "subject": item["subjectName"]}]
        if item["eventType"] in events:
            events[item["eventType"]].append(
                {"type": item["eventType"], "date": item["eventDate"], "subject": item["subjectName"]})
        else:
            events[item["eventType"]]=[{"type": item["eventType"], "date": item["eventDate"], "subject": item["subjectName"]}]
    return events

def get_schedule(cookies):
    url = "https://webtopserver.smartschool.co.il/server/api/shotef/ShotefSchedualeData"
    data = {
    "institutionCode": 415232,
    "selectedValue": "7|6",
    "typeView": 2
        }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    #print(response.json()["data"])
    for day in response.json()["data"]:
        print(str(day["dayIndex"]) + ": ", end="")
        for hour in day["hoursData"]:
            #print(hour)
            if hour["scheduale"]:
                print(hour["scheduale"][0]["subject"], end=", ")
                if hour["scheduale"][0]["changes"]:
                    print(hour["scheduale"][0]["changes"][0]["type"], end=", ")

        print()

def get_print(cookies):
    url = "https://webtopserver.smartschool.co.il/server/api/pdf/generate"
    data = {
    "exportToPdf": True,
    "fileName": "SchedualeView.pdf",
    "maxPages": 20,
    "path": "Timetable_Changes&tabIndex=1&selectedItem=7|6&selectedType=2",
    "skipPage1": False,
    "url": "https://webtop.smartschool.co.il"
        }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    #print(response.content)

    pdf_data = b''+response.content  # Your PDF binary data goes here

    with open('output.pdf', 'wb') as file:
        file.write(pdf_data)

    import webbrowser
    webbrowser.open("output.pdf")

def check_token(cookies):
    url = "https://webtopserver.smartschool.co.il/server/api/dashboard/CheckToken"
    data = {
    "studentID": student_id,
    "moduleID": 11
        }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    print(response.json())

def get_changes(cookies, student_id, grade="7|6"):
    url = "https://webtopserver.smartschool.co.il/server/api/shotef/ShotefSchedualeData"
    data = {
    "institutionCode": 444349,
    "selectedValue": grade,
    "typeView": 2
        }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    #print(response.json()["data"])
    print((datetime.now().isoweekday()+1)%7-1)
    scheduale= {}
    for i in response.json()["data"][(datetime.now().isoweekday()+1)%7-1]["hoursData"]:
        if i["scheduale"] != []:
            print("hour " + str(i["hour"]) + ": " + str(i["scheduale"][0]["subject"]))
            print(i["hour"])
            scheduale[i["hour"]]=i["scheduale"][0]["subject"]
    print(scheduale)
    url = "https://webtopserver.smartschool.co.il/server/api/shotef/ChangesAndMessagesData"
    data = {
    "institutionCode": 444349,
    "selectedValue": grade,
    "typeView": 2
        }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    for item in response.json()["data"]["changes"]:
        print("hour " + str(item["hour"]) + ": ", end=" ")
        if item["content"]=="מילוי מקום":
            print('מילוי מקום ע"י ' + item["privateName"] + " " + item["lastName"])
            scheduale[item["hour"]] += " (" + ' מילוי מקום - ' + item["privateName"] + " " + item["lastName"] + " )"
        elif item["content"]=="ביטול שיעור":
            print("בוטל")
            scheduale[item["hour"]] += " ( בוטל )"
        elif item["content"]=="הזזת שיעור":
            scheduale[item["hour"]] += f"(בוטל?)"

        else:
            print(item)
    scheduale_str = "סדר יום מעודכן:\n"
    for item in scheduale:
        print(scheduale[item])
        scheduale_str+=f"{item}: {scheduale[item]}\n"
    print(scheduale)
    scheduale_str = scheduale_str.replace(" ", "+")[:-1]
    #requests.post(f"https://api.callmebot.com/whatsapp.php?phone=972584004492&text={scheduale_str}&apikey=2105667")

def get_grades(cookies, student_id, period = "b", display: bool = False):
    url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilGrades"
    periodID = 1102
    if period == "a":
        periodID = 1103
    data = {
    "studyYear": date.today().year,
    "moduleID": 1,
    "periodID": periodID,
    "studentID": student_id,

        }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    #print(response.json()["data"])

    grades={}
    for i in response.json()["data"]:
        if i["grade"] is not None:
            if display:
                print(i["subject"] + " | " + i["title"] + " | " + str(i["grade"]))
            if i["subject"] not in grades:
                grades[i["subject"]] = {}
            grades[i["subject"]][i["title"]]= [i["grade"], i["weight"]]

    if display:
        print(grades)
    return grades
def get_grades2(cookies):
    url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilGrades"
    data = {
    "studyYear": date.today().year,
    "moduleID": 1,
    "periodID": 1102,
    "studentID": student_id,

        }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    grades=[]
    for i in response.json()["data"]:
        if i["grade"] is not None:

            grades.append({  f" {i['subject']} | {i['title']}  ": i["grade"] })
    return grades
def get_more(cookies, student_id):
    url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilLiteralEvaluations"
    data = {
        "studyYear": date.today().year,
        "moduleID": 1,
        "periodID": 1102,
        "studentID": student_id,

    }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    grades = {}
    for i in response.json()["data"]:
        if i["literal_Evaluation_types_name"]=="הערה למקצוע בתעודה":
            if i["textualNote"]==None:
                print(i["subject_name"] + ": " + str(i["assesment"]))
            else:
                print(i["subject_name"] + ": " + str ( i["textualNote"]))

def get_more2(cookies, student_id):
    url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilPeriodGrades"
    data = {
        "studyYear": date.today().year,
        "moduleID": 1,
        "periodID": 1102,
        "studentID": student_id,

    }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    print(response.json()["data"])
    grades = {}
    for i in response.json()["data"]:
        print(i)
def get_more3(cookies, student_id):
    url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilTrackingNotes"
    data = {
        "studyYear": date.today().year,
        "moduleID": 1,
        "periodID": 1102,
        "studentID": student_id,

    }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    print(response.json()["data"])
    grades = {}
    for i in response.json()["data"]:
        print(i)
def get_more4(cookies, student_id):
    url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilHomeroomTeacherNotes"
    data = {
        "studyYear": date.today().year,
        "moduleID": 1,
        "periodID": 1102,
        "studentID": student_id,

    }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    #print(response.json()["data"])
    grades = {}
    for i in response.json()["data"]:
        print(i["homeRoomTeacherTextualNotes_name"], end="")
        if i["assesment"] is not None:
            print(" | " + i["assesment"], end="")
        if i["homeRoomTeacherTextualNotes_text"] is not None:
            print(" | " + i["homeRoomTeacherTextualNotes_text"], end="")
        print()

def phone_book(cookies, student_id):
    url = "https://webtopserver.smartschool.co.il/server/api/general/SaveStatistics"
    data = {
        "isMobile": False,
        "moduleName": "PhoneBook",
        "functionName": ""
    }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    print(response.json()["data"])



def get_average(cookies, student_id,):
    url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilGrades"
    data = {
        "studyYear": date.today().year,
        "moduleID": 1,
        "periodID": 1102,
        "studentID": student_id,

    }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    total=0
    amount = 0
    grades = {}
    for i in response.json()["data"]:
        if i["grade"] is not None:
            #print(i["subject"] + " | " + i["title"] + " | " + str(i["grade"]) + " | " + str(i["weight"]) + "%")
            total+=i["grade"]
            amount+=1
            subject = i["subject"]
            if subject in grades:
                grades[subject] += [[i["grade"], i["weight"]]]
            else:
                grades[subject] = [[i["grade"], i["weight"]]]
    #print(grades)
    print(total/amount)
    #print(total)
    #print(amount)
    for subject in grades:
        total_prec = 0
        avg = 0
        #print(subject, end="")
        for grade in grades[subject]:
            total_prec+=grade[1]
            avg += grade[0] / (100/grade[1])
        #print(total_prec)
        #print(avg)


def get_final_grades(cookies, student_id,):
    url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilGrades"
    data = {
        "studyYear": date.today().year,
        "moduleID": 1,
        "periodID": 1102,
        "studentID": student_id,

    }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    total=0
    amount = 0
    grades = {}
    for i in response.json()["data"]:
        if i["grade"] is not None:
            total+=i["grade"]
            amount+=1
            subject = i["subject"]
            if subject in grades:
                grades[subject] += [[i["grade"], i["weight"]]]
            else:
                grades[subject] = [[i["grade"], i["weight"]]]
    print(grades)
    for subject in grades:
        total_prec = 0
        avg = 0
        print(subject, end=" ")
        for grade in grades[subject]:
            total_prec+=grade[1]
            avg += grade[0] / (100/grade[1])
        #print(str(avg) + " / " + str(total_prec))
        print(str(total_prec) + " / " + str(avg))
        print(str(int(avg*100/total_prec)) + " / " + "100")
def get_dicline_events(cookies, student_id, period = "b"):
    url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilDiciplineEvents"
    periodID = 1102
    if period == "a":
        periodID = 1103
    data = {
        "studyYear": date.today().year,
        "moduleID": 1,
        "periodID": periodID,
        "studentID": student_id,

    }

    response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    print(response.json()["data"]["diciplineEvents"])
    events = {}
    for i in response.json()["data"]["diciplineEvents"]:
        type = i["eventType"]
        if type in events:
            events[type]+=1
        else:
            events[type]=1
    return events
def bar_ilan_grades():
    url = "https://biumathpre.michlol4.co.il/api/Account/Login"
    data = {
    "grant_type": "password",
    "password": "PmGN5e",
    "zht": "335476065",
    "loginType": "student",

        }

    response = requests.post(url, json=data, headers={}, verify=False)
    cookies = response.cookies
    url = "https://biumathpre.michlol4.co.il/api/Grades/ApproveApprovalRequest"
    print(response.json()["token"])
    data = {
    "urlParameters": {}

        }

    response = requests.post(url, headers={}, cookies=response.json()["token"], verify=False)
    print(response.json())

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import base64


def encrypt_string_to_server(data, smart_key="01234567890000000150778345678901"):

    key_size = 256
    salt = get_random_bytes(16)
    key = PBKDF2(smart_key, salt, dkLen=key_size // 8, count=100)
    iv = get_random_bytes(16)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    padding_length = AES.block_size - len(data.encode('utf-8')) % AES.block_size
    padded_data = data + chr(padding_length) * padding_length
    encrypted_bytes = cipher.encrypt(padded_data.encode('utf-8'))

    result = base64.b64encode(salt + iv + encrypted_bytes).decode('utf-8')
    return result


# Example usage
# smart_key = '01234567890000000150778345678901'
# data = 'AHYC520'
# encrypted_data = encrypt_string_to_server(data, smart_key)

if __name__ == "__main__":

    main_tamar()
    username = "AHYC52"
    password = "Neches90210"
    # print(check_account(username, password))
    cookies, student_id, data = main(username, password, True)
    # #print(student_id)
    # #get_changes(cookies, student_id)
    # #get_print(cookies)
    # #get_average(cookies, student_id)
    #
    #
    get_more4(cookies, student_id)
    get_more(cookies, student_id)
    # get_final_grades(cookies, student_id)
    get_grades(cookies, student_id, "b", True)
    get_final_grades(cookies, student_id)
    #get_more2(cookies, student_id)
    #phone_book(cookies, student_id)
    #get_dicline_events(cookies, student_id)
    #bar_ilan_grades()
    #print(lesson_events(cookies, "QG6qT1cV+3pIAAZwLgxsKDbMzA2/VRYuVwu0h7+QQdskXwV8HyLRgOb/ddBZy2IW"))
    #check_token(cookies)
