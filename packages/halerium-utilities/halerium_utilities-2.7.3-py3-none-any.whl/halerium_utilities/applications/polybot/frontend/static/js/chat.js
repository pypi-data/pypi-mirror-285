"use strict";

/**
 * This JavaScript file defines a ChatManager class that handles a chat session between a user and an assistant.
 * The ChatManager is responsible for initializing the chat session, establishing a WebSocket connection,
 * handling incoming and outgoing messages, and managing the user interface.
 *
 * The ChatManager class includes methods to:
 * - Initialize the chat session and WebSocket connection
 * - Send messages from the user to the server
 * - Display messages from the user and the assistant in the chat interface
 * - Handle WebSocket messages and connectivity issues
 * - Append standalone and streamed messages to the chat interface
 * - Show and remove a "thinking" indicator for the assistant
 * - Scroll the chat to the latest message
 *
 * The code uses the 'marked' library to convert Markdown text to HTML and the 'hljs' library to highlight code blocks.
 *
 * The ChatManager is instantiated when the page loads, and it attaches event listeners to the chat and user input elements.
 */
class ChatManager {
  /**
   * Constructor for ChatManager.
   * Initializes all necessary elements, sets up event listeners,
   * starts auto-scroll for chat, and initializes WebSocket connection.
   */
  constructor() {
    this.initializeSessionAndUrls();
    this.initializeChatElements();
    this.initializeInteractionElements();
    this.initializeGetInTouchAndByeMessage()
    this.setupEventListeners();
    this.autoScrollChat();
    this.initializeWebSocket();
    this.pingPong = this.wsPingPong(); // websocket keep-alive
    this.renderer = new marked.Renderer();
    this.audioContext = "";
    this.evalInitialPrompt();

    // this.renderer.paragraph = (result) => {
    //   const text = marked.parse(result.text);
    //   return `${text}<br>`; // don't add <p> tags
    // };
    
    this.renderer.link = (result) => {
      return `<a href="${result.href}" title="${result.title}" target="_blank">${result.text}</a>`;
    }

    this.renderer.image = (result) => {
      if (result.href.startsWith("attachment:")) {
        return `<img class="halimg" filename="${result.href}" title="${result.title}" alt="${result.text}" />`
      }
      return `<img src="${result.href}" title="${result.title}" alt="${result.text}" />`;
    }
    
    this.renderer.listitem = (result) => {
        let text = marked.parse(result.text).trim();
        if (text.startsWith("<p>")) {
            text = text.substr(3);
        }
        if (text.endsWith("</p>")) {
            text = text.substr(0, text.length-4)
        }
        return `<li class="msglist">${text}</li>`; // remove <li> padding and margin
    };
    this.renderer.code = (result) => {
        const code = result.code;
        const language = result.language;

        var btn_ctc = '<button class="copy-btn" onclick="window.chatManager.copyToClipboard(this)">Copy code</button>';
        var lang_lbl = `<span class="lang-lbl">${language}</span>`;
        var escapedCode = this.escapeHTML(code);
        return `<pre>${lang_lbl}${btn_ctc}<code class=hljs ${language}>${escapedCode}</code></pre>` // add copy button and language label
    }
    this.renderer.blockquote = (quote) => {
      const text = marked.parse(quote.text)
      return `${text}<br>`; // remove blockquote
    }
    marked.setOptions({ renderer: this.renderer });

    // Attach the logout event listener
    document.getElementById('logout-link').addEventListener('click', this.logout.bind(this));
  }

  /**
   * Initializes session details and URLs for WebSocket and application.
   */
  initializeSessionAndUrls() {
    this.sessionId = this.getSessionId("chatbot_session_id");
    this.wsTextUrl = document.getElementById("wsTextUrl").value;
    this.wsAudioUrl = document.getElementById("wsAudioUrl").value;
    this.appUrl = document.getElementById("appurl").value;
    this.initialPrompt = document.getElementById("initialPrompt").value;
    this.initialResponse = document.getElementById("initialResponse").value;
    // TODO: INCLUDE THIS INTO THE CHATFLOW
    this.byeMessage_personalized = document.getElementById("byeMessage").value;
  }

