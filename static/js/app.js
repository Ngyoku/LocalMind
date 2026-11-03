// ==================================================
// LOCALMIND - INTERFACE JAVASCRIPT
// ==================================================


// ==================================================
// ÉLÉMENTS DE L'INTERFACE
// ==================================================

const historyList = document.getElementById("history-list");
const messagesContainer = document.getElementById("messages-container");
const welcomeScreen = document.getElementById("welcome-screen");

const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");

const newChatButton = document.getElementById("new-chat-button");
const sendButton = document.getElementById("send-button");

const micButton = document.getElementById("mic-button");
const modelStatus = document.getElementById("model-status");

const chatArea = document.getElementById("chat-area");


// ==================================================
// ÉTAT DE L'APPLICATION
// ==================================================

let currentConversationId = null;
let isSending = false;


// ==================================================
// COMMUNICATION AVEC LE BACKEND
// ==================================================

async function apiRequest(endpoint, options = {}) {

    const response = await fetch(
        `/api${endpoint}`,
        {
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            },
            ...options
        }
    );

    let data;

    try {
        data = await response.json();
    } catch (error) {
        throw new Error(
            "Réponse invalide reçue du serveur."
        );
    }

    if (!response.ok || data.success === false) {

        throw new Error(
            data.error || "Une erreur est survenue."
        );
    }

    return data;
}


// ==================================================
// AFFICHER / CACHER L'ÉCRAN D'ACCUEIL
// ==================================================

function showWelcomeScreen(show) {

    if (show) {

        welcomeScreen.style.display = "flex";
        messagesContainer.style.display = "none";

    } else {

        welcomeScreen.style.display = "none";
        messagesContainer.style.display = "flex";
    }
}


// ==================================================
// CHARGER LE STATUT DE LOCALMIND
// ==================================================

async function loadStatus() {

    try {

        const response = await fetch("/api/status");

        const data = await response.json();

        if (response.ok && data.status === "ready") {

            modelStatus.textContent = "Prête";

        } else {

            modelStatus.textContent = "Indisponible";
        }

    } catch (error) {

        console.error("Erreur statut :", error);

        modelStatus.textContent = "Indisponible";
    }
}


// ==================================================
// CRÉER UNE NOUVELLE CONVERSATION
// ==================================================

async function createNewConversation() {

    try {

        const data = await apiRequest(
            "/conversations",
            {
                method: "POST",

                body: JSON.stringify({
                    title: "Nouvelle conversation"
                })
            }
        );

        currentConversationId =
            data.conversation.id;

        messagesContainer.innerHTML = "";

        showWelcomeScreen(false);

        await loadConversations();

        messageInput.focus();

    } catch (error) {

        console.error(
            "Erreur création conversation :",
            error
        );

        alert(
            "Impossible de créer une nouvelle conversation : "
            + error.message
        );
    }
}


// ==================================================
// CHARGER LES CONVERSATIONS
// ==================================================

