import React, { useState, useEffect } from "react";
import SignupPhoto from "../../Svg/Signup.png";
import axios from "../../Api/axios";
import Alert from "../../Components/Alert";

const Email_Checker = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
const Mobile_Cheker = /^[6-9]\d{9}$/gi;

const Adduser = () => {
  const [alert, setalert] = useState({
    mode: false,
    message: "",
    type: "bg-[red]",
  });

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [regId, setRegId] = useState("");
  const [validEmail, setValidEmail] = useState(false);
  const [mobileno, setMobileNo] = useState();
  const [validMobile, setValidMobile] = useState(false);
  const [role, setRole] = useState(0);
  const [password, setPassword] = useState("");
  const [validPassword, setValidPassword] = useState(false);
  const [cpassword, setCPassword] = useState("");
  const [validCPasswd, setValidCPasswd] = useState(false);
  const [errMsg, setErrMsg] = useState("");
  const [success, setSuccess] = useState(false);

  const [image, setImage] = useState(null); // Added state for image file

  // validation in all fields
  useEffect(() => {
    setValidEmail(Email_Checker.test(email));
  }, [email]);

  useEffect(() => {
    setValidMobile(Mobile_Cheker.test(mobileno));
  }, [mobileno]);

  useEffect(() => {
    setValidPassword(true);
    setValidCPasswd(password === cpassword);
  }, [password, cpassword]);

  useEffect(() => {
    setErrMsg("");
  }, [email, password, cpassword]);

  // handling submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    const e1 = Email_Checker.test(email);
    const e2 = validPassword;
    if (!e1 || !e2) {
      setErrMsg("Invalid Entry");
      return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("email", email);
    formData.append("mobileno", mobileno);
    formData.append("role", role);
    formData.append("password", password);
    formData.append("cpassword", cpassword);
    formData.append("regId", regId);
    if (image) {
      formData.append("image", image);
    }

    try {
      const response = await axios.post("/users/signup", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        withCredentials: true,
      });

      console.log(JSON.stringify(response?.data));
      setSuccess(true);

      // Clear state and controlled inputs
      setName("");
      setEmail("");
      setRegId("");
      setMobileNo("");
      setRole(0);
      setPassword("");
      setCPassword("");
      setImage(null);
      setalert({
        mode: true,
        message: "User registered successfully",
        type: "bg-[green]",
      });

      // Call the encoding generation API
      try {
        const encodeResponse = await fetch(
          "http://localhost:5000/encode/generate_encodings",
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        if (!encodeResponse.ok) {
          throw new Error("Failed to generate encoding");
        }

        const encodeData = await encodeResponse.json();
        console.log("Encoding response:", encodeData);
      } catch (encodeError) {
        console.error("Error generating encodings:", encodeError);
        setalert({
          mode: true,
          message: "Encoding generation failed",
          type: "bg-[red]",
        });
      }
    } catch (err) {
      if (!err?.response) {
        setalert({
          mode: true,
          message: "No Server Response",
          type: "bg-[red]",
        });
      } else if (err.response?.status === 409) {
        setalert({
          mode: true,
          message: "User Name Taken",
          type: "bg-[red]",
        });
      } else {
        setalert({
          mode: true,
          message: "Registration failed",
          type: "bg-[red]",
        });
      }
    }
  };

  return (
    <>
      <section className="text-gray-600 body-font">
        {alert.mode ? <Alert alert={alert} setalert={setalert} /> : ""}
        <div className="container mx-auto flex flex-wrap items-center justify-between">
          <div className="lg:w-3/5 md:w-1/2 md:pr-16 lg:pr-0 flex-[5] pr-4">
            <img
              src={SignupPhoto}
              aria-hidden
              className="min-h-fit"
              alt="Photo coming please wait"
            />
          </div>
          <div className="lg:w-2/6 md:w-1/2 p-9 ml-8 bg-gray-100 rounded-lg flex flex-[5] flex-col md:ml-auto w-full mt-10 md:mt-0">
            <h2 className="text-gray-900 text-3xl text-center font-medium title-font ">
              Add user
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="relative mb-4">
                <label
                  htmlFor="full-name"
                  className="leading-7 text-sm text-gray-600"
                >
                  Full Name
                </label>
                <input
                  type="text"
                  id="full-name"
                  name="name"
                  onChange={(e) => setName(e.target.value)}
                  value={name}
                  className="w-full bg-white rounded border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
                />
              </div>

              <div className="relative mb-4">
                <label
                  htmlFor="regId"
                  className="leading-7 text-sm text-gray-600"
                >
                  ID
                </label>
                <input
                  type="text"
                  id="regId"
                  name="regId"
                  onChange={(e) => setRegId(e.target.value)}
                  value={regId}
                  className="w-full bg-white rounded border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
                />
              </div>

              <div className="relative mb-4">
                <label
                  htmlFor="email"
                  className="leading-7 text-sm text-gray-600"
                >
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  onChange={(e) => setEmail(e.target.value)}
                  value={email}
                  className="w-full bg-white rounded border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
                />
              </div>

              <div className="relative mb-4">
                <label
                  htmlFor="contact"
                  className="leading-7 text-sm text-gray-600"
                >
                  Contact Number
                </label>
                <input
                  type="number"
                  id="contact"
                  name="mobileno"
                  onChange={(e) => setMobileNo(e.target.value)}
                  value={mobileno}
                  className="w-full bg-white rounded border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
                />
              </div>

              <div className="relative mb-4">
                <label
                  htmlFor="role"
                  className="leading-7 text-sm text-gray-600"
                >
                  Role
                </label>
                <select
                  id="role"
                  name="role"
                  onChange={(e) => setRole(e.target.value)}
                  value={role}
                  className="w-full bg-white rounded border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
                >
                  <option value={0} defaultChecked>
                    User
                  </option>
                  <option value={1}> Admin </option>
                  <option value={2}> Employee </option>
                </select>
              </div>

              <div className="relative mb-4">
                <label
                  htmlFor="password"
                  className="leading-7 text-sm text-gray-600"
                >
                  Password
                </label>
                <input
                  type="text"
                  id="password"
                  name="password"
                  onChange={(e) => setPassword(e.target.value)}
                  value={password}
                  className="w-full bg-white rounded border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
                />
              </div>

              <div className="relative mb-4">
                <label
                  htmlFor="cpassword"
                  className="leading-7 text-sm text-gray-600"
                >
                  Confirm Password
                </label>
                <input
                  type="password"
                  id="cpassword"
                  name="cpassword"
                  onChange={(e) => setCPassword(e.target.value)}
                  value={cpassword}
                  className="w-full bg-white rounded border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
                />
              </div>

              {/* Image Upload */}
              <div className="relative mb-4">
                <label
                  htmlFor="image"
                  className="leading-7 text-sm text-gray-600"
                >
                  Profile Image
                </label>
                <input
                  type="file"
                  id="image"
                  name="image"
                  accept="image/*"
                  onChange={(e) => setImage(e.target.files[0])}
                  className="w-full bg-white rounded border border-gray-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
                />
              </div>

              <button
                type="submit"
                className="text-white bg-indigo-500 border-0 py-2 px-6 focus:outline-none hover:bg-indigo-600 rounded text-lg"
              >
                Add user
              </button>
            </form>
          </div>
        </div>
      </section>
    </>
  );
};

export default Adduser;
