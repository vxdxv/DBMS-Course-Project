
from flask import Flask, render_template, redirect, request
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

from urllib.parse import urlparse


app = Flask(__name__)

def db_connection():
    db = psycopg2.connect(database="permalist",user="postgres",password="B220584cs*",host="localhost",port="5432")
    result = urlparse(os.getenv("POSTGRES_URI"))
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    db = psycopg2.connect(
        database=database, user=username, password=password, host=hostname, port=port
    )
    cursor = db.cursor()
    cursor.execute(
        """
                   DROP TABLE IF EXISTS Disaster, Locality, Funding_Source, Essential, Organization, Volunteer,
Shelter, Emergency_Service, Incident, Incident_Funding, Incident_Resource_Allocation, Incident_Volunteer_Allotment ;

CREATE TABLE "disaster" (
  "id" integer PRIMARY KEY,
  "name" text,
  "description" text,
  "protocol" text
);

CREATE TABLE "locality" (
  "id" integer PRIMARY KEY,
  "name" text,
  "geographical_size" text,
  "development_level" text
);

CREATE TABLE "funding_source" (
  "id" integer PRIMARY KEY,
  "name" text,
  "contract_terms" text,
  "renewal_period" integer,
  "std_amt_donated" integer,
  "contact" text,
  "type_of_organization" text
);

CREATE TABLE "essential" (
  "id" integer PRIMARY KEY,
  "name" text,
  "price_per_unit" integer,
  "qty_in_stock" integer
);

CREATE TABLE "organization" (
  "id" integer PRIMARY KEY,
  "name" text,
  "type_of_organization" text,
  "contact" text,
  "reachability" text
);

CREATE TABLE "volunteer" (
  "id" integer PRIMARY KEY,
  "name" text,
  "contact" text,
  "address" text,
  "oid" integer
);

CREATE TABLE "shelter" (
  "id" integer PRIMARY KEY,
  "lid" integer,
  "name" text,
  "contact" text,
  "address" text,
  "max_capacity" integer,
  "current_capacity" integer
);

CREATE TABLE "emergency_service" (
  "id" integer PRIMARY KEY,
  "lid" integer,
  "name" text,
  "contact" text,
  "num_of_personnel" integer,
  "speed_of_response" text
);

CREATE TABLE "incident" (
  "id" integer PRIMARY KEY,
  "did" integer,
  "lid" integer,
  "date_time" timestamp,
  "description" text,
  "severity" text,
  "status" text,
  "active" integer,
  "monitoring_bureau" text,
  "reqd_funds" integer,
  "affected_population" integer,
  "reqd_volunteers" integer
);

CREATE TABLE "incident_funding" (
  "iid" integer,
  "fid" integer
);

CREATE TABLE "incident_resource_allocation" (
  "iid" integer,
  "eid" integer
);

CREATE TABLE "incident_volunteer_allotment" (
  "iid" integer,
  "vid" integer
);

ALTER TABLE "volunteer" ADD FOREIGN KEY ("oid") REFERENCES "organization" ("id");

ALTER TABLE "shelter" ADD FOREIGN KEY ("lid") REFERENCES "locality" ("id");

ALTER TABLE "emergency_service" ADD FOREIGN KEY ("lid") REFERENCES "locality" ("id");

ALTER TABLE "incident" ADD FOREIGN KEY ("did") REFERENCES "disaster" ("id");

ALTER TABLE "incident" ADD FOREIGN KEY ("lid") REFERENCES "locality" ("id");

ALTER TABLE "incident_funding" ADD FOREIGN KEY ("iid") REFERENCES "incident" ("id");

ALTER TABLE "incident_funding" ADD FOREIGN KEY ("fid") REFERENCES "funding_source" ("id");

ALTER TABLE "incident_resource_allocation" ADD FOREIGN KEY ("iid") REFERENCES "incident" ("id");

ALTER TABLE "incident_resource_allocation" ADD FOREIGN KEY ("eid") REFERENCES "essential" ("id");

ALTER TABLE "incident_volunteer_allotment" ADD FOREIGN KEY ("iid") REFERENCES "incident" ("id");

ALTER TABLE "incident_volunteer_allotment" ADD FOREIGN KEY ("vid") REFERENCES "volunteer" ("id");

INSERT INTO "locality" VALUES (1, 'kollam', 500, 'rural');
INSERT INTO "disaster" VALUES(1, 'Flood', 'Caused usually by heavy rainfall or poor drainage management.', 'Disaster relief teams must assemble to assess the situation and organize proper drainage and rescue personnel.');
INSERT INTO "incident" VALUES(1, 1, 1, NOW(), 'Severe rainfall in the monsoon season of 24', 'High', 'Actively monitoring', 1, 'Centre for Disaster Management Kerala', 5000, 10000, 50);
                   """
    )
    db.commit()
    return db, cursor

