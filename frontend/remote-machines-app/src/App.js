// src/App.js
import React, { useState } from 'react';
import api from './api';
import './App.css'; // Add this line to import the CSS file

function App() {
  const [ipAddress, setIpAddress] = useState('');
  const [contactInfo, setContactInfo] = useState('');
  const [machines, setMachines] = useState([]);
  const [error, setError] = useState(null);

  const searchByIpAddress = async () => {
    try {
      const data = await api.getMachineByIpAddress(ipAddress);
      setMachines([data]);
      setError(null);
    } catch (error) {
      setError({
        message: 'An error occurred',
        status: error.response?.status,
        data: error.response?.data?.detail,
      });
    }
  };

  const searchByContactInfo = async () => {
    try {
      const data = await api.getMachinesByContactInfo(contactInfo);
      setMachines(data);
      setError(null);
    } catch (error) {
      setError({
        message: 'An error occurred',
        status: error.response?.status,
        data: error.response?.data?.detail,
      });
    }
  };

  const getAllMachines = async () => {
    try {
      const data = await api.getAllMachines();
      setMachines(data);
      setError(null);
    } catch (error) {
      setError({
        message: 'An error occurred',
        status: error.response?.status,
        data: error.response?.data?.detail,
      });
    }
  };

  return (
    <div className="App">
      <h1>Remote Machines</h1>
      <input
        type="text"
        value={ipAddress}
        onChange={(e) => setIpAddress(e.target.value)}
        placeholder="IP Address"
      />
      <button onClick={searchByIpAddress}>Search by IP Address</button>
      <br />
      <input
        type="text"
        value={contactInfo}
        onChange={(e) => setContactInfo(e.target.value)}
        placeholder="Contact Info"
      />
      <button onClick={searchByContactInfo}>Search by Contact Info</button>
      <br />
      <button onClick={getAllMachines}>Get All Machines</button>
      {error && (
        <div className="error">
          <p>{error.message}</p>
          {error.status && <p>Status: {error.status}</p>}
          {error.data && <p>Detail: {error.data}</p>}
        </div>
      )}
      <table>
        <thead>
          <tr>
            <th>IP Address</th>
            <th>Description</th>
            <th>Contact Info</th>
          </tr>
        </thead>
        <tbody>
          {machines.map((machine, index) => (
            <tr key={index}>
              <td>{machine.ip_address}</td>
              <td>{machine.description}</td>
              <td>{machine.contact_info}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
