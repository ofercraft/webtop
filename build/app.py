from flask import Flask, render_template, request, redirect, url_for, session
from webtop3 import WebtopUser, validate_login
app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY_HERE"  # Replace with a strong random string

# Let Jinja use Python's 'enumerate' if you prefer
app.jinja_env.globals.update(enumerate=enumerate)

# Dummy user credentials
VALID_USERNAME = "AHYC52"
VALID_PASSWORD = "1234"


##############################################################################
# Data (Old-Style Schedule, Grades, Attendance, Student Profile)
##############################################################################

# "Old" schedule data:
#  - Each row = hour index
#  - Each row has 5 columns (חמישי=0, רביעי=1, שלישי=2, שני=3, ראשון=4)
#  - Each cell is (subject, teacher, color_class)
schedule_data = [
    [
        ("היסטוריה", "קרפל אביגיל", "pink-cell"),
        ("מדעים",   "רווה רות",     "lightgreen-cell"),
        ("ערבית",   "מורה צדק לדרון","lightpink-cell"),
        ("מתמטיקה", "יערי שרון",     "lightyellow-cell"),
        ("תנ\"ך",   "נירנבאום אתי",   "lightblue-cell")
    ],
    [
        ("היסטוריה", "קרפל אביגיל", "pink-cell"),
        ("מדעים",   "רווה רות",     "lightgreen-cell"),
        ("ערבית",   "מורה צדק לדרון","lightpink-cell"),
        ("מתמטיקה", "יערי שרון",     "lightyellow-cell"),
        ("תנ\"ך",   "נירנבאום אתי",   "lightblue-cell")
    ],
    [
        ("התעמלות", "פוקס משה",      "lightblue-cell"),
        ("אנגלית",  "איסקוב ענבר טלי","lightpink-cell"),
        ("ספרות",   "יפהלית שי",      "lightyellow-cell"),
        ("לשון",    "מורה ברקת",      "pink-cell"),
        ("אנגלית",  "איסקוב ענבר טלי","lightgreen-cell")
    ],
    [
        ("התעמלות", "פוקס משה",      "lightblue-cell"),
        ("אנגלית",  "איסקוב ענבר טלי","lightpink-cell"),
        ("ספרות",   "יפהלית שי",      "lightyellow-cell"),
        ("לשון",    "מורה ברקת",      "pink-cell"),
        ("אנגלית",  "איסקוב ענבר טלי","lightgreen-cell")
    ],
    [
        ("מוסיקה",       "קון אלנד",    "lightpink-cell"),
        ("פיזיקה",       "רווה רות",    "lightgreen-cell"),
        ("עברית",        "אלוני הרצאה", "lightblue-cell"),
        ("תושב\"ע",      "גבון אסתי",    "pink-cell"),
        ("מתמטיקה הנדסה","יערי שרון",   "lightyellow-cell")
    ]
]

grades_data = [
    {
        "date": "10/01/2025",
        "subject": "מתמטיקה הנדסה",
        "exam_type": "מבחן סוף פרק",
        "grade": 95,
        "notes": "עבודה מצוינת"
    },
    {
        "date": "05/01/2025",
        "subject": "אנגלית",
        "exam_type": "מבחן קריאה",
        "grade": 88,
        "notes": "דרוש חיזוק באוצר מילים"
    },
]

attendance_data = [
    {
        "date": "06/01/2025",
        "day": "יום שני",
        "hour": 2,
        "group": "היסטוריה - קרפל אביגיל",
        "event_type": "חיסור",
        "justification": "",
        "absence_reason": "יום שלג",
        "comments": "",
    },
    {
        "date": "26/12/2024",
        "day": "יום חמישי",
        "hour": 3,
        "group": "ערבית - מורה צדק לדרון",
        "event_type": "איחור",
        "justification": "",
        "absence_reason": "",
        "comments": "הגיע באיחור של 10 דקות",
    }
]

student_info = {
    "name": "פלדמן אופיר",
    "id": "123456789",
    "phone": "050-123-4567",
    "address": "רחוב הדוגמה 10, עיר דוגמה",
    "class": "ח'3 - תשפ\"ה"
}
parents_info = {
    "father_name": "יוסי פלדמן",
    "father_phone": "050-111-2222",
    "mother_name": "רינה אופיר",
    "mother_phone": "052-333-4444"
}


##############################################################################
# Authentication + Decorator
##############################################################################

def login_required(func):
    """Decorator to lock pages behind login."""
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/", methods=["GET", "POST"])
def login():
    """ Default route: login page """
    if session.get("logged_in"):
        # If already logged in, go home
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        req = validate_login(username, password)
        if req[1]=="fine":
            session["logged_in"] = True
            session["username"] = username
            session["cookies"]=req[2]
            session["student_id"]=req[3]
            session["info"]=req[4]
            session["class_code"]=req[5]
            session["institution"]=req[6]

            return redirect(url_for("home"))
        elif req[1]=="wrong":
            error_msg = "שם המשתמש או הסיסמה שגויים"
            return render_template("login.html", error=error_msg)
        else:
            error_msg = "בעיה לא צפויה"
            return render_template("login.html", error=error_msg)

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


##############################################################################
# Protected Routes
##############################################################################

@app.route("/home")
@login_required
def home():
    user_name = session.get("username", "משתמש")
    return render_template("index.html", username=user_name)

@app.route("/schedule")
@login_required
def schedule():
    return render_template("schedule.html", schedule_data=schedule_data)

@app.route("/grades")
@login_required
def grades():
    info = [session.get("cookies"), session.get("student_id"), session.get("info"), session.get("class_code"), session.get("institution")]
    grades_list = WebtopUser(info).get_grades()
    return render_template("grades.html", grades_data=grades_list)

@app.route("/attendance")
@login_required
def attendance():
    return render_template("attendance.html", attendance_data=attendance_data)

@app.route("/student_profile")
@login_required
def student_profile():
    return render_template("student_profile.html",
                           student_info=student_info,
                           parents_info=parents_info)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to port 5000 if PORT is not set
    app.run(host="0.0.0.0", port=port)
