const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');

const app = express();
const port = 3000;
const DB_PATH = './database.db'; // Assumes your DB file is named this

app.use(cors());
app.use(express.json());

// Helper to create a new DB connection
const connectDb = () => new sqlite3.Database(DB_PATH, sqlite3.OPEN_READWRITE);

// Promise-based wrapper for db.all
const dbAll = (db, sql, params = []) => {
    return new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
};

// The main API endpoint to get all data for a service call
app.get('/api/service-call/:id', async (req, res) => {
    const serviceCallId = req.params.id;
    const db = connectDb();

    try {
        // Query ERP data
        const erpDataQuery = `
        SELECT
            sc.Service_Call_ID,
            sc.CUSTNMBR,
            cust.CUSTNAME,
            cust.CNTCPRSN,
            eq.Equipment_ID,
            eq.Wennsoft_Model_Number as model,
            eq.Wennsoft_Serial_Number as serial,
            eq.Equipment_Type,
            eq.Warranty_Expiration
        FROM sv00300 sc
        LEFT JOIN rm00101 cust ON sc.CUSTNMBR = cust.CUSTNMBR
        LEFT JOIN sv00302 sceq ON sc.Service_Call_ID = sceq.Service_Call_ID
        LEFT JOIN sv00400 eq ON sceq.Equipment_ID = eq.Equipment_ID
        WHERE sc.Service_Call_ID = ?
        `;
        const erpRows = await dbAll(db, erpDataQuery, [serviceCallId]);

        // Query local quote data
        const quoteRevisionsQuery = `SELECT * FROM quote WHERE service_call_id = ? ORDER BY revision`;
        const quoteRows = await dbAll(db, quoteRevisionsQuery, [serviceCallId]);

        if (erpRows.length === 0 && quoteRows.length === 0) {
            return res.status(404).json({ message: 'Service Call not found.' });
        }

        // --- Prepare Base Data ---
        // Consolidate customer and unit info, prioritizing fresh ERP data.
        let customer = { name: 'N/A', company: 'N/A' };
        let unitInfo = {};
        if (erpRows.length > 0) {
            const firstErpRow = erpRows[0];
            customer = { name: firstErpRow.CNTCPRSN || firstErpRow.CUSTNAME, company: firstErpRow.CUSTNAME };
            erpRows.forEach(row => {
                if (row.Equipment_Type && row.Equipment_Type.toLowerCase().includes('generator')) {
                    unitInfo['generator.model'] = row.model;
                    unitInfo['generator.serial'] = row.serial;
                    unitInfo['generator.warranty'] = new Date(row.Warranty_Expiration) > new Date() ? 'Active' : 'Expired';
                } else if (row.Equipment_Type && row.Equipment_Type.toLowerCase().includes('ats')) {
                    unitInfo['ats.model'] = row.model;
                    unitInfo['ats.serial'] = row.serial;
                }
            });
        } else if (quoteRows.length > 0) {
            // Fallback to data from the first local quote if ERP data is missing
            customer = { name: quoteRows[0].customer_name, company: quoteRows[0].customer_name };
        }
        
        const baseData = { customer, unitInfo };

        // --- Prepare Revisions ---
        let revisions = [];
        if (quoteRows.length > 0) {
            const lineItemsQuery = `SELECT * FROM quote_line_item WHERE quote_service_call_id = ?`;
            const lineItems = await dbAll(db, lineItemsQuery, [serviceCallId]);

            revisions = quoteRows.map(quote => ({
                revision: quote.revision,
                customer: baseData.customer, // Use consistent base data
                unitInfo: baseData.unitInfo, // Use consistent base data
                rates: { tech: quote.tech_rate, travel: quote.travel_rate },
                parts: lineItems
                    .filter(item => item.quote_revision === quote.revision)
                    .map(p => ({ part: p.part_number, desc: p.description, vendor: p.vendor, onHand: p.on_hand, qty: p.quantity, unitCost: p.unit_cost }))
            }));
        }

        res.json({ revisions, baseData });
    } catch (err) {
        console.error('API Error:', err.message);
        res.status(500).json({ error: 'An error occurred while fetching data.' });
    } finally {
        db.close();
    }
});

app.listen(port, () => {
    console.log(`Quote API server listening on http://localhost:${port}`);
});