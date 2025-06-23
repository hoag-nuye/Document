const express = require('express');
const { exec } = require('child_process');
const fs = require('fs').promises;
const cors = require('cors');
const app = express();

// Enable CORS to allow requests from the frontend
app.use(cors());
app.use(express.json());

app.post('/run-python', async (req, res) => {
    const code = req.body.code;
    if (!code) {
        return res.status(400).json({ error: 'No code provided' });
    }

    try {
        // Save code to a temporary file
        const fileName = `temp_${Date.now()}.py`;
        await fs.writeFile(fileName, code);

        // Execute Python code with a timeout
        exec(`python3 ${fileName}`, { timeout: 5000 }, (error, stdout, stderr) => {
            // Delete temporary file
            fs.unlink(fileName).catch(err => console.error('Error deleting file:', err));

            if (error) {
                return res.json({ error: stderr || error.message });
            }
            res.json({ output: stdout });
        });
    } catch (err) {
        res.status(500).json({ error: 'Server error: ' + err.message });
    }
});

app.listen(3000, () => console.log('Server running on http://localhost:3000'));