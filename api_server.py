import sqlite3
from flask_cors import CORS
from flask import Flask, jsonify, request
import requests
from datetime import datetime

# --- CONFIGURATION ---
SQLITE_DB_NAME = "test_data_trim.db"
app = Flask(__name__)

OLLAMA_URL = "http://host.docker.internal:11434"
MODEL_NAME = "mistral"

# Enable CORS to allow the HTML file (served from file:// or localhost) to make requests
CORS(app)

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(SQLITE_DB_NAME)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def format_warranty(exp_date_str):
    """Formats the warranty status based on the expiration date."""
    if not exp_date_str or '1900' in exp_date_str:
        return "N/A"
    try:
        exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d %H:%M:%S')
        if exp_date > datetime.now():
            return f"Active until {exp_date.strftime('%m/%Y')}"
        else:
            return f"Expired on {exp_date.strftime('%m/%Y')}"
    except (ValueError, TypeError):
        return "Invalid Date"

def to_float(value, default=0.0):
    """Safely converts a value to a float, returning a default if conversion fails."""
    if value is None:
        return default
    try:
        # Handles numbers, strings, etc. Returns default for empty strings.
        return float(value) if value != '' else default
    except (ValueError, TypeError):
        return default

def setup_database():
    """Reads schema.sql and executes it to set up application tables if they don't exist."""
    conn = get_db_connection()
    try:
        # Check if our main 'quote' table exists. If not, run the schema.
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quote'")
        if cursor.fetchone() is None:
            print("⚠️ Application tables not found. Initializing from schema.sql...")
            with open('schema.sql', 'r') as f:
                conn.executescript(f.read())
            print("✅ Database schema initialized successfully.")
    finally:
        conn.close()

