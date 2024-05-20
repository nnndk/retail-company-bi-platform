import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { text_resources } from '../resources'


export const DataLineChart = ({ language, periodGroup, cubeInfo, cubeData }) => {
    const [filteredData, setFilteredData] = useState([]);
    const [filters, setFilters] = useState({});

    useEffect(() => {
        setFilteredData(cubeData);
        
        let newFilters = {}

        for (let key in cubeInfo['dimensions']) {
            newFilters[key] = 'all'
        }

        setFilters(newFilters)
        setFilteredData(sumByData(cubeData))
    }, [cubeData, periodGroup]);

    const handleFilterChange = (dimension, value) => {
        const newFilters = { ...filters, [dimension]: value };
        setFilters(newFilters);

        const filtered = cubeData.filter(item => {
            return Object.keys(newFilters).every(key => {
                if (newFilters[key] === '') return true;
                return item[key] === newFilters[key] || newFilters[key] === 'all';
            });
        });

        let summarized_data = sumByData(filtered)
        setFilteredData(summarized_data);
    };

    const sumByData = (rawData) => {
        // Группируем объекты по значению поля Data
        const groupedByData = {};
        rawData.forEach(obj => {
            if (!groupedByData[obj.Data]) {
                groupedByData[obj.Data] = [];
            }
            groupedByData[obj.Data].push(obj);
        });

        // Суммируем значения факта для каждой группы
        const sumByData = [];

        for (let data in groupedByData) {
            let sum = 0;
            groupedByData[data].forEach(obj => {
                sum += obj.Kolichestvo;
            });
            
            sumByData.push({'Data': data, [cubeInfo['fact']]: sum})
        }

        return sumByData;
    }

    const renderFilters = () => {
        if (!cubeInfo['dimensions']) return '';
        
        return Object.keys(cubeInfo['dimensions']).map(dimension => (
            <div key={dimension}>
                <label className="mr-2">{dimension}:</label>
                <select onChange={(e) => handleFilterChange(dimension, e.target.value)} defaultValue='all'>
                    <option key='all' value='all'>{text_resources["all"][language]}</option>
                    {cubeInfo['dimensions'][dimension].map(value => (
                        <option key={value} value={value}>{value}</option>
                    ))}
                </select>
            </div>
        ));
    };

    return (
        <div className='my-4'>
            {renderFilters()}
            <ResponsiveContainer width="100%" height={300}>
                <LineChart
                    data={filteredData}
                    margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="Data" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey={cubeInfo['fact']} stroke="#8884d8" />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};