@app.route('/')
def index():
    db, cursor = db_connection()
    cursor.execute('SELECT * FROM incident where active=1')
    results = cursor.fetchall()
    db.close()
    print(type(results[0]))
    return render_template("index.html", results=results[0])

#add incident
@app.route('/new-incident')
def show_new_incident_form():
    return render_template("add_incident.html")
# post
@app.route('/new-incident', methods=['POST'])
def new_incident():
    type_of_calamity = request.form.get('type_of_calamity')
    date = request.form.get('date')
    place = request.form.get('place')
    description = request.form.get('description')
    severity = request.form.get('severity')
    status = request.form.get('status')
    active = request.form.get('active')
    reqd_volunteers= request.form.get('reqd_volunteers')
    monitoring_bureau = request.form.get('monitoring_bureau')
    reqd_funds = request.form.get('reqd_funds')
    affected_pop = request.form.get('affected_pop')
    incident_name = request.form.get('incident_name')

    print(incident_name)

    db, cursor = db_connection()
    
    cursor.execute("select max(id) from incident")
    id=cursor.fetchone()

    cursor.execute("SELECT id FROM disaster WHERE name=%s", (type_of_calamity,))
    disaster_id = cursor.fetchone()

    cursor.execute("SELECT id FROM locality WHERE name=%s", (place,))
    locality_id = cursor.fetchone()
    
    print(id[0]+1,disaster_id[0], locality_id[0], date, description, severity, status, active,monitoring_bureau, reqd_funds, affected_pop,reqd_volunteers,incident_name)
    # Insert into Incident table
    cursor.execute(
        'INSERT INTO incident VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)',
        (id[0]+1,disaster_id[0], locality_id[0], date, description, severity, status, active,monitoring_bureau, reqd_funds, affected_pop,reqd_volunteers,incident_name)
    )
    db.commit()
    db.close()
    return redirect("/successfully-entered-page")


#add and update shelter
#get add shelter page
@app.route('/add-shelter')
def show_add_shelter():
    return render_template("add_shelter.html")

# post ()
@app.route('/add-shelter', methods=['POST'])
def add_shelter():
    place = request.form.get('place')
    name = request.form.get('name')
    contact=request.form.get('contact')
    address = request.form.get('address')
    max_capacity=request.form.get('max_capacity')

    print(type(max_capacity))
    print("Veda")
    db, cursor = db_connection()

    # Fetch Locality ID
    cursor.execute("SELECT id FROM locality WHERE name=%s", (place,))
    locality_id = cursor.fetchone()
    
    if(not locality_id):
        return "Sorry locality not found"
    else:
        # Insert into shleter table
        cursor.execute("select max(id) from shelter")
        id=cursor.fetchone()
        cursor.execute(
            'INSERT INTO shelter VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (id[0]+1,locality_id[0], name, contact, address, max_capacity, str(0),
            )
        )
        db.commit()
        db.close()
        return redirect("/successfully-entered-page")
        

