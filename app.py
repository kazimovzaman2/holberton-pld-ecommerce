from flask import Flask, request, jsonify
from models import db, User, Role, Company
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

SECRET_KEY = "secret"

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:postgres@localhost:5432/admindash"
)
app.config["SECRET_KEY"] = SECRET_KEY

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        user.generate_token()
        return jsonify({"token": user.token, "role": user.role.name})
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "GET":
        admin = User.query.filter_by(role=Role.ADMIN).all()

        return jsonify(
            [
                {
                    "name": a.name,
                    "surname": a.surname,
                    "email": a.email,
                    "role": Role.ADMIN.name,
                }
                for a in admin
            ]
        )
    elif request.method == "POST":
        data = request.json
        admin = User(
            name=data["name"],
            surname=data["surname"],
            email=data["email"],
            password=data["password"],
            role=Role.ADMIN,
        )
        db.session.add(admin)
        db.session.commit()

        return jsonify(
            {
                "message": "Admin created successfully",
                "data": {
                    "name": admin.name,
                    "surname": admin.surname,
                    "email": admin.email,
                    "role": Role.ADMIN.name,
                },
            }
        )


@app.route("/user", methods=["GET", "POST"])
def user():
    if request.method == "GET":
        user = User.query.filter_by(role=Role.USER).all()

        return jsonify(
            [
                {
                    "name": u.name,
                    "surname": u.surname,
                    "email": u.email,
                    "role": Role.USER.name,
                }
                for u in user
            ]
        )
    elif request.method == "POST":
        data = request.json
        user = User(
            name=data["name"],
            surname=data["surname"],
            email=data["email"],
            password=data["password"],
            role=Role.USER,
        )
        db.session.add(user)
        db.session.commit()

        return jsonify(
            {
                "message": "User created successfully",
                "data": {
                    "name": user.name,
                    "surname": user.surname,
                    "email": user.email,
                    "role": Role.USER.name,
                },
            }
        )


@app.route("/company", methods=["GET", "POST"])
def company():
    if request.method == "GET":
        company = Company.query.all()

        return jsonify(
            [
                {
                    "name": c.user.name,
                    "surname": c.user.surname,
                    "email": c.user.email,
                    "role": c.user.role.name,
                    "company_name": c.company_name,
                    "company_address": c.company_address,
                    "token": c.user.token,
                }
                for c in company
            ]
        )
    elif request.method == "POST":
        data = request.json
        user = User(
            name=data["name"],
            surname=data["surname"],
            email=data["email"],
            password=data["password"],
            role=Role.COMPANY,
        )
        company = Company(
            company_name=data["company_name"],
            company_address=data["company_address"],
            user=user,
        )
        db.session.add(company)
        db.session.commit()

        return jsonify(
            {
                "message": "Company created successfully",
                "data": {
                    "id": company.id,
                    "name": user.name,
                    "surname": user.surname,
                    "email": user.email,
                    "role": Role.COMPANY.name,
                    "company_name": company.company_name,
                    "company_address": company.company_address,
                },
            }
        )


@app.route("/approve/<company_id>", methods=["POST"])
def approve(company_id):
    request_data = request.json

    company = Company.query.get(company_id)
    if company is None:
        return jsonify({"error": "Company not found"}), 404
    elif company.is_active:
        return jsonify({"error": "Company already approved"}), 400

    if request_data.get("approve") == False:
        return jsonify({"error": "Request blocked"}), 400

    company.is_active = True
    db.session.commit()

    return jsonify(
        {
            "message": "Company approved successfully",
            "data": {
                "name": company.user.name,
                "surname": company.user.surname,
                "email": company.user.email,
                "role": company.user.role.name,
                "company_name": company.company_name,
                "company_address": company.company_address,
                "is_active": company.is_active,
            },
        }
    )


@app.route("/approve-waiting", methods=["GET"])
def approve_waiting():
    company = Company.query.filter_by(is_active=False).all()

    return jsonify(
        [
            {
                "name": c.user.name,
                "surname": c.user.surname,
                "email": c.user.email,
                "role": c.user.role.name,
                "company_name": c.company_name,
                "company_address": c.company_address,
                "is_active": c.is_active,
            }
            for c in company
        ]
    )


if __name__ == "__main__":
    app.run(debug=True)
