const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-input")
const chatBox = document.getElementById("chat-box")
const uploadBtn = document.getElementById("upload-btn");
const pdfFile = document.getElementById("pdf-file");

uploadBtn.addEventListener("click", uploadPDF);
sendBtn.addEventListener("click", sendMessage);

async function sendMessage(){
        const message = userInput.value.trim();
        if(message ===""){
            return;
        }
        addMessage(message,"user");
        userInput.value="";

        const typingDiv = addMessage("Typing...","bot");

        const response = await fetch("/chat",{
            method :"POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        const data = await response.json();
        console.log(data);
        typingDiv.remove();

        const botDiv = addMessage(data.response, "bot");

        if (data.sources && data.sources.length > 0) {
            const sourceDiv = document.createElement("div");
            sourceDiv.classList.add("source-list");

            sourceDiv.innerHTML =
                "<strong>Sources:</strong><br>" +
                data.sources.join("<br>");

            chatBox.appendChild(sourceDiv);
        }

    }

async function uploadPDF(){
    const file = pdfFile.files[0];
    if(!file){
        alert("Please select a PDF file to upload.");
        return;
    }
    const formData = new FormData();
    formData.append("pdf", file);
    const response = await fetch("/upload",{
        method: "POST",
        body: formData
    });
    //console.log(await response.text());
    const data = await response.json();
    alert(data.message);
}
function addMessage(message,sender){
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message");
    if(sender === 'user'){
        messageDiv.classList.add("user-message");
    }
    else{
        messageDiv.classList.add("bot-message")
    }
    messageDiv.innerText = message;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return messageDiv;
}