@app.route('/update-shelter', methods=['POST'])
def update_shelter():
    place = request.form.get('place')
    name = request.form.get('name')
    contact=request.form.get('contact')
    no_new_ppl = request.form.get('no_new_ppl')
    db, cursor = db_connection()

    cursor.execute("SELECT id FROM locality WHERE name=%s", (place,))
    locality_id = cursor.fetchone()
    if(not locality_id):
        return "Sorry locality not found"
    
    else:
        cursor.execute("select id from shelter where name=%s and contact=%s",(name,contact,))
        id=cursor.fetchone()
        cursor.execute("select max_capacity,current_capacity from shelter where id=%s",(id,))
        result=cursor.fetchone()
        if(result[0]>=result[1]):
            return "Sorry cant add"
        cursor.execute(
        'update shelter set current_capacity=current_capacity+%s where id=%s',
        (no_new_ppl,id[0],)
        )
        db.commit()
        db.close()
        return redirect("/successfully-entered-page")
   

@app.route("/donate-fund-indi", methods=["POST"])
def donate_fund_indi():
    name = request.form.get('name')
    contact = request.form.get('contact')
    std_amt_donated = request.form.get('std_amt_donated')
    incident_name = request.form.get('incident_name')
    
    db, cursor = db_connection()
    cursor.execute("SELECT MAX(id) FROM funding_source")
    max_id = cursor.fetchone()[0]
    new_fund_id = max_id + 1 if max_id is not None else 1
    cursor.execute("SELECT id FROM incident WHERE LOWER(incident_name) LIKE %s", (f"%{incident_name.lower()}%",))
    cursor.execute(
        "SELECT id FROM incident WHERE LOWER(incident_name) LIKE %s",
        (f"%{incident_name.lower()}%",),
    )
    iid = cursor.fetchone()
    if not iid:
        return "Could not add: Incident not found."

    cursor.execute("SELECT id FROM funding_source WHERE name=%s", (name,))
    funding_id = cursor.fetchone()

    if funding_id is None:
        # Insert new funding source if not found
        cursor.execute(
            "INSERT INTO funding_source (id, name, contact, type_of_organization) VALUES (%s, %s, %s,%s)",
            (new_fund_id, name, contact, "Individual")
        )
        funding_id = (new_fund_id,)  

    cursor.execute(
        "INSERT INTO incident_funding (iid, fid, std_amt_donated, amt_left) VALUES (%s, %s, %s, %s)",
        (iid[0], funding_id[0], std_amt_donated, std_amt_donated)
    )

    db.commit()
    db.close()
    return redirect("/successfully-entered-page")


@app.route('/donate-fund-org', methods=['POST'])
def donate_fund_org():
    name = request.form.get('name')
    contact = request.form.get('contact')
    std_amt_donated = request.form.get('std_amt_donated')
    incident_name = request.form.get('incident_name')
    contract_terms = request.form.get('contract_terms')
    renewal_period = request.form.get('renewal_period')
    type_of_organisation = request.form.get('type_of_organisation')

    db, cursor = db_connection()

    # Get the next funding source ID
    cursor.execute("SELECT MAX(id) FROM funding_source")
    max_id = cursor.fetchone()[0]
    if(not max_id):
        new_fund_id=1
    new_fund_id = max_id + 1 

    # Fetch the incident ID
    cursor.execute("SELECT id FROM incident WHERE LOWER(incident_name) LIKE %s", (f"%{incident_name.lower()}%",))
    iid = cursor.fetchone()
    if not iid:
        return "Incident not found, could not add funding."
    
    # Check if funding source already exists
    cursor.execute("SELECT id FROM funding_source WHERE name=%s", (name,))
    funding_id = cursor.fetchone()

    if funding_id is None:
        # Insert new funding source if not found
        cursor.execute(
            "INSERT INTO funding_source (id, name, contract_terms, renewal_period, contact, type_of_organization) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (new_fund_id, name, contract_terms, renewal_period, contact, type_of_organisation)
        )
        funding_id = (new_fund_id,)  # Set funding_id for later use

    # Insert into incident_funding
    cursor.execute(
        "INSERT INTO incident_funding (iid, fid, std_amt_donated, amt_left) VALUES (%s, %s, %s, %s)",
        (iid[0], funding_id[0], std_amt_donated, std_amt_donated)
    )
    
    db.commit()
    db.close()
    return redirect("/successfully-entered-page")

