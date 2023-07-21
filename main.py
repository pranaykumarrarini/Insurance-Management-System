import datetime
from datetime import date, timedelta
import os
import random

from bson import ObjectId
from flask import Flask, request, render_template, session, redirect
import pymongo
my_collections = pymongo.MongoClient("mongodb://localhost:27017/")
my_db = my_collections['HealthInsuranceManagement']
admin_col = my_db['Admin']
hospital_col = my_db['Hospital']
user_col = my_db['User']
treatment_col = my_db['Treatments']
policies_col = my_db['Policies']
user_policy_col = my_db['user_policy']
user_climes_col = my_db['User_Climes']
payment_col = my_db['Payments']

app = Flask(__name__)
app.secret_key = "Health"


App_Root = os.path.dirname(__file__)
App_Root = App_Root + "/static"

status_user_clime_request = "Clime Request Raised"
status_clime_accepted_hospital = "Clime Request Accepted by Hospital"
status_clime_rejected_hospital = "clime Request Rejected by Hospital"
status_user_clime_payment = "Clime Amount Paid by Insurance Company"
status_clime_approved = "Clime Approved by Insurance "

if admin_col.count_documents({}) == 0:
    admin_col.insert_one({"name": "admin", "password": "admin", "role": "admin"})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/adminLogin")
def adminLogin():
    return render_template("adminLogin.html")


@app.route("/adminLogin1", methods=['post'])
def adminLogin1():
    name = request.form.get("username")
    password = request.form.get("password")
    query = {"username": name, "password": password}
    admin = admin_col.find_one(query)

    if admin != None:
        session['admin_id'] = str(admin['_id'])
        session['role'] = 'Admin'
        return redirect("/adminHome")
    else:
        return render_template("msg.html", message="Invalid Login Details", color="bg-danger text-white")


@app.route("/adminHome")
def adminHome():
    return render_template("adminHome.html")


@app.route("/hospitalLogin")
def hospitalLogin():
    return render_template("hospitalLogin.html")


@app.route("/hospitalLogin1", methods=['post'])
def hospitalLogin1():
    email = request.form.get('email')
    password = request.form.get('password')
    query = {"email": email, "password": password}
    count = hospital_col.count_documents(query)
    if count > 0:
        hospital = hospital_col.find_one(query)
        if hospital["status"] == "Activated":
            session['hospital_id'] = str(hospital['_id'])
            session['role'] = 'Hospital'
            return redirect("/hospitalHome")
        else:
            return render_template("msg.html", message="Hospital is Not Activated", color="bg-danger text-white")
    else:
        return render_template("msg.html", message="Invalid Login Details", color="bg-danger text-white")


@app.route("/hospitalHome")
def hospitalHome():
    return render_template("hospitalHome.html")


@app.route("/hospitalRegistration")
def hospitalRegistration():
    return render_template("hospitalRegistration.html")


@app.route("/hospitalRegistration1", methods=['post'])
def hospitalRegistration1():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    password = request.form.get('password')
    hospital_type = request.form.get('hospital_type')
    address = request.form.get('address')
    about = request.form.get('about')
    status = "Deactivated"
    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = hospital_col.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Details", color="bg-danger text-white")
    else:
        query = {"name": name, "phone": phone, "email": email, "password": password, "hospital_type": hospital_type, "address": address,"about": about, "status": status}
    hospital_col.insert_one(query)
    return render_template("msg.html", message="Hospital Registered Successfully")


@app.route("/viewHospitals")
def viewHospitals():
    hospitals = hospital_col.find()
    return render_template("viewHospitals.html", hospitals=hospitals)


@app.route("/activateHospital")
def activateHospital():
    hospital_id = ObjectId(request.args.get("hospital_id"))
    query = {'_id': ObjectId(hospital_id)}
    query1 = {"$set": {"status": "Activated"}}
    hospital_col .update_one(query, query1)
    return redirect("/viewHospitals")


@app.route("/inactivateHospital")
def inactivateHospital():
    hospital_id = ObjectId(request.args.get("hospital_id"))
    query = {'_id': ObjectId(hospital_id)}
    query1 = {"$set": {"status": "Deactivated"}}
    hospital_col .update_one(query, query1)
    return redirect("/viewHospitals")


@app.route("/userLogin")
def userLogin():
    return render_template("userLogin.html")


