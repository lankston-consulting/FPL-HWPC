import json
import os
import random
import string
import tempfile
from datetime import datetime
from io import StringIO
from os import environ as env
from urllib.parse import quote_plus, urlencode
import random, string
import base64

import config
import pandas as pd
import requests
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, render_template, request, session, url_for
from utils.s3_helper import S3Helper
from werkzeug.exceptions import HTTPException

user_data_folder = "hwpc-user-inputs/"
user_data_output_folder = "hwpc-user-outputs/"
user_json_path = "/user_input.json"

_flask_debug = env.get("FLASK_DEBUG", default="False")
FLASK_DEBUG = _flask_debug.lower() in {"1", "t", "true"}

SECRET_KEY = env.get("SECRET_KEY")

app = Flask(__name__, template_folder="templates")
app.secret_key = env.get("FLASK_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("FSAPPS_CLIENT_ID"),
    client_secret=env.get("FSAPPS_CLIENT_SECRET"),
    redirect_uri="http://localhost:8080/login",
)

# Routing for html template files
@app.route("/index")
@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("pages/home.html", session=session.get("user"))


@app.route("/calculator", methods=["GET"])
def calculator():
    return render_template("pages/calculator.html", session=session.get("user"))


@app.route("/reference", methods=["GET"])
def test():
    return render_template("pages/reference.html", session=session.get("user"))


@app.route("/privacy", methods=["GET"])
def advanced():
    return render_template("pages/privacy.html", session=session.get("user"))


@app.route("/terms", methods=["GET"])
def references():
    return render_template("pages/terms.html", session=session.get("user"))


@app.route("/contact", methods=["GET"])
def contact():
    return render_template("contact.html", session=session.get("user"))


