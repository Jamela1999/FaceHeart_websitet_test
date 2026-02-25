// Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyD1pSfVCSuURgsY4Vb1oQxKWtPZqh7Sr68",
    authDomain: "pdca-tracker.firebaseapp.com",
    databaseURL: "https://pdca-tracker-default-rtdb.firebaseio.com",
    projectId: "pdca-tracker",
    storageBucket: "pdca-tracker.firebasestorage.app",
    messagingSenderId: "525235659576",
    appId: "1:525235659576:web:775508f84754933bd497cd"
};

// Initialize Firebase
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
const database = firebase.database();