@app.route("/userLogin1", methods=['post'])
def userLogin1():
    email = request.form.get('email')
    password = request.form.get('password')
    query = {"email": email, "password": password}
    count = user_col.count_documents(query)
    if count > 0:
        user = user_col.find_one(query)
        session['user_id'] = str(user['_id'])
        session['role'] = 'User'
        return redirect("/userHome")
    else:
        return render_template("msg.html", message="Invalid Login Details", color="bg-danger text-white")


@app.route("/userHome")
def userHome():
    return render_template("userHome.html")


@app.route("/userRegistration")
def userRegistration():
    return render_template("userRegistration.html")


@app.route("/userRegistration1", methods=['post'])
def userRegistration1():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    password = request.form.get('password')
    insurance_type = request.form.get('insurance_type')
    gender = request.form.get('gender')
    age = request.form.get('age')
    dob = request.form.get('dob')

    picture = request.files.get('picture')
    path = App_Root + "/picture/" + picture.filename
    picture.save(path)

    id_proof = request.form.get("id_proof")

    proof = request.files.get('proof')
    path = App_Root + "/proof/" + proof.filename
    proof.save(path)

    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = user_col.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Details", color="bg-danger text-white")
    else:
        query = {"name": name, "phone": phone, "email": email, "password": password, "insurance_type": insurance_type,
                 "gender": gender, "age": age, "dob": dob, "picture": picture.filename, "id_proof": id_proof, "proof": proof.filename}
    user_col.insert_one(query)
    return redirect("/userLogin")


@app.route("/treatments")
def treatments():
    treatments = treatment_col.find()
    return render_template("treatments.html", treatments=treatments, get_treatment_id=get_treatment_id)


@app.route("/addTreatments")
def addTreatments():
    return render_template("addTreatments.html")


@app.route("/addTreatments1", methods=['post'])
def addTreatments1():
    treatment_name = request.form.get("treatment_name")
    description = request.form.get("description")
    terms_conditions = request.form.get("terms_conditions")
    query = {"treatment_name": treatment_name, "description": description, "terms_conditions": terms_conditions}
    treatment_col.insert_one(query)
    return redirect("/treatments")

@app.route("/makeAsAvailable")
def makeAsAvailable():
    hospital_id = session['hospital_id']
    treatment_id = request.args.get("treatment_id")
    query = {'$push': {'hospital_ids': ObjectId(hospital_id)}}
    treatment_col.update_one({"_id": ObjectId(treatment_id)}, query)
    return redirect("/treatments")

def get_treatment_id(treatment_id):
    hospital_id = session['hospital_id']
    query = {'_id': treatment_id}
    treatment = treatment_col.find_one(query)
    if 'hospital_ids' in treatment and ObjectId(hospital_id) in treatment['hospital_ids']:
        return True
    else:
        return False


@app.route("/policies")
def policies():
    policies = policies_col.find()
    return render_template("policies.html", policies=policies)


@app.route("/addPolicies")
def addPolicies():
    return render_template("addPolicies.html")


@app.route("/addPolicies1", methods=['post'])
def addPolicies1():
    policy_name = request.form.get("policy_name")
    insurance_duration = request.form.get("insurance_duration")
    installment_premium = request.form.get("installment_premium")
    premium_amount = request.form.get("premium_amount")
    clime_amount = request.form.get("clime_amount")
    query = {"policy_name": policy_name, "insurance_duration": insurance_duration, "installment_premium": installment_premium, "premium_amount": premium_amount, "clime_amount": clime_amount}
    policies_col.insert_one(query)
    return redirect("/policies")


@app.route("/adminAddTreatments")
def adminAddTreatments():
    policy_id = request.args.get("policy_id")
    treatments = treatment_col.find()
    return render_template("adminAddTreatments.html", policy_id=policy_id, treatments=treatments)


@app.route("/adminAddTreatments1", methods=['post'])
def adminAddTreatments1():
    policy_id = request.form.get("policy_id")
    treatment_id = request.form.get("treatment_id")
    query = {'$push': {'treatment_ids': ObjectId(treatment_id)}}
    policies_col.update_one({"_id": ObjectId(policy_id)}, query)
    return redirect("/policies")


@app.route("/viewPolicies")
def viewPolicies():
    policies = policies_col.find()
    return render_template("viewPolicies.html", get_treatment_by_hospital_id=get_treatment_by_hospital_id, policies=policies, get_treatment_id_by_policy=get_treatment_id_by_policy, user_buy_policy=user_buy_policy)


def user_buy_policy(policy_id):
    user_id = session['user_id']
    query = {"policy_id": ObjectId(policy_id), "user_id": ObjectId(user_id)}
    count = user_policy_col.count_documents(query)
    return count


