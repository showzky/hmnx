<template>
    <div class="staff-lounge">
      <h2>Staff Lounge</h2>
      
      <!-- Chat Room Styled as a Break Room -->
      <section class="chat-room">
        <h3>Break Room Chat</h3>
        <div class="messages">
          <!-- Example static messages; later you can integrate real-time chat functionality -->
          <p><strong>Dr. Galskap:</strong> Who's up for a coffee break?</p>
          <p><strong>Nurse Loco:</strong> I need a fix, stat!</p>
        </div>
        <input v-model="newMessage" placeholder="Type a message..." @keyup.enter="sendMessage" />
        <button @click="sendMessage">Send</button>
      </section>
      
      <!-- Kitchen Area with Random Events -->
      <section class="kitchen">
        <div class="coffee-machine" @click="simulateCoffeeBreak">
          <p>{{ coffeeStatus }}</p>
        </div>
        <div class="microwave" @click="simulateMicrowave">
          <p>{{ microwaveStatus }}</p>
        </div>
      </section>
      
      <!-- Medical Gossip Board -->
      <section class="gossip-board">
        <h3>Medical Gossip Board</h3>
        <ul>
          <li v-for="(gossip, index) in gossips" :key="index">
            {{ gossip }}
          </li>
        </ul>
        <input v-model="newGossip" placeholder="Share a rumor..." @keyup.enter="postGossip" />
        <button @click="postGossip">Post</button>
      </section>
    </div>
  </template>
  
  <script>
  export default {
    name: 'StaffLounge',
    data() {
      return {
        // Chat room data (for a simple demo, static messages are used)
        newMessage: "",
        // Kitchen status messages
        coffeeStatus: "Coffee machine is brewing...",
        microwaveStatus: "Microwave is warming up...",
        // Gossip board data
        gossips: [
          "Who used the defibrillator to charge their phone? 🔌"
        ],
        newGossip: ""
      };
    },
    methods: {
      // Chat room functionality (placeholder)
      sendMessage() {
        if (this.newMessage.trim() !== "") {
          // For now, just log the message. Later, integrate a real chat service or push it into a messages array.
          console.log("New message:", this.newMessage);
          this.newMessage = "";
        }
      },
      // Simulate a random event for the coffee machine
      simulateCoffeeBreak() {
        const events = [
          "Coffee machine broke down! ☕️💥",
          "Coffee machine is overheating! ☕️🔥",
          "Coffee machine is working perfectly."
        ];
        this.coffeeStatus = events[Math.floor(Math.random() * events.length)];
      },
      // Simulate a random event for the microwave
      simulateMicrowave() {
        const events = [
          "Microwave caused a biohazard explosion! 💣🧫",
          "Microwave is humming normally."
        ];
        this.microwaveStatus = events[Math.floor(Math.random() * events.length)];
      },
      // Add a new gossip post to the board
      postGossip() {
        if (this.newGossip.trim() !== "") {
          this.gossips.push(this.newGossip);
          this.newGossip = "";
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .staff-lounge {
    padding: 2rem;
    background-color: #f7f9fc;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    margin: 2rem 0;
  }
  
  .staff-lounge h2 {
    text-align: center;
    margin-bottom: 1.5rem;
  }
  
  /* Chat Room Styles */
  .chat-room {
    margin-bottom: 2rem;
  }
  
  .chat-room .messages {
    background: #fff;
    padding: 1rem;
    border-radius: 8px;
    max-height: 150px;
    overflow-y: auto;
    margin-bottom: 1rem;
  }
  
  .chat-room input {
    width: calc(100% - 100px);
    padding: 0.5rem;
    margin-right: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 8px;
  }
  
  .chat-room button {
    padding: 0.5rem 1rem;
    border: none;
    background: #3498db;
    color: #fff;
    border-radius: 8px;
    cursor: pointer;
  }
  
  /* Kitchen Area Styles */
  .kitchen {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .coffee-machine,
  .microwave {
    flex: 1;
    background: #fff;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    cursor: pointer;
    text-align: center;
    transition: transform 0.2s ease;
  }
  
  .coffee-machine:hover,
  .microwave:hover {
    transform: scale(1.05);
  }
  
  /* Gossip Board Styles */
  .gossip-board ul {
    list-style: none;
    padding: 0;
    margin-bottom: 1rem;
  }
  
  .gossip-board li {
    background: #e8f4ff;
    padding: 0.5rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
  }
  
  .gossip-board input {
    width: calc(100% - 100px);
    padding: 0.5rem;
    margin-right: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 8px;
  }
  
  .gossip-board button {
    padding: 0.5rem 1rem;
    border: none;
    background: #2ecc71;
    color: #fff;
    border-radius: 8px;
    cursor: pointer;
  }
  </style>
  