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

const defaultData = []
let sampleDate = moment()
for(let i=0; i<=100; i++) {
  defaultData.push({
    date: sampleDate.valueOf(),
    energy: Math.cos(i / 5)
  })
  sampleDate.add('1', 'minute')
}

function App() {
  const navigate = useNavigate();
  const jobId = useLoaderData();
  const [shouldConnect, setShouldConnect] = useState(!!jobId)
  const [shouldReconnect, setShouldReconnect] = useState(true)
  const [socketUrl, setSocketUrl] = useState(jobId ? socketBaseUrl + jobId.jobId + '/' : "");
  const [data, setData] = useState(defaultData)
  const [minEnergy, setMinEnergy] = useState(0.0)
  const [buttonState, setButtonState] = useState("loading")
  const [lastStopReason, setLastStopReason] = useState("")
  const [demoMode, setDemoMode] = useState(true)

  function getStatusText() {
    if (buttonState === 'waiting') {
      return "Waiting for a worker to pickup your task."
    } else if (buttonState === 'running') {
      return (
        <div>Worker is running your task at the moment.</div>
      )
    } else if (buttonState === 'active' && lastStopReason) {
      return lastStopReason
    }
    return (<div>&nbsp;</div>)
  }
  function onClickStart() {
    setButtonState('waiting')
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
  useWebSocket(socketUrl, {
    onOpen: () => {
      setDemoMode(false)
      setData([])
      console.log("WebSocket opened")
    },
    shouldReconnect: (closeEvent) => false,
    onMessage: (event) => {
      console.log("Message event:", event)
      setButtonState('running')
      const d = JSON.parse(event.data)
      if (d.type === "solution") {
        const startDate = moment(d.date)
        const energy = parseFloat(d.energy)
        let date = startDate.valueOf()
        // hack to fix chart: broken if there are more than one point in
        // particular millisecond (max resolution of moment.js)
        if (data.length > 0) {
          const lastDate = data[data.length-1].date
          if (date <= lastDate) {
            date = lastDate + 1
          }
        }
        data.push({date: date, energy: energy + 1000})
        setData([...data])
        if (energy < minEnergy) {
          setMinEnergy(energy)
        }
      } else if (d.type === "stop") {
        setButtonState('active')
        setShouldReconnect(false)
        setLastStopReason(d.reason)
        console.log("STOP RECEIVED")
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
  return (
    <div className="App">
      <header className="App-header">
        <h1>Evolution Log</h1>
      </header>
      <Chart data={data} demoMode={demoMode} hackOffset={1000} />
      <p className="energy-text">Min energy: {minEnergy.toFixed(2)}</p>
      <Button onClick={onClickStart} state={buttonState} />
      <div style={{marginTop: "2em", color: "gray"}}>{getStatusText()}</div>
    </div>
  );
}

export default App;
