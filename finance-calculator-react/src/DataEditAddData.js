import React, { useState } from 'react';
import Axios from 'axios';
import './DataEditAddData.css';

const DadaEditAddData = ({ showAddModal, setShowAddModal, refreshData }) => {
  const [formData, setFormData] = useState({
    tradeDate: '',
    company: '',
    department: '',
    portfolioCode: '',
    stockSymbol: '',
    stockName: '',
    amount: '',
    cost: '',
    closePrice:'',
    marketValue: '',
    industry: '',
  });

  const [conflictModal, setConflictModal] = useState(false); // 控制冲突提示框的显示
  const [successModal, setSuccessModal] = useState(false); 

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleAddModalConfirm = async () => {
    try {
      const response = await Axios.post('http://localhost:3000/data/edit/add', formData);
      if (response.status === 200 ) {
        setConflictModal(true); // 显示冲突提示框
        console.log('Conflict modal is shown'); // 输出信息到控制台
      } else if (response.status === 201 && response.data.message === 'Data added successfully!') {
        setSuccessModal(true);
        refreshData(); // 刷新数据
        console.log('Success modal is shown'); // 输出信息到控制台
      }
    } catch (error) {
      console.error('Error adding data:', error);
    }
  };

  const handleAddModalClose = () => {
    setShowAddModal(false);
  };

  const handleAddConflictConfirm = () =>{
    setConflictModal(false); 
  }

  const handleAddSuccessConfirm = () =>{
    setSuccessModal(false); 
    setShowAddModal(false);
  }

  return (
    <div>
      {showAddModal && (
        <div className="add-modal">
          <p>数据新增</p>
          <div className="add-modal-input">
          <label htmlFor="addTradeDate">业务日期：</label>
          <input type="date" id="addTradeDate" name="tradeDate" value={formData.tradeDate} onChange={handleInputChange} />
          <label htmlFor="addCompany">公司名称：</label>
          <input type="text" id="addCompany" name="company" value={formData.company} onChange={handleInputChange} />
          <label htmlFor="addDepartment">部门：</label>
          <input type="text" id="addDepartment" name="department" value={formData.department} onChange={handleInputChange} />
          <label htmlFor="addPortfolioCode">组合代码：</label>
          <input type="text" id="addPortfolioCode" name="portfolioCode" value={formData.portfolioCode} onChange={handleInputChange} />
          <label htmlFor="addStockSymbol">证券代码：</label>
          <input type="text" id="addStockSymbol" name="stockSymbol" value={formData.stockSymbol} onChange={handleInputChange} />
          <label htmlFor="addStockName">证券名称：</label>
          <input type="text" id="addStockName" name="stockName" value={formData.stockName} onChange={handleInputChange} />
          <label htmlFor="addAmount">数量：</label>
          <input type="text" id="addAmount" name="amount" value={formData.amount} onChange={handleInputChange} />
          <label htmlFor="addCost">成本：</label>
          <input type="text" id="addCost" name="cost" value={formData.cost} onChange={handleInputChange} />
          <label htmlFor="addCloesPrice">收盘价：</label>
          <input type="text" id="addCloesPrice" name="closePrice" value={formData.closePrice} onChange={handleInputChange} />
          <label htmlFor="addMarketValue">市值：</label>
          <input type="text" id="addMarketValue" name="marketValue" value={formData.marketValue} onChange={handleInputChange} />
          <label htmlFor="addIndustry">所属行业：</label>
          <input type="text" id="addIndustry" name="industry" value={formData.industry} onChange={handleInputChange} />
          <button onClick={handleAddModalConfirm}>确定</button>
          <button onClick={handleAddModalClose}>关闭</button>
          </div>
        </div>
      )}
           {conflictModal && (
            <div className="conflict-modal">
                <p>录入数据有冲突，请检查！</p>
                <button onClick={handleAddConflictConfirm}>确定</button>
            </div>
          )}
            {successModal && (
            <div className="success-modal">
                <p>录入成功！</p>
                <button onClick={handleAddSuccessConfirm}>确定</button>
            </div>
            )}
    </div>
  );
};
export default DadaEditAddData;
