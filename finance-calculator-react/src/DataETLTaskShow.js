import React, { useState, useEffect, useRef } from 'react';
import './DataETLTaskShow.css';
import Axios from 'axios';

import DataETLTaskModify from './DataETLTaskModify';


const DataETLTaskShow = () => {

  const [tableData, setTableData] = useState([]);
  const [filters, setFilters] = useState({
    selectedTaskId: '',
    selectedTaskName: ''
  });

  const [selectedRow, setSelectedRow] = useState(null);
  const [showModifyModal, setShowModifyModal] = useState(false);
  const [rowData, setRowData] = useState({});
  const tableRef = useRef(null); 
  const modifyModalRef = useRef(null);

  const fetchData = () => {
    Axios.get('http://localhost:3000/data/collect/etl/task/show', { params: filters })
      .then((response) => {
        if (Array.isArray(response.data)) {
          setTableData(response.data);
        } else {
          console.error('Received data is not an array:', response.data);
        }
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
      });
  };

  const handleClickOutside = (event) => {
    if (
      tableRef.current &&
      !tableRef.current.contains(event.target)&&
      !event.target.classList.contains('modify-button')
    ) {
      setSelectedRow(null);
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside); // 添加点击事件监听器
    return () => {
      document.removeEventListener('mousedown', handleClickOutside); // 移除点击事件监听器
    };
  }, []); 

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters({
      ...filters,
      [name]: value
    });
  };

  const handleFilterSubmit = () => {
    fetchData();
  };

  const handleRowClick = (index) => {
    setSelectedRow(index);
    setRowData(tableData[index]);
  };

  const handleModify = () => {
    setShowModifyModal(true);
  };

  const refreshData = async () => {
    try {
      const response = await Axios.get('http://localhost:3000/data/collect/etl/task/show',  { params: filters });
      if (Array.isArray(response.data)) {
        setTableData(response.data);
      } else {
        console.error('Received data is not an array:', response.data);
      }
    } catch (error) {
      console.error('Error refreshing data:', error);
    }
  };
 
  return (
    <div>
      <h2>ETL任务设置</h2>
      <div className="filter-bar">
        <label htmlFor="taskId">任务ID：</label>
        <input type="text" id="taskId" name="selectedTaskId" value={filters.selectedStartDate} onChange={handleFilterChange} />
        <label htmlFor="taskName">任务名称：</label>
        <input type="text" id="taskName" name="selectedTaskName" value={filters.selectedTaskName} onChange={handleFilterChange} />
        <button onClick={handleFilterSubmit}>查询</button>
      </div>
      <section>
        <div className="table-container-holding">
          <h3>任务列表
              <button className="modify-button" onClick={handleModify} disabled={selectedRow === null}>修改</button>
          </h3>
          <table ref={tableRef}>
            <thead>
              <tr>
                <th>任务ID</th>
                <th>任务名称</th>
                <th>任务执行时间</th>
                <th>任务开关</th>
              </tr>
            </thead>
            <tbody>
              {tableData.map((task, index) => (
                <tr
                  key={task.id}
                  className={selectedRow === index ? 'selected' : ''}
                  onClick={() => handleRowClick(index)}
                >
                  <td>{task.task_id}</td>
                  <td>{task.task_name}</td>
                  <td>{task.task_time}</td>
                  <td>{task.task_switch}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      {showModifyModal && rowData && (
        <div ref={modifyModalRef}>
          <DataETLTaskModify
            showModifyModal={showModifyModal}
            setShowModifyModal={setShowModifyModal}
            refreshData={refreshData}
            rowData={rowData}
          />
        </div>
       )}
    </div>
  );
};

export default DataETLTaskShow;
