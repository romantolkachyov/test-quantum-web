import moment from "moment";

const socketBaseUrl = `ws://${window.location.host}/ws/process/`

export function generateDemoData() {
  const defaultData = []
  let sampleDate = moment()
  for (let i = 0; i <= 100; i++) {
    defaultData.push({
      date: sampleDate.valueOf(),
      energy: Math.cos(i / 5)
    })
    sampleDate.add('1', 'minute')
  }
  return defaultData
}

export function jobWebSocketUrl(jobId) {
  return jobId ? socketBaseUrl + jobId + '/' : ""
}