async function loadConversations() {

    try {

        const data = await apiRequest("/conversations");

        historyList.innerHTML = "";

        data.conversations.forEach(conversation => {

            // Conteneur
            const item = document.createElement("div");

            item.className =
                "history-item-container";


            // ------------------------------------------
            // BOUTON CONVERSATION
            // ------------------------------------------

            const button =
                document.createElement("button");

            button.className = "history-item";

            button.type = "button";

            if (
                conversation.id === currentConversationId
            ) {

                button.classList.add("active");
            }

            button.textContent =
                conversation.title;

            button.addEventListener(
                "click",
                () => {

                    openConversation(
                        conversation.id
                    );
                }
            );


            // ------------------------------------------
            // BOUTON SUPPRIMER
            // ------------------------------------------

            const deleteButton =
                document.createElement("button");

            deleteButton.className =
                "delete-conversation-button";

            deleteButton.type = "button";

            deleteButton.innerHTML = "🗑";

            deleteButton.title =
                "Supprimer cette conversation";

            deleteButton.setAttribute(
                "aria-label",
                "Supprimer cette conversation"
            );

            deleteButton.addEventListener(
                "click",
                async (event) => {

                    event.stopPropagation();

                    const confirmed = confirm(
                        `Voulez-vous vraiment supprimer "${conversation.title}" ?`
                    );

                    if (!confirmed) {
                        return;
                    }

                    try {

                        await apiRequest(
                            `/conversations/${conversation.id}`,
                            {
                                method: "DELETE"
                            }
                        );

                        // Si conversation actuellement ouverte
                        if (
                            currentConversationId ===
                            conversation.id
                        ) {

                            currentConversationId = null;

                            messagesContainer.innerHTML = "";

                            showWelcomeScreen(true);
                        }

                        await loadConversations();

                    } catch (error) {

                        console.error(
                            "Erreur suppression :",
                            error
                        );

                        alert(
                            "Impossible de supprimer la conversation : "
                            + error.message
                        );
                    }
                }
            );


            // ------------------------------------------
            // AJOUT DANS LA SIDEBAR
            // ------------------------------------------

            item.appendChild(button);

            item.appendChild(deleteButton);

            historyList.appendChild(item);
        });

    } catch (error) {

        console.error(
            "Impossible de charger l'historique :",
            error
        );
    }
}


// ==================================================
// OUVRIR UNE CONVERSATION
// ==================================================

async function openConversation(conversationId) {

    try {

        const data = await apiRequest(
            `/conversations/${conversationId}`
        );

        currentConversationId = conversationId;

        messagesContainer.innerHTML = "";

        showWelcomeScreen(false);


        // ------------------------------------------
        // AFFICHER LES MESSAGES
        // ------------------------------------------

        data.messages.forEach(message => {

            addMessageToInterface(
                message.role,
                message.content
            );
        });


        await loadConversations();

        scrollToBottom();

    } catch (error) {

        console.error(
            "Erreur ouverture conversation :",
            error
        );

        alert(
            "Impossible d'ouvrir la conversation : "
            + error.message
        );
    }
}


// ==================================================
// AFFICHER UN MESSAGE
// ==================================================

function addMessageToInterface(role, content) {

    const messageElement =
        document.createElement("div");

    messageElement.className =
        `message ${role}-message`;


    const bubble =
        document.createElement("div");

    bubble.className =
        "message-bubble";


    // Utiliser textContent pour éviter
    // d'interpréter du HTML.
    bubble.textContent = content;


    // Bouton lire la réponse
    if (role === "assistant") {

        const actions =
            document.createElement("div");

        actions.className =
            "message-actions";


        const speakButton =
            document.createElement("button");

        speakButton.type = "button";

        speakButton.className =
            "speak-button";

        speakButton.textContent = "🔊";

        speakButton.title =
            "Lire cette réponse";

        speakButton.addEventListener(
            "click",
            () => {

                speakText(content);
            }
        );

        actions.appendChild(speakButton);

        messageElement.appendChild(bubble);

        messageElement.appendChild(actions);

    } else {

        messageElement.appendChild(bubble);
    }


    messagesContainer.appendChild(
        messageElement
    );
}


// ==================================================
// INDICATEUR "LOCALMIND RÉFLÉCHIT"
// ==================================================

function showTypingIndicator() {

    const typing =
        document.createElement("div");

    typing.className =
        "message assistant-message typing-message";

    typing.id =
        "typing-indicator";


    const bubble =
        document.createElement("div");

    bubble.className =
        "message-bubble";

    bubble.textContent =
        "LocalMind réfléchit...";


    typing.appendChild(bubble);

    messagesContainer.appendChild(typing);

    scrollToBottom();
}


function removeTypingIndicator() {

    const typing =
        document.getElementById(
            "typing-indicator"
        );

    if (typing) {
        typing.remove();
    }
}


// ==================================================
// ENVOYER UN MESSAGE
// ==================================================

