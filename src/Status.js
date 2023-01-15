import './Status.css'

function Status({ state, lastStopReason, error, ...props }) {
  let statusText = "Press Start button to generate sample and run solver."
  if (error) {
    statusText = error;
  }
  if (state === 'waiting') {
    statusText = "Waiting for a worker to pickup your task."
  } else if (state === 'running') {
    statusText = "Worker is running your task at the moment."
  } else if (state === 'loading') {
    statusText = <div>&nbsp;</div>
  } else if (state === 'active' && lastStopReason) {
    statusText = lastStopReason
  }
  return <div className="Status" {...props}>{statusText}</div>
}

export default Status
