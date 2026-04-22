const { GoogleGenerativeAI } = require("@google/generative-ai");

async function testKey() {
    const genAI = new GoogleGenerativeAI("AIzaSyCkZEVe53duzsibZGrd2WiCtL2M4jxKtWs");
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

    try {
        const result = await model.generateContent("Hello!");
        const response = await result.response;
        console.log("Success! Response:", response.text());
    } catch (error) {
        console.error("Error testing key:", error.message);
    }
}

testKey();
