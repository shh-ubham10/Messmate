import React, { useState } from "react";
import QrScanner from "react-qr-scanner";
import axios from "../../Api/axios";
import Alert from "../../Components/Alert";
import Card from "./Card";

const QrAttendance = () => {
  const [data, setData] = useState([]);
  const [possible, setPossible] = useState(false);
  const [possible1, setPossible1] = useState(false);
  const [possible2, setPossible2] = useState(false);
  const [type, setType] = useState(null);
  const [isCard, setIsCard] = useState(false);
  const [alert, setalert] = useState({
    mode: false,
    message: "",
    type: "bg-[red]",
  });
  const [scanResultWebCam, setScanResultWebCam] = useState("");

  const handleErrorWebCam = (error) => {
    console.log(error);
  };

  const handleScanWebCam = (result) => {
    if (result) {
      setTimeout(() => {
        var result1 = JSON.parse(result.text); // Adjust this line if the result needs parsing
        if (type === "breakfast" && result1.isTodayBreakfast) {
          setPossible(true);
        } else {
          setPossible(false);
        }
        if (type === "lunch" && result1.isTodayLunch) {
          setPossible1(true);
        } else {
          setPossible1(false);
        }
        if (type === "dinner" && result1.isTodayDinner) {
          setPossible2(true);
        } else {
          setPossible2(false);
        }
        setScanResultWebCam(result1);
        setIsCard(true);
      }, 5);
    }
  };

  const takeAttendance = async (userId, planId) => {
    try {
      const verifyThing = type;
      const response = await axios.patch(
        `dailyentry/updateentry`,
        JSON.stringify({ userId, verifyThing, planId }),
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
        }
      );
      setalert({
        mode: true,
        message: response.data.message,
        type: "bg-[green]",
      });
    } catch (error) {
      const message = error.response?.data?.message || "No Server Response";
      setalert({
        mode: true,
        message: message,
        type: "bg-[red]",
      });
    }
  };

  return (
    <div>
      {alert.mode && <Alert alert={alert} setalert={setalert} />}
      <div className="flex items-center justify-center">
        <div className="flex-[1] flex flex-col items-center justify-center h-[40rem]">
          <div className="dayselect flex flex-col">
            <select
              id="day"
              name="menu_day"
              className="bg-gray-50 w-[20rem] border border-gray-300 text-gray-900 text-sm rounded-lg p-2.5 dark:bg-gray-700 dark:border-gray-600"
              value={type}
              onChange={(e) => setType(e.target.value)}
            >
              <option value="" disabled selected>
                Select type
              </option>
              <option value="breakfast">Breakfast</option>
              <option value="lunch">Lunch</option>
              <option value="dinner">Dinner</option>
            </select>
          </div>

          {isCard && (
            <div className="lg:w-4/5 mx-auto flex flex-wrap p-[2rem]">
              {scanResultWebCam.isTodayBreakfast && possible ? (
                <Card
                  scanResultWebCam={scanResultWebCam}
                  takeAttendance={takeAttendance}
                  info="Breakfast"
                />
              ) : scanResultWebCam.isTodayLunch && possible1 ? (
                <Card
                  scanResultWebCam={scanResultWebCam}
                  takeAttendance={takeAttendance}
                  info="Lunch"
                />
              ) : scanResultWebCam.isTodayDinner && possible2 ? (
                <Card
                  scanResultWebCam={scanResultWebCam}
                  takeAttendance={takeAttendance}
                  info="Dinner"
                />
              ) : (
                "You have no plan for today"
              )}
            </div>
          )}
        </div>

        <div className="flex-[1] w-[500px]">
          <h3 className="h2">QR Code Scan by WebCam</h3>
          <QrScanner
            delay={300}
            style={{ width: "400px" }}
            onError={handleErrorWebCam}
            onScan={handleScanWebCam}
          />
        </div>
      </div>
    </div>
  );
};

export default QrAttendance;