@app.route("/files", methods=["GET"])
def files():
    return render_template("files.html", session=session.get("user"))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    # All inputs from the UI are pulled here through with jquery Ajax
    yearly_harvest_input = request.files["yearlyharvestinput"]
    if yearly_harvest_input.filename != "":
        yearly_harvest_input = pd.read_csv(yearly_harvest_input)
        yearly_harvest_input.columns = yearly_harvest_input.columns.str.replace(" ", "")
        if len(yearly_harvest_input.columns) > 2:
            # Ensures that any long formatted data will start with YearID to begin the melt process
            yearly_harvest_input.rename(
                columns={yearly_harvest_input.columns[0]: "YearID"}, inplace=True
            )
            yearly_harvest_input = yearly_harvest_input.melt(
                id_vars="YearID", var_name="Year", value_name="ccf"
            )

            yearly_harvest_input = yearly_harvest_input[
                yearly_harvest_input["ccf"] != 0
            ]
            yearly_harvest_input = yearly_harvest_input.drop(["YearID"], axis=1)
            start_year = str(yearly_harvest_input["Year"].min())
            stop_year = str(yearly_harvest_input["Year"].max())
            for i in yearly_harvest_input.columns:
                if yearly_harvest_input[i].dropna().empty:
                    return render_template(
                        "pages/calculator.html",
                        error="Missing Column Data in File: Harvest Data Column: " + i,
                    )

            yearly_harvest_input = yearly_harvest_input.to_csv(index=False)
        else:
            yearly_harvest_input.rename(
                columns={
                    yearly_harvest_input.columns[0]: "Year",
                    yearly_harvest_input.columns[1]: "ccf",
                },
                inplace=True,
            )
            for i in yearly_harvest_input.columns:
                if yearly_harvest_input[i].dropna().empty:
                    return render_template(
                        "pages/calculator.html",
                        error="Missing Column Data in File: Harvest Data Column: " + i,
                    )

            start_year = str(yearly_harvest_input["Year"].min())
            stop_year = str(yearly_harvest_input["Year"].max())
            yearly_harvest_input = yearly_harvest_input.to_csv(index=False)

    harvest_data_type = request.form["harvestdatatype"]
    timber_product_ratios = request.files["yearlytimberproductratios"]

    if timber_product_ratios.filename != "":
        timber_product_ratios = pd.read_csv(timber_product_ratios)
        timber_product_ratios.columns = timber_product_ratios.columns.str.replace(
            " ", ""
        )
        if len(timber_product_ratios.columns) > 3:
            # Ensures that any long formatted data will start with TimberProductID to begin the melt process
            timber_product_ratios.rename(
                columns={timber_product_ratios.columns[0]: "TimberProductID"},
                inplace=True,
            )
            timber_product_ratios = timber_product_ratios.melt(
                id_vars="TimberProductID", var_name="Year", value_name="Ratio"
            )
            timber_product_ratios.rename(
                columns={
                    timber_product_ratios.columns[0]: "TimberProductID",
                    timber_product_ratios.columns[1]: "Year",
                    timber_product_ratios.columns[2]: "Ratio",
                },
                inplace=True,
            )
            for i in timber_product_ratios.columns:
                if timber_product_ratios[i].dropna().empty:
                    return render_template(
                        "pages/calculator.html",
                        error="Missing Column Data in File: Timber Product Ratios Column: "
                        + i,
                    )
            timber_product_ratios = timber_product_ratios.to_csv(index=False)

        else:
            timber_product_ratios.rename(
                columns={
                    timber_product_ratios.columns[0]: "TimberProductID",
                    timber_product_ratios.columns[1]: "Year",
                    timber_product_ratios.columns[2]: "Ratio",
                },
                inplace=True,
            )
            for i in timber_product_ratios.columns:
                if timber_product_ratios[i].dropna().empty:
                    return render_template(
                        "pages/calculator.html",
                        error="Missing Column Data in File: Timber Product Ratios Column: "
                        + i,
                    )
            timber_product_ratios = timber_product_ratios.to_csv(index=False)

    region_selection = request.form["regionselection"]
    if region_selection == "Custom":
        custom_region_file = request.files["customregion"]
        if custom_region_file.filename != "":
            custom_region_file = pd.read_csv(custom_region_file)
            custom_region_file.columns = custom_region_file.columns.str.replace(" ", "")
            if len(custom_region_file.columns) > 3:
                # Ensures that any long formatted data will start with PrimaryProductID to begin the melt process
                custom_region_file.rename(
                    columns={custom_region_file.columns[0]: "PrimaryProductID"},
                    inplace=True,
                )
                custom_region_file = custom_region_file.melt(
                    id_vars="PrimaryProductID", var_name="Year", value_name="Ratio"
                )
                for i in custom_region_file.columns:
                    if custom_region_file[i].dropna().empty:
                        return render_template(
                            "pages/calculator.html",
                            error="Missing Column Data in File: Primary Product Ratios Column: "
                            + i,
                        )
                custom_region_file = custom_region_file.to_csv(index=False)
            else:
                custom_region_file.rename(
                    columns={
                        custom_region_file.columns[0]: "PrimaryProductID",
                        custom_region_file.columns[1]: "Year",
                        custom_region_file.columns[2]: "Ratio",
                    },
                    inplace=True,
                )
                for i in custom_region_file.columns:
                    if custom_region_file[i].dropna().empty:
                        return render_template(
                            "pages/calculator.html",
                            error="Missing Column Data in File: Primary Product Ratios Column: "
                            + i,
                        )
                custom_region_file = custom_region_file.to_csv(index=False)
    else:
        custom_region_file = ""
    end_use_product_ratios = request.files["EndUseRatiosFilename"]
    if end_use_product_ratios.filename != "":
        end_use_product_ratios = pd.read_csv(end_use_product_ratios)
        end_use_product_ratios.columns = end_use_product_ratios.columns.str.replace(
            " ", ""
        )
        if len(end_use_product_ratios.columns) > 3:
            # Ensures that any long formatted data will start with EndUseID to begin the melt process
            end_use_product_ratios.rename(
                columns={end_use_product_ratios.columns[0]: "EndUseID"}, inplace=True
            )
            end_use_product_ratios = end_use_product_ratios.melt(
                id_vars="EndUseID", var_name="Year", value_name="Ratio"
            )
            for i in end_use_product_ratios.columns:
                if end_use_product_ratios[i].dropna().empty:
                    return render_template(
                        "pages/calculator.html",
                        error="Missing Column Data in File: End Use Product Ratios Column: "
                        + i,
                    )
            end_use_product_ratios = end_use_product_ratios.to_csv(index=False)
        else:
            end_use_product_ratios.rename(
                columns={
                    end_use_product_ratios.columns[0]: "EndUseID",
                    end_use_product_ratios.columns[1]: "Year",
                    end_use_product_ratios.columns[2]: "Ratio",
                },
                inplace=True,
            )
            for i in end_use_product_ratios.columns:
                if end_use_product_ratios[i].dropna().empty:
                    return render_template(
                        "pages/calculator.html",
                        error="Missing Column Data in File: End Use Product Ratios Column: "
                        + i,
                    )
            end_use_product_ratios = end_use_product_ratios.to_csv(index=False)

    if request.form.get("enduseproductrates"):
        end_use_product_rates = request.form["enduseproductrates"]

    dispositions = request.files["DispositionsFilename"]
    disposition_half_lives = request.files["DispositionHalfLivesFilename"]
    burned_ratios = request.files["BurnedRatiosFilename"]
    mbf_to_ccf = request.files["MbfToCcfFilename"]
    loss_factor = request.form["lossfactor"]
    temp_loss_factor = float(loss_factor)
    temp_loss_factor = temp_loss_factor / 100.0
    loss_factor = str(temp_loss_factor)
    iterations = request.form["iterations"]
    email = request.form["email"]
    run_name = request.form["runname"]
    run_name = run_name.replace(" ", "_")

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%YT%H:%M:%S")
    new_id = str(run_name + "-" + dt_string)
    # The data is compiled to a dictionary to be processed with the S3Helper class
    data = {
        "harvest_data.csv": yearly_harvest_input,
        "harvest_data_type": harvest_data_type,
        "timber_product_ratios.csv": timber_product_ratios,
        "region": region_selection,
        "primary_product_ratios.csv": custom_region_file,
        "end_use_product_ratios.csv": end_use_product_ratios,
        "decay_function": end_use_product_rates,
        "discard_destinations.csv": dispositions,
        "discard_destination_ratios.csv": disposition_half_lives,
        # "distribution_data.csv":distribution_data,
        "discard_burned_w_energy_capture.csv": burned_ratios,
        "mbf_to_ccf_conversion.csv": mbf_to_ccf,
        "end_use_loss_factor": loss_factor,
        "iterations": iterations,
        "email": email,
        "scenario_name": run_name,
        "simulation_date": dt_string,
        "start_year": start_year,
        "end_year": stop_year,
        "user_string": new_id,
    }

    S3Helper.upload_input_group("hwpc", user_data_folder + new_id + "/", data)
    return render_template("pages/submit.html")