async function sendMessage(message) {

    if (isSending) {
        return;
    }

    message = message.trim();

    if (!message) {
        return;
    }


    // Créer automatiquement une conversation
    if (!currentConversationId) {

        await createNewConversation();
    }


    try {

        isSending = true;

        sendButton.disabled = true;


        // Afficher message utilisateur
        addMessageToInterface(
            "user",
            message
        );

        messageInput.value = "";

        autoResizeTextarea();

        scrollToBottom();


        // Afficher attente
        showTypingIndicator();


        // Envoyer au backend
        const data = await apiRequest(
            "/chat",
            {
                method: "POST",

                body: JSON.stringify({
                    conversation_id:
                        currentConversationId,

                    message:
                        message
                })
            }
        );


        removeTypingIndicator();


        // Afficher réponse IA
        addMessageToInterface(
            "assistant",
            data.response
        );


        await loadConversations();

        scrollToBottom();

    } catch (error) {

        removeTypingIndicator();

        console.error(
            "Erreur message :",
            error
        );

        addMessageToInterface(
            "assistant",
            "⚠️ Une erreur est survenue : "
            + error.message
        );

    } finally {

        isSending = false;

        sendButton.disabled = false;

        messageInput.focus();
    }
}


// ==================================================
// LIRE UNE RÉPONSE
// ==================================================

async function speakText(text) {

    try {

        await apiRequest(
            "/speak",
            {
                method: "POST",

                body: JSON.stringify({
                    text: text
                })
            }
        );

    } catch (error) {

        console.error(
            "Erreur synthèse vocale :",
            error
        );

        alert(
            "Impossible de lire la réponse : "
            + error.message
        );
    }
}


// ==================================================
// MICROPHONE
// ==================================================

async function listenToMicrophone() {

    if (isSending) {
        return;
    }

    try {

        micButton.disabled = true;

        micButton.textContent = "🎙️";

        const data = await apiRequest(
            "/listen",
            {
                method: "POST"
            }
        );


        if (data.text) {

            messageInput.value = data.text;

            autoResizeTextarea();

            messageInput.focus();
        }

    } catch (error) {

        console.error(
            "Erreur microphone :",
            error
        );

        alert(
            "Impossible d'utiliser le microphone : "
            + error.message
        );

    } finally {

        micButton.disabled = false;

        micButton.textContent = "🎤";
    }
}


// ==================================================
// REDIMENSIONNEMENT DU TEXTAREA
// ==================================================

function autoResizeTextarea() {

    messageInput.style.height = "auto";

    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            180
        ) + "px";
}


// ==================================================
// DESCENDRE EN BAS DE LA CONVERSATION
// ==================================================

function scrollToBottom() {

    chatArea.scrollTo({
        top: chatArea.scrollHeight,

        behavior: "smooth"
    });
}


// ==================================================
// ÉVÉNEMENTS
// ==================================================


// Nouvelle discussion
newChatButton.addEventListener(
    "click",
    () => {

        createNewConversation();
    }
);


// Envoyer formulaire
messageForm.addEventListener(
    "submit",
    (event) => {

        event.preventDefault();

        sendMessage(
            messageInput.value
        );
    }
);


// Envoyer avec ENTER
messageInput.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            messageForm.requestSubmit();
        }
    }
);


// Ajuster textarea
messageInput.addEventListener(
    "input",
    autoResizeTextarea
);


// Microphone
micButton.addEventListener(
    "click",
    listenToMicrophone
);


// Cartes de suggestions
document
    .querySelectorAll(".suggestion-card")
    .forEach(card => {

        card.addEventListener(
            "click",
            () => {

                const prompt =
                    card.dataset.prompt;

                if (prompt) {

                    sendMessage(prompt);
                }
            }
        );
    });


// ==================================================
// INITIALISATION
// ==================================================

async function initializeLocalMind() {

    showWelcomeScreen(true);

    await loadStatus();

    await loadConversations();
}


document.addEventListener(
    "DOMContentLoaded",
    initializeLocalMind
);