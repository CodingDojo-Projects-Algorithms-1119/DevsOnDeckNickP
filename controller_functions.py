from flask import Flask, render_template, request, redirect, flash, session
from config import db
from models import Developer, Organization, Position, Language
from sqlalchemy.sql import func
from config import EMAIL_REGEX, password_reg, bcrypt


def logout():
    session.clear()
    pmall = Position.query.all()
    dmall = Developer.query.all()
    for pm in pmall:
        if pm.match:
            pm.match = None
            db.session.commit()
    for dm in dmall:
        if dm.match:
            dm.match = None
            db.session.commit()
    return redirect("/")
def index():
    devs = Developer.query.all()
    orgs = Organization.query.all()
    lang = Language.query.all()
    if not lang:
        print("lang empty")
        Language.fillLangauges()
    return render_template("register.html", lang=lang, devs=devs, orgs = orgs)
def login_page():
    return render_template("login.html")
def login_check():
    switch = request.form["switch"]
    if switch == "dev":
        user = Developer.query.filter_by(email=request.form["email"]).all()
    elif switch == "org":
        user = Organization.query.filter_by(email=request.form["email"]).all()
    for user_login in user:
        print(user_login.fname)
        print(user_login.lname)
        print(user_login.password)
        print(request.form["password"])

    if user:
        hashed_pw = user[0].password
        if bcrypt.check_password_hash(hashed_pw, request.form['password']):
            session["user_id"] = {
                "first": user[0].fname,
                "lname": user[0].lname,
                "email":user[0].email,
                "id": user[0].id,
                "role": switch
                }
            print("ID:", session["user_id"])
            if switch == "dev":
                return redirect("/dev_dash")
            elif switch == "org":
                return redirect("/{}_landing".format(switch))
        else:
            flash("Invalid Password", "login")
            return redirect("/login_page#{}_log".format(switch))
    else:
        flash("Email not registered", "login")
        return redirect("/login_page#{}_log".format(switch)) 
def register():
    switch = request.form["switch"]
    print(switch)
    is_valid = True
    if switch == "org":
        email = Organization.query.filter_by(email = request.form["email"]).all()
        email2 = Developer.query.filter_by(email = request.form["email"]).all()
        if len(request.form["orgname"]) == 0:
            is_valid = False
            flash("Organization name cannot be blank", "reg")
    elif switch == "dev":
        email = Developer.query.filter_by(email = request.form["email"]).all()
        email2 = Organization.query.filter_by(email = request.form["email"]).all()
    if email:
        is_valid = False
        flash("Email in use")
    if email2:
        is_valid = False
        if switch == "dev":
            flash("Email registered as an Organization")
        if switch == "org":
            flash("Email registered as a Developer")
    if not request.form["fname"].isalpha() or not len(request.form["fname"]) >=2:
        is_valid = False
        flash("First name can only contain letters and must be at least 2 characters long", "reg")
    if not request.form['lname'].isalpha() or not len(request.form['lname']) >= 2:
        is_valid = False
        flash("Last name can only contain letters and must be at least 2 characters long", "reg")
    if not EMAIL_REGEX.match(request.form["email"]):
        is_valid = False
        flash("Invalid Email Address")
    if not len(request.form['address']) > 5:
        is_valid = False
        flash("Address must be longer than 5 characters", "reg")                
    if not len(request.form['city']) >= 2:
        is_valid = False
        flash("City name must be at least 3 characters long", "reg")
    if not password_reg.match(request.form["password"]):
        is_valid = False
        flash("Password should be at least 5 characters, have one number, one uppercase and one lowercase letter, and one symbol")                
    if request.form["password"] != request.form["confirmpass"]:
        is_valid = False
        flash("Passwords do not match", "reg")
    if is_valid:
        pw_hash = bcrypt.generate_password_hash(request.form["password"])
        if switch == "dev":
            user = Developer(
                fname= request.form["fname"],
                lname= request.form["lname"],
                email= request.form["email"],
                address = request.form["address"],
                city = request.form["city"],
                state = request.form["state"],
                password= pw_hash
                )
        elif switch == "org":
            user = Organization(
                orgname= request.form["orgname"],
                fname= request.form["fname"],
                lname= request.form["lname"],
                email= request.form["email"],
                address = request.form["address"],
                city = request.form["city"],
                state = request.form["state"],
                password= pw_hash
                )          
        db.session.add(user)
        db.session.commit()
        session["user_id"] = {
            "fname": user.fname,
            "lname": user.lname,
            "email": user.email,
            "id": user.id,
            "role": switch
        }          
        return redirect("/{}_landing".format(switch))
    return redirect("/#{}_reg".format(switch))
    # return render_template("{}Signup.html".format(switch))
