import { useState } from 'react';
import { authHeader } from 'tools/fetch-wrapper';

import { text_resources } from '../resources'
import { AnalyticalSection } from 'components/AnalyticalSection'


export const Main = ({ language }) => {
    const [dataFile, setDataFile] = useState(null);

    async function handleFileChange(event) {
        const file = event.target.files[0];
        setDataFile(file);
    }

    async function sendExcel() {
        const fileInput = document.getElementById('fileInput');
        if (fileInput.files.length === 0) {
            console.error('No file selected');
            return;
        }
        
        const factColumnNamesInput = document.getElementById('factColumnNames');
        const factColumnNames = factColumnNamesInput.value.split(',').map(col => col.trim());

        const formData = new FormData();
        formData.append('file', dataFile);
        formData.append('fact_column_names', factColumnNames);
    
        try {
            const url = `${process.env.REACT_APP_API_URL}/upload_excel/`;
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: authHeader(url)
            });
            
            if (!response.ok) {
                throw new Error('Failed to upload Excel file');
            }

            alert(text_resources["sentDataSuccessfully"][language]);
        } catch (error) {
            console.error('Error uploading Excel file:', error);
            alert(text_resources["sendingDataFailed"][language]);
        }
    }

    return (
        <div>
            <div className="container mt-5">
                <div className="row justify-content-center">
                    <div className="col-md-8">
                        <div className="text-center mb-5">
                            <h1 className="mb-3">{text_resources["mainPage"][language]}</h1>
                            <h5 className="mb-5">{text_resources["analyzeData"][language]}</h5>
                        </div>
                        <div className="mb-3">
                            <label аor="fileInput" className="form-label">{text_resources["uploadFile"][language]}:</label>
                            <input className="form-control-file" type="file" id="fileInput" onChange={handleFileChange} />
                        </div>
                        <div className="mb-3">
                            <label htmlFor="factColumnNames" className="form-label">{text_resources["factColumnNames"][language]}:</label>
                            <input className="form-control" type="text" id="factColumnNames" placeholder={text_resources["enterColumnNames"][language]} />
                        </div>
                        <div className="text-center">
                            <button className="btn btn-primary mb-3 mt-3" onClick={sendExcel}>{text_resources["uploadData"][language]}</button>
                        </div>
                    </div>
                </div>
            </div>
            <hr className='hr-bright' />
            <AnalyticalSection language={language} />
        </div>
    );
}