  /**
   * Initializes chat elements including bot name, user name, and message containers.
   */
  initializeChatElements() {
    this.botName = document.getElementById("botname").value;
    this.userName = document.getElementById("username").value;
    this.chat = document.getElementById("chat");
    this.messages = document.getElementById("messages");
  }

  /**
   * Initializes elements related to user interaction.
   */
  initializeInteractionElements() {
    this.userInputContainer = document.getElementById("user-input-container");
    this.userInput = document.getElementById("user-input");
    this.userInputOverlay = document.getElementById("user-input-overlay");
    this.shiftRPressed = false; // flag for shift + r key for recording voice
    this.sendOnEnterDisabled = false;
    this.isRecording = false;
  }

  /**
   * Initializes the contact link and the goodbye message for the chat.
   * TODO: this should be configurable by the user!
   */
  initializeGetInTouchAndByeMessage() {
    this.byeMessage = `Thank you for using ${this.botName}.`;
  }

  /**
   * Logs out the user by clearing cookies and redirecting to the login page.
   */
  logout(event) {
    event.preventDefault(); // Prevent the default link behavior

    // Ensure the appUrl ends with a slash before appending the logout segment
    const baseUrl = this.appUrl.endsWith('/') ? this.appUrl : `${this.appUrl}/`;
    const logoutUrl = `${baseUrl}logout`;

    fetch(logoutUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => {
      if (response.ok) {
        // Redirect to the landing page
        window.location.href = this.appUrl;
      } else {
        console.error('Logout failed:', response.statusText);
      }
    })
    .catch(error => {
      console.error('Error during logout:', error);
    });
  }

  /**
   * Sets up the WebSocket connection and its event handlers.
   */
  initializeWebSocket() {
    // websocket for text messages
    this.wsText = new WebSocket(`${this.wsTextUrl}ws/text?token=${this.sessionId}`);
    this.wsText.binaryType = "blob";
    this.wsText.onmessage = (event) => this.handleWsMessage(event);
    this.wsText.onclose = (event) => this.handleWsConnectivityProblem(event);
    this.wsText.onerror = (error) => {
      console.error("WebSocket for text encountered an error:", error);
    };

    // websocket for audio messages
    this.wsAudio = new WebSocket(`${this.wsTextUrl}ws/voice?token=${this.sessionId}`);
    this.wsAudio.onmessage = (event) => this.handleWsAudioMessage(event);
    this.wsAudio.onclose = (event) => // console.log(`WebSocket for voice closed: ${event}`);
    this.wsAudio.onerror = (error) => {
      console.error("WebSocket for voice encountered an error:", error);
    };
  }

  /**
   * Sets up various event listeners for chat and user input.
   */
  setupEventListeners() {
    this.setupChatScrollListener();
    this.setupInputListeners();
  }

  /**
   * Adds a scroll event listener to the chat element to handle auto-scrolling.
   */
  setupChatScrollListener() {
    this.chat.addEventListener("scroll", () => {
      this.autoScroll = this.chat.scrollTop + this.chat.clientHeight >=
                        this.chat.scrollHeight - this.chat.scrollHeight / 100;
    });
  }

  /**
   * Sets up event listeners for user input, including send button and keyboard interactions.
   */
  setupInputListeners() {
    // Send Button Listener
    document.getElementById("send").addEventListener("click", () => this.sendMessage());

    // Record Button Listener
    document.getElementById("record").addEventListener("click", () => this.toggleRecordingVoice());

    // Global Keydown Listener
    document.addEventListener("keydown", (event) => this.handleGlobalKeydown(event));

    // User Input Listeners
    this.userInput.addEventListener("input", () => this.resetUserInputAreaSize());
    this.userInput.addEventListener("keydown", (event) => this.handleUserInputKeydown(event));
  }

