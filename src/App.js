import './App.css';
import './Chart.js';
import Chart from "./Chart";
import Button from "./Button";

import useWebSocket, {ReadyState} from 'react-use-websocket';
import moment from "moment/moment";
import {useEffect, useState} from "react";
import {useLoaderData, useNavigate} from "react-router-dom";

const socketBaseUrl = "ws://localhost:8000/ws/process/"

export async function loader({ params }) {
  return {jobId: params.jobId};
}

function App() {
  const navigate = useNavigate();
  const jobId = useLoaderData();
  const [shouldConnect, setShouldConnect] = useState(!!jobId)
  const [shouldReconnect, setShouldReconnect] = useState(true)
  const [socketUrl, setSocketUrl] = useState(jobId ? socketBaseUrl + jobId.jobId + '/' : "");
  const [data, setData] = useState([])
  const [minEnergy, setMinEnergy] = useState(0.0)
  function onClickStart() {
    fetch("/api/start")
      .then((response) => response.json())
      .then(data => {
        if (!('job_id' in data)) {
          alert("Invalid server response")
          return
        }
        setShouldReconnect(true)
        setData([])
        setMinEnergy(0.0)
        navigate('/job/' + data.job_id + '/')
      })
  }
  const {
    readyState,
    lastMessage
  } = useWebSocket(socketUrl, {
    onOpen: () => {
      setData([])
      console.log("WebSocket opened")
    },
    shouldReconnect: (closeEvent) => {
      console.log("Reconnect reason event:", closeEvent)
      return shouldReconnect
    },
    onMessage: (event) => {
      console.log("Message event:", event)
      const d = JSON.parse(event.data)
      if (d.type === "solution") {
        const startDate = moment(d.date)
        const energy = parseFloat(d.energy)
        const date = startDate.valueOf()
        data.push({date: date, energy: energy + 1000})
        data.sort((a, b) => (a.date > b.date) ? 1 : -1)
        setData([...data])
        if (energy < minEnergy) {
          setMinEnergy(energy)
        }
      } else if (d.type === "stop") {
        setShouldReconnect(false)
      }
    },
  }, shouldConnect)
  useEffect(() => {
    console.log("use effect", jobId)
    if (jobId) {
      const newUrl = socketBaseUrl + jobId.jobId + '/';
      if (newUrl !== socketUrl) {
        setSocketUrl(socketBaseUrl + jobId.jobId + '/');
        setShouldConnect(true);
      }
    }
  }, [jobId])
  const connectionStatus = {
    [ReadyState.CONNECTING]: 'Connecting',
    [ReadyState.OPEN]: 'Open',
    [ReadyState.CLOSING]: 'Closing',
    [ReadyState.CLOSED]: 'Closed',
    [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
  }[readyState];
  return (
    <div className="App">
      <header className="App-header">
        <h1>Evolution Log</h1>
      </header>
      <Chart data={data} />
      <p className="energy-text">Min energy: {minEnergy.toFixed(2)}</p>
      <Button onClick={onClickStart} />
      <p style={{marginTop: "2em", color: "gray"}}>
        Job ID: { jobId ? jobId.jobId : null } &nbsp;
        Last message: {lastMessage ? lastMessage.data : null}.
        Connection status: {readyState ? connectionStatus : null}
      </p>
    </div>
  );
}

export default App;
