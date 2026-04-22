const https = require('https');

const API_KEY = process.env.GEMINI_API_KEY || "AIzaSyCkZEVe53duzsibZGrd2WiCtL2M4jxKtWs";
const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${API_KEY}`;

https.get(url, (res) => {
    let data = '';
    res.on('data', (chunk) => { data += chunk; });
    res.on('end', () => {
        console.log("Status:", res.statusCode);
        console.log("Body:", data);
    });
}).on("error", (err) => {
    console.log("Error: " + err.message);
});