def get_treatment_id_by_policy(treatment_id):
    query = {'_id': ObjectId(treatment_id)}
    treatment = treatment_col.find_one(query)
    return treatment


@app.route("/viewAvailableHospitals")
def viewAvailableHospitals():
    treatment_id = request.args.get("treatment_id")
    query = {"_id": ObjectId(treatment_id)}
    treatments = treatment_col.find(query)
    return render_template("viewAvailableHospitals.html", treatments=treatments, get_hospital_id=get_hospital_id)


def get_treatment_by_hospital_id(treatment_id):
    query = {"_id": treatment_id}
    treatment = treatment_col.find_one(query)
    if 'hospital_ids' in treatment:
        return True
    else:
        return False


def get_hospital_id(hospital_id):
    query = {'_id': ObjectId(hospital_id)}
    hospital = hospital_col.find_one(query)
    return hospital


@app.route("/buy_policy")
def buy_policy():
    policy_id = request.args.get("policy_id")
    return render_template("buy_policy.html", policy_id=policy_id)


@app.route("/buy_policy1", methods=['post'])
def buy_policy1():
    policy_id = request.form.get("policy_id")
    query = {"_id": ObjectId(policy_id)}
    policy = policies_col.find_one(query)
    insurance_duration = policy['insurance_duration']
    user_id = session['user_id']
    start_date = datetime.datetime.now()
    delta = int(insurance_duration) * 30
    end_date = start_date + datetime.timedelta(days=delta)

    policy_number = random.randint(10000000000, 99999999999)
    while user_policy_col.count_documents({"policy_number": policy_number}) > 0:
        policy_number = random.randint(10000000000, 99999999999)
    query = {"policy_id": ObjectId(policy_id), "user_id": ObjectId(user_id), "policy_number": policy_number, "start_date": start_date, "end_date": end_date}
    result = user_policy_col.insert_one(query)
    userPolicy_id = result.inserted_id
    premium_amount = request.form.get("premium_amount")
    date = datetime.datetime.now()
    query = {'userPolicy_id': ObjectId(userPolicy_id), "premium_amount":premium_amount, "date": date, "status": "Installment Premium Paid by User"}
    payment_col.insert_one(query)
    return redirect("/viewUserPolicies")


@app.route("/viewUserPolicies")
def viewUserPolicies():
    policy_id = request.args.get("policy_id")
    userPolicy_id = request.args.get("userPolicy_id")
    if userPolicy_id == None:
        if session['role'] == "User":
            query = {"user_id": ObjectId(session['user_id'])}
        elif session['role'] == "Admin":
            query = {"policy_id": ObjectId(policy_id)}
    else:
        query = {"_id": ObjectId(userPolicy_id)}
    userPolicies = user_policy_col.find(query)
    userPolicies = list(userPolicies)
    if len(userPolicies) == 0:
        return render_template("msg.html", message="User Policies Not Available",  color="text-danger")
    return render_template("viewUserPolicies.html", userPolicies=userPolicies, get_policy_id=get_policy_id, grt_user_id=grt_user_id)


def get_policy_id(policy_id):
    query = {'_id': ObjectId(policy_id)}
    policy = policies_col.find_one(query)
    return policy


def grt_user_id(user_id):
    query = {'_id': ObjectId(user_id)}
    user = user_col.find_one(query)
    return user


@app.route("/climeRequest")
def climeRequest():
    userPolicy_id = request.args.get("userPolicy_id")
    clime_amount = request.args.get("clime_amount")
    hospitals = hospital_col.find()
    return render_template("climeRequest.html", userPolicy_id=userPolicy_id, hospitals=hospitals, clime_amount=clime_amount)


@app.route("/climeRequest1", methods=['post'])
def climeRequest1():
    userPolicy_id = request.form.get("userPolicy_id")
    hospital_id = request.form.get("hospital_id")

    reports = request.files.get('reports')
    path = App_Root + "/reports/" + reports.filename
    reports.save(path)

    amount = request.form.get("amount")
    date = datetime.datetime.now()
    status = status_user_clime_request
    query = {"userPolicy_id": ObjectId(userPolicy_id), "hospital_id": ObjectId(hospital_id), "reports": reports.filename, "amount": amount, "date": date, "status": status}
    user_climes_col.insert_one(query)
    return redirect("/viewUserClimes")