def dev_landing():
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "dev":
        return redirect("/logout")
    user = Developer.query.filter_by(id=(session["user_id"]["id"])).all()
    dev_langs  = Language.query.all()
    return render_template("devLanding.html", user = user[0], dev_langs = dev_langs)
def org_landing():
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "org":
        return redirect("/logout")        
    if "position_id" in session:
        session.pop("position_id")
    user = Organization.query.filter_by(email=(session["user_id"]["email"])).all()
    positions = Position.query.filter_by(owner_id = (session["user_id"]["id"]))
    all_devs = Developer.query.all()
    return render_template("orgLanding.html", user=user[0], devs=all_devs, positions = positions)
def create_dev_bio():
    if session["user_id"]["role"] != "dev":
        return redirect("/logout")     
    print(request.form["dev_bio"])
    is_valid = True
    if not request.form["dev_bio"]:
        is_valid = False
        flash("You cannot post an empty bio.")
    if len(request.form["dev_bio"]) > 600:
        flash("Bio must be under 600 characters.")
        is_valid = False
    if is_valid:
        Developer.query.get(session["user_id"]["id"]).bio = request.form["dev_bio"]
        db.session.commit()   
        return redirect("/dev_dash")
    return redirect("/dev_landing")
def dev_add_lang(lang_id):
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "dev":
        return redirect("/logout")     
    lang = Language.query.get(lang_id)
    dev = Developer.query.get(session["user_id"]["id"])
    if session["user_id"]["email"] != dev.email:
        return redirect("/logout")
    dev.langs.append(lang)
    db.session.commit()
    return redirect("/dev_landing")
def dev_remove_lang(lang_id):
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "dev":
        return redirect("/logout")     
    lang = Language.query.get(lang_id)
    dev = Developer.query.get(session["user_id"]["id"])
    dev.langs.remove(lang)
    db.session.commit()
    return redirect("/dev_landing")
def pos_add_lang(lang_id):
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "org":
        return redirect("/logout")     
    lang = Language.query.get(lang_id)
    pos = Position.query.get(session["position_id"]["id"])
    pos.langs.append(lang)
    db.session.commit()
    return redirect("/edit_position/{}".format(session["position_id"]["id"]))   
def pos_remove_lang(lang_id):
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "org":
        return redirect("/logout")     
    lang = Language.query.get(lang_id)
    pos = Position.query.get(session["position_id"]["id"])
    pos.langs.remove(lang)
    db.session.commit()
    return redirect("/edit_position/{}".format(session["position_id"]["id"]))    
def dev_dash():
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "dev":
        return redirect("/logout")         
    user = Developer.query.get((session["user_id"]["id"]))
    positions = Position.query.all()
    for position in positions:
        count = 0
        for poslang in position.langs:
            for lang in user.langs:
                if lang.lang_id == poslang.lang_id:
                    count = count+1
        match = int(count/(len(position.langs))*100)
        insert_match = Position.query.get(position.position_id)
        insert_match.match = match
        db.session.commit()    
    return render_template("devDash.html", user=user, positions=positions)
def org_add_pos():
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "org":
        return redirect("/logout")         
    org = Organization.query.get(session["user_id"]["id"])
    return render_template("positionNew.html", org = org)
