import React, { useState, useRef } from 'react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

import { authHeader } from 'tools/fetch-wrapper';
import { DataLineChart } from '../charts/DataLineChart';
import { DataPieChart } from '../charts/DataPieChart';
import { EditableTitle } from './EditableTitle';
import { text_resources } from '../resources'


export const AnalyticalSection = ({ language }) => {
    const [periodGroup, setPeriodGroup] = useState('day');
    const [cubeInfo, setCubeInfo] = useState({});
    const [cubeData, setCubeData] = useState([]);
    const [showButtons, setShowButtons] = useState(true);
    const chartContainerRef = useRef(null);

    const [lineChartFilters, setLineChartFilters] = useState([]);
    const [pieChartFilters, setPieChartFilters] = useState([]);

    const handlePeriodGroupTypeChange = (e) => {
        const newPeriodGroup = e.target.value;
        setPeriodGroup(newPeriodGroup);
        setCubeData([]);
    };

    const handleAddLineChart = () => {
        setLineChartFilters([...lineChartFilters, { title: text_resources["LineChartDefaultTitle"][language] }]);
    };

    const handleAddPieChart = () => {
        setPieChartFilters([...pieChartFilters, { title: text_resources["PieChartDefaultTitle"][language] }]);
    };

    const handleRemoveLineChart = (index) => {
        setLineChartFilters(lineChartFilters.filter((_, i) => i !== index));
    };

    const handleRemovePieChart = (index) => {
        setPieChartFilters(pieChartFilters.filter((_, i) => i !== index));
    };

    const handleTitleChange = (index, type, newTitle) => {
        if (type === 'line') {
            const updatedFilters = [...lineChartFilters];
            updatedFilters[index].title = newTitle;
            setLineChartFilters(updatedFilters);
        } else if (type === 'pie') {
            const updatedFilters = [...pieChartFilters];
            updatedFilters[index].title = newTitle;
            setPieChartFilters(updatedFilters);
        }
    };

    const handleDownloadPdf = async () => {
        // Устанавливаем флаг в false, чтобы скрыть кнопки
        setShowButtons(false);
    
        const chartContainer = document.getElementById('chart-container');
        if (!chartContainer) {
            console.error('Element with id "chart-container" not found');
            return;
        }
    
        const pdf = new jsPDF();
        const options = { background: 'white' };
    
        const charts = chartContainer.querySelectorAll('.chart-wrapper');
        let yOffset = 10; // Начальный y-offset
    
        for (let i = 0; i < charts.length; i++) {
            const chart = charts[i];
            const canvas = await html2canvas(chart, options);
    
            const imgData = canvas.toDataURL('image/png');
            const imgWidth = 190; // Ширина A4 в мм
            const imgHeight = (canvas.height * imgWidth) / canvas.width;
    
            if (yOffset + imgHeight > 280) {
                pdf.addPage(); // Создаем новую страницу, если текущий график не помещается на текущей странице
                yOffset = 10; // Сбрасываем y-offset
            }
    
            if (charts.length === 1) {
                pdf.setPageSize([imgWidth, imgHeight]); // Устанавливаем размер страницы, чтобы он соответствовал размеру графика
            }
    
            pdf.addImage(imgData, 'PNG', 10, yOffset, imgWidth, imgHeight);
            yOffset += imgHeight + 10; // Увеличиваем y-offset для следующего графика
        }
    
        pdf.save('charts.pdf');
    
        // Восстанавливаем состояние, чтобы кнопки снова были видимы
        setShowButtons(true);
    };

    async function getCubeData() {
        try {
            const urlCubeInfo = `${process.env.REACT_APP_API_URL}/get_cube_info/`;
            const cubeInfoResponse = await fetch(urlCubeInfo, {
                method: 'GET',
                headers: authHeader(urlCubeInfo)
            });

            if (!cubeInfoResponse.ok) {
                throw new Error('Failed to get cube info');
            }

            const cubeInfo = await cubeInfoResponse.json();
            setCubeInfo(cubeInfo);

            const urlCubeData = `${process.env.REACT_APP_API_URL}/get_cube_data/?period_group=${periodGroup}`;
            const cubeDataResponse = await fetch(urlCubeData, {
                method: 'GET',
                headers: authHeader(urlCubeData)
            });

            if (!cubeDataResponse.ok) {
                throw new Error('Failed to get cube data');
            }

            let cubeData = await cubeDataResponse.json();

            if (periodGroup === 'day') {
                cubeData = cubeData.map(item => ({
                    ...item,
                    Data: item.Data.split('T')[0]
                }));
            }

            setCubeData(cubeData);
            alert(text_resources["gotDataSuccessfully"][language]);

            console.log('Cube Info:', cubeInfo);
            console.log('Cube Data:', cubeData);
        } catch (error) {
            alert(text_resources["receivingDataFailed"][language]);
            console.error('Error receiving cube info or data:', error);
        }
    }

    return (
        <section>
            <div>
                <label className="mr-2">{text_resources["periodGroup"][language]}:</label>
                <select onChange={handlePeriodGroupTypeChange} value={periodGroup}>
                    <option value="day">{text_resources["day"][language]}</option>
                    <option value="month">{text_resources["month"][language]}</option>
                    <option value="year">{text_resources["year"][language]}</option>
                </select>
                <br />
                <button className='btn btn-primary mb-3 mt-3' onClick={getCubeData}>{text_resources["getCube"][language]}</button>
                <hr className="hr-bright" />
            </div>
            <div ref={chartContainerRef} id='chart-container'>
                <div>
                    {lineChartFilters.map((filters, index) => (
                        <div key={`line-chart-${index}`} style={{ position: 'relative', marginBottom: '20px' }} className='chart-wrapper'>
                            <EditableTitle
                                title={filters.title}
                                onChange={(newTitle) => handleTitleChange(index, 'line', newTitle)}
                            />
                            <DataLineChart language={language} periodGroup={periodGroup} cubeInfo={cubeInfo} cubeData={cubeData} />
                            {showButtons && 
                                <button 
                                    className='btn btn-danger mt-2' 
                                    onClick={() => handleRemoveLineChart(index)} 
                                    style={{ position: 'absolute', right: 0, top: 0 }}>
                                        {text_resources["delete"][language]}
                                </button>
                            }
                            <hr />
                        </div>
                    ))}
                    <button className='btn btn-success' onClick={handleAddLineChart}>{text_resources["addLineChart"][language]}</button>
                    <hr className="hr-bright" />
                </div>
                <div>
                    {pieChartFilters.map((filters, index) => (
                        <div key={`pie-chart-${index}`} style={{ position: 'relative', marginBottom: '20px' }} className='chart-wrapper'>
                            <EditableTitle
                                title={filters.title}
                                onChange={(newTitle) => handleTitleChange(index, 'pie', newTitle)}
                            />
                            <DataPieChart language={language} periodGroup={periodGroup} cubeInfo={cubeInfo} cubeData={cubeData} />
                            {showButtons && 
                                <button 
                                    className='btn btn-danger mt-2' 
                                    onClick={() => handleRemovePieChart(index)} 
                                    style={{ position: 'absolute', right: 0, top: 0 }}>
                                        {text_resources["delete"][language]}
                                </button>
                            }
                            <hr />
                        </div>
                    ))}
                    <button className='btn btn-success' onClick={handleAddPieChart}>{text_resources["addPieChart"][language]}</button>
                    <hr className="hr-bright" />
                </div>
            </div>
            <button className='btn btn-secondary mb-3 mt-3' onClick={handleDownloadPdf}>{text_resources["downloadPDF"][language]}</button>
        </section>
    );
};