@app.route("/submit")
def submit():
    return render_template("pages/submit.html", session=session.get("user"))


@app.route("/set-official", methods=["GET"])
def set_official():
    p = request.args.get("p")
    data_json = S3Helper.download_file("hwpc", user_data_folder + p + user_json_path)
    deliver_json = {}
    with open(data_json.name, "r+") as f:
        data = json.load(f)
        data["is_official_record"] = "true"
        deliver_json = json.dumps(data)
    deliver_json = deliver_json.encode()
    user_file = tempfile.TemporaryFile()
    user_file.write(deliver_json)
    user_file.seek(0)
    S3Helper.upload_file(user_file, "hwpc", user_data_folder + p + user_json_path)
    user_file.close()


@app.route("/output", methods=["GET"])
def output():
    is_single = "false"
    p = request.args.get("p")
    q = request.args.get("q")
    y = request.args.get("y")
    print(p)
    print(q)
    data_dict = {}
    if y == None:
        user_json = S3Helper.download_file(
            "hwpc", user_data_folder + p + user_json_path
        )
        user_json = json.dumps(user_json.read().decode("utf-8"))

        user_zip = S3Helper.read_zipfile(
            "hwpc-output", user_data_output_folder + p + "/results/" + q + ".zip"
        )
        for file in user_zip:
            if ".csv" in file and "results" not in file:
                csv_string_io = StringIO(user_zip[file])
                test = pd.read_csv(csv_string_io, sep=",", header=0)
                try:
                    test = test.drop(columns="DiscardDestinationID")
                except Exception as e:
                    print("Missing Discard Destination ID: " + str(e))
                test.drop(test.tail(1).index, inplace=True)
                test = test.loc[:, ~test.columns.str.contains("^Unnamed")]
                data_dict[file[:-4]] = test.to_csv(index=False)

        data_json = json.dumps(data_dict)

        data_json = data_json.replace('\\"', " ")
    if y != None:
        print("years: " + y)
        is_single = "true"

        user_json = S3Helper.download_file(
            "hwpc", user_data_folder + p + user_json_path
        )
        user_json = json.dumps(user_json.read().decode("utf-8"))

        user_zip = S3Helper.read_zipfile(
            "hwpc-output",
            user_data_output_folder + p + "/results/" + y + "_" + q + ".zip",
        )

        for file in user_zip:
            if ".csv" in file and y in file and "results" not in file:
                print(file[:-4])
                csv_string_io = StringIO(user_zip[file])
                test = pd.read_csv(csv_string_io, sep=",", header=0)
                try:
                    print("Missing Discard Destination ID: " + str(e))
                    test = test.drop(columns="DiscardDestinationID")
                except Exception as e:
                    print(str(e))
                    data_dict[file[5:-4]] = test.to_csv(index=False)
        data_json = json.dumps(data_dict)

        data_json = data_json.replace('\\"', " ")

    return render_template(
        "pages/output.html",
        data_json=data_json,
        bucket=p,
        file_name=q,
        is_single=is_single,
        scenario_json=user_json,
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )


