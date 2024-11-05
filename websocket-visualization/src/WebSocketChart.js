// src/WebSocketChart.js
import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import io from 'socket.io-client';
import 'chartjs-adapter-date-fns';

const socket = io('http://localhost:5000');

const WebSocketChart = () => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Pressure 1',
        data: [],
        borderColor: 'rgba(75, 192, 192, 1)',
        fill: false,
        tension: 0.4,
      },
      {
        label: 'Pressure 2',
        data: [],
        borderColor: 'rgb(164, 18, 18)',
        fill: false,
        tension: 0.4,
      },
    ],
  });

  useEffect(() => {
    socket.on('new_data', (latestData) => {
      const timeString = latestData.time;
      const [hours, minutes, seconds, milliseconds] = timeString.split(':').map(Number);
      const time = new Date();
      time.setHours(hours, minutes, seconds, milliseconds);

      setChartData((prevData) => ({
        ...prevData,
        labels: [...prevData.labels, time],
        datasets: [
          {
            ...prevData.datasets[0],
            data: [...prevData.datasets[0].data, latestData.pressure1],
          },
          {
            ...prevData.datasets[1],
            data: [...prevData.datasets[1].data, latestData.pressure2],
          },
        ],
      }));
    });

    return () => {
      socket.off('new_data');
    };
  }, []);

  const options = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Real-time Pressure Data',
      },
    },
    interaction: {
      intersect: false,
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'second',
          tooltipFormat: 'HH:mm:ss:SSS',
          displayFormats: {
            second: 'ss',
          },
        },
        display: true,
        title: {
          display: true,
          text: 'Time',
        },
      },
      y: {
        display: true,
        title: {
          display: true,
          text: 'Pressure',
        },
        suggestedMin: 0,
        suggestedMax: 100,
      },
    },
  };

  return <Line data={chartData} options={options} />;
};

export default WebSocketChart;