document.addEventListener('DOMContentLoaded', (event) => {
    const chartDom1 = document.getElementById('pressure');
    const chartDom2 = document.getElementById('newton');
    const chartDom3 = document.getElementById('temperature');
    
    
    const myChart = echarts.init(chartDom1,'dark');

    const option = {
        animationDuration: 1000,
        // title: {
        //     text: 'Pressure Data Visualization'
        // },
        // backgroundColor: 'transparent',
        legend: {
            data: ['Pressure 1', 'Pressure 2', 'Pressure 3'],
            textStyle: {
                color: '#333'  // Ensure legend text remains visible
            },
            backgroundColor: 'transparent'
            // backgroundColor: 'rgb(0, 0, 0)',
        },
        tooltip: {
            order: 'valueDesc',
            trigger: 'axis'
        },
        toolbox: {
            feature: {
                saveAsImage: {},
                // brush: {},
                // restore: {},
                // dataView: {}
            }
        },
        xAxis: {
            type: 'category',
            name: 'Time (s)',
            nameLocation: 'middle',
            nameGap: 22,
            data: [] // Time labels
        },
        yAxis: {
            name: 'Pressure (psi)',
            nameLocation: 'middle',
            nameGap: 30,
            // offset:10
            // boundaryGap: ['20%']
        },
        grid: {
            left: '7%',
            right: '0%',
            top: '10%',
            bottom: '10%'
        },
        dataZoom: [
            // {
            //     type: 'slider',
            //     start: 0,
            //     end: 100
            // },
            {
                type: 'inside',
                start: 0,
                end: 100
            }
        ],
        series: [
            {
                name: 'Pressure 1',
                type: 'line',
                showSymbol: true,
                smooth: true,
                emphasis: {
                    focus: 'series'
                },
                data: [] // Pressure 1 data
            },
            {
                name: 'Pressure 2',
                type: 'line',
                showSymbol: true,
                smooth: true,
                emphasis: {
                    focus: 'series'
                },
                data: [] // Pressure 2 data
            },
            {
                name: 'Pressure 3',
                type: 'line',
                showSymbol: true,
                smooth: true,
                emphasis: {
                    focus: 'series'
                },
                data: [] // Pressure 2 data
            }

        ]
    };

    // loadcell
    const loadChart = echarts.init(chartDom2 ,'dark');

    const loadoption = {
        animationDuration: 1000,
        // title: {
        //     text: 'Pressure Data Visualization'
        // },
        legend: {
            data: ['loadcell']
        },
        tooltip: {
            order: 'valueDesc',
            trigger: 'axis'
        },
        toolbox: {
            feature: {
                saveAsImage: {},
                // brush: {},
                // restore: {},
                // dataView: {}
            }
        },
        xAxis: {
            type: 'category',
            name: 'Time (s)',
            nameLocation: 'middle',
            data: [] // Time labels
            , nameGap: 22,
        },
        yAxis: {
            name: 'loadcell (N)',
            nameLocation: 'middle',
            nameGap: 30,
        },
        grid: {
            left: '7%',
            right: '0%',
            top: '10%',
            bottom: '10%'
        },
        dataZoom: [
            // {
            //     type: 'slider',
            //     start: 0,
            //     end: 100
            // },
            {
                type: 'inside',
                start: 0,
                end: 100
            }
        ],
        series: [
            {
                name: 'loadcell',
                type: 'line',
                showSymbol: true,
                smooth: true,
                emphasis: {
                    focus: 'series'
                },
                data: [] // loadcell data
            }
        ]
    };

    //for temp
    const tempChart = echarts.init(chartDom3,'dark');

    const tempOption = {
        animationDuration: 1000,
        legend: {
            data: ['Temperature 1']
        },
        tooltip: {
            order: 'valueDesc',
            trigger: 'axis'
        },
        toolbox: {
            feature: {
                saveAsImage: {},
                // brush: {},
                // restore: {},
                // dataView: {}
            }
        },
        xAxis: {
            type: 'category',
            name: 'Time (s)',
            nameLocation: 'middle',
            data: [] // Time labels
            , nameGap: 22,
        },
        yAxis: {
            name: 'Temperature (°C)',
            nameLocation: 'middle',
            nameGap: 30,
        },
        grid: {
            left: '7%',
            right: '0%',
            top: '10%',
            bottom: '10%'
        },
        dataZoom: [{
            type: 'inside',
            start: 0,
            end: 100
        }],
        series: [
            {
                name: 'Temperature 1',
                type: 'line',
                showSymbol: true,
                smooth: true,
                emphasis: {
                    focus: 'series'
                },
                data: [] // Temperature 1 data
            },
            // {
            //     name: 'Temperature 2',
            //     type: 'line',
            //     showSymbol: true,
            //     smooth: true,
            //     emphasis: {
            //         focus: 'series'
            //     },
            //     data: [] // Temperature 2 data
            // }
        ]
    };

    myChart.setOption(option);
    loadChart.setOption(loadoption);
    tempChart.setOption(tempOption);

    // Plot initial data
    const initialData = JSON.parse('{{ data | tojson | safe }}');
    // const initialDataElement = document.getElementById('initial-data');
    // const initialData = initialDataElement ? JSON.parse(initialDataElement.textContent) : [];
    const timeSet = new Set();
    initialData.forEach(record => {
        const timeString = record.time;
        const pressure1 = record.pressure1;
        const pressure2 = record.pressure2;
        const pressure3 = record.pressure3;
        const temperature1 = record.temperature1;
        const loadcell = record.loadcell;

        option.xAxis.data.unshift(timeString);
        option.series[0].data.unshift(pressure1);
        option.series[1].data.unshift(pressure2);
        option.series[2].data.unshift(pressure3);

        //for temp
        tempOption.xAxis.data.unshift(timeString);
        tempOption.series[0].data.unshift(temperature1);

        //for loadcell
        loadoption.xAxis.data.unshift(timeString);
        loadoption.series[0].data.unshift(loadcell);
        timeSet.add(timeString);
    });

    myChart.setOption(option);
    loadChart.setOption(loadoption);
    tempChart.setOption(tempOption);

    let fetchDataInterval;
    const fetchData = () => {
        fetch('/latest_data')
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    const latestData = data[0];
                    console.log(latestData);
                    const timeString = latestData.time;
                    const pressure1 = latestData.pressure1;
                    const pressure2 = latestData.pressure2;
                    const pressure3 = latestData.pressure3;
                    const temperature1 = latestData.temperature1;
                    const loadcell = latestData.loadcell;

                    option.xAxis.data.push(timeString);
                    option.series[0].data.push(pressure1);
                    option.series[1].data.push(pressure2);
                    option.series[2].data.push(pressure3);

                    //for temp
                    tempOption.xAxis.data.push(timeString);
                    tempOption.series[0].data.push(temperature1);

                    //for loadcell
                    loadoption.xAxis.data.push(timeString);
                    loadoption.series[0].data.push(loadcell);


                    myChart.setOption(option);
                    loadChart.setOption(loadoption);
                    tempChart.setOption(tempOption);
                }
            })
            .catch(error => console.error('Error fetching data:', error));
    };

    // Fetch data every 1 second
    fetchDataInterval = setInterval(fetchData, 1000);

    // Resize chart on window resize
    window.addEventListener('resize', () => {
        myChart.resize();
        tempChart.resize();
    });

    // Control button to pause/resume fetching data
    const controlBtn = document.getElementById('controlBtn');
    let isPaused = false;
    controlBtn.addEventListener('click', () => {
        if (isPaused) {
            fetchDataInterval = setInterval(fetchData, 1000);
            controlBtn.textContent = 'Pause';
        } else {
            clearInterval(fetchDataInterval);
            controlBtn.textContent = 'Resume';
        }
        isPaused = !isPaused;
    });
});