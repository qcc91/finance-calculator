// ExcelUploader.js
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import * as XLSX from 'xlsx';
import './ExcelUploader.css';

const ExcelUploader = ({ onUpload, onDelete }) => {
  const [uploadedData, setUploadedData] = useState(null);
  const [fileName, setFileName] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];

    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (e) => {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: 'array' });

      // Assume Excel file has only one sheet
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];

      // Convert Excel data to JSON format
      const jsonData = XLSX.utils.sheet_to_json(sheet);

      setUploadedData(jsonData);
      onUpload(jsonData);
    };

    reader.readAsArrayBuffer(file);
  }, [onUpload]);

  const handleDelete = () => {
    setUploadedData(null);
    setFileName('');
    onDelete();
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: '.xls, .xlsx',
    multiple: false,
  });

  return (
    <div className="dropzone">
      <div className="file-info">
        <p>{fileName}</p>
        {fileName && <button onClick={handleDelete}>X</button>}
      </div>
      {!fileName && (
        <div {...getRootProps()} className="file-dropzone">
          <input {...getInputProps()} />
          <p>请拖拽或者上传文件到此处</p>
        </div>
      )}
    </div>
  );
};

export default ExcelUploader;