  /**
   * Sends a periodic 'ping' message over WebSocket to keep the connection alive.
   */
  wsPingPong() {
    setInterval(() => {
      if (this.wsText.readyState === WebSocket.OPEN) {
        try {
          this.wsText.send(`ping, ${this.sessionId}`);
        } catch (error) {
          console.error(`Ping failed: ${error}`);
        }
      }
    }, 30000);
  }

  /**
   * Copies the text content of a code block to the clipboard.
   * @param {HTMLElement} btn - The button element that was clicked.
   */
  copyToClipboard(btn) {
      var text = btn.nextElementSibling.textContent;
      navigator.clipboard.writeText(text).then(function() {
        btn.textContent = "\u2713 Copied!"; // ✓
        setTimeout(() => {
            btn.textContent = "Copy code";
        }, 2000);
      }).catch(function(err) {
        console.error('Error in copying text: ', err);
      });
  }

  /**
   * Escapes HTML special characters in a string.
   * @param {string} str - The string to be escaped.
   * @returns {string} The escaped string.
   */
  escapeHTML(str) {
    return str.replace(/[&<>'"]/g, function(tag) {
        const charsToReplace = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '\'': '&#39;',
            '"': '&quot;'
        };
        return charsToReplace[tag] || tag;
    });
  }

  /**
   * Handles keyboard key down events for the user input area.
   * @param {KeyboardEvent} event - The keyboard event.
   */
  handleUserInputKeydown(event) {
    // enter key: send message
    if (event.key === "Enter" && !event.shiftKey) {
      if (this.sendOnEnterDisabled === false) {
        event.preventDefault();
        this.sendMessage();
      } else {
        event.preventDefault();
        // do nothing.
      }
    }
    // shift + enter key: new line
    if (event.key === "Enter" && event.shiftKey) {
      event.preventDefault();
      this.userInput.value += "\n";
      this.resetUserInputAreaSize();
    }
  }

  /**
   * Handles keyboard key down events for the entire page.
   * @param {KeyboardEvent} event - The keyboard event.
   */
  handleGlobalKeydown(event) {
    // ctrl + shift + V: toggle recording voice
    if (event.ctrlKey && event.shiftKey && event.key === "V") {
      event.preventDefault();
      this.toggleRecordingVoice();
    }
  }

  /**
   * Handles incoming WebSocket messages.
   * @param {MessageEvent} event - The WebSocket message event.
   */
  handleWsMessage(message) {
    event = JSON.parse(message.data);
    console.log(event);

    if (event.event == "chunk") {
        console.log("chunk received");
        this.removeThinkingIndicator();

        this.displayAssistantMessage(event.data.chunk || "");
    } else if (event.event == "attachment") {
        console.log("attachment received");
        const currentTextSpan = document.getElementById("currSpan");
        const attachmentsDiv = currentTextSpan.parentElement.querySelector(".attachments")
        attachmentsDiv[event.data["filename"]] = event.data["attachment"];
    } else if (event.event == "audio") {
      var url = URL.createObjectURL(atob(event.data.audio));
      var audio = new Audio(url);
      audio.play();
    }
  }

  handleWsAudioMessage(event) {
    /**
     * Currently, we do not want to send the transcript to the
     * chat windwow right away. Instead, it should go to the 
     * user input field. This is why we do not call sendMessage()
     */
    // append the transcript to the user input field.
    // add a space if there is no space OR no linebreak at the end.
    if (this.userInput.value.length > 0) { 
      if (this.userInput.value[this.userInput.value.length - 1] === " " ||
          this.userInput.value[this.userInput.value.length - 1] === "\n") {
        this.userInput.value += event.data;
      } else {
        this.userInput.value += ` ${event.data}`;
      }
    } else {
      this.userInput.value += event.data;
    }

    // hide the overlay
    this.userInputOverlay.style.display = "none";

    this.userInput.disabled = false;
    this.disableUserInput(false);
    this.userInput.focus();
    this.resetUserInputAreaSize();
  }

  /**
   * Handles connectivity issues with the WebSockets.
   * @param {CloseEvent} event - The WebSocket close event.
   */
  handleWsConnectivityProblem(event) {
    console.error("WebSocket error observed:", event);
    this.removeThinkingIndicator();
    this.appendStandaloneMessageToChat("assistant", this.byeMessage);
    this.scrollToBottomOfElement(chat);
  }

  /**
   * Evaluates the initial prompt as defined on the chatbot Board.
   * If a initial response was found, it displays that in the chat instead.
   */
  evalInitialPrompt() {
    if (this.initialResponse === "" && this.initialPrompt !== "") {
      this.initIdentifier = `<INITIAL>, ${this.sessionId}\n\n`
      this.sendMessage(`${this.initIdentifier}${this.initialPrompt}`, true);
    } else if (this.initialResponse !== "") {
      this.appendStandaloneMessageToChat("assistant", this.initialResponse);
    }
  }

  /**
   * Sends the user's message to the chat and performs necessary UI updates.
   * @param {string} [query=""] - The message text to be sent.
   */
  sendMessage(query="", isInitialPrompt=false) {
    if (query==="") {
      query = this.getUserInput();
    }
    if (query) {
      this.disableUserInput(true);
      if (!isInitialPrompt) {
        this.displayUserMessage(query);
      }
      this.sendMessageToServer(query);
      this.clearUserInput();
      this.showThinkingIndicator();
      this.scrollToBottomOfElement();
      }
  }

  /**
   * Toggles the recording of the user's voice.
   */
  toggleRecordingVoice() {
    // console.log(`isRecording: ${this.isRecording}`)
    if (this.isRecording) {
      document.getElementById("record").classList.remove("active-recording");
      this.stopStreamingVoice();
      this.isRecording = false;
      // console.log(`set isRecording to ${this.isRecording}.`)
    } else {
      document.getElementById("record").classList.add("active-recording");
      this.startStreamingVoice();
    }
  }

  /**
   * Access the microphone and return a MediaStream object.
   */
  async getAudioStream() {
    try {
      const newStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      return newStream;
    } catch (error) {
      console.error(`Error accessing microphone: ${error}`);
      this.appendStandaloneMessageToChat("assistant", "I'm sorry, but your message could not be recorded: No microphone detected.");
      throw error;
    }
  }

  /**
   * Returns an AudioContext object for live streaming
   * @returns {AudioConext}
   */
  async getAudioContext() {
    try {
      const newAudioContext = new (window.AudioContext || window.webkitAudioContext());
      return newAudioContext;
    } catch (error) {
      console.error(`Error accessing microphone: ${error}`);
      this.appendStandaloneMessageToChat("assistant", "I'm sorry, but your message could not be recorded: No microphone detected.");
      return null;
    }
  }

  /**
   * Records the user's voice.
   */
  async startStreamingVoice() {
    // get audio stream from microphone
    try {
      this.stream = await this.getAudioStream();
    } catch(error) {
      console.error(`Error getting media stream: ${error}`);
    }

    // connect the source to the processor and the processor to the context's destination
    try {
      this.audioContext = await this.getAudioContext();
      await this.audioContext.audioWorklet.addModule(window.location.href + "static/js/audio-processor.js");
      this.source = this.audioContext.createMediaStreamSource(this.stream);
      this.processor = new AudioWorkletNode(this.audioContext, "audio-processor");
      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);
    } catch(error) {
      console.error(`Error creating audio context: ${error}`);
    }

    // send start signal to backend
    try {
      if (this.wsAudio.readyState === WebSocket.OPEN) {
        this.isRecording = true;
        this.userInput.disabled = true;
        this.sendButtonDisabled(true);
        this.userInputOverlay.textContent = "Listening...";
        this.userInputOverlay.style.height = document.getElementById("user-input-container").height;

        this.userInputOverlay.style.display = "block";
        this.wsAudio.send(JSON.stringify({type: "audio-start", samplerate: this.audioContext.sampleRate}));
      }
    } catch (error) {
      console.error(`Error registering audio stream with backend: ${error}`);
    }

    // handle messages from the audio worklet
    try {
      this.processor.port.onmessage = (event) => {
        // get the raw audio data from the message
        const inputData = event.data;

        // convert the raw audio data to a binary format
        const outputData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          outputData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
        }

        // send the binary audio data (16 bit PCM) to the server via websocket
        if (this.wsAudio.readyState === WebSocket.OPEN) {
          this.wsAudio.send(outputData);
        }
      };
    }
    catch (error) {
      console.error(`Error sending audio stream to backend: ${error}`);
    }
}

  /**
   * Stops the recording of the user's voice.
   */
  stopStreamingVoice() {
    // disconnect the source from the processor and the processor from the context's destination
    if (this.processor) {
      // console.log("disconnecting processor");
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.source) {
      // console.log("disconnecting source");
      this.source.disconnect();
      this.source = null;
    }
    // close the audio context
    if (this.audioContext) {
      // console.log("closing audio context");
      this.audioContext.close();
      this.audioContext = null;
    }
    // stop the audio stream from the microphone
    if (this.stream) {
      // console.log("stopping stream");
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }

    // tell the backend streaming is finished and modify frontend
    // console.log(this.wsAudio.readyState);
    // console.log(WebSocket.OPEN);
    if (this.wsAudio.readyState === WebSocket.OPEN) {
      // console.log("sending audio-end");
      this.userInputOverlay.textContent = "Processing recording...";
      this.recordButtonDisabled(true);
      this.wsAudio.send(JSON.stringify({ type: "audio-end" }));
    }
  }

  /**
   * Sends the user's message to the server via WebSocket.
   * @param {string} query - The message text to be sent.
   */
  sendMessageToServer(query) {
    try {
      if (this.wsText.readyState === WebSocket.OPEN) {
        this.wsText.send(query);   
      } else {
        if (this.wsText.readyState === WebSocket.CONNECTING) {
          console.warn("WebSocket is still connecting.");
          // just wait a second and try again
          setTimeout(() => {
            this.sendMessageToServer(query);
          }, 150);
        } else if (this.wsText.readyState === WebSocket.CLOSED) {
          console.error("Websocket is closed.")
          this.appendStandaloneMessageToChat("assistant", "I'm sorry, but your message could not be sent.");
        }
      }
    } catch (error) {
      console.error(`Error sending message: ${error}`);
      this.appendStandaloneMessageToChat("assistant", "I'm sorry, but your message could not be sent.");
      this.disableUserInput(false);
    }
  }

