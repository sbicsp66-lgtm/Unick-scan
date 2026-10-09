const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(cors());

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
});

pool.query(`
    CREATE TABLE IF NOT EXISTS customers (
        id SERIAL PRIMARY KEY,
        machine_id VARCHAR(255) UNIQUE NOT NULL,
        license_key VARCHAR(255),
        trial_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        trial_expiry TIMESTAMP,
        status VARCHAR(50) DEFAULT 'trial'
    );
`).then(() => console.log("Database Table Ready!"));

// App Open: Check Status (and auto-register new machine ID)
app.post('/api/check-status', async (req, res) => {
    const { machine_id } = req.body;
    try {
        const result = await pool.query('SELECT * FROM customers WHERE machine_id = $1', [machine_id]);
        
        // If Machine ID is new, save it to DB and start 15 days trial
        if (result.rows.length === 0) {
            const expiryDate = new Date();
            expiryDate.setDate(expiryDate.getDate() + 15);
            await pool.query('INSERT INTO customers (machine_id, trial_expiry) VALUES ($1, $2)', [machine_id, expiryDate]);
            return res.json({ status: 'trial', days_left: 15 });
        }
        
        // If already exists, check status
        const customer = result.rows[0];
        if (customer.status === 'blocked') return res.json({ status: 'blocked' });
        if (customer.status === 'active') return res.json({ status: 'active' });

        const now = new Date();
        const expiry = new Date(customer.trial_expiry);
        const daysLeft = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));
        
        if (daysLeft <= 0) {
            await pool.query('UPDATE customers SET status = $1 WHERE machine_id = $2', ['expired', machine_id]);
            return res.json({ status: 'expired', days_left: 0 });
        }
        return res.json({ status: 'trial', days_left: daysLeft });
    } catch (err) { 
        console.error(err);
        res.status(500).json({ error: 'Server error' }); 
    }
});

// Client App: Activate License
app.post('/api/activate', async (req, res) => {
    const { machine_id, license_key } = req.body;
    try {
        const result = await pool.query('SELECT * FROM customers WHERE machine_id = $1', [machine_id]);
        if (result.rows.length > 0) {
            const customer = result.rows[0];
            if (customer.license_key === license_key) {
                await pool.query('UPDATE customers SET status = $1 WHERE machine_id = $2', ['active', machine_id]);
                return res.json({ success: true, message: 'Software Activated Successfully!' });
            }
        }
        return res.json({ success: false, message: 'Invalid License Key!' });
    } catch (err) { 
        console.error(err);
        res.status(500).json({ error: 'Activation failed' }); 
    }
});

// Admin Panel: Generate License
app.post('/api/admin/generate', async (req, res) => {
    const { machine_id, new_key } = req.body;
    try {
        await pool.query('UPDATE customers SET license_key = $1 WHERE machine_id = $2', [new_key, machine_id]);
        res.json({ success: true });
    } catch (err) { 
        console.error(err);
        res.status(500).json({ error: 'Failed to generate key' }); 
    }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
