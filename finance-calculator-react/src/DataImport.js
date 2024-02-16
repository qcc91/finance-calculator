import React, { useState } from 'react';
import ExcelUploader from './ExcelUploader';
import Axios from 'axios';
import './DataImport.css';

const DataImport = () => {
  const [uploadedData, setUploadedData] = useState(null);
  const [importing, setImporting] = useState(false);
  const [importSuccess, setImportSuccess] = useState(false);
  const [conflictAlert, setConflictAlert] = useState(false); 

  const handleUpload = (data) => {
    if (!uploadedData) {
      setUploadedData(data);
    }
  };

  const handleImport = () => {
    setImporting(true);

    // 发送数据到后台
    Axios.post('http://localhost:3000/data/collect/import', { data: uploadedData })
      .then(response => {
        if (response.data.message === 'Data conflict. Please Check!') {
          // 如果有冲突，弹出提示框
          setConflictAlert(true);
        } else {
          // 如果没有冲突，直接导入成功
          console.log(response.data);
          setImportSuccess(true);
        }
      })
      .catch(error => {
        console.error('Error importing data:', error);
      })
      .finally(() => {
        // 无论请求成功还是失败，都在最终结束时设置导入状态为 false
        setImporting(false);
      });
  };

  const handleDownloadTemplate = () => {
    // 发送 GET 请求，从后端获取文件
    Axios.get('http://localhost:3000/data/collect/import/download/input_template', {
      responseType: 'arraybuffer', // 告诉 Axios 服务器响应的数据是二进制数据
    })
      .then(response => {
        // 创建 Blob 对象并设置 MIME 类型
        const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

        // 创建下载链接
        const downloadLink = document.createElement('a');
        downloadLink.href = URL.createObjectURL(blob);
        downloadLink.download = 'input_Data.xlsx'; // 设置下载文件的名称

        // 将链接添加到文档，并触发点击
        document.body.appendChild(downloadLink);
        downloadLink.click();

        // 清理创建的链接
        document.body.removeChild(downloadLink);
      })
      .catch(error => {
        console.error('下载模板时出错：', error);
      });
  };

  const handleDelete = () => {
    setUploadedData(null);
  };

  const handleConfirm = () => {
    setConflictAlert(false);
    setImportSuccess(false);
  };

  return (
    <div>
      <h2>数据导入</h2>
      <div className="filter-bar">
        <label htmlFor="excel-uploader">请上传文件：</label>
        <div className="excel-uploader-container">
          <ExcelUploader onUpload={handleUpload} onDelete={handleDelete} />
        </div>
        <div className="button-bar">
          <button onClick={handleImport}>导入</button>
          <button onClick={handleDownloadTemplate}>下载模板</button>
        </div>
      </div>
      {conflictAlert && (
        <div className="importing-modal">
          <p>数据有冲突，请检查数据！</p>
          <button onClick={handleConfirm}>确定</button>
        </div>
      )}
      {importing && (
        <div className="importing-modal">
          <p>正在导入...</p>
        </div>
      )}
      {importSuccess && (
        <div className="import-success-modal">
          <p>导入成功</p>
          <button onClick={handleConfirm}>确定</button>
        </div>
      )}
      {uploadedData && (
        <div className="preview-container">
          <h3>上传的数据</h3>
          <table>
            <thead>
              <tr>
                {Object.keys(uploadedData[0]).map((key) => (
                  <th key={key}>{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {uploadedData.map((row, index) => (
                <tr key={index}>
                  {Object.values(row).map((value, idx) => (
                    <td key={idx}>{value}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default DataImport;
