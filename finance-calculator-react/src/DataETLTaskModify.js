import React, { useState } from 'react';
import Axios from 'axios';
import './DataETLTaskModify.css';

const DataETLTaskModify = ({ setShowModifyModal, refreshData, rowData }) => {
  const [formData, setFormData] = useState({
    task_id: (rowData && rowData.task_id) || '',
    task_name: (rowData && rowData.task_name) || '',
    task_time: (rowData && rowData.task_time) || '',
    task_switch: (rowData && rowData.task_switch) || ''
  });

  const [successModifyModal, setSuccessModifyModal] = useState(false); 

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleModifyModalConfirm = async (event) => {
    event.preventDefault();
    try {
      // 发送更新数据请求到后端
      await Axios.put('http://localhost:3000/data/collect/etl/task/set', {
        ...rowData, // 传递原始数据，用于确定要更新的记录
        ...formData // 更新的字段数据
      });
      // 刷新数据
      await refreshData();
      // 关闭模态框
      setSuccessModifyModal(true);
    } catch (error) {
      console.error('Error updating data:', error);
      // 处理更新失败情况
    }
  };

  const handleModifyModalClose = () => {
    setShowModifyModal(false);
  };

  const handleModifySuccessConfirm = () => {
    setSuccessModifyModal(false); 
    setShowModifyModal(false);
  };

  return (
    <div className="modify-modal">
      <p>任务修改</p>
      <form onSubmit={handleModifyModalConfirm}>
        <label htmlFor="taskTime">任务时间：</label>
        <input type="time" id = "taskTime" name="task_time" value={formData.task_time} onChange={handleChange} placeholder="任务时间" />
        <label htmlFor="taskSwitch">任务开关：</label>
        <select id="taskSwitch" name="task_switch" value={formData.task_switch} onChange={handleChange}>
          <option value="开">开</option>
          <option value="关">关</option>
        </select>
        <button type="submit">确定</button>
        <button type="button" onClick={handleModifyModalClose}>关闭</button>
      </form>
      {successModifyModal && (
        <div className="success-modal">
          <p>任务修改成功！</p>
          <button onClick={handleModifySuccessConfirm}>确定</button>
        </div>
      )}
    </div>
  );
};

export default DataETLTaskModify;
