import requests
from datetime import datetime, timezone, timedelta, date
import random
import math
import requests
import json
import time
import certifi
from bs4 import BeautifulSoup
import urllib3
from dataclasses import dataclass

from requests import Response
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import base64
import webbrowser


def get_grades1(cookies, student_id):
    """
    Get a webtop account's grades.

    Args:
        self: the user object.
        period: the year period (a, b, or ab).

    Returns:
        boolean: True if the webtop account exists, False otherwise.
    """

    url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilGrades"
    data: dict = dict(
        studyYear=date.today().year, moduleID=1, periodID=1103, studentID=student_id)
    response: Response = requests.post(url, json=data, headers={}, cookies=cookies, verify=False)
    grades = []
    for i in response.json()["data"]:
        if i["grade"] is not None:
            if i["gradeTranslation"]==None:
                notes = "   "
            else:
                notes = i["gradeTranslation"]

            grades.append(
                {
                    "date": i["date"][:10],
                    "subject": i["subject"],
                    "exam_type": i["type"],
                    "grade": i["grade"],
                    "notes": notes
                }
            )

    return grades
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


urllib3.disable_warnings()

cookies = ""
student_id = ""


class Except(Exception):
    """Exception raised for errors in the input salary.

    Attributes:
        salary -- input salary which caused the error
        message -- explanation of the error
    """

    def __init__(self, message="Invalid username / password"):
        self.message = message
        super().__init__(self.message)

def validate_login(username: str, password: str):

    url = "https://webtopserver.smartschool.co.il/server/api/user/LoginByUserNameAndPassword"
    data = {
        "Data": "09lFSU9KIBot/BiLk/kRejU7vANwHPdnOggkiUZVLsVbAfSWaZJL8fDjD9Fess5c",
        "UserName": username,
        "Password": password,
        "deviceDataJson": '{"isMobile":true,"isTablet":false,"isDesktop":false,"getDeviceType":"Mobile","os":"Android","osVersion":"6.0","browser":"Chrome","browserVersion":"122.0.0.0","browserMajorVersion":122,"screen_resolution":"1232 x 840","cookies":true,"userAgent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"}'

    }
    try:
        response = requests.post(url, json=data, verify=False)
        cookies = response.cookies  # get the response cookies.
        student_id = response.json()["data"]["userId"]  # pull the student id from the response json
        info = response.json()["data"]  # get info about the user, from the response.
        class_code = f"{response.json()['data']['classCode']}|{str(response.json()['data']['classNumber'])}"
        institution = response.json()["data"]["institutionCode"]
    except:
        return False, "error", None
    if (response.json()["errorDescription"]=="User Name or Password incorrect"):
        return False, "wrong", None
    return True, "fine", [cookies, student_id, info, class_code, institution]

