import moment from "moment/moment";
import useWebSocket from 'react-use-websocket';
import {useCallback, useEffect, useState} from "react";
import {useLoaderData, useNavigate} from "react-router-dom";
import {generateDemoData, jobWebSocketUrl} from "./utils";

import './App.css';
import Chart from "./Chart";
import Button from "./Button";
import Status from "./Status";

export async function loader({ params }) {
  return 'jobId' in params ? params.jobId : null;
}

function App() {
  const navigate = useNavigate();
  // jobId from the path
  const jobId = useLoaderData();
  const [shouldConnect, setShouldConnect] = useState(!!jobId)
  const [socketUrl, setSocketUrl] = useState(jobWebSocketUrl(jobId));
  const [chartData, setChartData] = useState(generateDemoData())
  const [minEnergy, setMinEnergy] = useState(0.0)
  const [status, setStatus] = useState("loading")
  const [lastStopReason, setLastStopReason] = useState("")
  const [demoMode, setDemoMode] = useState(true)

  const onClickStart = useCallback(() => {
    setStatus('waiting')
    fetch("/api/start")
      .then((response) => response.json())
      .then(data => {
        if (!('job_id' in data)) {
          alert("Invalid server response")
          return
        }
        setChartData([])
        setMinEnergy(0.0)
        navigate('/job/' + data.job_id + '/')
      })
  }, [navigate])

  function addSolution(date, energy) {
    let dateValue = moment(date).valueOf()
    // hack to fix chart: broken if there are more than one point in
    // particular millisecond (max resolution of moment.js)
    if (chartData.length > 0) {
      const lastDate = chartData[chartData.length-1].date
      if (dateValue <= lastDate) {
        dateValue = lastDate + 1
      }
    }
    chartData.push({date: dateValue, energy: energy + 1000})
    return [...chartData]
  }

  useWebSocket(socketUrl, {
    onOpen: () => {
      setDemoMode(false)
      setChartData([])
    },
    shouldReconnect: (closeEvent) => false,
    onMessage: (event) => {
      if (status === 'waiting') {
        setStatus('running')
      }
      const d = JSON.parse(event.data)
      if (d.type === "solution") {
        const energy = parseFloat(d.energy)
        if (energy < minEnergy) {
          setMinEnergy(energy)
        }
        setChartData(addSolution(d.date, energy))
      } else if (d.type === "stop") {
        setStatus('active')
        setLastStopReason(d.reason)
      }
    },
  }, shouldConnect)

  useEffect(() => {
    if (jobId) {
      const newUrl = jobWebSocketUrl(jobId);
      if (newUrl !== socketUrl) {
        setSocketUrl(newUrl);
        setShouldConnect(true);
      }
    } else {
      setStatus('active')
    }
  }, [jobId])

  return (
    <div className="App">
      <header className="App-header">
        <h1>Evolution Log</h1>
      </header>
      <Chart data={chartData} demoMode={demoMode} hackOffset={1000} />
      <p className="energy-text">Min energy: {minEnergy.toFixed(2)}</p>
      <Button onClick={onClickStart} state={status} />
      <Status state={status} lastStopReason={lastStopReason} />
    </div>
  );
}

export default App;
