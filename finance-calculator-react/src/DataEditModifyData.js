import React, { useState } from 'react';
import Axios from 'axios';
import './DataEditModifyData.css';

const DataEditModifyData = ({ setShowModifyModal, refreshData, rowData }) => {
  const [formData, setFormData] = useState({
    amount: (rowData && rowData.amount) || 0,
    cost: (rowData && rowData.cost) || 0,
    marketValue: (rowData && rowData.market_value) || 0,
    closePrice: (rowData && rowData.close_price) || 0,
    industry: (rowData && rowData.industry) || '',
    tradeDate: (rowData && rowData.trade_date) || '',
    company: (rowData && rowData.company) || '',
    department: (rowData && rowData.department) || '',
    portfolioCode: (rowData && rowData.portfolio_code) || '',
    stockSymbol: (rowData && rowData.stock_symbol) || '',
    stockName: (rowData && rowData.stock_name) || ''
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
      await Axios.put('http://localhost:3000/data/edit/update', {
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
      <p>数据修改</p>
      <div className="modify-modal-input">
      <form onSubmit={handleModifyModalConfirm}>
        <label htmlFor="ModifyAmount">数量：</label>
        <input type="number" id = "ModifyAmount" name="amount" value={formData.amount} onChange={handleChange} placeholder="数量" />
        <label htmlFor="ModifyCost">成本：</label>
        <input type="number" id = "ModifyCost"name="cost" value={formData.cost} onChange={handleChange} placeholder="成本" />
        <label htmlFor="ModifyMarketValue">市值：</label>
        <input type="number" id = "ModifyMarketValue" name="marketValue" value={formData.marketValue} onChange={handleChange} placeholder="市值" />
        <label htmlFor="ModifyClosePrice">收盘价：</label>
        <input type="number" id = "ModifyClosePrice" name="closePrice" value={formData.closePrice} onChange={handleChange} placeholder="收盘价" />
        <label htmlFor="ModifyIndustry">行业：</label>
        <input type="text" id = "ModifyIndustry" name="industry" value={formData.industry} onChange={handleChange} placeholder="行业" />
        <button type="submit">确定</button>
        <button type="button" onClick={handleModifyModalClose}>关闭</button>
      </form>
      </div>
      {successModifyModal && (
        <div className="success-modal">
          <p>数据修改成功！</p>
          <button onClick={handleModifySuccessConfirm}>确定</button>
        </div>
      )}
    </div>
  );
};

export default DataEditModifyData;