#get fund alloc page
@app.route('/fund-alloc')
def show_fund_alloc():
    return render_template("fund_alloc.html")



@app.route('/fund-alloc', methods=['POST'])
def fund_alloc():
    incident_name = request.form.get('incident_name')
    fund = request.form.get('fund') # Ensure fund is treated as a numeric value
    
    db, cursor = db_connection()
    
    # Fetch the incident ID
    cursor.execute("SELECT id FROM incident WHERE LOWER(incident_name) LIKE %s", (f"%{incident_name.lower()}%",))
    iid = cursor.fetchone()
    
    if not iid:
        return "Incident not found"
    
    # Check if required funds are sufficient
    cursor.execute("SELECT reqd_funds FROM incident WHERE id=%s", (iid[0],))
    result = cursor.fetchone()
    print(type(result))

    if result[0] == 0 or result[0] < int(fund):
        return "Sorry, cannot allocate the requested fund amount"

    # Fetch funding sources linked to the incident
    cursor.execute("SELECT fid FROM incident_funding WHERE iid=%s", (iid[0],))
    funding_sources = cursor.fetchall()

    for funding_source in funding_sources:
        fid = funding_source[0]  # Extract funding source ID from tuple
        
        # Get the amount left in each funding source
        cursor.execute("SELECT amt_left FROM incident_funding WHERE fid=%s and iid=%s", (fid,iid[0]))
        amt_left = cursor.fetchone()[0]
        
        # Calculate remaining funds
        temp = int(fund) - int(amt_left)
        
        if temp >= 0:
            # If funds are fully used, delete the allocation entry
            cursor.execute("DELETE FROM incident_funding WHERE fid=%s AND iid=%s", (fid, iid[0]))
        else:
            # Otherwise, update the remaining amount in the allocation
            cursor.execute(
                "UPDATE incident_funding SET amt_left=%s WHERE fid=%s AND iid=%s",
                (int(int(amt_left) - int(fund)), fid, iid[0])
            )
            fund = 0  # Set remaining fund to zero since allocation is complete
            break  # Stop looping since the allocation is satisfied
    
        # Update fund variable for the next iteration if needed
        fund = temp

    db.commit()
    db.close()
    return redirect("/successfully-entered-page")

    






# Volunteer signup
@app.route('/volunteer-signup', methods=['POST'])
def volunteer_signup():
    name = request.form.get('name')
    contact = request.form.get('contact')
    address = request.form.get('address')
    oid = request.form.get('oid')
    print(name,contact,address,oid)
    db, cursor = db_connection()
    cursor.execute("select max(id) from volunteer")
    id=cursor.fetchone()
    #print(id)
    cursor.execute(
        'INSERT INTO volunteer(id,name, contact, address, oid) VALUES (%s, %s, %s, %s, %s)',
        (id[0]+1,name, contact, address,oid)
    )
    db.commit()
    db.close()
    return redirect("/successfully-entered-page")



# Redirect after successful entry
@app.route('/successfully-entered-page')
def successfully_entered_page():
    return render_template("success_page.html")

#Contact page route
@app.route('/contact-us')
def contact_us():
    return render_template("contact.html")

#view locality incident details
#get
@app.route('/locality-search', methods=['GET', 'POST'])
def locality_search():
    locality_info = None
    not_found_message = None


    if request.method == "POST":
        locality_name = request.form.get("locality_name")
        print(locality_name)
        db, cursor = db_connection()
        cursor.execute("select id from locality where name = %s", (locality_name,))
        id = cursor.fetchone()
        print(id)
        cursor.execute("SELECT * FROM incident WHERE lid = %s", (id[0],))

        locality_info = cursor.fetchall() 
        db.close()

        if not locality_info:
            not_found_message = "The locality you have entered is invalid or there are no active incidents there."
        print(locality_info)
    
    return render_template('locality_search.html', locality_info=locality_info, not_found_message=not_found_message)
    
