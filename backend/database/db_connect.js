import mongoose from "mongoose";
console.log("Welcome to mongoose");
import dotenv from "dotenv";
import firebaseAdmin from "firebase-admin";
import serviceAccount from "../assets/serviceAccountKey.json" assert { type: "json" };

// dotenv.config({path:'../config.env'})

const Connection = async () => {
  console.log("go to db connect");
  // const url = process.env.DATABASE
  // const url ='mongodb+srv://Jenil45:Rb@45-93@messmanagement.wxqw4s9.mongodb.net/test'
  firebaseAdmin.initializeApp({
    credential: firebaseAdmin.credential.cert(serviceAccount),
    storageBucket: "messmate-82681.appspot.com", // Set your storage bucket here
    databaseURL: "https://messmate-82681-default-rtdb.firebaseio.com/", // Add your Firebase Realtime Database URL here
  });

  await mongoose
    .connect(process.env.DATABASE)
    .then(() => {
      console.log("Connection Successfull");
    })
    .catch((e) => {
      console.log("Error of db :", e);
    });
};

export default Connection;