/**
 * disables all user input sending interactions
 * @param {bool} state 
 */
  disableUserInput(state) {
    this.sendButtonDisabled(state);
    this.recordButtonDisabled(state);
    this.toggleSendOnEnterDisabled(state);
  }


  /**
   * Enables or disables the send button.
   * @param {boolean} state - True to disable the button, false to enable it.
   */
  sendButtonDisabled(state) {
    document.getElementById("send").disabled = state;
  }

  /**
   * Enables or disables the record button.
   * @param {boolean} state - True to disable the button, false to enable it.
   */
  recordButtonDisabled(state) {
    document.getElementById("record").disabled = state;
  }

  toggleSendOnEnterDisabled(state) {
    this.sendOnEnterDisabled = state;
  }

  /**
   * Appends the user's message to the chat interface.
   * @param {string} query - The message text from the user.
   */
  displayUserMessage(query) {
    this.appendStandaloneMessageToChat("user", query);
  }

  /**
   * Appends the assistant's message to the chat interface.
   * @param {string} response - The message text from the assistant.
   */
  displayAssistantMessage(response) {
    this.appendStreamedMessageToChat("assistant", response);
  }

  /**
   * Automatically scrolls the chat content.
   * Continuously checks and adjusts the scroll position to reveal new messages.
   */
  autoScrollChat() {
    setInterval(() => {
        if (this.autoScroll) {
            this.chat.scrollTop = this.chat.scrollHeight;
        }
    }, 50);
  }

  /**
   * Returns the current value of the user input text area.
   */
  getUserInput() {
    return this.userInput.value.trim();
  }

  /**
   * Returns the current session ID from cookies.
   * @param {string} key - The name of the cookie.
   */
  getSessionId(key) {
    const id = document.cookie.match(new RegExp("(^| )" + key + "=([^;]+)"));
    if (id) {
      return id[2];
    } else {
      return "";
    }
  }

  /**
   * Returns the current timestamp as a string.
   * Format: dd.mm.yyyy, HH:MM:SS
   */
  static getCurrentTimestamp() {
    const date = new Date();
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    return `${day}.${month}.${year}, ${hours}:${minutes}:${seconds}`;
  }

  /**
   * Clears the user input field and resets its size.
   */
  clearUserInput() {
    // clear prompt text field and resize it accordingly
    this.userInput.value = "";
    this.resetUserInputAreaSize();
  }

  /**
   * Dynamically adjusts the size of the user input area based on its content.
   * Ensures the chat interface accommodates the varying size of the input area.
   */
  resetUserInputAreaSize() {
    this.userInput.style.height = "auto";
    this.userInputContainer.style.height = "auto";
    this.userInput.style.height = this.userInput.scrollHeight + "px";
    this.userInputContainer.style.height = this.userInput.scrollHeight + "px";
  }

  /**
   * Appends a standalone message to the chat interface.
   * Used for messages that are not part of a streamed conversation.
   * @param {string} role - The role of the message sender (e.g., 'user', 'assistant').
   * @param {string} messageText - The text of the message to be appended.
   */
  appendStandaloneMessageToChat(role, messageText) {
    // get current timestamp
    const timestamp = ChatManager.getCurrentTimestamp();

    // create list item for sender and timestamp line
    const senderListItem = document.createElement("li");
    senderListItem.className = `sender-${role}`;

    const senderNameSpan = document.createElement("span");
    senderNameSpan.className = "name";
    senderNameSpan.textContent = role === "user" ? this.userName + " " : this.botName + " ";

    const timestampSpan = document.createElement("span");
    timestampSpan.className = "timestamp";
    timestampSpan.textContent = timestamp;

    senderListItem.appendChild(senderNameSpan);
    senderListItem.appendChild(timestampSpan);

    // create list item for message text
    const messageListItem = document.createElement("li");
    messageListItem.className = `msg-${role}`;

    const messageTextSpan = document.createElement("span");
    messageTextSpan.textContent = messageText;
    messageListItem.appendChild(messageTextSpan);

    const messagesContainer = document.getElementById("messages");
    messagesContainer.appendChild(senderListItem);
    messagesContainer.appendChild(messageListItem);

    // parse assistant messages for markdown
    if (role === "assistant") {
      this.parseMarkdown(messageTextSpan)
    }
  }

  /**
   * Handles the appending of streamed messages to the chat interface.
   * This method manages the state of messages being received in parts.
   * @param {string} role - The role of the message sender (e.g., 'user', 'assistant').
   * @param {string} messageText - The text of the message or control tokens like <sos>, <eos>.
   */
  appendStreamedMessageToChat(role, messageText) {
    
    const currentTextSpan = document.getElementById("currSpan");

    switch (messageText) {

      case "<sos>":
        // get current timestamp
        const timestamp = ChatManager.getCurrentTimestamp();

        // create list item for sender and timestamp line
        const senderListItem = document.createElement("li");
        senderListItem.className = `sender-${role}`;

        const senderNameSpan = document.createElement("span");
        senderNameSpan.className = "name";
        senderNameSpan.textContent = role === "user" ? this.userName + " " : this.botName + " ";

        const timestampSpan = document.createElement("span");
        timestampSpan.className = "timestamp";
        timestampSpan.textContent = timestamp;

        senderListItem.appendChild(senderNameSpan);
        senderListItem.appendChild(timestampSpan);

        // create list item for message text
        const messageListItem = document.createElement("li");
        messageListItem.className = `msg-${role}`;

        const imageDiv = document.createElement("div");
        imageDiv.classList.add("attachments");
        messageListItem.appendChild(imageDiv);

        const messageTextSpan = document.createElement("span");
        messageTextSpan.id = "currSpan";
        messageListItem.appendChild(messageTextSpan);

        const messagesContainer = document.getElementById("messages");
        messagesContainer.appendChild(senderListItem);
        messagesContainer.appendChild(messageListItem);
        break;
      
      case "<eos>":
        this.parseMarkdown(currentTextSpan);
        document.querySelectorAll('pre code:not(.highlighted)').forEach((block) => {
            hljs.highlightElement(block);
            block.classList.add('highlighted');
        });
        currentTextSpan.id = "";
        this.disableUserInput(false);
        break;
      
      case "<pong>":
        break;

      default:
        if (messageText) {
          currentTextSpan.textContent += messageText;
        }
        break;
    }
  }

  getMimeType(filename) {
    const mimeTypes = {
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'gif': 'image/gif',
      'bmp': 'image/bmp',
      'webp': 'image/webp',
      'tiff': 'image/tiff',
      'tif': 'image/tiff',
      'svg': 'image/svg+xml',
      'ico': 'image/vnd.microsoft.icon',
      'heic': 'image/heic',
      'heif': 'image/heif'
    };

    const extension = filename.split('.').pop().toLowerCase();
    return mimeTypes[extension] || 'application/octet-stream';
  }

  /**
   * Parses markdown text from an element and converts it into HTML.
   * Then sets the parsed content as innerHTML of that element.
   * @param {HTMLElement} el - The element containing the markdown text.
   */
  parseMarkdown(el) {
    const value = el.textContent.trim();
    const parsedValue = marked.parse(value);
    el.innerHTML = parsedValue;
    el.querySelectorAll(".halimg").forEach((img) => {
        const attachments = img.closest(".msg-assistant").querySelector(".attachments");
        const filename = img.getAttribute("filename").substr("attachments:".length-1);
        const img_b64 = attachments[filename];
        const mime = this.getMimeType(filename)
        img.src = `data:${mime};base64,${img_b64}`;
    });
  }

  /**
   * Displays a visual indicator that the assistant is processing/thinking.
   * @param {string} [role='assistant'] - The role of the message sender.
   */
  showThinkingIndicator(role = "assistant") {
    const loadingListItem = document.createElement("li");
    loadingListItem.className = `msg-${role}`;
    loadingListItem.id = "loading-container";

    const loadingDots = document.createElement("div");
    loadingDots.className = "loading-dots";

    loadingListItem.appendChild(loadingDots);

    const messagesContainer = document.getElementById("messages");
    messagesContainer.appendChild(loadingListItem);
  }

  /**
   * Removes the thinking indicator from the chat interface.
   */
  removeThinkingIndicator() {
    const loadingContainer = document.getElementById("loading-container");
    if (loadingContainer) {
      loadingContainer.remove();
      }
  }

  /**
   * Scrolls the specified element to its bottom.
   * Typically used to keep the chat scrolled to the latest message.
   * @param {HTMLElement} [el=this.chat] - The element to scroll.
   */
  scrollToBottomOfElement(el = this.chat) {
    el.scrollTop = el.scrollHeight;
  }
}

window.onload = () => {
  // document.getElementById("fmt").innerHTML = ChatManager.getCurrentTimestamp();
  window.chatManager = new ChatManager();
};