def new_position():
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "org":
        return redirect("/logout")    
    req_langs = request.form.getlist("pos_lang")
    for i in range(0, len(req_langs)):
        req_langs[i] = int(req_langs[i])
    print("languages", req_langs)
    is_valid = True
    if not len(request.form["title"]) >= 2:
        is_valid = False
        flash("You Job Title must be at least 3 characters long")
    if not request.form["description"]:
        is_valid = False
        flash("You cannot post an empty job description.")
    if len(request.form["description"]) > 1000:
        flash("Job Description must be under 1000 characters.")
        is_valid = False
    if is_valid:
        new_position = Position(
            name=request.form["title"],
            description=request.form["description"],
            owner_id = session["user_id"]["id"]
        )
        db.session.add(new_position)
        db.session.commit()
        print(new_position.position_id)
        cur_pos = Position.query.get(new_position.position_id)
        for i in range(0, len(req_langs)):
            lang_to_add = Language.query.get(req_langs[i])
            cur_pos.langs.append(lang_to_add)
            db.session.commit()
        return redirect ("/org_landing")
    return redirect("/org_add_pos")
def edit_position(pos_id):
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "org":
        return redirect("/logout")        
    pos_to_edit = Position.query.get(pos_id)
    if session["user_id"]["id"] != pos_to_edit.owner.id:
        return redirect("/")
    session["position_id"] = {
        "id": pos_to_edit.position_id
    }
    return render_template("positionEdit.html", pos=pos_to_edit)
def val_edit_pos(pos_id):
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "org":
        return redirect("/logout")
    is_valid = True
    print(request.form["description"])
    if not len(request.form["title"]) >= 2:
        is_valid = False
        flash("You Job Title must be at least 3 characters long")
    if not request.form["description"]:
        is_valid = False
        flash("You cannot post an empty job description.")
    if len(request.form["description"]) > 1000:
        flash("Job Description must be under 1000 characters.")
        is_valid = False
    if is_valid:
        pos_to_edit = Position.query.get(pos_id)
        if session["user_id"]["id"] != pos_to_edit.owner.id:
            return redirect("/logout")
        pos_to_edit.name = request.form["title"]
        pos_to_edit.description = request.form["description"]
        db.session.commit()
        return redirect ("/org_landing")
    return redirect("/edit_position/{}".format(pos_id))
def del_position(pos_id):
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "org":
        return redirect("/logout")
    pos_to_del = Position.query.get(pos_id)
    if session["user_id"]["id"] != pos_to_del.owner.id:
        return redirect("/")
    print(pos_to_del.position_id, pos_to_del.name, pos_to_del.description, pos_to_del.owner_id, pos_to_del.owner.id)
    if pos_to_del.owner.id == session["user_id"]["id"]:
        pos_owner= pos_to_del.owner
        pos_owner.org_positions.remove(pos_to_del)
        db.session.commit()
    test_clean = Position.query.filter_by(owner_id=None).all()
    for test_case in test_clean:
        db.session.delete(test_case)
        db.session.commit()
    return redirect("/org_landing")
def position_details(pos_id):
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "org":
        return redirect("/logout")        
    listing = Position.query.get(pos_id)
    if session["user_id"]["id"] != listing.owner.id:
        return redirect("/")
    devs = Developer.query.all()
    for dev in devs:
        count = 0
        for lang in listing.langs:
            for devlang in dev.langs:
                if lang.lang_id == devlang.lang_id:
                    count = count+1
        match = int(count/(len(listing.langs))*100)
        insert_match = Developer.query.get(dev.id)
        insert_match.match = match
        db.session.commit()
        print("Name:", dev.fname, "match:", dev.match)
    return render_template("positionDetails.html", listing=listing, devs = devs)
def apply(pos_id):
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "dev":
        return redirect("/logout") 
    pos = Position.query.get(pos_id)
    dev = Developer.query.get(session["user_id"]["id"])
    # pos.applied.append(dev)
    dev.applied.append(pos)
    db.session.commit()
    return redirect("/dev_dash")
def unapply(pos_id):
    if "user_id" not in session:
        return redirect("/")
    if session["user_id"]["role"] != "dev":
        return redirect("/logout")
    pos = Position.query.get(pos_id)
    print("POS:", pos.position_id)
    dev = Developer.query.get(session["user_id"]["id"])
    # pos.applied.append(dev)
    dev.applied.remove(pos)
    db.session.commit()
    return redirect("/dev_dash")

# for adding ajax later
def email_check():
    print("checkpoint")
    found = False
    user = Developer.query.filter_by(email=request.form["email"]).all()
    if user:
        found = True
    return render_template("partials/invalid.html", found = found)
