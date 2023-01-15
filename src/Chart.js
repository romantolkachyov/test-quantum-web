import {
  AreaChart,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Area
} from 'recharts';
import moment from "moment";

function Chart({ data, dataOffset, demoMode }) {
  if (demoMode) {
    dataOffset = 0;
  }
  const dateFormatter = date => {
    return moment(date).format('DD MMM HH:mm');
  };

  const energyFormatter = value => {
    return (value - dataOffset).toFixed(2)
  }

  const tooltipContentFormatter = (label, payload) => {
    return moment(label).format('DD MMM HH:mm')
  }
  if (demoMode) {
    return (
      <ResponsiveContainer
        width="80%"
        height={400}
        key={(data.startIndex || 0) + (data.endIndex || 0)}>
        <AreaChart
          width={900}
          height={400}
          data={data}
          margin={{ top: 20, right: 20, left: 30, bottom: 10 }}>
          <Area type="monotone"
            dataKey="energy"
            stroke="#8884d8"
            animationDuration={600}
            dot={true}/>
        </AreaChart>
    </ResponsiveContainer>
    )
  }
  return (
    <ResponsiveContainer width="80%" height={400} key={(data.startIndex || 0) + (data.endIndex || 0)}>
      <AreaChart
        width={900}
        height={400}
        data={data}
        margin={{ top: 20, right: 20, left: 30, bottom: 10 }}>
        <Area
          type="monotone"
          dataKey="energy"
          stroke="#8884d8"
          animationDuration={600}
          dot={true}/>
        <XAxis
          dataKey="date"
          tickFormatter={dateFormatter}
          scale="time"
          tickLine={false}
          type="number"
          tickMargin={15}
          domain={['dataMin', 'dataMax']}/>
        <YAxis
          type="number"
          scale="linear"
          tickCount={4}
          domain={['dataMin', 'dataMax']}
          tickMargin={10}
          tickFormatter={energyFormatter}/>
        <Tooltip
          animationDuration="150"
          formatter={energyFormatter}
          labelFormatter={tooltipContentFormatter}
          contentStyle={{color: "black"}}/>
      </AreaChart>
    </ResponsiveContainer>
  )
}

export default Chart