class WebtopUser:
    def __init__(self, username, password: str="cookies"):
        """
        an unofficial webtop api, to get much information like: grades, schedule, average, and more.
        this function initialises a webtop user,
        gets a cookie for a webtop user, logins by username and password

        Args:
            username (str): the username of the webtop user.
            password (str): The password of the webtop user.
        Returns:
            None.
        """
        if(password=="cookies"):
            self.cookies = username[0]
            self.student_id = username[1]
            self.info = username[2]
            self.class_code = username[3]
            self.institution = username[4]
        else:

            data = encrypt_string_to_server(f"{username}0")  # encrypt the username to give to the database.

            url = "https://webtopserver.smartschool.co.il/server/api/user/LoginByUserNameAndPassword"
            data = {  # the request parameters.
                "Data": data,
                "UserName": username,
                "Password": password,
                "deviceDataJson": '{"isMobile":false,"isTablet":false,"isDesktop":true}'

            }
            response = requests.post(url, json=data,
                                     verify=False)  # send the request, and get the response and the cookie
            try:
                if response.json()["status"]:
                    self.student_id = response.json()["data"]["userId"]  # pull the student id from the response json
                    self.cookies = response.cookies  # get the response cookies.
                    self.info = response.json()["data"]  # get info about the user, from the response.
                    self.class_code = f"{response.json()['data']['classCode']}|{str(response.json()['data']['classNumber'])}"
                    self.institution = response.json()["data"]["institutionCode"]
                else:
                    raise Except()
            except:
                raise Except()

    def login_get_info(self):
        """
        get user's information

        Args:
            self: The user object.

        Returns:
            int: the wanted cookie value, and the student id.
        """

        return self.info

    def get_grades(self, period="a"):
        """
        Get a webtop account's grades.

        Args:
            self: the user object.
            period: the year period (a, b, or ab).

        Returns:
            boolean: True if the webtop account exists, False otherwise.
        """
        if period not in ("a", "b", "ab"):
            raise Except(message="the period must be a, b, or ab")

        url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilGrades"
        period_id: int = 1103 if period == "a" else 1102 if period == "b" else 0
        data: dict = dict(
            studyYear=date.today().year, moduleID=1, periodID=period_id, studentID=self.student_id)
        response: Response = requests.post(url, json=data, headers={}, cookies=self.cookies, verify=False)
        grades: dict = {}
        for i in response.json()["data"]:
            if i["grade"] is not None:
                if i["subject"] not in grades:
                    grades[i["subject"]] = {}
                grades[i["subject"]][i["title"]] = [i["grade"], i["weight"]]

        return grades
    def get_grades1(self, period="a"):
        """
        Get a webtop account's grades.

        Args:
            self: the user object.
            period: the year period (a, b, or ab).

        Returns:
            boolean: True if the webtop account exists, False otherwise.
        """
        if period not in ("a", "b", "ab"):
            raise Except(message="the period must be a, b, or ab")

        url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilGrades"
        period_id: int = 1103 if period == "a" else 1102 if period == "b" else 0
        print(type(self.student_id))
        data: dict = dict(
            studyYear=date.today().year, moduleID=1, periodID=period_id, studentID="saad")
        response: Response = requests.post(url, json=data, headers={}, cookies=self.cookies, verify=False)
        grades = []
        print(response.json())
        for i in response.json()["data"]:
            if i["grade"] is not None:
                grades.append(
                    {
                        "date": i["date"],
                        "subject": i["subject"],
                        "exam_type": i["type"],
                        "grade": i["grade"],
                        "notes": i["gradeTranslation"]
                    }
                )

        return grades
    def get_grades_list(self, period="b"):
        """
        Get a webtop account's grades, in a list.

        Args:
            self: the user object.
            period: the year period (a, b, or ab).

        Returns:
            list: A list of a user's grades.
        """
        if period not in ("a", "b", "ab"):
            raise Except(message="the period must be a, b, or ab")

        url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilGrades"
        period_id: int = 1103 if period == "a" else 1102 if period == "b" else 0

        data: dict = dict(
            studyYear=date.today().year, moduleID=1, periodID=period_id, studentID=self.student_id)
        response: Response = requests.post(url, json=data, headers={}, cookies=self.cookies, verify=False)
        grades: list = []

        for i in response.json()["data"]:
            if i["grade"] is not None:
                grades.append(i["grade"])

        return grades

    def get_average(self, period="b"):
        """
        Get a webtop account's average, by getting the grades.

        Args:
            self: The user object.
            period: The year period (a, b, or ab).

        Returns:
            double: The average.
        """
        if period not in ("a", "b", "ab"):  #check if the period is valid.
            raise Except(message="the period must be a or b, or ab")
        grades: list = self.get_grades_list(period=period)  #get the grades.
        return sum(grades) / len(grades)  #return the average.

    def get_discipline_events(self, period="b"):
        """
        Get a webtop user's discipline events.

        Args:
            self: The user object.
            period (string): The year period (a, b, or ab).

        Returns:
            dict: Containing all the user's decline events in the following form:
                  [{'type': string, 'date': string, 'subject': string}...]
        """

        if period not in ("a", "b", "ab"):
            raise Except(message="the period must be a, b, or ab")

        period_id = 1103 if period == "a" else 1102 if period == "b" else 0
        print(period_id)

        url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilDiciplineEvents"
        data = dict(studentID=self.student_id, moduleID=11, periodID=period_id)
        response = requests.post(url, json=data, headers={}, cookies=self.cookies, verify=False)
        events_data = response.json()["data"]["diciplineEvents"]

        events = {}
        for item in events_data:
            event_type = item["eventType"]
            event_info = {"type": event_type, "date": item["eventDate"], "subject": item["subjectName"]}
            events.setdefault(event_type, []).append(event_info)

        return events

    def get_changes(self, grade: str = None, institution_code: int = None):
        """
        Get a webtop user's schedule and changes for today.

        Args:
            self: The user object.
            grade (string): The class grade.
            institution_code (int): The school id, find at https://apps.education.gov.il/imsnet/itur.aspx.

        Returns:
            dict: Containing the schedule and changes for today.
        """
        if grade is None:
            grade = self.class_code
        if institution_code is None:
            institution_code = self.institution
        url = "https://webtopserver.smartschool.co.il/server/api/shotef/ShotefSchedualeData"
        data = dict(institutionCode=institution_code, selectedValue=grade, typeView=2)
        response = requests.post(url, json=data, headers={}, cookies=self.cookies, verify=False)

        schedule_data = response.json()["data"]
        weekday = datetime.now().isoweekday() + 1
        hours_data = schedule_data[str(weekday)]["hoursData"]

        schedule = {
            i["hour"]: i["scheduale"][0]["subject"]
            for i in hours_data if i["scheduale"]
        }

        url = "https://webtopserver.smartschool.co.il/server/api/shotef/ChangesAndMessagesData"
        response = requests.post(url, json=data, headers=headers, cookies=cookies, verify=False)
        changes = response.json()["data"]["changes"]

        for item in changes:
            hour = item["hour"]
            if item["content"] == "מילוי מקום":
                schedule[hour] += f" ( מילוי מקום - {item['privateName']} {item['lastName']} )"
            elif item["content"] == "ביטול שיעור":
                schedule[hour] += " ( בוטל )"
            elif item["content"] == "הזזת שיעור":
                schedule[hour] += " (בוטל?)"
            else:
                print(f"unknown change detected {item['content']}")

        return schedule

    def get_notes(self, period="a"):
        """
        Get a webtop user's notes from teachers.

        Args:
            self: The user object.
            period (string): The year period (a, b, or ab).

        Returns:
            dict: A dictionary containing the teacher's notes.
        """

        url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilLiteralEvaluations"

        if period not in ("a", "b", "ab"):
            raise Except(message="the period must be a, b, or ab")

        period_id = 1103 if period == "a" else 1102 if period == "b" else 0

        data = {
            "studyYear": date.today().year,
            "moduleID": 1,
            "periodID": period_id,
            "studentID": self.student_id,

        }

        response = requests.post(url, json=data, headers={}, cookies=self.cookies, verify=False)
        notes = {}

        for item in response.json()["data"]:
            if item["literal_Evaluation_types_name"] == "הערה למקצוע בתעודה":
                subject = item["subject_name"]
                notes[subject] = item["textualNote"] if item["textualNote"] else str(item["assesment"])

        return notes

    def get_homeroom_notes(self, period="b"):
        """
        Get a webtop user's homeroom teacher notes.

        Args:
            self: The user object.
            period (string): The year period (a, b, or ab).

        Returns:
            dict: A dictionary containing the homeroom teacher's notes.
        """
        if period not in {"a", "b", "ab"}:
            raise Except(message="the period must be a, b, or ab")

        period_id = 1103 if period == "a" else 1102 if period == "b" else 0
        url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilHomeroomTeacherNotes"
        data = {
            "studyYear": date.today().year,
            "moduleID": 1,
            "periodID": period_id,
            "studentID": self.student_id,
        }

        response = requests.post(url, json=data, headers={}, cookies=self.cookies, verify=False)
        notes = {}

        for item in response.json()["data"]:
            key = item["homeRoomTeacherTextualNotes_name"]
            note = " | ".join(filter(None, [str(item.get("assesment")), item.get("homeRoomTeacherTextualNotes_text")]))
            notes[key] = note

        return notes

    def get_final_grades(self, period="b"):
        """
        Get a webtop user's final grades for a specific period.

        Args:
            self: The user object.
            period (string): The year period (a, b, or ab).

        Returns:
            dict: A dictionary containing the final grades for each subject.
        """
        if period not in {"a", "b", "ab"}:
            raise Except(message="the period must be a, b, or ab")

        period_id = 1103 if period == "a" else 1102 if period == "b" else 0
        url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilGrades"
        data = {
            "studyYear": date.today().year,
            "moduleID": 1,
            "periodID": period_id,
            "studentID": self.student_id,
        }

        response = requests.post(url, json=data, headers={}, cookies=self.cookies, verify=False)
        grades_data = response.json()["data"]

        grades = {}
        for item in grades_data:
            if item["grade"] is not None:
                subject = item["subject"]
                if subject not in grades:
                    grades[subject] = []
                grades[subject].append((item["grade"], item["weight"]))

        final_grades = {}
        for subject, grade_list in grades.items():
            total_weight = sum(weight for _, weight in grade_list)
            weighted_sum = sum(grade * weight for grade, weight in grade_list)

            if total_weight != 0:
                normalized_avg = (weighted_sum / total_weight) * 100
            else:
                normalized_avg = 0

            final_grades[subject] = round(normalized_avg / 100, 1)

        return final_grades

    def get_messages(self):
        """
        Get the messages inbox from a webtop account.

        Args:
            self: The user object.

        Returns:
            a list containing all the messages in the inbox.
        """

        url = "https://webtopserver.smartschool.co.il/server/api/messageBox/GetMessagesInbox"  # The endpoint url.
        data = {  # The request data
            "PageId": 1,
            "LabelId": 0,
            "SearchQuery": "",
        }
        response = requests.post(url, json=data, cookies=self.cookies,
                                 verify=False)  # send the request, and get the response and the cookie
        messages = []
        for message in response.json()["data"]:  # Loop through all the messages in the inbox.
            url = "https://webtopserver.smartschool.co.il/server/api/messageBox/GetMessagesInboxData"
            data = {
                "MessageId": message['messageId'],
                "FilterId": 0,
                "IsInbox": True
            }
            response = requests.post(url, json=data, cookies=cookies,
                                     verify=False)  # Get the message content and more information.
            soup = BeautifulSoup(response.json()["data"]["messageData"]["messageContent"],
                                 "lxml")  # Make the message readable.
            text = soup.get_text().replace("\n\n", "\n")  # Remove unneeded new lines.
            messages.append({"subject": response.json()["data"]["messageData"]["subject"],
                             "sender": message["student_F_name"] + " " + message["student_L_name"],
                             "content": text})  # Add the message information to the list.
        return messages  # Return all the messages in the inbox.

    def get_schedule(self, grade=None, institution=None):
        """
        Get a webtop user's weekly schedule, including this week's changes.

        Args:
            self: The user object.
            grade: the grade to get schedule.
            institution: the institution of the grade.

        Returns:
            dict: containing the weekly schedule.
        """

        if grade is None:
            grade = self.class_code
        if institution is None:
            institution = self.institution

        url = "https://webtopserver.smartschool.co.il/server/api/shotef/ShotefSchedualeData"  # The endpoint url.
        data = {  # The request data.
            "institutionCode": institution,
            "selectedValue": grade,
            "typeView": 2
        }

        response = requests.post(url, json=data, headers={}, cookies=self.cookies, verify=False)
        schedule = {}
        for day in response.json()["data"]:  # Go through all the days in the response.
            day1 = {}
            for hour in day["hoursData"]:  # Go through all the hours in the day.
                if hour["scheduale"]:
                    day1[str(hour["hour"])] = hour["scheduale"][0]["subject"]  # Add the hour information to the json.
                    if hour["scheduale"][0]["changes"]:
                        day1[str(hour["hour"])] += hour["scheduale"][0]["changes"][0]["type"]
            schedule[day["dayIndex"]] = day1
        return schedule  # Return the schedule.

    def get_schedule_pdf(self):
        """
            Get a webtop user's weekly schedule, including this week's changes.

            Args:
                self: The user object.

            Returns:
                bool: True if good.
            """
        url = "https://webtopserver.smartschool.co.il/server/api/pdf/generate"
        data = {
            "exportToPdf": True,
            "fileName": "SchedualeView.pdf",
            "maxPages": 20,
            "path": "Timetable_Changes&tabIndex=1&selectedItem=7|6&selectedType=2",
            "skipPage1": False,
            "url": "https://webtop.smartschool.co.il"
        }

        response = requests.post(url, json=data, headers={}, cookies=self.cookies, verify=False)
        pdf_data = b'' + response.content  # Your PDF binary data goes here
        with open('output.pdf', 'wb') as file:
            file.write(pdf_data)
        webbrowser.open("output.pdf")
        return True

    def get_tracking_notes(self):  #never tried getting this to work, have fun!
        url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilTrackingNotes"
        data = {
            "studyYear": date.today().year,
            "moduleID": 1,
            "periodID": 1102,
            "studentID": self.student_id,

        }

        response = requests.post(url, json=data, headers={}, cookies=self.cookies, verify=False)
        print(response.json()["data"])
        for i in response.json()["data"]:
            print(i)

    def get_period_grades(self):
        """
        Fetch and process pupil period grades.

        Args:
            self: The user object.

        Returns:
            dict: A dictionary containing the grades for each subject.
        """
        url = "https://webtopserver.smartschool.co.il/server/api/PupilCard/GetPupilPeriodGrades"
        data = {
            "studyYear": date.today().year,
            "moduleID": 1,
            "periodID": 1102,
            "studentID": self.student_id,
        }

        response = requests.post(url, json=data, headers={}, cookies=self.cookies, verify=False)
        grades_data = response.json()["data"]

        grades = {}
        for item in grades_data:
            subject_name = item.get('subject_name')
            final_grade = item.get('final_grade')
            weighted_grade = item.get('weighted_grade')
            grade_translation = item.get('grade_translation')
            assessment = item.get('assesment')

            grades[subject_name] = {
                'final_grade': final_grade,
                'weighted_grade': weighted_grade,
                'grade_translation': grade_translation,
                'assessment': assessment,
            }

        return grades

    def _str_(self):
        info = self.info
        return (
            f"user: {info['fullName']}\n"
            f"school: {info['schoolName']}\n"
            f"class: {info['classCode']} | {info['classNumber']}"
        )


