import './Status.css'

function Status({ state, lastStopReason, ...props }) {
  let statusText = "Press Start button to generate sample and run solver."
  if (state === 'waiting') {
    statusText = "Waiting for a worker to pickup your task."
  } else if (state === 'running') {
    statusText = "Worker is running your task at the moment."
  } else if (state === 'active' && lastStopReason) {
    statusText = lastStopReason
  }
  return <div className="Status" {...props}>{statusText}</div>
}

export default Status
