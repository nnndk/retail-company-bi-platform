import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import { text_resources } from '../resources'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A28AD4', '#D32F2F'];


export const DataPieChart = ({ language, cubeInfo, cubeData, periodGroup }) => {
    const [filteredData, setFilteredData] = useState([]);
    const [selectedDimension, setSelectedDimension] = useState('');
    const [periodOptions, setPeriodOptions] = useState([]);
    const [selectedPeriod, setSelectedPeriod] = useState('all');

    useEffect(() => {
        if (cubeInfo && cubeInfo['dimensions'] && Object.keys(cubeInfo['dimensions']).length > 0) {
            setSelectedDimension(Object.keys(cubeInfo['dimensions'])[0]);
            updatePeriodOptions(cubeInfo['dimensions']);
        }
    }, [cubeInfo['dimensions']]);

    useEffect(() => {
        updatePeriodOptions(cubeInfo);
    }, [periodGroup, cubeInfo]);

    useEffect(() => {
        filterData();
    }, [selectedDimension, selectedPeriod, cubeData]);

    const updatePeriodOptions = (cubeInfo) => {
        let options = [];
        const minDate = new Date(cubeInfo.min_date);
        const maxDate = new Date(cubeInfo.max_date);

        if (periodGroup === 'month') {
            let current = new Date(minDate.getFullYear(), minDate.getMonth(), 1);

            while (current <= maxDate) {
                current.setMonth(current.getMonth() + 1);
                options.push(current.toISOString().slice(0, 7)); // YYYY-MM
            }
        } else if (periodGroup === 'year') {
            let currentYear = minDate.getFullYear();
            const maxYear = maxDate.getFullYear();

            while (currentYear <= maxYear) {
                options.push(currentYear.toString());
                currentYear++;
            }
        }

        setPeriodOptions(options);
        setSelectedPeriod('all');
    };

    const filterData = () => {
        let data = cubeData;

        if (selectedPeriod !== 'all') {
            data = data.filter(item => {
                if (periodGroup === 'month') {
                    return item.Data.startsWith(selectedPeriod);
                } else if (periodGroup === 'year') {
                    return item.Data.startsWith(selectedPeriod);
                }
                return true;
            });
        }

        let summarized_data = sumByDim(data, selectedDimension)
        setFilteredData(summarized_data);
    };

    const sumByDim = (rawData, dim) => {
        // Группируем объекты по значению поля Data
        const groupedByDim = {};
        rawData.forEach(obj => {
            if (!groupedByDim[obj[dim]]) {
                groupedByDim[obj[dim]] = [];
            }

            groupedByDim[obj[dim]].push(obj);
        });

        // Суммируем значения поля Kolichestvo для каждой группы
        const sumByDim = [];

        for (let dimVal in groupedByDim) {
            let sum = 0;
            groupedByDim[dimVal].forEach(obj => {
                sum += obj.Kolichestvo;
            });
            
            sumByDim.push({dim: dimVal, [cubeInfo['fact']]: sum})
        }

        return sumByDim;
    }

    const handleDimSelection = (val) => {
        setSelectedDimension(val)
        filterData()
    }

    const handlePeriodSelection = (val) => {
        setSelectedPeriod(val)
        filterData()
    }

    return (
        <div className='my-4'>
            <div>
                <label className="mr-2">Select Dimension:</label>
                <select onChange={(e) => handleDimSelection(e.target.value)} value={selectedDimension || ""}>
                    {selectedDimension && Object.keys(cubeInfo['dimensions']).map(dimension => (
                        <option key={dimension} value={dimension}>{dimension}</option>
                    ))}
                </select>
            </div>
            <div>
                <label className="mr-2">Select Period:</label>
                <select onChange={(e) => handlePeriodSelection(e.target.value)} value={selectedPeriod}>
                    <option key='all' value='all'>{text_resources["allPeriod"][language]}</option>
                    {periodOptions.map(option => (
                        <option key={option} value={option}>{option}</option>
                    ))}
                </select>
            </div>
            <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                    <Pie
                        data={filteredData}
                        dataKey={cubeInfo['fact']}
                        nameKey="dim"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        fill="#8884d8"
                        label
                    >
                        {filteredData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};