if __name__ == "__main__":
    #validate_login("AHYC52", "")
    username = input("enter username -->\n")
    if username == "" or username == "ofer":
        username = "AHYC52"
    password = input("enter password -->\n")
    if password == "" or password == "ofer":
        password = "Neches90210"

    user = WebtopUser(username, password)
    print("0: done\n"
          "1: get info\n"
          "2: get grades\n"
          "3: get average\n"
          "4: get final grades\n"
          "5: get notes\n"
          "6: get homeroom notes\n"
          "7: get schedule\n"
          "8: get changes\n"
          "9: get schedule pdf\n"
          "10: get messages\n"
          "11: get grades list\n"
          "12: get discipline events")
    while True:

        task = int(input("select task"))
        if task == 0:
            break
        elif task == 1:
            print(user.login_get_info())
        elif task == 2:
            print(user.get_grades1())
        elif task == 3:
            print(user.get_average())
        elif task == 4:
            print(user.get_final_grades())
        elif task == 5:
            print(user.get_notes())
        elif task == 6:
            print(user.get_homeroom_notes())
        elif task == 7:
            print(user.get_schedule())
        elif task == 8:
            print(user.get_changes())
        elif task == 9:
            print(user.get_schedule_pdf())
        elif task == 10:
            print(user.get_messages())
        elif task == 11:
            print(user.get_grades_list())
        elif task == 12:
            print(user.get_discipline_events())