@app.route('/api/service-call/<service_call_id>')
def get_service_call_data(service_call_id):
    """
    Fetches all necessary data for a given service call ID from the SQLite DB
    and formats it for the quote sheet frontend.
    """
    conn = get_db_connection()
    try:
        # --- 1. Fetch Base Service Call Details from ERP data ---
        details_cursor = conn.execute(
            "SELECT * FROM service_call_details WHERE TRIM(SV00300_Service_Call_ID) = ?",
            (service_call_id.strip(),)
        )
        details = details_cursor.fetchone()

        # --- 2. Fetch saved revisions from local application DB ---
        quote_cursor = conn.execute(
            """SELECT q.id, q.revision, q.description, q.tech_count, q.tech_hours, q.travel_hours, q.tech_rate, q.travel_rate
               FROM quote q
               WHERE TRIM(q.service_call_id) = ? ORDER BY q.revision ASC""",
            (service_call_id.strip(),)
        )
        saved_quotes = quote_cursor.fetchall()
 
        # --- 3. Validate if any data exists for this ID ---
        # If the ID is not in the ERP data and has no saved revisions, it's not found.
        if not details and not saved_quotes:
            return jsonify({"error": "Service Call ID not found"}), 404

        # --- 4. Process saved revisions (if they exist) ---
        revisions = []
        # --- OPTIMIZATION: Solve N+1 query problem by fetching all children in two queries ---
        quote_ids = [q['id'] for q in saved_quotes]
        parts_by_quote_id = {}
        subs_by_quote_id = {}

        if quote_ids:
            # Create placeholders for the IN clause, e.g., (?, ?, ?)
            placeholders = ','.join('?' for _ in quote_ids)

            # Fetch all parts for all relevant quotes in one go
            parts_sql = f"""
                SELECT quote_id, part_number as part, description as "desc", vendor, 
                       on_hand as onHand, quantity as qty, unit_cost as unitCost 
                FROM quote_line_item WHERE quote_id IN ({placeholders})
            """
            parts_cursor = conn.execute(parts_sql, quote_ids)
            for part_row in parts_cursor:
                qid = part_row['quote_id']
                if qid not in parts_by_quote_id:
                    parts_by_quote_id[qid] = []
                part_data = dict(part_row)
                del part_data['quote_id'] # Don't need to send this to the frontend
                parts_by_quote_id[qid].append(part_data)

            # Fetch all subcontractors for all relevant quotes in one go
            subs_sql = f"SELECT quote_id, contact_name, contact_details, cost FROM subcontractor WHERE quote_id IN ({placeholders})"
            subs_cursor = conn.execute(subs_sql, quote_ids)
            for sub_row in subs_cursor:
                qid = sub_row['quote_id']
                if qid not in subs_by_quote_id:
                    subs_by_quote_id[qid] = []
                sub_data = dict(sub_row)
                del sub_data['quote_id'] # Don't need to send this to the frontend
                subs_by_quote_id[qid].append(sub_data)

        # Now, assemble the revisions using the pre-fetched data
        for quote_row in saved_quotes:
            quote_id = quote_row['id']
            # Assemble the revision object to match the structure expected by the save endpoint
            revision_data = {
                "id": quote_id,
                "revision": quote_row['revision'],
                "description": quote_row['description'],
                "tech_count": quote_row['tech_count'],
                "tech_hours": quote_row['tech_hours'],
                "travel_hours": quote_row['travel_hours'],
                "parts": parts_by_quote_id.get(quote_id, []),
                "subcontractors": subs_by_quote_id.get(quote_id, [])
            }
            revisions.append(revision_data)

        # --- 5. Assemble Base Data ---
        # This structure matches what the frontend JavaScript expects.
        if details:
            # --- 5a. Data exists in ERP, build from that ---
            notes_cursor = conn.execute(
                "SELECT Record_Notes FROM sv000805_service_notes WHERE TRIM(Service_Call_ID) = ?",
                (service_call_id.strip(),)
            )
            notes = notes_cursor.fetchall()
            service_writeup = "\n".join([note['Record_Notes'].strip() for note in notes if note['Record_Notes']])

            default_tech_rate = 75.00
            default_travel_rate = 75.00
            labor_group_name = details['PL_Labor_Group_Name']
            if labor_group_name:
                rate_cursor = conn.execute(
                    "SELECT Billing_Amount FROM sv000123_overhead_groups WHERE Labor_Group_Name = ?",
                    (labor_group_name,)
                )
                rate_result = rate_cursor.fetchone()
                if rate_result and rate_result['Billing_Amount'] is not None:
                    default_tech_rate = rate_result['Billing_Amount']
                    default_travel_rate = rate_result['Billing_Amount']
            
            base_data = {
                "customer": { "name": details['PL_CUSTNAME'], "company": details['BillCustomer_CUSTNAME'] or details['PL_CUSTNAME'] },
                "unitInfo": {
                    "generator.model": details['Generator_Wennsoft_Model_Number'], "generator.serial": details['Generator_Wennsoft_Serial_Number'],
                    "generator.warranty": format_warranty(details['SV00400_Warranty_Expiration']), "ats.model": details['ATS_Wennsoft_Model_Number'],
                    "ats.serial": details['ATS_Wennsoft_Serial_Number'], "engine.model": details['Engine_Wennsoft_Model_Number'],
                    "engine.serial": details['Engine_Wennsoft_Serial_Number'], "generator.spec": "N/A", "generator.kw": "N/A", "generator.voltage": "N/A",
                },
                "writeup": service_writeup,
                "rates": { "tech": default_tech_rate, "travel": default_travel_rate }
            }
        else:
            # --- 5b. No ERP data, but saved revisions exist. Create a default structure. ---
            base_data = {
                "customer": {"name": "N/A (Manual Entry)", "company": "N/A (Manual Entry)"},
                "unitInfo": {
                    "generator.model": "N/A", "generator.serial": "N/A", "generator.warranty": "N/A",
                    "ats.model": "N/A", "ats.serial": "N/A", "engine.model": "N/A",
                    "engine.serial": "N/A", "generator.spec": "N/A", "generator.kw": "N/A",
                    "generator.voltage": "N/A",
                },
                "writeup": "No service write-up found in ERP. Description from latest revision is shown.",
                "rates": {"tech": 75.00, "travel": 75.00} # Default fallback rates
            }

        # --- 6. Assemble the final response ---
        response_data = {
            "revisions": revisions,
            "baseData": base_data
        }

        return jsonify(response_data)
    finally:
        conn.close()