@app.route("/viewUserClimes")
def viewUserClimes():
    userPolicy_id = request.args.get("userPolicy_id")
    if session['role'] == "Hospital":
        query = {"hospital_id": ObjectId(session['hospital_id'])}
    elif session['role'] == "User":
        query = {"user_id": ObjectId(session['user_id'])}
        userPolicies = user_policy_col.find(query)
        userPolicy_ids = []
        for userPolicy in userPolicies:
            userPolicy_ids.append({"userPolicy_id": userPolicy['_id']})
            query = {"$or": userPolicy_ids}
    elif session['role'] == "Admin":
        query = {"userPolicy_id": ObjectId(userPolicy_id)}
    user_climes = user_climes_col.find(query)
    return render_template("viewUserClimes.html", user_climes=user_climes, userPolicy_id=userPolicy_id, get_user_policy_id=get_user_policy_id, get_hospital_id=get_hospital_id, get_clime_id_by_payment=get_clime_id_by_payment, status_user_clime_request=status_user_clime_request, status_clime_approved=status_clime_approved)


def get_user_policy_id(userPolicy_id):
    query = {'_id': ObjectId(userPolicy_id)}
    user_policy = user_policy_col.find_one(query)
    return user_policy


@app.route("/acceptClimeRequest")
def acceptClimeRequest():
    user_clime_id = ObjectId(request.args.get("user_clime_id"))
    query = {'_id': ObjectId(user_clime_id)}
    query1 = {"$set": {"status": status_clime_accepted_hospital}}
    user_climes_col .update_one(query, query1)
    return redirect("/viewUserClimes")


@app.route("/rejectClimeRequest")
def rejectClimeRequest():
    user_clime_id = ObjectId(request.args.get("user_clime_id"))
    query = {'_id': ObjectId(user_clime_id)}
    query1 = {"$set": {"status": status_clime_rejected_hospital}}
    user_climes_col .update_one(query, query1)
    return redirect("/viewUserClimes")


@app.route("/payAmount")
def payAmount():
    user_clime_id = request.args.get("user_clime_id")
    amount = request.args.get("amount")
    userPolicy_id = request.args.get("userPolicy_id")
    premium_amount = request.args.get("premium_amount")
    return render_template("payAmount.html", user_clime_id=user_clime_id, amount=amount, premium_amount=premium_amount, userPolicy_id=userPolicy_id)


@app.route("/payAmount1", methods=['post'])
def payAmount1():
    userPolicy_id = request.form.get("userPolicy_id")
    premium_amount = request.form.get("premium_amount")
    user_clime_id = request.form.get("user_clime_id")
    insurance_paid_amount = request.form.get("amount")
    date = datetime.datetime.now()
    status = status_user_clime_payment
    if session['role'] == "Admin":
        query = {"user_clime_id": ObjectId(user_clime_id), "insurance_paid_amount": insurance_paid_amount, "date": date, "status": status}
        payment_col.insert_one(query)
        query = {'_id': ObjectId(user_clime_id)}
        query1 = {"$set": {"status": status_clime_approved}}
        user_climes_col.update_one(query, query1)
    elif session['role'] == "User":
        query = {'userPolicy_id': ObjectId(userPolicy_id), "premium_amount": premium_amount, "date": date, "status": "Installment Premium Paid by User"}
        payment_col.insert_one(query)

    return render_template("msg.html", message="User PAid the Amount", color="bg-success text-white")


@app.route("/viewPayments")
def viewPayments():
    userPolicy_id = request.args.get("userPolicy_id")
    user_clime_id = request.args.get("user_clime_id")
    if session['role'] == "User":
        if user_clime_id !=None:
            query = {"user_clime_id": ObjectId(user_clime_id)}
        elif userPolicy_id!=None:
            query = {"userPolicy_id": ObjectId(userPolicy_id)}
    elif session['role'] == "Admin":
        if user_clime_id !=None:
            query = {"user_clime_id": ObjectId(user_clime_id)}
        elif userPolicy_id!=None:
            query = {"userPolicy_id": ObjectId(userPolicy_id)}
    elif session['role'] == "Hospital":
        query = {"user_clime_id": ObjectId(user_clime_id)}
    payments = payment_col.find(query)
    return render_template("viewPayments.html", payments=payments, status_user_clime_payment=status_user_clime_payment)


def get_clime_id_by_payment(user_clime_id):
    query = {"user_clime_id": ObjectId(user_clime_id)}
    count = payment_col.count_documents(query)
    return count


def get_user_clime_id(user_clime_id):
    query = {'_id': ObjectId(user_clime_id)}
    user_clime = user_climes_col.find_one(query)
    return user_clime


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")


app.run(debug=True)
