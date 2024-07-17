from flask import Flask

app = Flask(__name__)

emp = [{"name": "emp1"}, {"name": "emp2"}]


@app.route("/")
def get_emp_data():
    return emp


# @app.route("/<id>")
# def get_emp_data_id(id):
#     print(id)
#     return emp[int(id)]
