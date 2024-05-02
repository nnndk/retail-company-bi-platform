import { useSelector } from 'react-redux';

import { fetchWrapper } from 'tools/fetch-wrapper';

export const Home = () => {
    const { user: authUser } = useSelector(x => x.auth);

    async function testPrivateApi() {
        const baseUrl = `${process.env.REACT_APP_API_URL}/auth`;
        console.log(await fetchWrapper.get(`${baseUrl}/test`))
    }

    async function sendExcel() {
        const fileInput = document.getElementById('fileInput');
        if (fileInput.files.length === 0) {
            console.error('No file selected');
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        try {
            const url = `${process.env.REACT_APP_API_URL}/upload_excel`;
            const response = await fetchWrapper.post(url)

            if (!response.ok) {
                throw new Error('Failed to upload Excel file');
            }
            
            console.log('Excel file uploaded successfully');
        } catch (error) {
            console.error('Error uploading Excel file:', error);
        }
    }

    return (
        <div>
            <h1>Hi {authUser?.user_info.username}!</h1>
            <button onClick={testPrivateApi}>Test private api</button>
            <input type="file" id="fileInput" />
            <button onClick={sendExcel}>Send excel</button>
        </div>
    );
}