@app.route("/")
@app.route("/login", methods=["GET"])
def login():
    state = "".join(random.choices(string.ascii_letters + string.digits, k=6))

    authorized_code = request.args.get("code")

    if authorized_code is not None:
        print(f"Caught code {authorized_code}")
        print(env.get("FSAPPS_CLIENT_ID")+":"+env.get("FSAPPS_CLIENT_SECRET"))
        url = "https://fsapps-stg.fs2c.usda.gov/oauth/token"

        payload = {
            "grant_type": env.get("FSAPPS_GRANT_TYPE"),
            "redirect_uri": env.get("FSAPPS_REDIRECT_URI"),
            "code": f"{authorized_code}",
        }
        files = []
        headers = {
            "Authorization": "basic "+ base64.b64encode(env.get("FSAPPS_CLIENT_ID")+":"+env.get("FSAPPS_CLIENT_SECRET")),
            "Accept": env.get("FSAPPS_ACCEPT"),
        }

        response = requests.request(
            "POST", url, headers=headers, data=payload, files=files
        )
        
        print("RESPONSE")
        print(response.text)

        return home()

    return render_template(
        "pages/login.html",
        url="https://fsapps-stg.fs2c.usda.gov/oauth/authorize?client_id=HWPCLOCAL&redirect_uri=http://localhost:8080/login&response_type=code&state="
        + state,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template("pages/404.html", title="404"), 404


@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return render_template("pages/500.html", e=e), 500


if __name__ == "__main__":

    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="0.0.0.0", port=int(env.get("PORT", 8080)), debug=FLASK_DEBUG)
