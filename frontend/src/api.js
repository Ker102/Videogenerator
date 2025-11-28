import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const generateVideo = async (formData) => {
    const response = await axios.post(`${API_URL}/generate`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getStatus = async (operationName) => {
    const response = await axios.get(`${API_URL}/status/${operationName}`);
    return response.data;
};

export const getVideoUrl = (filename) => {
    // If filename is a full URL or path, handle it?
    // The backend returns /videos/{filename}
    if (filename.startsWith('http')) return filename;
    return `${API_URL}${filename}`;
}
