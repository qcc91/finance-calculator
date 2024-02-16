// AppRouter.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './Navbar';
import Home from './Home'; 
import HoldingsShow from './HoldingsShow'; 
import HoldingsAnalyse from './HoldingsAnalyse'; 
import DataImport from './DataImport'; 
import DataEdit from './DataEdit'; 
import MarketVar from './MarketVar'; 
import DataEtl from './DataETLTaskShow';

const MarketInterest = () => <div>利率类敏感性内容</div>;
const MarketEquity = () => <div>权益类敏感性内容</div>;
const MarketBond = () => <div>债券估值内容</div>;
const MarketDerivative = () => <div>衍生品估值内容</div>;

const AppRouter = () => {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/holdings/show" element={<HoldingsShow />} />
        <Route path="/holdings/analyse" element={<HoldingsAnalyse />} />
        <Route path="/market/var" element={<MarketVar />} />
        <Route path="/market/sensitivity/interest" element={<MarketInterest />} />
        <Route path="/market/sensitivity/equity" element={<MarketEquity />} />
        <Route path="/market/valuation/bond" element={<MarketBond />} />
        <Route path="/market/valuation/derivative" element={<MarketDerivative />} />
        <Route path="/data/collect/import" element={<DataImport />} />
        <Route path="/data/collect/etl" element={<DataEtl />} />
        <Route path="/data/edit" element={<DataEdit />} />
      </Routes>
    </Router>
  );
}

export default AppRouter;