@app.route('/api/quote', methods=['POST'])
def save_quote():
    """Saves a new or updated quote revision to the database."""
    data = request.json
    conn = get_db_connection()
    try:
        with conn: # Use a transaction
            # Check if this revision already exists
            existing_quote = conn.execute(
                "SELECT id FROM quote WHERE TRIM(service_call_id) = ? AND revision = ?",
                (data['serviceCallId'], data['revision'])
            ).fetchone()

            if existing_quote:
                # If it exists, delete it and its children (thanks to ON DELETE CASCADE)
                conn.execute("DELETE FROM quote WHERE id = ?", (existing_quote['id'],))

            # Insert the new quote record
            cursor = conn.execute(
                """INSERT INTO quote (service_call_id, revision, description, customer_name, status, 
                                     tech_count, tech_hours, travel_hours, tech_rate, travel_rate)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data['serviceCallId'], data['revision'], data['description'],
                    data['customer']['name'], 'Draft', data['labor']['techCount'],
                    data['labor']['techHours'], data['labor']['travelHours'],
                    data['labor']['techRate'], data['labor']['travelRate']
                )
            )
            quote_id = cursor.lastrowid

            # Insert parts
            if data.get('parts'):
                parts_to_insert = []
                for p in data.get('parts', []):
                    qty = to_float(p.get('qty'))
                    unit_cost = to_float(p.get('unitCost'))
                    parts_to_insert.append((
                        quote_id, p.get('part'), p.get('desc'), p.get('vendor'), 
                        p.get('onHand', 'N/A'), qty, unit_cost, qty * unit_cost
                    ))
                conn.executemany(
                    """INSERT INTO quote_line_item (quote_id, part_number, description, vendor, on_hand, quantity, unit_cost, total_cost)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    parts_to_insert
                )
            
            # Insert subcontractors
            if data.get('subcontractors'):
                subs_to_insert = [
                    (quote_id, s.get('contact_name'), s.get('contact_details'), to_float(s.get('cost')))
                    for s in data.get('subcontractors', [])
                ]
                conn.executemany(
                    """INSERT INTO subcontractor (quote_id, contact_name, contact_details, cost)
                       VALUES (?, ?, ?, ?)""",
                    subs_to_insert
                )

        return jsonify({"message": f"Quote revision {data['revision']} saved successfully.", "quote_id": quote_id}), 200
    finally:
        conn.close()

@app.route('/health')
def health_check():
    """Simple health check endpoint for Docker."""
    return jsonify({"status": "healthy"}), 200

@app.route('/summarize', methods=['POST'])
def summarize_writeup():
    """
    Receives a service write-up and uses an LLM to generate
    a customer-facing quote description.
    """
    data = request.get_json()
    if not data or 'writeup' not in data:
        return jsonify({"error": "Missing 'writeup' in request body"}), 400

    service_writeup = data['writeup']

    # This prompt is a starting point. You can refine it for better results.
    prompt = f"""You are an expert technical writer for an HVAC company.
A technician provided this service call write-up. Rewrite it into a clear, professional, customer-facing description for a quote.
Focus on the work performed and its value. Omit internal jargon. The output must be a single paragraph.

Technician's Write-up:
"{service_writeup}"

Customer-Facing Quote Description:"""

    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False  # Get the full response at once
        }
        # This request goes to the internal ollama service.
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=90)

        # Check for non-successful responses first.
        if not response.ok:
            error_message = "Unknown error from LLM service"
            # Try to parse a JSON error from Ollama, but don't fail if it's not JSON
            try:
                error_data = response.json()
                error_message = error_data.get("error", error_message)
            except ValueError:
                # If the response isn't JSON, use the raw text.
                error_message = response.text or f"Service returned status {response.status_code}"

            print(f"Ollama service returned an error: {response.status_code} - {error_message}")
            # Pass a clear error to the frontend.
            return jsonify({"error": f"LLM Error: {error_message}"}), response.status_code

        # If we get here, the response was OK, so it should be valid JSON.
        response_data = response.json()
        summary = response_data.get('response', '').strip()

        return jsonify({"summary": summary})
    except requests.exceptions.RequestException as e:
        # This catches network errors, timeouts, etc.
        print(f"Error connecting to Ollama service: {e}")
        return jsonify({"error": "Failed to connect to the LLM service. Is it running?"}), 503
    except Exception as e:
        # Catch-all for other unexpected errors (e.g., JSON decoding during success)
        print(f"An unexpected error occurred in summarize_writeup: {e}")
        return jsonify({"error": "An unexpected server error occurred while generating the summary."}), 500

# --- APPLICATION STARTUP ---

# This code runs when the container starts, ensuring the database is ready.
try:
    setup_database()
except Exception as e:
    print(f"🔴 CRITICAL: An error occurred during database setup: {e}")

# The if __name__ == '__main__' block is kept for convenience, allowing you to
# run the server directly in a local environment (outside of Docker) for debugging.
if __name__ == '__main__':
    print("--- Starting Quote API Server in local debug mode ---")
    app.run(host='0.0.0.0', port=3000, debug=True)