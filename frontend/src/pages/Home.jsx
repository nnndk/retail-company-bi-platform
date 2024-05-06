import { useState } from 'react';
import { authHeader } from 'tools/fetch-wrapper';

export const Home = () => {
    const [imageSrc, setImageSrc] = useState('');

    async function sendExcel() {
        const fileInput = document.getElementById('fileInput');
        if (fileInput.files.length === 0) {
            console.error('No file selected');
            return;
        }
    
        const file = fileInput.files[0];
        const factColumnNamesInput = document.getElementById('factColumnNames');
        const factColumnNames = factColumnNamesInput.value.split(',').map(col => col.trim());
        const formData = new FormData();
        formData.append('file', file);
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

            const html = await response.text(); // Get HTML response
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const imgElement = doc.querySelector('img'); // Find img element
            const src = imgElement.getAttribute('src');
            setImageSrc(src);
        } catch (error) {
            console.error('Error uploading Excel file:', error);
        }
    }

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'center' }} className='mb-5' id='excelUploadForm'>
                <div>
                    <h1 className='mb-3'>Analyze your data</h1>
                    <h5 className='mb-5'>Upload your data in .xlsx format to analyze it</h5>
                    <span>Upload Excel file with your data:</span>
                    <br />
                    <input className='mb-3 mt-1' type="file" id="fileInput" />
                    <br />
                    <span>Write fact column names:</span>
                    <br />
                    <input className='mb-3 mt-1' type="text" id="factColumnNames" placeholder="Enter fact column names separated by commas" size={50}/>
                    <br />
                    <button className='mb-3 mt-3' onClick={sendExcel}>Analyze data</button>
                </div>
            </div>
            <hr />
            <div id='chartsSection' className='mt-4'>
                {imageSrc && <img src={imageSrc} alt="Matplotlib Plot" />}
            </div>
        </div>
        
    );
}
