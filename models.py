from config import db
from sqlalchemy.sql import func, desc

lang_table = db.Table("lang_table",
    db.Column("lang_id", db.Integer, db.ForeignKey("languages.lang_id"), primary_key=True),
    db.Column("dev_id", db.Integer, db.ForeignKey("devs.id"), primary_key=True)
)

position_lang = db.Table("position_lang",
    db.Column("lang_id", db.Integer, db.ForeignKey("languages.lang_id"), primary_key=True),
    db.Column("pos_id", db.Integer, db.ForeignKey("positions.position_id"), primary_key=True)
)

applied_table = db.Table("applied_table",
    db.Column("dev_id", db.Integer, db.ForeignKey("devs.id"), primary_key=True),
    db.Column("pos_id", db.Integer, db.ForeignKey("positions.position_id"), primary_key = True)
)

class Developer(db.Model):
    __tablename__ = "devs"
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(45))
    lname = db.Column(db.String(45))
    email = db.Column(db.String(255))
    address = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(2))
    password = db.Column(db.String(255))
    bio = db.Column(db.String(600))
    match = db.Column(db.Integer)
    langs = db.relationship("Language", secondary = lang_table)
    applied = db.relationship("Position", secondary = applied_table)
    created_at = db.Column(db.DateTime, server_default=func.now())    
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    
class Organization(db.Model):
    __tablename__ = "orgs"
    id = db.Column(db.Integer, primary_key=True)
    orgname = db.Column(db.String(255))
    fname = db.Column(db.String(45))
    lname = db.Column(db.String(45))
    email = db.Column(db.String(255))    
    address = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(2))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())    
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Position(db.Model):
    __tablename__="positions"
    position_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    match = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey("orgs.id"))#, nullable=False)
    owner = db.relationship("Organization", foreign_keys=[owner_id], backref="org_positions", cascade="all")
    created_at = db.Column(db.DateTime, server_default=func.now())    
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    applied = db.relationship("Developer", secondary = applied_table)
    langs = db.relationship("Language", secondary = position_lang)  

class Language(db.Model):
    __tablename__="languages"
    lang_id = db.Column(db.Integer, primary_key=True)
    lang_name = db.Column(db.String(20))
    devs = db.relationship("Developer", secondary = lang_table)
    positions = db.relationship("Position", secondary = position_lang)

    def fillLangauges():
        langs = ["HTML", "CSS", "Ruby","Python","JavaScript","Java","C#","C++", "SQL", "Django", "Flask", "Rails"]
        for lang in langs:
            add_lang = Language(lang_name=lang)
            db.session.add(add_lang)
            db.session.commit()
        verify = "success"
        return verify

# class Framework(db.Model):
#     __tablename__="frameworks"
#     framework_id  = db.Column(db.Integer, primary_key=True)
#     frame_name = db.Column(db.String(50))

#     def fillFrameworks():
#         fws = ["django","flask","rails","spring","sql","ember","jquery","boostrap"]
#         for fw in fws:
#             add_fw = Framework(frame_name=fw)
#             db.session.add(add_fw)
#             db.session.commit()
#         verify = "success"
#         return verify